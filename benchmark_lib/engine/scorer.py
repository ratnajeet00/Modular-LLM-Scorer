from __future__ import annotations

from collections import defaultdict

from ..utils.types import EvalRecord


DOMAIN_WEIGHTS = {
    "math": 0.25,
    "logic": 0.25,
    "knowledge": 0.35,
    "code": 0.15,
}


def _acc(records: list[EvalRecord]) -> float:
    if not records:
        return 0.0
    return sum(1 for r in records if r.correct) / len(records)


def score(records: list[EvalRecord], model_name: str, mode: str) -> dict:
    by_dataset: dict[str, list[EvalRecord]] = defaultdict(list)
    by_domain: dict[str, list[EvalRecord]] = defaultdict(list)

    total_cost = 0.0
    error_count = 0
    call_error_count = 0
    empty_prediction_count = 0
    error_examples: list[str] = []
    call_error_examples: list[str] = []
    seen_errors: set[str] = set()
    seen_call_errors: set[str] = set()
    for r in records:
        by_dataset[r.dataset].append(r)
        by_domain[r.domain].append(r)
        total_cost += r.cost
        if r.error:
            error_count += 1
            if r.error not in seen_errors and len(error_examples) < 5:
                seen_errors.add(r.error)
                error_examples.append(r.error)
        if not r.prediction.strip():
            empty_prediction_count += 1
            if r.error:
                call_error_count += 1
                if r.error not in seen_call_errors and len(call_error_examples) < 5:
                    seen_call_errors.add(r.error)
                    call_error_examples.append(r.error)

    per_dataset = {k: round(_acc(v), 6) for k, v in sorted(by_dataset.items())}
    per_domain = {k: round(_acc(v), 6) for k, v in sorted(by_domain.items())}
    total_questions = len(records)
    correct_count = sum(1 for r in records if r.correct)
    wrong_count = total_questions - correct_count
    accuracy = (correct_count / total_questions) if total_questions else 0.0
    error_rate = (wrong_count / total_questions) if total_questions else 0.0
    failure_rate = (call_error_count / total_questions) if total_questions else 0.0

    final_score = 0.0
    for domain, weight in DOMAIN_WEIGHTS.items():
        final_score += weight * per_domain.get(domain, 0.0)

    return {
        "model": model_name,
        "mode": mode,
        "accuracy": round(accuracy, 6),
        "per_dataset": per_dataset,
        "per_domain": per_domain,
        "final_score": round(final_score, 6),
        "total_questions": total_questions,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "error_rate": round(error_rate, 6),
        "failure_rate": round(failure_rate, 6),
        "non_empty_predictions": total_questions - empty_prediction_count,
        "empty_predictions": empty_prediction_count,
        "call_error_count": call_error_count,
        "call_error_examples": call_error_examples,
        "error_count": error_count,
        "error_examples": error_examples,
        "cost": round(total_cost, 6),
    }
