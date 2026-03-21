from __future__ import annotations

import re


def _band(score: float) -> str:
    if score < 1.0:
        return "easy"
    if score < 2.0:
        return "medium"
    return "hard"


def math_difficulty(question: str, answer: str = "") -> str:
    q = question.lower()
    ops = len(re.findall(r"[+\-*/^]", q))
    nums = len(re.findall(r"\b\d+(?:\.\d+)?\b", q))
    words = len(q.split())
    score = 0.5 * min(ops, 6) + 0.3 * min(nums, 8) + 0.2 * min(words / 30, 3)
    return _band(score)


def logic_difficulty(question: str, options_count: int = 0) -> str:
    q = question.lower()
    cues = len(re.findall(r"\b(if|then|unless|only if|therefore|because|all|some|none)\b", q))
    words = len(q.split())
    score = 0.6 * min(cues, 6) + 0.2 * min(options_count, 6) + 0.2 * min(words / 40, 3)
    return _band(score)


def knowledge_difficulty(question: str, context: str = "") -> str:
    q_words = len(question.split())
    c_words = len(context.split())
    hops = len(re.findall(r"\b(and|before|after|while|which|that|from|by)\b", question.lower()))
    score = 0.5 * min(q_words / 20, 3) + 0.3 * min(c_words / 120, 3) + 0.2 * min(hops, 5)
    return _band(score)


def code_difficulty(prompt: str, test_count: int = 0, canonical_solution: str = "") -> str:
    p_words = len(prompt.split())
    constraints = len(re.findall(r"\b(time|space|complexity|constraint|optimi[sz]e)\b", prompt.lower()))
    sol_len = len(canonical_solution.splitlines())
    score = 0.35 * min(p_words / 40, 3) + 0.35 * min(test_count / 8, 3) + 0.2 * min(sol_len / 30, 3) + 0.1 * min(constraints, 5)
    return _band(score)
