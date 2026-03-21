from __future__ import annotations

from abc import ABC, abstractmethod


class BaseModel(ABC):
    model_name: str = "custom-model"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def get_last_cost(self) -> float:
        return 0.0
