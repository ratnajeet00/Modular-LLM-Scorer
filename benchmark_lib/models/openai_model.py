from __future__ import annotations

from .base_model import BaseModel


class OpenAIModel(BaseModel):
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install openai package to use OpenAIModel") from exc

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.model_name = f"openai:{model}"
        self._last_cost = 0.0

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        self._last_cost = 0.0
        return response.choices[0].message.content.strip()

    def get_last_cost(self) -> float:
        return self._last_cost
