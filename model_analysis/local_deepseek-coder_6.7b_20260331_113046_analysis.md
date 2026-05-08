# Benchmark Report: local:deepseek-coder:6.7b

**Generated:** 2026-04-26 12:36:50

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 14.60% |
| Final Score (Weighted) | 0.114800 |
| Total Questions | 500 |
| Correct Answers | 73 |
| Failure Rate | 16.80% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 32.80% | 125 | 15% | 0.049200 |
| knowledge | 1.60% | 125 | 35% | 0.005600 |
| logic | 17.60% | 125 | 25% | 0.044000 |
| math | 6.40% | 125 | 25% | 0.016000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 337 | 63 | 18.69% |
| medium | 126 | 8 | 6.35% |
| hard | 37 | 2 | 5.41% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 6.35% |
| gsm8k_socratic | 6.45% |
| mbpp_full | 25.40% |
| mbpp_sanitized | 40.32% |
| natural_questions | 1.59% |
| proofwriter | 22.22% |
| reclor | 12.90% |
| squad | 1.61% |

## Error Analysis

- **Total Errors:** 854
- **Call Errors (failed API):** 84
- **Empty Predictions:** 84

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- invalid-output-format
- wrong_answer
- execution-error:argument of type 'int' is not iterable

## Per-Domain Error Breakdown

### Code

- invalid-output-format: 71
- execution-error:test-failed: 10
- execution-error:argument of type 'int' is not iterable: 1
- execution-error:can only concatenate str (not "int") to str: 1
- execution-error:name 'date' is not defined: 1

### Knowledge

- wrong_answer: 122
- invalid-output-format: 1

### Logic

- wrong_answer: 73
- invalid-output-format: 30

### Math

- wrong_answer: 94
- invalid-output-format: 23

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 39.119 | 1.334 | 94.002 | 4342.234 | 111 |
| knowledge | 9.020 | 0.375 | 52.261 | 1001.269 | 111 |
| logic | 14.462 | 0.168 | 95.860 | 1359.381 | 94 |
| math | 19.319 | 1.814 | 69.599 | 2163.693 | 112 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
