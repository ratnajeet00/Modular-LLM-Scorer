"""Together AI provider – OpenAI-compatible chat completions endpoint.

Environment variable: TOGETHER_API_KEY
Default model: mistralai/Mistral-7B-Instruct-v0.3
Endpoint: https://api.together.xyz/v1/chat/completions
"""
from __future__ import annotations

import logging
import time

import requests

from .base_model import BaseModel
from ._rate_limit import wait_for_rate_limit

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.together.xyz/v1"


class TogetherModel(BaseModel):
    """Calls the Together AI OpenAI-compatible chat/completions endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = "mistralai/Mistral-7B-Instruct-v0.3",
        timeout: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError(
                "TOGETHER_API_KEY is required. "
                "Get one at https://api.together.xyz/settings/api-keys"
            )
        self.api_key = api_key
        self.model = model
        self.model_name = f"together:{model}"
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_cost = 0.0
        self._last_token_usage: dict = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, prompt: str, max_tokens: int | None) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        return payload

    @staticmethod
    def _parse_response(payload: dict) -> str:
        """Extract text from an OpenAI-style response."""
        choices = payload.get("choices") or []
        if not choices:
            raise RuntimeError("Together AI returned no choices in response")
        message = choices[0].get("message") or {}
        text = message.get("content", "").strip()
        if not text:
            finish = choices[0].get("finish_reason", "unknown")
            raise RuntimeError(
                f"Together AI choice has empty content. finish_reason={finish!r}"
            )
        return text

    @staticmethod
    def _extract_token_usage(payload: dict) -> dict:
        usage = payload.get("usage") or {}
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }

    @staticmethod
    def _is_retryable(status_code: int) -> bool:
        return status_code in (429, 500, 502, 503, 504)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        url = f"{_BASE_URL}/chat/completions"
        current_max_tokens = max_tokens
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                logger.warning(
                    "[Together] Retry %d/%d (previous error: %s)",
                    attempt,
                    self.max_retries,
                    last_exc,
                )

            payload = self._build_payload(prompt, current_max_tokens)
            t0 = time.time()
            try:
                response = requests.post(
                    url,
                    headers=self._headers(),
                    json=payload,
                    timeout=self.timeout,
                )
                elapsed = time.time() - t0
                logger.info("[Together] HTTP %d in %.2fs", response.status_code, elapsed)

                if not response.ok:
                    body = response.text[:400]
                    last_exc = RuntimeError(
                        f"Together AI error ({response.status_code}): {body}"
                    )
                    if response.status_code == 429:
                        wait_for_rate_limit(response, "Together", attempt)
                        continue
                    if self._is_retryable(response.status_code):
                        time.sleep(2 ** (attempt + 1))
                        continue
                    raise last_exc

                data = response.json()
                self._last_token_usage = self._extract_token_usage(data)
                logger.info("[Together] Token usage: %s", self._last_token_usage)
                text = self._parse_response(data)
                return text

            except requests.Timeout as exc:
                elapsed = time.time() - t0
                logger.warning("[Together] Request timed out after %.2fs", elapsed)
                last_exc = exc
                continue
            except requests.RequestException as exc:
                logger.error("[Together] Request failed: %s", exc)
                last_exc = exc
                continue

        raise RuntimeError(
            f"Together AI request failed after {self.max_retries + 1} attempts: {last_exc}"
        )

    def get_last_cost(self) -> float:
        return self._last_cost

    def get_last_token_usage(self) -> dict:
        """Return token usage from the last successful call."""
        return self._last_token_usage
