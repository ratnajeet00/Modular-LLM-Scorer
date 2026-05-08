# Benchmark Report: local:mistral:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 12.60% |
| Final Score (Weighted) | 0.129200 |
| Total Questions | 500 |
| Correct Answers | 63 |
| Failure Rate | 20.40% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 18.40% | 125 | 15% | 0.027600 |
| knowledge | 21.60% | 125 | 35% | 0.075600 |
| logic | 7.20% | 125 | 25% | 0.018000 |
| math | 3.20% | 125 | 25% | 0.008000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 337 | 49 | 14.54% |
| medium | 126 | 13 | 10.32% |
| hard | 37 | 1 | 2.70% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 6.35% |
| gsm8k_socratic | 0.00% |
| mbpp_full | 12.70% |
| mbpp_sanitized | 24.19% |
| natural_questions | 20.63% |
| proofwriter | 14.29% |
| reclor | 0.00% |
| squad | 22.58% |

## Error Analysis

- **Total Errors:** 874
- **Call Errors (failed API):** 102
- **Empty Predictions:** 102

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- wrong_answer
- execution-error:name 'types' is not defined
- invalid-output-format

## Per-Domain Error Breakdown

### Code

- invalid-output-format: 81
- execution-error:test-failed: 4
- execution-error:name 'factorial' is not defined: 3
- execution-error:name 'types' is not defined: 1
- execution-error:name 'Union' is not defined: 1

### Knowledge

- wrong_answer: 90
- invalid-output-format: 8

### Logic

- wrong_answer: 116

### Math

- wrong_answer: 121

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 16.342 | 0.824 | 39.692 | 1863.024 | 114 |
| knowledge | 2.741 | 0.096 | 21.876 | 304.284 | 111 |
| logic | 1.552 | 0.066 | 9.149 | 172.297 | 111 |
| math | 1.857 | 0.102 | 8.629 | 222.877 | 120 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
