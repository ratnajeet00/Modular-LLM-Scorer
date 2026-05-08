# Benchmark Report: local:llama3.1:8b

**Generated:** 2026-04-26 12:36:50

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 25.20% |
| Final Score (Weighted) | 0.211200 |
| Total Questions | 500 |
| Correct Answers | 126 |
| Failure Rate | 12.00% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 52.00% | 125 | 15% | 0.078000 |
| knowledge | 11.20% | 125 | 35% | 0.039200 |
| logic | 22.40% | 125 | 25% | 0.056000 |
| math | 15.20% | 125 | 25% | 0.038000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 336 | 106 | 31.55% |
| medium | 127 | 17 | 13.39% |
| hard | 37 | 3 | 8.11% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 19.05% |
| gsm8k_socratic | 11.29% |
| mbpp_full | 42.86% |
| mbpp_sanitized | 61.29% |
| natural_questions | 7.94% |
| proofwriter | 28.57% |
| reclor | 16.13% |
| squad | 14.52% |

## Error Analysis

- **Total Errors:** 748
- **Call Errors (failed API):** 60
- **Empty Predictions:** 60

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- execution-error:name 'np' is not defined
- wrong_answer
- execution-error:test-failed

## Per-Domain Error Breakdown

### Code

- execution-error:test-failed: 36
- execution-error:name 'np' is not defined: 6
- execution-error:name 'Counter' is not defined: 3
- execution-error:'int' object is not iterable: 2
- execution-error:list index out of range: 2

### Knowledge

- wrong_answer: 107
- invalid-output-format: 4

### Logic

- wrong_answer: 97

### Math

- wrong_answer: 106

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 26.577 | 3.121 | 98.155 | 3242.438 | 122 |
| knowledge | 5.319 | 0.599 | 41.364 | 664.897 | 125 |
| logic | 4.754 | 0.402 | 24.888 | 589.440 | 124 |
| math | 5.383 | 0.414 | 26.720 | 667.473 | 124 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
