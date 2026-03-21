from __future__ import annotations

from ..utils.types import NormalizedSample


# Concise prompts to minimize token usage
PROMPT_TEMPLATES = {
    "math": "Solve and give final answer only.",
    "logic": "Choose correct answer only.",
    "knowledge": "Answer concisely.",
    "code": "Write only the required function.",
}

# Domain-specific max_tokens limits
MAX_TOKENS_BY_DOMAIN = {
    "math": 256,
    "logic": 256,
    "knowledge": 128,
    "code": 512,
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
        # Reduce tokens for local models to speed up inference and reduce timeouts
        local_tokens = {
            "math": 128,      # Reduced from 256
            "logic": 128,     # Reduced from 256
            "knowledge": 64,  # Reduced from 128
            "code": 256,      # Reduced from 512
        }
        return local_tokens.get(domain, 128)
    
    return MAX_TOKENS_BY_DOMAIN.get(domain, 256)


def build_prompt(sample: NormalizedSample) -> str:
    """Build optimized prompt with truncated inputs."""
    template = PROMPT_TEMPLATES[sample.domain]
    question = truncate_text(sample.question, max_chars=500)
    
    # Build complete prompt with template and question
    prompt = f"{template}\n\n{question}"
    
    # Add options for logic domain
    if sample.domain == "logic" and sample.options:
        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(sample.options)])
        prompt = f"{prompt}\n\nOptions:\n{options_text}"
    
    return prompt
