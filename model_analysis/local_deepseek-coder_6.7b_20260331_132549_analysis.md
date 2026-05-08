# Benchmark Report: local:deepseek-coder:6.7b

**Generated:** 2026-04-26 12:36:50

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 14.20% |
| Final Score (Weighted) | 0.112400 |
| Total Questions | 500 |
| Correct Answers | 71 |
| Failure Rate | 17.40% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 30.40% | 125 | 15% | 0.045600 |
| knowledge | 0.80% | 125 | 35% | 0.002800 |
| logic | 21.60% | 125 | 25% | 0.054000 |
| math | 4.00% | 125 | 25% | 0.010000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 335 | 63 | 18.81% |
| medium | 128 | 4 | 3.12% |
| hard | 37 | 4 | 10.81% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 3.17% |
| gsm8k_socratic | 4.84% |
| mbpp_full | 31.75% |
| mbpp_sanitized | 29.03% |
| natural_questions | 0.00% |
| proofwriter | 30.16% |
| reclor | 12.90% |
| squad | 1.61% |

## Error Analysis

- **Total Errors:** 858
- **Call Errors (failed API):** 87
- **Empty Predictions:** 87

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- wrong_answer
- invalid-output-format
- execution-error:test-failed

## Per-Domain Error Breakdown

### Code

- invalid-output-format: 81
- execution-error:test-failed: 4
- execution-error:'in <string>' requires string as left operand, not list: 1
- execution-error:'int' object is not iterable: 1

### Knowledge

- wrong_answer: 120
- invalid-output-format: 4

### Logic

- wrong_answer: 67
- invalid-output-format: 31

### Math

- wrong_answer: 96
- invalid-output-format: 24

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 52.354 | 2.519 | 104.265 | 5497.134 | 105 |
| knowledge | 10.127 | 0.244 | 75.795 | 1032.952 | 102 |
| logic | 16.381 | 0.182 | 70.801 | 1638.144 | 100 |
| math | 24.389 | 2.496 | 106.167 | 2731.610 | 112 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
