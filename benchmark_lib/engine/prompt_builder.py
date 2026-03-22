from __future__ import annotations

import json

from ..utils.types import NormalizedSample


# Shared instruction block used across domains/datasets.
BASE_INSTRUCTION = (
    "You are a helpful AI assistant with expertise in all domains.\n"
    "Answer ALL types of questions: math, science, logic, code, general knowledge.\n"
    "NEVER refuse or say 'I cannot help' or 'I don't have expertise'.\n"
    "NEVER say you only support one topic or refuse out-of-domain questions.\n"
    "NEVER say 'as an AI assistant' or similar caveats.\n"
    "ALWAYS provide a direct, concise answer.\n"
    "Answer even difficult questions - do your best.\n\n"
    "Output format rules:\n"
    "- For math/logic/knowledge: give ONLY the final answer, no explanation.\n"
    "- For code: return complete executable Python code.\n"
    "- ALWAYS respond with content. NEVER leave output empty."
)

# Domain defaults.
PROMPT_TEMPLATES = {
    "math": (
        "Solve and give ONLY the final numeric answer.\n"
        "Do not explain."
    ),
    "logic": (
        "Read the question carefully.\n"
        "Then RETURN ONLY ONE LETTER: A, B, C, or D.\n"
        "NO explanation. NO code. NO full sentences.\n"
        "Format: Just the letter (e.g., A). WRONG: 'The answer is A', 'Option A'"
    ),
    "knowledge": (
        "Answer the question directly in one short sentence.\n"
        "ALWAYS answer. DO NOT refuse. DO NOT say 'I don't know' or 'I cannot help'.\n"
        "Even if uncertain, provide your best answer."
    ),
    "code": (
        "Return complete, executable Python code that runs without errors.\n"
        "Include ALL necessary imports at the top.\n"
        "Return the ENTIRE solution - not just a function definition.\n"
        "Format: [imports on lines 1-N][code definition][function call if needed].\n"
        "Use proper Python syntax. Test in your head first.\n"
        "Do NOT explain. Output ONLY code. No text before/after."
    ),
}

# Dataset-specific prompt overrides.
DATASET_PROMPT_OVERRIDES = {
    "mbpp_full": (
        "Return the COMPLETE, RUNNABLE Python code that will be tested.\n"
        "Include the function with EXACT name and parameters as given.\n"
        "Include ALL necessary imports (e.g., import re, import math, etc).\n"
        "Include the ENTIRE code block ready to execute.\n"
        "Do NOT change the function signature.\n"
        "Do NOT add explanations or comments.\n"
        "Only return executable Python code."
    ),
    "mbpp_sanitized": (
        "Return the COMPLETE, RUNNABLE Python code that will be tested.\n"
        "Include the function with EXACT name and parameters as given.\n"
        "Include ALL necessary imports (e.g., import re, import math, etc).\n"
        "Include the ENTIRE code block ready to execute.\n"
        "Do NOT change the function signature.\n"
        "Do NOT add explanations or comments.\n"
        "Only return executable Python code."
    ),
    "gsm8k_main": "Solve step-by-step internally, but return ONLY the final numeric answer.",
    "gsm8k_socratic": "Solve step-by-step internally, but return ONLY the final numeric answer.",
    "squad": "Answer in one short sentence. No explanation.",
    "natural_questions": "Answer in one short sentence. No explanation.",
    "proofwriter": (
        "Read the context and question.\n"
        "Determine if the statement is True or False based on the context.\n"
        "Return ONLY: True or False."
    ),
}

# Domain-specific max_tokens limits
MAX_TOKENS_BY_DOMAIN = {
    "math": 512,
    "logic": 512,
    "knowledge": 512,
    "code": 2048,  # Increased for DeepSeek and other local models
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
        return MAX_TOKENS_BY_DOMAIN.get(domain, 512)

    return MAX_TOKENS_BY_DOMAIN.get(domain, 512)


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
                f"Return COMPLETE, RUNNABLE Python code that will be executed.\n"
                f"Include ALL necessary imports.\n"
                f"Include the ENTIRE code block (not just the function).\n"
                f"Use EXACT function signature from problem.\n"
                f"Do NOT change number of arguments.\n"
                f"Do NOT use print(). Return values only.\n"
                f"Only return executable Python code. NO explanations."
            )
            prompt = f"{prompt}{_build_example_input_hint(sample)}"
    
    # Add options for logic domain with explicit MCQ response slot.
    if sample.domain == "logic":
        if sample.options:
            # Multiple choice format (Reclor, etc.)
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(sample.options)])
            prompt = (
                f"{prompt}\n\n"
                f"Options:\n{options_text}\n\n"
                "==MANDATORY==\n"
                "Answer with ONLY the letter (A, B, C, or D).\n"
                "NO explanation. NO code. NO period.\n\n"
                "Answer: "
            )
        else:
            # True/False format (ProofWriter)
            prompt = (
                f"{prompt}\n\n"
                "==MANDATORY==\n"
                "Answer with ONLY: True or False\n"
                "NO explanation. NO code. NO period.\n\n"
                "Answer: "
            )

    if sample.domain in ("math", "knowledge"):
        if sample.domain == "math":
            prompt = (
                f"{prompt}\n\n"
                "==MANDATORY==\n"
                "Answer with ONLY a number (e.g., 42, 3.14, -5).\n"
                "NO code. NO explanation. NO period.\n\n"
                "Answer: "
            )
        else:  # knowledge
            prompt = (
                f"{prompt}\n\n"
                "==MANDATORY==\n"
                "Answer with ONLY the short phrase (max 10 words).\n"
                "NO code. NO explanation.\n\n"
                "Answer: "
            )
    
    return prompt
