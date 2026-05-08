from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class NormalizedSample:
    id: str
    dataset: str
    domain: str
    question: str
    answer: str
    options: list[str] | None
    difficulty: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvalRecord:
    sample_id: str
    dataset: str
    domain: str
    difficulty: str
    prompt: str
    prediction: str
    expected: str
    correct: bool
    error: str | None = None
    error_type: str | None = None  # generation_failure | format_error | wrong_answer | execution_error
    cost: float = 0.0
    elapsed_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
