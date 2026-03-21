"""Google Gemini provider using the REST generateContent endpoint.

Environment variable: GEMINI_API_KEY
Default model: gemini-2.0-flash

Endpoint resolution strategy:
  Tries v1 first (stable), then v1beta (preview/experimental).
  The probe uses a real generateContent call on the first request, NOT the
  models-metadata endpoint, because a model can appear in the registry on
  both versions while only supporting generateContent on one of them.
  The working version is cached (thread-safe) for all subsequent calls.
"""
from __future__ import annotations

import logging
import threading
import time

import requests

from .base_model import BaseModel
from ._rate_limit import wait_for_rate_limit

logger = logging.getLogger(__name__)

_API_ROOT = "https://generativelanguage.googleapis.com"

# Current Gemini model names.  Pass via --model-name.
_KNOWN_MODELS = [
    "gemini-2.0-flash",         # latest, fast – recommended default
    "gemini-2.0-flash-lite",    # lightweight / low-cost
    "gemini-1.5-flash",         # stable, widely available
    "gemini-1.5-flash-8b",      # smallest 1.5 variant
    "gemini-1.5-pro",           # larger 1.5 (may need paid tier)
]

# Resolution order: stable endpoint first, then preview.
_API_VERSIONS = ("v1", "v1beta")


class GeminiModel(BaseModel):
    """Calls the Google Gemini generateContent REST endpoint.

    On the very first call the model tries each API version in order
    (v1 → v1beta) using a real generateContent request.  The first version
    that does NOT return a 404 is cached and used for every subsequent call,
    so there is zero overhead after warm-up.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Get one at https://aistudio.google.com/app/apikey"
            )
        self.api_key = api_key
        self.model = model
        self.model_name = f"gemini:{model}"
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_cost = 0.0
        self._last_token_usage: dict = {}

        # Thread-safe version caching
        self._api_version: str | None = None
        self._version_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, version: str) -> str:
        return (
            f"{_API_ROOT}/{version}/models/{self.model}"
            f":generateContent?key={self.api_key}"
        )

    def _build_payload(self, prompt: str, max_tokens: int | None) -> dict:
        payload: dict = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        return payload

    @staticmethod
    def _parse_response(payload: dict) -> str:
        """Extract text from a Gemini generateContent response."""
        candidates = payload.get("candidates") or []
        if not candidates:
            feedback = payload.get("promptFeedback", {})
            block_reason = feedback.get("blockReason", "")
            raise RuntimeError(
                f"Gemini returned no candidates. blockReason={block_reason!r}"
            )
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        texts = [p.get("text", "") for p in parts if "text" in p]
        text = "".join(texts).strip()
        if not text:
            finish = candidates[0].get("finishReason", "unknown")
            raise RuntimeError(
                f"Gemini candidate has empty text. finishReason={finish!r}"
            )
        return text

    @staticmethod
    def _extract_token_usage(payload: dict) -> dict:
        meta = payload.get("usageMetadata") or {}
        return {
            "prompt_tokens": meta.get("promptTokenCount", 0),
            "completion_tokens": meta.get("candidatesTokenCount", 0),
            "total_tokens": meta.get("totalTokenCount", 0),
        }

    def _get_api_version(self) -> str:
        """Return the cached API version (fast path, no lock needed)."""
        return self._api_version  # type: ignore[return-value]

    def _post(self, version: str, payload: dict) -> requests.Response:
        return requests.post(
            self._url(version),
            json=payload,
            timeout=self.timeout,
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        payload = self._build_payload(prompt, max_tokens)

        # --- Fast path: version already resolved, just call the API ---
        if self._api_version is not None:
            return self._call_with_retries(self._api_version, payload)

        # --- Slow path: find the right API version (runs once per model instance) ---
        with self._version_lock:
            # Double-check after acquiring lock
            if self._api_version is not None:
                return self._call_with_retries(self._api_version, payload)

            last_404_body = ""
            for version in _API_VERSIONS:
                t0 = time.time()
                try:
                    response = self._post(version, payload)
                    elapsed = time.time() - t0
                    logger.info(
                        "[Gemini] Version probe %s → HTTP %d in %.2fs",
                        version,
                        response.status_code,
                        elapsed,
                    )

                    if response.status_code == 404:
                        last_404_body = response.text[:300]
                        logger.debug(
                            "[Gemini] Model not available on %s (404), trying next",
                            version,
                        )
                        continue  # Try the next version

                    # Non-404 response (success OR a different error like 403/429)
                    # Lock in this version and let _call_with_retries handle the result
                    self._api_version = version
                    logger.info("[Gemini] Locked API version: %s", version)

                    if response.ok:
                        data = response.json()
                        self._last_token_usage = self._extract_token_usage(data)
                        logger.info("[Gemini] Token usage: %s", self._last_token_usage)
                        return self._parse_response(data)

                    # Non-404 error (e.g. 429 rate limit) – delegate to retry logic
                    return self._call_with_retries(version, payload)

                except requests.Timeout:
                    # Timeout counts as "this version might work, keep it"
                    self._api_version = version
                    logger.warning("[Gemini] Probe timed out on %s, using it anyway", version)
                    return self._call_with_retries(version, payload)
                except requests.RequestException as exc:
                    logger.error("[Gemini] Network error probing %s: %s", version, exc)
                    self._api_version = version
                    return self._call_with_retries(version, payload)

            # All versions returned 404 → model name is wrong or not accessible
            known = ", ".join(_KNOWN_MODELS)
            hint = f"\nLast API response: {last_404_body}" if last_404_body else ""
            raise RuntimeError(
                f"Gemini model '{self.model}' returned 404 on all API versions "
                f"({', '.join(_API_VERSIONS)}).\n"
                f"Check the model name. Known working models: {known}\n"
                f"Full model list: https://ai.google.dev/gemini-api/docs/models{hint}"
            )

    def _call_with_retries(self, version: str, payload: dict) -> str:
        """POST to a known-good version with retry/backoff logic."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                wait = 2 ** attempt
                logger.warning(
                    "[Gemini] Retry %d/%d after %ds (previous error: %s)",
                    attempt,
                    self.max_retries,
                    wait,
                    last_exc,
                )
                time.sleep(wait)

            t0 = time.time()
            try:
                response = self._post(version, payload)
                elapsed = time.time() - t0
                logger.info("[Gemini] HTTP %d in %.2fs", response.status_code, elapsed)

                if response.status_code == 404:
                    # Model vanished from a previously-working version (e.g. deprecated)
                    known = ", ".join(_KNOWN_MODELS)
                    raise RuntimeError(
                        f"Gemini model '{self.model}' is no longer available "
                        f"on the {version} endpoint (404).\n"
                        f"Known working models: {known}"
                    )

                if not response.ok:
                    body = response.text[:400]
                    last_exc = RuntimeError(
                        f"Gemini API error ({response.status_code}): {body}"
                    )
                    if response.status_code == 429:
                        wait_for_rate_limit(response, "Gemini", attempt)
                        continue
                    # Retry on other transient server errors
                    if response.status_code in (500, 502, 503, 504):
                        time.sleep(2 ** (attempt + 1))
                        continue
                    raise last_exc  # Non-retryable (e.g. 400, 403)

                data = response.json()
                self._last_token_usage = self._extract_token_usage(data)
                logger.info("[Gemini] Token usage: %s", self._last_token_usage)
                return self._parse_response(data)

            except RuntimeError:
                raise  # Already a clean error; propagate immediately
            except requests.Timeout as exc:
                elapsed = time.time() - t0
                logger.warning("[Gemini] Request timed out after %.2fs", elapsed)
                last_exc = exc
                continue
            except requests.RequestException as exc:
                logger.error("[Gemini] Request failed: %s", exc)
                last_exc = exc
                continue

        raise RuntimeError(
            f"Gemini request failed after {self.max_retries + 1} attempts: {last_exc}"
        )

    def get_last_cost(self) -> float:
        return self._last_cost

    def get_last_token_usage(self) -> dict:
        """Return token usage from the last successful call."""
        return self._last_token_usage
