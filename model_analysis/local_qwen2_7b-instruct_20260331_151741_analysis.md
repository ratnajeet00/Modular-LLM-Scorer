# Benchmark Report: local:qwen2:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 31.20% |
| Final Score (Weighted) | 0.268800 |
| Total Questions | 500 |
| Correct Answers | 156 |
| Failure Rate | 10.40% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 58.40% | 125 | 15% | 0.087600 |
| knowledge | 15.20% | 125 | 35% | 0.053200 |
| logic | 19.20% | 125 | 25% | 0.048000 |
| math | 32.00% | 125 | 25% | 0.080000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 337 | 117 | 34.72% |
| medium | 126 | 30 | 23.81% |
| hard | 37 | 9 | 24.32% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 34.92% |
| gsm8k_socratic | 29.03% |
| mbpp_full | 49.21% |
| mbpp_sanitized | 67.74% |
| natural_questions | 15.87% |
| proofwriter | 17.46% |
| reclor | 20.97% |
| squad | 14.52% |

## Error Analysis

- **Total Errors:** 688
- **Call Errors (failed API):** 52
- **Empty Predictions:** 52

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- wrong_answer
- execution-error:test-failed
- execution-error:object of type 'int' has no len()

## Per-Domain Error Breakdown

### Code

- execution-error:test-failed: 37
- execution-error:name 'cmath' is not defined: 3
- execution-error:object of type 'int' has no len(): 1
- execution-error:'list' object has no attribute 'split': 1
- execution-error:k must be a non-negative integer: 1

### Knowledge

- wrong_answer: 102
- invalid-output-format: 4

### Logic

- wrong_answer: 101

### Math

- wrong_answer: 85

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 2.300 | 0.267 | 12.309 | 285.203 | 124 |
| knowledge | 0.857 | 0.118 | 6.864 | 107.133 | 125 |
| logic | 0.559 | 0.092 | 5.368 | 69.276 | 124 |
| math | 0.573 | 0.108 | 4.812 | 71.609 | 125 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
