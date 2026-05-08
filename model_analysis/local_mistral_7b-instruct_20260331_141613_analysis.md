# Benchmark Report: local:mistral:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 13.20% |
| Final Score (Weighted) | 0.136000 |
| Total Questions | 500 |
| Correct Answers | 66 |
| Failure Rate | 21.20% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 15.20% | 125 | 15% | 0.022800 |
| knowledge | 19.20% | 125 | 35% | 0.067200 |
| logic | 15.20% | 125 | 25% | 0.038000 |
| math | 3.20% | 125 | 25% | 0.008000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 335 | 57 | 17.01% |
| medium | 128 | 8 | 6.25% |
| hard | 37 | 1 | 2.70% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 3.17% |
| gsm8k_socratic | 3.23% |
| mbpp_full | 20.63% |
| mbpp_sanitized | 9.68% |
| natural_questions | 19.05% |
| proofwriter | 26.98% |
| reclor | 3.23% |
| squad | 19.35% |

## Error Analysis

- **Total Errors:** 868
- **Call Errors (failed API):** 106
- **Empty Predictions:** 106

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

- invalid-output-format: 80
- execution-error:test-failed: 7
- execution-error:name 'Counter' is not defined: 3
- execution-error:name 'List' is not defined: 2
- execution-error:name 'factorial' is not defined: 2

### Knowledge

- wrong_answer: 92
- invalid-output-format: 9

### Logic

- wrong_answer: 106

### Math

- wrong_answer: 121

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 15.241 | 0.743 | 44.400 | 1874.612 | 123 |
| knowledge | 2.113 | 0.120 | 17.841 | 259.938 | 123 |
| logic | 1.474 | 0.065 | 8.059 | 176.858 | 120 |
| math | 1.853 | 0.093 | 12.292 | 227.945 | 123 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
