"""Google Gemini provider using the official Google GenAI SDK.

Environment variable: GEMINI_API_KEY
Default model: gemini-2.0-flash
"""
from __future__ import annotations

import logging
import time

try:
    from google import genai
except ImportError:  # pragma: no cover - handled at runtime with a clear error
    genai = None  # type: ignore[assignment]

from .base_model import BaseModel

logger = logging.getLogger(__name__)

# Current Gemini model names.  Pass via --model-name.
_KNOWN_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
]


class EmptyGeminiResponseError(RuntimeError):
    """Raised when Gemini returns an empty text payload."""


class GeminiModel(BaseModel):
    """Calls Gemini using the official SDK.

    Equivalent SDK pattern:
        from google import genai
        client = genai.Client(api_key="...")
        response = client.models.generate_content(model="...", contents="...")
        print(response.text)
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
        if genai is None:
            raise RuntimeError(
                "google-genai package is required for Gemini. "
                "Install with: pip install google-genai"
            )
        self.api_key = api_key
        self.model = model
        self.model_name = f"gemini:{model}"
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_cost = 0.0
        self._last_token_usage: dict = {}
        self._client = genai.Client(api_key=self.api_key)

    def _extract_text(self, response: object) -> str:
        text = (getattr(response, "text", "") or "").strip()
        if text:
            return text

        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            raise EmptyGeminiResponseError("Gemini returned no candidates.")

        first = candidates[0]
        content = getattr(first, "content", None)
        if content is None and isinstance(first, dict):
            content = first.get("content")

        parts = getattr(content, "parts", None) if content is not None else None
        if parts is None and isinstance(content, dict):
            parts = content.get("parts")

        texts: list[str] = []
        for part in parts or []:
            part_text = getattr(part, "text", None)
            if part_text is None and isinstance(part, dict):
                part_text = part.get("text")
            if part_text:
                texts.append(str(part_text))

        text = "".join(texts).strip()
        if text:
            return text

        finish_reason = getattr(first, "finish_reason", None)
        if finish_reason is None and isinstance(first, dict):
            finish_reason = first.get("finishReason")
        raise EmptyGeminiResponseError(
            f"Gemini candidate has empty text. finishReason={finish_reason!r}"
        )

    @staticmethod
    def _extract_token_usage(response: object) -> dict:
        meta = getattr(response, "usage_metadata", None)
        if meta is None:
            meta = getattr(response, "usageMetadata", None)
        if meta is None and hasattr(response, "to_dict"):
            data = response.to_dict()
            meta = data.get("usageMetadata") or {}
        if meta is None:
            meta = {}

        def _get(name_snake: str, name_camel: str) -> int:
            value = getattr(meta, name_snake, None)
            if value is None and isinstance(meta, dict):
                value = meta.get(name_camel)
            return int(value or 0)

        return {
            "prompt_tokens": _get("prompt_token_count", "promptTokenCount"),
            "completion_tokens": _get("candidates_token_count", "candidatesTokenCount"),
            "total_tokens": _get("total_token_count", "totalTokenCount"),
        }

    def preflight_model_check(self) -> tuple[bool, str]:
        """Validate model availability/support before running full benchmark."""
        try:
            models = list(self._client.models.list())
        except Exception as exc:
            return False, f"[Gemini] Preflight failed (list models): {exc}"

        target_name = f"models/{self.model}"
        target = None
        available_model_names: list[str] = []
        for model_info in models:
            name = getattr(model_info, "name", "") or ""
            if name:
                available_model_names.append(name)
            if name == target_name:
                target = model_info

        if target is None:
            available = ", ".join(available_model_names)
            recommended = ""
            for preferred in (
                "models/gemini-2.5-flash",
                "models/gemini-2.0-flash",
                "models/gemini-2.5-flash-lite",
            ):
                if preferred in available_model_names:
                    recommended = preferred.replace("models/", "")
                    break
            return (
                False,
                f"[Gemini] Model '{self.model}' is not available for your API key. "
                f"Available models: {available or 'none'}"
                + (
                    f". Try: python run_benchmark.py --model gemini --model-name {recommended} --mode quick"
                    if recommended
                    else ""
                ),
            )

        methods = getattr(target, "supported_generation_methods", None)
        if methods is None:
            methods = getattr(target, "supportedGenerationMethods", None)
        if methods is None and hasattr(target, "to_dict"):
            methods = (target.to_dict() or {}).get("supportedGenerationMethods")
        methods = methods or []
        if methods and "generateContent" not in methods:
            return (
                False,
                f"[Gemini] Model '{self.model}' does not support generateContent "
                f"for this API key. Supported methods: {methods}",
            )

        return True, f"[Gemini] Preflight OK: {target_name} supports generateContent"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        return self._call_with_retries(prompt, max_tokens)

    def _call_with_retries(self, prompt: str, max_tokens: int | None) -> str:
        """Call Gemini SDK with retry/backoff logic."""
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

            try:
                call_kwargs: dict = {
                    "model": self.model,
                    "contents": prompt,
                }
                config: dict = {"temperature": 0.2}
                if max_tokens:
                    config["max_output_tokens"] = max_tokens
                # Add stop sequences to prevent truncation and control output
                config["stop_sequences"] = ["```", "\n\n", "\nAnswer:", "print(", "return "]
                call_kwargs["config"] = config

                response = self._client.models.generate_content(**call_kwargs)
                response_text = (getattr(response, "text", "") or "").strip()
                print("[Gemini DEBUG] status_code=SDK")
                print(f"[Gemini DEBUG] response.text={response_text}")

                self._last_token_usage = self._extract_token_usage(response)
                logger.info("[Gemini] Token usage: %s", self._last_token_usage)
                return self._extract_text(response)

            except EmptyGeminiResponseError as exc:
                logger.warning("[Gemini] Empty output, retrying: %s", exc)
                last_exc = exc
                continue
            except Exception as exc:
                logger.error("[Gemini] SDK request failed: %s", exc)
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
