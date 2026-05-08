# Benchmark Report: local:qwen2:7b-instruct

**Generated:** 2026-04-26 12:36:51

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 31.40% |
| Final Score (Weighted) | 0.267600 |
| Total Questions | 500 |
| Correct Answers | 157 |
| Failure Rate | 10.20% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 59.20% | 125 | 15% | 0.088800 |
| knowledge | 12.80% | 125 | 35% | 0.044800 |
| logic | 24.00% | 125 | 25% | 0.060000 |
| math | 29.60% | 125 | 25% | 0.074000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 335 | 126 | 37.61% |
| medium | 128 | 23 | 17.97% |
| hard | 37 | 8 | 21.62% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 25.40% |
| gsm8k_socratic | 33.87% |
| mbpp_full | 49.21% |
| mbpp_sanitized | 69.35% |
| natural_questions | 12.70% |
| proofwriter | 30.16% |
| reclor | 17.74% |
| squad | 12.90% |

## Error Analysis

- **Total Errors:** 686
- **Call Errors (failed API):** 51
- **Empty Predictions:** 51

**Failure Breakdown:**
- Empty predictions: 0
- Execution errors: 0
- Format errors: 0
- Other errors: 0


**Example Errors:**
- wrong_answer
- execution-error:str.format() argument after * must be an iterable, not int
- execution-error:test-failed

## Per-Domain Error Breakdown

### Code

- execution-error:test-failed: 37
- execution-error:name 'Counter' is not defined: 2
- execution-error:str.format() argument after * must be an iterable, not int: 1
- execution-error:maximum recursion depth exceeded: 1
- execution-error:'in <string>' requires string as left operand, not list: 1

### Knowledge

- wrong_answer: 101
- invalid-output-format: 8

### Logic

- wrong_answer: 95

### Math

- wrong_answer: 88

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 2.808 | 0.387 | 11.898 | 297.667 | 106 |
| knowledge | 0.814 | 0.111 | 5.304 | 93.605 | 115 |
| logic | 0.659 | 0.092 | 3.971 | 73.766 | 112 |
| math | 0.614 | 0.109 | 3.427 | 73.007 | 119 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
