# Benchmark Report: local:llama3.1:8b

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 28.60% |
| Final Score (Weighted) | 0.254000 |
| Total Questions | 500 |
| Correct Answers | 143 |
| Failure Rate | 11.00% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 56.00% | 125 | 15% | 0.084000 |
| knowledge | 24.00% | 125 | 35% | 0.084000 |
| logic | 19.20% | 125 | 25% | 0.048000 |
| math | 15.20% | 125 | 25% | 0.038000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 337 | 115 | 34.12% |
| medium | 126 | 20 | 15.87% |
| hard | 37 | 8 | 21.62% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 15.87% |
| gsm8k_socratic | 14.52% |
| mbpp_full | 39.68% |
| mbpp_sanitized | 72.58% |
| natural_questions | 22.22% |
| proofwriter | 23.81% |
| reclor | 14.52% |
| squad | 25.81% |

## Error Analysis

- **Total Errors:** 714
- **Call Errors (failed API):** 55
- **Empty Predictions:** 55

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- wrong_answer
- execution-error:test-failed
- execution-error:cannot access local variable 'inversions' where it is not associ...

## Per-Domain Error Breakdown

### Code

- execution-error:test-failed: 38
- execution-error:name 'cmath' is not defined: 3
- execution-error:name 'Counter' is not defined: 2
- execution-error:name 'np' is not defined: 2
- execution-error:cannot access local variable 'inversions' where it is not associated with a value: 1

### Knowledge

- wrong_answer: 93
- invalid-output-format: 2

### Logic

- wrong_answer: 101

### Math

- wrong_answer: 106

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 29.405 | 2.923 | 139.393 | 3116.969 | 106 |
| knowledge | 7.963 | 0.668 | 54.249 | 891.825 | 112 |
| logic | 6.338 | 0.377 | 34.088 | 716.206 | 113 |
| math | 5.443 | 0.417 | 26.791 | 658.577 | 121 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
