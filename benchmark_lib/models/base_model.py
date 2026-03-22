from __future__ import annotations

from abc import ABC, abstractmethod


class BaseModel(ABC):
    model_name: str = "custom-model"

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        raise NotImplementedError

    def get_last_cost(self) -> float:
        return 0.0
    
    def get_last_token_count(self) -> tuple[int, int]:
        """Get (input_tokens, output_tokens) from last API call. 
        
        Returns:
            Tuple of (input_tokens, output_tokens). Returns (0, 0) if not available.
        """
        return (0, 0)
