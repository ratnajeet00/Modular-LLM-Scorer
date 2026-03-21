from __future__ import annotations

from ..utils.types import NormalizedSample


PROMPT_TEMPLATES = {
    "math": "Solve step by step and give final answer.\n\nQuestion:\n{question}",
    "logic": "Choose correct answer with reasoning.\n\nQuestion:\n{question}\n\nOptions:\n{options}",
    "knowledge": "Answer concisely.\n\nQuestion:\n{question}",
    "code": "Write correct function. Return only Python code.\n\nTask:\n{question}",
}


def build_prompt(sample: NormalizedSample) -> str:
    template = PROMPT_TEMPLATES[sample.domain]
    options = ""
    if sample.options:
        options = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(sample.options)])
    return template.format(question=sample.question, options=options)
