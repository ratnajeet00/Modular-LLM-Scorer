from __future__ import annotations

import threading

import requests

from .base_model import BaseModel


class OpenRouterModel(BaseModel):
    def __init__(self, api_key: str, model: str, base_url: str = "https://openrouter.ai/api/v1") -> None:
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.model_name = f"openrouter:{model}"
        self._last_cost = 0.0
        self._model_checked = False
        self._model_check_error: str | None = None
        self._model_check_lock = threading.Lock()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                err = payload.get("error")
                if isinstance(err, dict):
                    msg = err.get("message")
                    if isinstance(msg, str) and msg.strip():
                        return msg.strip()
                if isinstance(err, str) and err.strip():
                    return err.strip()
        except Exception:
            pass
        return response.text.strip()[:300] if response.text else ""

    def _candidate_models(self) -> list[str]:
        response = requests.get(
            f"{self.base_url}/models",
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get("data", []) if isinstance(payload, dict) else []
        ids: list[str] = []
        for item in items:
            if isinstance(item, dict):
                mid = item.get("id")
                if isinstance(mid, str) and mid:
                    ids.append(mid)
        return ids

    def _maybe_fix_model_name(self) -> None:
        if self._model_check_error:
            raise ValueError(self._model_check_error)
        if self._model_checked:
            return
        with self._model_check_lock:
            if self._model_check_error:
                raise ValueError(self._model_check_error)
            if self._model_checked:
                return
            try:
                ids = self._candidate_models()
            except Exception:
                # If listing models fails, continue and let generation surface request error details.
                self._model_checked = True
                return

            if self.model in ids:
                self._model_checked = True
                return

            free_variant = f"{self.model}:free"
            if ":" not in self.model and free_variant in ids:
                self.model = free_variant
                self.model_name = f"openrouter:{self.model}"
                self._model_checked = True
                return

            base = self.model.split(":", 1)[0]
            suggestions = [m for m in ids if base in m][:5]
            hint = ", ".join(suggestions) if suggestions else "no close matches found"
            self._model_check_error = (
                f"OpenRouter model '{self.model}' was not found. "
                f"Closest available models: {hint}"
            )
            raise ValueError(self._model_check_error)

    def generate(self, prompt: str) -> str:
        self._maybe_fix_model_name()
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=60,
        )
        if not response.ok:
            detail = self._extract_error_message(response)
            if detail:
                raise RuntimeError(
                    f"OpenRouter request failed ({response.status_code}): {detail}"
                )
            response.raise_for_status()
        payload = response.json()
        usage = payload.get("usage", {})
        self._last_cost = float(usage.get("cost", 0.0) or 0.0)
        return payload["choices"][0]["message"]["content"].strip()

    def get_last_cost(self) -> float:
        return self._last_cost
