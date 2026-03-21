"""Groq API provider using the official groq SDK.

Environment variable: GROQ_API_KEY
Default model: llama-3.1-8b-instant

Install: uv add groq
See https://console.groq.com/docs/deprecations for decommissioned models.
"""
from __future__ import annotations

import os
import threading
import logging
import time
from collections import deque

from .base_model import BaseModel

logger = logging.getLogger(__name__)

# Current Groq models (as of 2025-Q4). Old llama3-*-8192 names are decommissioned.
_KNOWN_MODELS = [
    "llama-3.1-8b-instant",         # fast, default
    "llama-3.3-70b-versatile",      # most capable
    "llama-3.1-70b-versatile",      # alternative 70B
    "llama3-groq-8b-8192-tool-use-preview",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

# Minimum seconds to wait after a rate-limit error, with jitter applied on top.
_MIN_RATE_LIMIT_WAIT = 5.0

# Groq free-tier limits (can be overridden with environment variables).
_GROQ_WINDOW_SECONDS = 60.0
_DEFAULT_GROQ_RPM_LIMIT = 30
_DEFAULT_GROQ_TPM_LIMIT = 6000


class GroqModel(BaseModel):
    """Uses the official Groq SDK to call the chat completions endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is required. "
                "Get one at https://console.groq.com/keys"
            )
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "Install the groq package to use GroqModel: uv add groq"
            ) from exc

        self._client = Groq(api_key=api_key)
        self.model = model
        self.model_name = f"groq:{model}"
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_cost = 0.0
        self._last_token_usage: dict = {}

        self._rpm_limit = int(os.getenv("GROQ_RPM_LIMIT", str(_DEFAULT_GROQ_RPM_LIMIT)))
        self._tpm_limit = int(os.getenv("GROQ_TPM_LIMIT", str(_DEFAULT_GROQ_TPM_LIMIT)))

        # Thread-safe rolling window accounting for requests and tokens.
        self._rate_lock = threading.Lock()
        self._request_timestamps: deque[float] = deque()
        self._token_events: deque[dict[str, float]] = deque()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_fatal_error(exc: Exception) -> None:
        """Re-raise with a helpful message for decommissioned / unknown models."""
        msg = str(exc).lower()
        if any(k in msg for k in ("decommissioned", "not found", "not active", "model_not")):
            known = ", ".join(_KNOWN_MODELS)
            raise RuntimeError(
                f"Groq model error: {exc}\n"
                f"Currently available models: {known}\n"
                f"Full list: https://console.groq.com/docs/models"
            ) from exc

    @staticmethod
    def _parse_retry_after(exc: Exception) -> float:
        """Extract the suggested wait time from a RateLimitError message."""
        import re
        msg = str(exc)
        m = re.search(
            r"(?:try again|retry after|please wait)\s+in\s+([\d.]+)\s*(s|second|ms|m|min)?",
            msg,
            re.IGNORECASE,
        )
        if m:
            value = float(m.group(1))
            unit = (m.group(2) or "s").lower()
            if unit.startswith("m") and not unit.startswith("ms"):
                value *= 60
            elif unit.startswith("ms"):
                value /= 1000
            return value
        return 0.0

    @staticmethod
    def _estimate_prompt_tokens(prompt: str) -> int:
        # Approximate token estimate for proactive TPM throttling.
        return max(1, len(prompt) // 4)

    def _prune_windows_locked(self, now: float) -> None:
        cutoff = now - _GROQ_WINDOW_SECONDS
        while self._request_timestamps and self._request_timestamps[0] <= cutoff:
            self._request_timestamps.popleft()
        while self._token_events and self._token_events[0]["ts"] <= cutoff:
            self._token_events.popleft()

    def _acquire_rate_slot(self, prompt: str, max_tokens: int | None) -> dict[str, float]:
        predicted_tokens = self._estimate_prompt_tokens(prompt) + int(max_tokens or 200)

        while True:
            with self._rate_lock:
                now = time.monotonic()
                self._prune_windows_locked(now)

                req_used = len(self._request_timestamps)
                tok_used = int(sum(evt["tokens"] for evt in self._token_events))

                if req_used < self._rpm_limit and (tok_used + predicted_tokens) <= self._tpm_limit:
                    self._request_timestamps.append(now)
                    reservation = {"ts": now, "tokens": float(predicted_tokens)}
                    self._token_events.append(reservation)
                    return reservation

                wait_req = 0.0
                if req_used >= self._rpm_limit and self._request_timestamps:
                    wait_req = max(0.0, self._request_timestamps[0] + _GROQ_WINDOW_SECONDS - now)

                wait_tok = 0.0
                if (tok_used + predicted_tokens) > self._tpm_limit and self._token_events:
                    running = tok_used
                    for evt in self._token_events:
                        running -= int(evt["tokens"])
                        if (running + predicted_tokens) <= self._tpm_limit:
                            wait_tok = max(0.0, evt["ts"] + _GROQ_WINDOW_SECONDS - now)
                            break

                wait_for = max(wait_req, wait_tok, 0.05)

            logger.info(
                "[Groq] Local throttle active: waiting %.2fs (rpm=%d/%d, tpm~%d/%d)",
                wait_for,
                req_used,
                self._rpm_limit,
                tok_used,
                self._tpm_limit,
            )
            time.sleep(wait_for)

    def _finalize_token_reservation(self, reservation: dict[str, float], actual_total_tokens: int | None) -> None:
        if actual_total_tokens is None:
            return
        with self._rate_lock:
            reservation["tokens"] = float(max(1, actual_total_tokens))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        import random
        from groq import RateLimitError, APIStatusError

        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                logger.warning(
                    "[Groq] Retry %d/%d (previous error: %s)",
                    attempt,
                    self.max_retries,
                    last_exc,
                )

            try:
                reservation = self._acquire_rate_slot(prompt, max_tokens)
                kwargs: dict = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "stream": False,
                }
                if max_tokens:
                    kwargs["max_completion_tokens"] = max_tokens

                t0 = time.time()
                completion = self._client.chat.completions.create(**kwargs)
                elapsed = time.time() - t0

                # Log response time and token usage
                usage = completion.usage
                if usage:
                    self._finalize_token_reservation(reservation, usage.total_tokens)
                    self._last_token_usage = {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens,
                    }
                    logger.info(
                        "[Groq] %.2fs | tokens: prompt=%d completion=%d total=%d",
                        elapsed,
                        usage.prompt_tokens,
                        usage.completion_tokens,
                        usage.total_tokens,
                    )
                else:
                    logger.info("[Groq] %.2fs", elapsed)

                text = completion.choices[0].message.content or ""
                text = text.strip()
                if not text:
                    finish = completion.choices[0].finish_reason or "unknown"
                    raise RuntimeError(
                        f"Groq returned empty content. finish_reason={finish!r}"
                    )
                return text

            except RateLimitError as exc:
                suggested = self._parse_retry_after(exc)
                base_wait = max(suggested, _MIN_RATE_LIMIT_WAIT)
                jitter = random.uniform(0, base_wait * 0.5)
                wait = base_wait + jitter
                logger.warning(
                    "[Groq] Rate limited (429). Waiting %.1fs (hint=%.1fs + jitter=%.1fs).",
                    wait,
                    base_wait,
                    jitter,
                )
                last_exc = exc
                time.sleep(wait)
                continue

            except APIStatusError as exc:
                # Decommissioned model or other permanent errors → fail fast
                self._check_fatal_error(exc)
                logger.error("[Groq] API error %d: %s", exc.status_code, exc.message)
                last_exc = RuntimeError(f"Groq API error ({exc.status_code}): {exc.message}")
                # Retry on 5xx only
                if exc.status_code >= 500:
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise last_exc from exc

            except Exception as exc:
                logger.error("[Groq] Unexpected error: %s", exc)
                last_exc = exc
                continue

        raise RuntimeError(
            f"Groq request failed after {self.max_retries + 1} attempts. "
            f"Last error: {last_exc}"
        )

    def get_last_cost(self) -> float:
        return self._last_cost

    def get_last_token_usage(self) -> dict:
        """Return token usage from the last successful call."""
        return self._last_token_usage
