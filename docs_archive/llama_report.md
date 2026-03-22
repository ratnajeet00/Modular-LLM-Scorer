# Benchmark Report: local:llama3.1:8b

**Generated:** 2026-03-22 22:18:11

## Executive Summary

| Metric | Value |
|--------|-------|
| Mode | quick |
| Overall Accuracy | 19.00% |
| Final Score (Weighted) | 0.158000 |
| Total Questions | 100 |
| Correct Answers | 19 |
| Failure Rate | 15.00% |
| Total Cost | $0.00 |

## Per-Domain Performance

| Domain | Accuracy | Samples | Weight | Weighted Score |
|--------|----------|---------|--------|-----------------|

## Per-Dataset Performance

| Dataset | Accuracy |
|---------|----------|
| gsm8k_main | 15.38% |
| gsm8k_socratic | 0.00% |
| mbpp_full | 30.77% |
| mbpp_sanitized | 50.00% |
| natural_questions | 7.69% |
| proofwriter | 15.38% |
| reclor | 25.00% |
| squad | 8.33% |

## Error Analysis

- **Total Errors:** 16
- **Call Errors (failed API):** 15
- **Empty Predictions:** 15

**Example Errors:**
- execution-error:test-failed
- execution-error:name 'calendar' is not defined
- execution-error:invalid literal for int() with base 10: '('

## Performance Timing

| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |
|--------|----------|---------|---------|-----------|---------|
| code | 33.601 | 5.088 | 107.536 | 840.036 | 25 |
| knowledge | 7.451 | 1.125 | 27.933 | 186.275 | 25 |
| logic | 5.164 | 0.472 | 16.002 | 129.112 | 25 |
| math | 7.806 | 0.691 | 30.629 | 195.153 | 25 |

## Reproducibility

