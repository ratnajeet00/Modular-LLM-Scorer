#!/usr/bin/env python3
"""
Validation pipeline for benchmark evaluator correctness.

Tests the evaluator with 10 known Q&A pairs to verify it works correctly
before running expensive benchmarks.
"""

import json
import sys
from pathlib import Path

from benchmark_lib.utils.types import EvalRecord, NormalizedSample
from benchmark_lib.engine.evaluator import evaluate as evaluate_answer


# Test cases: (domain, question, expected_answer, list_of_correct_predictions)
VALIDATION_CASES = [
    # Math
    {
        "domain": "math",
        "dataset": "gsm8k_main",
        "question": "If a watermelon costs $5, how much do 3 watermelons cost?",
        "expected": "15",
        "options": None,
        "entry_point": None,
        "correct_predictions": ["15", "15.0", "15.", "The answer is 15", "=$15 total", "15 dollars"],
        "wrong_predictions": ["5", "20", "25", "three", ""],
    },
    # Logic - multiple choice
    {
        "domain": "logic",
        "dataset": "reclor",
        "question": "Which of these is a color?",
        "expected": "A",
        "options": ["Red", "Number", "Word", "Sound"],
        "entry_point": None,
        "correct_predictions": ["A", "a", "Option A", "red"],
        "wrong_predictions": ["B", "C", "D", "Number", ""],
    },
    # Logic - true/false
    {
        "domain": "logic",
        "dataset": "proofwriter",
        "question": "Is water wet?",
        "expected": "True",
        "options": None,
        "entry_point": None,
        "correct_predictions": ["true", "True", "TRUE", "Yes", "T"],
        "wrong_predictions": ["false", "False", "No", "N", "Maybe"],
    },
    # Knowledge
    {
        "domain": "knowledge",
        "dataset": "natural_questions",
        "question": "What is the capital of France?",
        "expected": "Paris",
        "options": None,
        "entry_point": None,
        "correct_predictions": ["Paris", "paris", "The capital of France is Paris", "It's Paris"],
        "wrong_predictions": ["France", "Europe", "The Eiffel Tower", ""],
    },
    # Code
    {
        "domain": "code",
        "dataset": "mbpp_full",
        "question": "Write a function that returns 42",
        "expected": "def answer(x):\n    return 42",
        "options": None,
        "entry_point": "answer",
        "correct_predictions": [
            "def answer(x):\n    return 42",
            "def answer(x):\n    return 42\n",
        ],
        "wrong_predictions": ["return 42", "42", "def answer(x): pass"],
    },
]


def test_evaluator() -> bool:
    """Test evaluator with known cases."""
    print(f"\n{'='*80}")
    print(f"Validation Pipeline: Testing Evaluator Correctness")
    print(f"{'='*80}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_cases = []
    
    for case_idx, case in enumerate(VALIDATION_CASES, 1):
        domain = case["domain"]
        dataset = case["dataset"]
        expected = case["expected"]
        
        # Create a sample
        sample = NormalizedSample(
            id=f"validation-{case_idx}",
            dataset=dataset,
            domain=domain,
            question=case["question"],
            answer=expected,
            options=case["options"],
            difficulty="medium",
            metadata={
                "entry_point": case["entry_point"],
            }
        )
        
        print(f"Test {case_idx}/{len(VALIDATION_CASES)}: {domain} ({dataset})")
        print(f"  Question: {case['question'][:60]}...")
        print(f"  Expected: {expected}")
        
        # Test correct predictions
        correct_count = 0
        for pred in case["correct_predictions"]:
            total_tests += 1
            correct, error = evaluate_answer(sample, pred)
            if correct:
                correct_count += 1
                passed_tests += 1
                status = "[OK]"
            else:
                status = "[FAIL]"
                failed_cases.append((case_idx, "correct", pred, error))
            print(f"    {status} Correct: '{pred[:40]}...' -> {correct}")
        
        # Test wrong predictions
        wrong_correct_count = 0
        for pred in case["wrong_predictions"]:
            total_tests += 1
            correct, error = evaluate_answer(sample, pred)
            if not correct:
                wrong_correct_count += 1
                passed_tests += 1
                status = "[OK]"
            else:
                status = "[FAIL]"
                failed_cases.append((case_idx, "wrong", pred, error))
            print(f"    {status} Wrong: '{pred[:40]}...' -> {correct}")
        
        if correct_count == len(case["correct_predictions"]) and wrong_correct_count == len(case["wrong_predictions"]):
            print(f"  [PASS]\n")
        else:
            print(f"  [FAIL]\n")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    print(f"Pass rate: {100*passed_tests/total_tests:.1f}%")
    print(f"{'='*80}")
    
    if failed_cases:
        print(f"\nFailed Cases ({len(failed_cases)}):")
        for case_idx, prediction_type, prediction, error in failed_cases:
            print(f"  Case {case_idx} ({prediction_type}): '{prediction[:40]}...'")
            if error:
                print(f"    Error: {error}")
        return False
    else:
        print(f"\n[SUCCESS] All validation tests passed!")
        return True


def main() -> None:
    success = test_evaluator()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
