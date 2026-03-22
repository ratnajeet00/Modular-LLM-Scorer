#!/usr/bin/env python3
"""
Statistical comparison tests for benchmark models.
Includes McNemar's test for paired classifier comparison.
"""

import json
import sys
from pathlib import Path
from typing import Optional

try:
    from scipy.stats import chi2_contingency
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def load_jsonl_predictions(jsonl_path: str) -> dict[str, dict]:
    """Load predictions from JSONL log file.
    
    Returns dict mapping sample_id -> {correct: bool, prediction: str}
    """
    predictions = {}
    with open(jsonl_path) as f:
        for line in f:
            rec = json.loads(line)
            sample_id = rec.get("sample_id")
            if sample_id:
                predictions[sample_id] = {
                    "correct": rec.get("correct", False),
                    "prediction": rec.get("prediction", ""),
                }
    return predictions


def load_json_results(json_path: str) -> dict:
    """Load results from final JSON output."""
    with open(json_path) as f:
        return json.load(f)


def extract_predictions_from_jsonl(raw_outputs_path: str) -> dict[str, bool]:
    """Extract correctness for each sample from raw JSONL.
    
    Returns dict mapping sample_id -> is_correct (bool)
    """
    predictions = {}
    with open(raw_outputs_path) as f:
        for line in f:
            rec = json.loads(line)
            sample_id = rec.get("sample_id")
            if sample_id:
                predictions[sample_id] = rec.get("correct", False)
    return predictions


def mcnemar_test(model1_preds: dict[str, bool], model2_preds: dict[str, bool]) -> dict:
    """Perform McNemar's test on paired predictions.
    
    Args:
        model1_preds: dict mapping sample_id -> is_correct (bool)
        model2_preds: dict mapping sample_id -> is_correct (bool)
    
    Returns:
        dict with test results: statistic, p_value, contingency_table,
        disagreement_count, model1_wins, model2_wins
    """
    if not SCIPY_AVAILABLE:
        return {"error": "scipy not installed"}
    
    from scipy.stats import chi2_contingency
    
    # Find common samples
    common_ids = set(model1_preds.keys()) & set(model2_preds.keys())
    if not common_ids:
        return {"error": "No common samples between models"}
    
    # Build contingency table for McNemar's test
    # Only off-diagonal elements matter for McNemar test
    m1_correct_m2_wrong = 0  # Model1 correct, Model2 wrong
    m1_wrong_m2_correct = 0  # Model1 wrong, Model2 correct
    
    for sample_id in common_ids:
        m1_correct = model1_preds[sample_id]
        m2_correct = model2_preds[sample_id]
        
        if m1_correct and not m2_correct:
            m1_correct_m2_wrong += 1
        elif not m1_correct and m2_correct:
            m1_wrong_m2_correct += 1
    
    # McNemar's test statistic: (b - c)^2 / (b + c)
    # where b = model1_correct_m2_wrong, c = model1_wrong_m2_correct
    b = m1_correct_m2_wrong
    c = m1_wrong_m2_correct
    total_disagreement = b + c
    
    if total_disagreement == 0:
        # No disagreement - models always agree
        stat = 0.0
        p_value = 1.0
    else:
        # McNemar statistic 
        stat = (b - c) ** 2 / total_disagreement
        # Approximate as chi-squared(1) for p-value
        from scipy.stats import chi2
        p_value = 1 - chi2.cdf(stat, df=1)
    
    # Calculate accuracy difference
    m1_correct_total = sum(1 for v in model1_preds.values() if v)
    m2_correct_total = sum(1 for v in model2_preds.values() if v)
    
    m1_accuracy = m1_correct_total / len(common_ids)
    m2_accuracy = m2_correct_total / len(common_ids)
    
    result = {
        "test": "McNemar's Test",
        "description": "Tests whether two classifiers have significantly different error rates on paired samples.",
        "samples_compared": len(common_ids),
        "model1_accuracy": round(m1_accuracy, 4),
        "model2_accuracy": round(m2_accuracy, 4),
        "accuracy_difference": round(m1_accuracy - m2_accuracy, 4),
        "test_statistic": round(float(stat), 4),
        "p_value": round(float(p_value), 6),
        "significance_level": 0.05,
        "significant": p_value < 0.05,
        "interpretation": (
            f"The models have {'SIGNIFICANTLY' if p_value < 0.05 else 'NO SIGNIFICANT'} "
            f"difference in error rates (p={round(p_value, 4)}). "
            f"Model 1: {m1_correct_m2_wrong} wins vs Model 2: {m1_wrong_m2_correct} wins "
            f"on discordant pairs."
        ),
        "contingency_table": {
            "model1_correct_model2_wrong": m1_correct_m2_wrong,
            "model1_wrong_model2_correct": m1_wrong_m2_correct,
            "total_disagreements": total_disagreement,
        }
    }
    
    return result


def compare_jsonl_logs(log1_path: str, log2_path: str, 
                       model1_name: str = "Model 1", 
                       model2_name: str = "Model 2") -> None:
    """Compare two JSONL logs using McNemar's test."""
    
    print(f"\n{'='*80}")
    print(f"McNemar's Test: {model1_name} vs {model2_name}")
    print(f"{'='*80}\n")
    
    if not SCIPY_AVAILABLE:
        print("ERROR: scipy not installed. Install with: pip install scipy")
        return
    
    try:
        m1_preds = extract_predictions_from_jsonl(log1_path)
        m2_preds = extract_predictions_from_jsonl(log2_path)
        
        result = mcnemar_test(m1_preds, m2_preds)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print(f"Result: {model1_name}")
        print(f"  Accuracy: {result['model1_accuracy']:.2%}")
        print(f"\nResult: {model2_name}")
        print(f"  Accuracy: {result['model2_accuracy']:.2%}")
        print(f"\nDifference: {result['accuracy_difference']:+.2%}")
        print(f"\nMcNemar's Test Statistic: {result['test_statistic']}")
        print(f"P-value: {result['p_value']:.6f}")
        print(f"Significant at α=0.05: {result['significant']}")
        print(f"\nInterpretation: {result['interpretation']}")
        print(f"\nSamples compared: {result['samples_compared']}")
        print(f"Contingency (discordant pairs):")
        print(f"  {model1_name} correct, {model2_name} wrong: {result['contingency_table']['model1_correct_model2_wrong']}")
        print(f"  {model1_name} wrong, {model2_name} correct: {result['contingency_table']['model1_wrong_model2_correct']}")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python mcnemar_test.py <model1_jsonl> <model2_jsonl> [model1_name] [model2_name]")
        print("\nExample:")
        print("  python mcnemar_test.py temp_eval/llama_raw.jsonl temp_eval/mistral_raw.jsonl LLaMA Mistral")
        sys.exit(1)
    
    model1 = sys.argv[1]
    model2 = sys.argv[2]
    model1_name = sys.argv[3] if len(sys.argv) > 3 else "Model 1"
    model2_name = sys.argv[4] if len(sys.argv) > 4 else "Model 2"
    
    compare_jsonl_logs(model1, model2, model1_name, model2_name)
