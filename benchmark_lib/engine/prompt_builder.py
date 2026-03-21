from __future__ import annotations

import json

from ..utils.types import NormalizedSample


# Shared instruction block used across domains/datasets.
BASE_INSTRUCTION = (
    "You are solving a problem from a benchmark dataset.\n\n"
    "Rules:\n"
    "- Give ONLY the final answer.\n"
    "- For coding questions: return COMPLETE runnable Python code.\n"
    "- Do NOT omit function definitions.\n"
    "- Do NOT give explanation unless asked.\n"
    "- Ensure variables and functions are defined.\n"
    "- Output must be directly executable."
)

# Domain defaults.
PROMPT_TEMPLATES = {
    "math": "Solve step-by-step internally, but return ONLY the final numeric answer.",
    "logic": "Choose the correct option and return ONLY the final answer.",
    "knowledge": "Answer in one short sentence. No explanation.",
    "code": (
        "Write a COMPLETE Python function.\n"
        "\n"
        "Rules:\n"
        "- Use correct input types (list, tuple, int).\n"
        "- Do NOT assume fixed length.\n"
        "- Handle edge cases (empty list, small input).\n"
        "- Do NOT use print().\n"
        "- Return only function."
    ),
}

# Dataset-specific prompt overrides.
DATASET_PROMPT_OVERRIDES = {
    "mbpp_full": "Write a complete Python function to solve the problem. Return ONLY code. No explanation.",
    "mbpp_sanitized": "Write a complete Python function to solve the problem. Return ONLY code. No explanation.",
    "gsm8k_main": "Solve step-by-step internally, but return ONLY the final numeric answer.",
    "gsm8k_socratic": "Solve step-by-step internally, but return ONLY the final numeric answer.",
    "squad": "Answer in one short sentence. No explanation.",
    "natural_questions": "Answer in one short sentence. No explanation.",
}

# Domain-specific max_tokens limits
MAX_TOKENS_BY_DOMAIN = {
    "math": 200,
    "logic": 200,
    "knowledge": 200,
    "code": 200,
}


def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text to max_chars while preserving word boundaries."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    # Try to cut at last space if available
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:  # Only cut at space if it's reasonably close
        truncated = truncated[:last_space]
    return truncated.strip()


def get_max_tokens(domain: str, is_local_model: bool = False) -> int:
    """Get domain-specific max_tokens limit.
    
    Args:
        domain: The domain (math, logic, knowledge, code)
        is_local_model: If True, use reduced tokens for faster local inference
    
    Returns:
        max_tokens limit for the domain
    """
    if is_local_model:
        return 200

    return MAX_TOKENS_BY_DOMAIN.get(domain, 200)


def _build_example_input_hint(sample: NormalizedSample) -> str:
    raw_input = sample.metadata.get("input")
    if raw_input is not None:
        try:
            rendered = json.dumps(raw_input, ensure_ascii=False)
        except Exception:
            rendered = str(raw_input)
        rendered = rendered[:220]
        return (
            "\n\nExample input:\n"
            f"{rendered}\n"
            "Ensure your function works for this input."
        )

    tests = sample.metadata.get("tests")
    if isinstance(tests, list) and tests:
        first_test = str(tests[0]).strip()[:220]
        return (
            "\n\nExample input:\n"
            f"{first_test}\n"
            "Ensure your function handles that input format correctly."
        )

    return ""


def build_prompt(sample: NormalizedSample) -> str:
    """Build task-specific prompt with consistent output constraints."""
    template = DATASET_PROMPT_OVERRIDES.get(sample.dataset, PROMPT_TEMPLATES[sample.domain])
    question = truncate_text(sample.question, max_chars=500)

    prompt = f"{BASE_INSTRUCTION}\n\n{template}\n\nQuestion:\n{question}"

    if sample.domain == "code":
        entry_point = sample.metadata.get("entry_point")
        if isinstance(entry_point, str) and entry_point.strip():
            prompt = (
                f"{prompt}\n\n"
                f"Use EXACT function name: {entry_point.strip()}\n"
                f"Return ONLY the function.\n"
                f"Do NOT use print(). Return values only.\n"
                f"Use EXACT function signature from problem.\n"
                f"Do NOT change number of arguments.\n"
                f"Function must accept the correct number of arguments.\n"
                f"Follow problem input format exactly; do not assume extra parameters.\n"
                f"Ensure correct data types; avoid tuple/int and list/power type mistakes."
            )
            prompt = f"{prompt}{_build_example_input_hint(sample)}"
    
    # Add options for logic domain
    if sample.domain == "logic" and sample.options:
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(sample.options)])
        prompt = f"{prompt}\n\nOptions:\n{options_text}"
    
    return prompt
