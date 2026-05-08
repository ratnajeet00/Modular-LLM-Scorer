# Benchmark Report: local:deepseek-coder:6.7b

**Generated:** 2026-04-26 12:36:50

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 16.60% |
| Final Score (Weighted) | 0.129200 |
| Total Questions | 500 |
| Correct Answers | 83 |
| Failure Rate | 15.60% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 37.60% | 125 | 15% | 0.056400 |
| knowledge | 0.80% | 125 | 35% | 0.002800 |
| logic | 24.00% | 125 | 25% | 0.060000 |
| math | 4.00% | 125 | 25% | 0.010000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 336 | 74 | 22.02% |
| medium | 127 | 7 | 5.51% |
| hard | 37 | 2 | 5.41% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 4.76% |
| gsm8k_socratic | 3.23% |
| mbpp_full | 31.75% |
| mbpp_sanitized | 43.55% |
| natural_questions | 0.00% |
| proofwriter | 30.16% |
| reclor | 17.74% |
| squad | 1.61% |

## Error Analysis

- **Total Errors:** 834
- **Call Errors (failed API):** 78
- **Empty Predictions:** 78

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- invalid-output-format
- wrong_answer
- execution-error:test-failed

## Per-Domain Error Breakdown

### Code

- invalid-output-format: 67
- execution-error:test-failed: 9
- execution-error:name 'pd' is not defined: 1
- execution-error:'int' object is not iterable: 1

### Knowledge

- wrong_answer: 122
- invalid-output-format: 2

### Logic

- wrong_answer: 68
- invalid-output-format: 27

### Math

- wrong_answer: 86
- invalid-output-format: 34

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 40.152 | 1.614 | 90.146 | 4175.788 | 104 |
| knowledge | 8.571 | 0.535 | 52.640 | 917.089 | 107 |
| logic | 12.939 | 0.159 | 87.349 | 1345.673 | 104 |
| math | 19.166 | 0.602 | 86.712 | 2299.945 | 120 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
