from __future__ import annotations

import requests

from .base_model import BaseModel


class LocalModel(BaseModel):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "",
    ) -> None:
        if not model:
            raise ValueError("A local model name is required")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model_name = f"local:{model}"
        self._last_cost = 0.0

    def generate(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        usage = payload.get("usage", {})
        self._last_cost = float(usage.get("cost", 0.0) or 0.0)
        return payload["choices"][0]["message"]["content"].strip()

    def get_last_cost(self) -> float:
        return self._last_cost
