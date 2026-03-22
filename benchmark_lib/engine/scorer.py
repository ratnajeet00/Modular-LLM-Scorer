from __future__ import annotations

from collections import defaultdict
import subprocess
import os

from ..utils.types import EvalRecord

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


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


def _calc_confidence_interval(
    records: list[EvalRecord],
    confidence: float = 0.95,
) -> dict[str, float] | None:
    """
    Calculate confidence interval using Wilson score interval (better for binary proportions).
    Returns {'lower': float, 'upper': float} or None if scipy not available.
    """
    if not HAS_SCIPY or not records:
        return None
    
    try:
        from scipy.stats import proportion_confint
        correct_count = sum(1 for r in records if r.correct)
        total_count = len(records)
        
        # Use Wilson score interval (method='wilson') - more reliable than normal approximation
        lower, upper = proportion_confint(
            correct_count,
            total_count,
            alpha=1 - confidence,
            method='wilson'
        )
        return {
            'lower': round(lower, 6),
            'upper': round(upper, 6),
            'accuracy': round(correct_count / total_count, 6) if total_count else 0.0,
        }
    except Exception:
        return None


def _get_git_commit_hash() -> str | None:
    """Get the current git commit hash if in a git repo."""
    try:
        # Get the repo root directory
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        # Get the current commit hash
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        # Get if there are uncommitted changes
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        
        has_uncommitted = bool(status)
        return f"{commit_hash}{'*' if has_uncommitted else ''}"
    except Exception:
        return None


def score(records: list[EvalRecord], model_name: str, mode: str, selected_datasets_by_domain: dict[str, set[str]] | None = None) -> dict:
    by_dataset: dict[str, list[EvalRecord]] = defaultdict(list)
    by_domain: dict[str, list[EvalRecord]] = defaultdict(list)
    by_difficulty: dict[str, list[EvalRecord]] = defaultdict(list)
    errors_by_domain: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    total_cost = 0.0
    error_count = 0
    call_error_count = 0
    empty_prediction_count = 0
    error_examples: list[str] = []
    call_error_examples: list[str] = []
    seen_errors: set[str] = set()
    seen_call_errors: set[str] = set()
    total_input_tokens = 0
    total_output_tokens = 0
    token_counts_by_domain: dict[str, dict[str, int]] = defaultdict(lambda: {"input": 0, "output": 0})
    
    for r in records:
        by_dataset[r.dataset].append(r)
        by_domain[r.domain].append(r)
        by_difficulty[r.difficulty].append(r)
        total_cost += r.cost
        total_input_tokens += r.input_tokens
        total_output_tokens += r.output_tokens
        token_counts_by_domain[r.domain]["input"] += r.input_tokens
        token_counts_by_domain[r.domain]["output"] += r.output_tokens
        if r.error:
            error_count += 1
            # Track per-domain error breakdown
            errors_by_domain[r.domain][r.error] += 1
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
    
    # Track sample counts per difficulty tier
    difficulty_stats: dict[str, dict] = {}
    for tier in ["easy", "medium", "hard"]:
        tier_records = by_difficulty.get(tier, [])
        tier_count = len(tier_records)
        tier_correct = sum(1 for r in tier_records if r.correct)
        tier_accuracy = (tier_correct / tier_count) if tier_count > 0 else 0.0
        
        difficulty_stats[tier] = {
            "count": tier_count,
            "correct": tier_correct,
            "accuracy": round(tier_accuracy, 6),
        }
        # Add confidence interval if available
        ci = _calc_confidence_interval(tier_records)
        if ci:
            difficulty_stats[tier]["confidence_interval_95"] = {
                "lower": ci['lower'],
                "upper": ci['upper'],
            }
    
    total_questions = len(records)
    correct_count = sum(1 for r in records if r.correct)
    wrong_count = total_questions - correct_count
    accuracy = (correct_count / total_questions) if total_questions else 0.0
    error_rate = (wrong_count / total_questions) if total_questions else 0.0
    failure_rate = (call_error_count / total_questions) if total_questions else 0.0

    final_score = 0.0
    for domain, weight in DOMAIN_WEIGHTS.items():
        final_score += weight * per_domain.get(domain, 0.0)

    # Compute confidence intervals for overall accuracy and per-domain
    overall_ci = _calc_confidence_interval(records)
    domain_ci: dict[str, dict] = {}
    for domain, records_in_domain in sorted(by_domain.items()):
        ci = _calc_confidence_interval(records_in_domain)
        if ci:
            domain_ci[domain] = {
                "lower": ci['lower'],
                "upper": ci['upper'],
            }

    # Compute timing statistics per domain
    domain_timings: dict[str, list[float]] = defaultdict(list)
    for r in records:
        if hasattr(r, 'elapsed_seconds') and r.elapsed_seconds:
            domain_timings[r.domain].append(r.elapsed_seconds)
    
    per_domain_timing = {}
    for domain, times in sorted(domain_timings.items()):
        if times:
            total_time = sum(times)
            per_domain_timing[domain] = {
                "mean_seconds": round(total_time / len(times), 3),
                "min_seconds": round(min(times), 3),
                "max_seconds": round(max(times), 3),
                "total_seconds": round(total_time, 3),
                "sample_count": len(times),
            }

    # Build summary table
    summary_table = {
        "overall_accuracy": round(accuracy, 6),
        "overall_samples": total_questions,
        "overall_correct": correct_count,
        "domain_breakdown": [],
    }
    for domain in sorted(DOMAIN_WEIGHTS.keys()):
        domain_records = by_domain.get(domain, [])
        if domain_records:
            domain_acc = round(_acc(domain_records), 6)
            domain_count = len(domain_records)
            summary_table["domain_breakdown"].append({
                "domain": domain,
                "accuracy": domain_acc,
                "sample_count": domain_count,
                "weight": DOMAIN_WEIGHTS[domain],
                "weighted_score": round(domain_acc * DOMAIN_WEIGHTS[domain], 6),
            })
    
    # Build per-domain error breakdown
    per_domain_errors = {}
    for domain in sorted(DOMAIN_WEIGHTS.keys()):
        if domain in errors_by_domain and errors_by_domain[domain]:
            # Sort errors by frequency
            sorted_errors = sorted(
                errors_by_domain[domain].items(),
                key=lambda x: x[1],
                reverse=True
            )
            per_domain_errors[domain] = dict(sorted_errors)
    
    # Build failure breakdown: categorize failures types
    failure_breakdown = {
        "empty_predictions": 0,
        "execution_errors": 0,
        "format_errors": 0,
        "other_errors": 0,
        "total_failures": call_error_count,
    }
    for error_type, count in errors_by_domain.values[0].items() if errors_by_domain else []:
        pass
    # Actually, let's build this by scanning the records directly
    for r in records:
        if r.error:
            error_lower = r.error.lower()
            if "execution-error" in error_lower:
                failure_breakdown["execution_errors"] += 1
            elif "invalid-output-format" in error_lower or "format" in error_lower:
                failure_breakdown["format_errors"] += 1
            else:
                failure_breakdown["other_errors"] += 1
        elif not r.prediction.strip():
            failure_breakdown["empty_predictions"] += 1

    result = {
        "model": model_name,
        "mode": mode,
        "accuracy": round(accuracy, 6),
        "per_dataset": per_dataset,
        "per_domain": per_domain,
        "per_domain_timing": per_domain_timing,
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
        # New fields for quality metrics
        "confidence_intervals_95": {
            "overall_accuracy": overall_ci if overall_ci else None,
            "per_domain": domain_ci,
        } if HAS_SCIPY else None,
        "difficulty_breakdown": difficulty_stats,
        "summary_table": summary_table,
        "per_domain_errors": per_domain_errors,
        "failure_breakdown": failure_breakdown,
        "git_commit_hash": _get_git_commit_hash(),
        "selected_datasets_by_domain": {k: sorted(list(v)) for k, v in (selected_datasets_by_domain or {}).items()} if selected_datasets_by_domain else None,
        "token_usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "by_domain": {
                domain: {
                    "input_tokens": counts["input"],
                    "output_tokens": counts["output"],
                    "total_tokens": counts["input"] + counts["output"],
                }
                for domain, counts in sorted(token_counts_by_domain.items())
            },
        },
    }
    
    # Remove None confidence intervals if scipy unavailable
    if not HAS_SCIPY and result.get("confidence_intervals_95") is None:
        del result["confidence_intervals_95"]
    
    return result
