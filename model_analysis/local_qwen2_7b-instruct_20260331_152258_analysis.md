# Benchmark Report: local:qwen2:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 33.00% |
| Final Score (Weighted) | 0.289200 |
| Total Questions | 500 |
| Correct Answers | 165 |
| Failure Rate | 10.80% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 56.80% | 125 | 15% | 0.085200 |
| knowledge | 16.00% | 125 | 35% | 0.056000 |
| logic | 27.20% | 125 | 25% | 0.068000 |
| math | 32.00% | 125 | 25% | 0.080000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 336 | 126 | 37.50% |
| medium | 127 | 28 | 22.05% |
| hard | 37 | 11 | 29.73% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 36.51% |
| gsm8k_socratic | 27.42% |
| mbpp_full | 49.21% |
| mbpp_sanitized | 64.52% |
| natural_questions | 17.46% |
| proofwriter | 28.57% |
| reclor | 25.81% |
| squad | 14.52% |

## Error Analysis

- **Total Errors:** 670
- **Call Errors (failed API):** 54
- **Empty Predictions:** 54

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- execution-error:test-failed
- wrong_answer
- execution-error:base is not invertible for the given modulus

## Per-Domain Error Breakdown

### Code

- execution-error:test-failed: 45
- execution-error:'int' object is not iterable: 2
- execution-error:base is not invertible for the given modulus: 1
- execution-error:'list' object has no attribute 'split': 1
- execution-error:integer modulo by zero: 1

### Knowledge

- wrong_answer: 99
- invalid-output-format: 6

### Logic

- wrong_answer: 91

### Math

- wrong_answer: 85

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 2.586 | 0.280 | 11.657 | 284.505 | 110 |
| knowledge | 0.668 | 0.096 | 5.776 | 77.471 | 116 |
| logic | 0.499 | 0.094 | 3.114 | 58.913 | 118 |
| math | 0.491 | 0.108 | 3.054 | 59.902 | 122 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
