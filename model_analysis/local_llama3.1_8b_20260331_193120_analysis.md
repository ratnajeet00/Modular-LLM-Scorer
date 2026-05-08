# Benchmark Report: local:llama3.1:8b

**Generated:** 2026-04-26 12:36:50

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 27.20% |
| Final Score (Weighted) | 0.242400 |
| Total Questions | 500 |
| Correct Answers | 136 |
| Failure Rate | 12.40% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|
| code | 50.40% | 125 | 15% | 0.075600 |
| knowledge | 20.80% | 125 | 35% | 0.072800 |
| logic | 24.80% | 125 | 25% | 0.062000 |
| math | 12.80% | 125 | 25% | 0.032000 |

## Difficulty Breakdown

| Tier | Count | Correct | Accuracy |
|------|-------|---------|----------|
| easy | 335 | 112 | 33.43% |
| medium | 128 | 18 | 14.06% |
| hard | 37 | 6 | 16.22% |

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 9.52% |
| gsm8k_socratic | 16.13% |
| mbpp_full | 46.03% |
| mbpp_sanitized | 54.84% |
| natural_questions | 22.22% |
| proofwriter | 28.57% |
| reclor | 20.97% |
| squad | 19.35% |

## Error Analysis

- **Total Errors:** 728
- **Call Errors (failed API):** 62
- **Empty Predictions:** 62

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

- execution-error:test-failed: 37
- execution-error:name 'Counter' is not defined: 3
- execution-error:name 'np' is not defined: 2
- invalid-output-format: 1
- execution-error:name 'defaultdict' is not defined: 1

### Knowledge

- wrong_answer: 95
- invalid-output-format: 4

### Logic

- wrong_answer: 94

### Math

- wrong_answer: 109

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 33.798 | 3.538 | 112.204 | 3819.205 | 113 |
| knowledge | 7.559 | 0.569 | 53.180 | 899.543 | 119 |
| logic | 5.909 | 0.394 | 39.031 | 691.304 | 117 |
| math | 7.154 | 0.409 | 40.642 | 865.680 | 121 |

## Reproducibility

- **Git Commit:** `ff5c5f9ed17e7d06d429d9deee654306faf4da9f*`
- **Selected Datasets:**
  - code: mbpp_full, mbpp_sanitized
  - knowledge: natural_questions, squad
  - logic: proofwriter, reclor
  - math: gsm8k_main, gsm8k_socratic
