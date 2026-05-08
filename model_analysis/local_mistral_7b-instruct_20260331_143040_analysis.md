# Benchmark Report: local:mistral:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 14.00% |
| Final Score (Weighted) | 0.139200 |
| Total Questions | 500 |
| Correct Answers | 70 |
| Failure Rate | 20.40% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 18.40% | 125 | 15% | 0.027600 |
| knowledge | 17.60% | 125 | 35% | 0.061600 |
| logic | 15.20% | 125 | 25% | 0.038000 |
| math | 4.80% | 125 | 25% | 0.012000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 336 | 56 | 16.67% |
| medium | 127 | 13 | 10.24% |
| hard | 37 | 1 | 2.70% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 3.17% |
| gsm8k_socratic | 6.45% |
| mbpp_full | 17.46% |
| mbpp_sanitized | 19.35% |
| natural_questions | 15.87% |
| proofwriter | 22.22% |
| reclor | 8.06% |
| squad | 19.35% |

## Error Analysis

- **Total Errors:** 860
- **Call Errors (failed API):** 102
- **Empty Predictions:** 102

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

- invalid-output-format: 66
- execution-error:test-failed: 14
- execution-error:name 'Counter' is not defined: 4
- execution-error:name 'factorial' is not defined: 2
- execution-error:name 'sqrt' is not defined: 2

### Knowledge

- wrong_answer: 95
- invalid-output-format: 8

### Logic

- wrong_answer: 106

### Math

- wrong_answer: 119

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 13.015 | 0.716 | 63.527 | 1548.830 | 119 |
| knowledge | 1.838 | 0.091 | 15.967 | 215.023 | 117 |
| logic | 1.307 | 0.066 | 6.754 | 151.562 | 116 |
| math | 1.595 | 0.089 | 15.819 | 191.389 | 120 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
