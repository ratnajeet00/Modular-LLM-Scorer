# Evaluation and Scoring

## Overview

All evaluation is **deterministic and rule-based** — no LLM-as-judge is used. The evaluator (`benchmark_lib/engine/evaluator.py`) returns a triple `(is_correct: bool, error_msg: str | None, error_type: str | None)` for each sample.

**Structured error types** (stored in `EvalRecord.error_type`):
- `generation_failure` — empty or refused prediction
- `format_error` — prediction in an invalid format
- `wrong_answer` — syntactically valid but incorrect
- `execution_error` — code failed to execute or timed out

---

## Rule-Based Evaluators

### Math (`benchmark_lib/engine/evaluator.py → _eval_math`)

1. Normalized text exact match (`_norm_text`)
2. Numeric extraction from both prediction and expected
3. Tolerance comparison via `math.isclose(rel_tol=1e-3, abs_tol=1e-3)`

Prompts enforce "provide only the final numeric answer" to prevent explanatory text from causing false negatives.

---

### Logic (`benchmark_lib/engine/evaluator.py → _eval_logic`)

1. Boolean normalization: `True/False`, `T/F`, `Yes/No`, `Y/N` → canonical `true` / `false`
2. For MCQ (when `options` field exists):
   - Normalized text match against answer text
   - Single-letter match (A–E) against `answer_letter`
   - Normalized match against the correct option text
   - Letter extraction with `re.search(r"\b([A-E])\b")`
3. For boolean questions: direct `true` / `false` comparison

---

### Knowledge (`benchmark_lib/engine/evaluator.py → _eval_knowledge`)

Applied in order; the first match wins:

1. **Refusal detection** — `_is_refusal()` scans for patterns like "sorry, I cannot..." or "outside my expertise" → returns `False` immediately
2. **Normalized exact match** — `_norm_text(answer) == _norm_text(prediction)`
3. **Strict numeric equivalence** — if `answer` is a pure number, requires `prediction` to also be numeric and uses `math.isclose(rel_tol=1e-9)`
4. **Alias list matching** — checks `sample.metadata["aliases"]` (from SQuAD/TriviaQA alternative answer variants)
5. **Short-span containment** — if `answer` is ≤5 tokens, checks if prediction contains or is contained by the answer
6. **Token F1 acceptance** — `_token_f1(answer, prediction) >= F1_THRESHOLD_KNOWLEDGE` (default 0.75)

**Configurable threshold**:
```python
# benchmark_lib/engine/evaluator.py
F1_THRESHOLD_KNOWLEDGE = 0.75  # Adjustable (0.0 = most lenient, 1.0 = exact)
```

---

### Code (`benchmark_lib/engine/evaluator.py → _eval_code`)

Evaluation flow:

1. **Extract code block** — pulls fenced ` ```python ``` ` block; falls back to raw prediction
2. **Empty check** — returns `empty-code` if no code found
3. **Sandbox safety check** — if `ENABLE_SANDBOXED_EVAL = True`, calls `validate_code_safety()` before execution
4. **Code patches** — fixes deprecated `from collections import <ABC>` imports for Python 3.10+; prepends common stdlib imports (`math`, `re`, `sys`, `itertools`, etc.)
5. **Test harness** (when `tests` / `test` in metadata):
   - Writes candidate code and test code to a `TemporaryDirectory`
   - Runs `runner.py` in a subprocess with `timeout=10s`
   - `runner.py` uses `exec()` + smart function binding (`_select_best_callable`, `_adapt_signature`)
   - Returns `True` if `{"ok": true}`, otherwise the error message
6. **Output comparison** (when `expected_output` in metadata, no test assertions):
   - Runs `candidate.py` as a script with `stdin` input
   - Compares normalized `stdout` to expected output
   - Tolerates trailing explanations via substring containment
7. **Exact match fallback** — normalized string comparison when no executable checks exist

**Code error types**:

| Error | Meaning |
|---|---|
| `empty-code` | No code block found in prediction |
| `syntax-error` | Code fails to parse (SyntaxError) |
| `test-failed` | Code runs but test assertions fail |
| `code-timeout` | Subprocess exceeded 5-second limit |
| `output-mismatch` | stdout doesn't match expected output |
| *(exec error msg)* | Runtime exception (NameError, TypeError, etc.) |
| `sandbox-*` | Code blocked by safety check |

---

## Inference Orchestration (`benchmark_lib/engine/runner.py`)

Per-sample execution flow:

1. **Build prompt** — domain-specific template with refusal-blocking system instruction
2. **Check cache** — SHA-256 hash of `prompt + model_name`; validates cached entry before reuse
3. **Call model** — with retry loop and exponential backoff on failure
4. **Evaluate prediction** — calls domain-specific evaluator (possibly sandboxed)
5. **Append `EvalRecord`** — includes prompt text, prediction, tokens, timing, and error classification

**Key behaviors**:
- **No timeout enforcement** for model inference — models run to completion (timeout arg accepted for backward compatibility only)
- **Timing** tracked per sample as `elapsed_seconds`
- **Output cleaning** before evaluation: whitespace normalization, fence stripping
- **Format retry**: if response is in an invalid format, re-prompts once before accepting
- **Math outputs**: normalized to numeric value
- **Code outputs**: fenced wrappers removed, full runnable code preserved
- **Knowledge outputs**: trimmed to max 10 words for consistency

---

## Scoring & Statistical Analysis (`benchmark_lib/engine/scorer.py`)

### Domain Weights

| Domain | Weight |
|---|---|
| Math | 0.25 |
| Logic | 0.25 |
| Knowledge | 0.35 |
| Code | 0.15 |

### Final Score Formula

```
final_score = Σ (domain_accuracy[d] × domain_weight[d])
              for d in {math, logic, knowledge, code}
```

### Outputs Produced by `score()`

| Field | Description |
|---|---|
| `accuracy` | Overall fraction correct |
| `per_domain` | Accuracy per domain |
| `per_dataset` | Accuracy per dataset |
| `final_score` | Weighted domain score |
| `confidence_intervals_95` | Wilson CIs for overall + per-domain |
| `difficulty_breakdown` | Count, accuracy, CI per `easy`/`medium`/`hard` |
| `failure_breakdown` | Counts of each `error_type` |
| `per_domain_errors` | Error message frequency per domain |
| `per_domain_timing` | mean/min/max/total seconds per domain |
| `token_usage` | Total + per-domain input/output token counts |
| `git_commit_hash` | Current commit + `*` if dirty |
| `selected_datasets_by_domain` | Which 2 datasets were used per domain |
| `cost` | Total API cost |

---

## Confidence Intervals — Wilson Score (95%)

**Implementation**: `scipy.stats.proportion_confint(method='wilson')`

$$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Where:
- $\hat{p}$ = accuracy (proportion correct)
- $n$ = sample count
- $z = 1.96$ (95% confidence level)

**Benefits over normal approximation**: Handles 0% and 100% accuracy gracefully; recommended for small samples.

**Applied to**: overall accuracy, per-domain accuracy, per-difficulty-tier accuracy.

**Requires**: `scipy>=1.8.0`. If unavailable, CIs are omitted from results.

---

## McNemar's Test — Model Comparison

**Files**: `mcnemar_test.py` (standalone) and `run_benchmark.py --compare` (integrated)

### Purpose

Test whether two models have **statistically significant differences** in error rate on the same evaluation set (paired samples).

### Test Statistic

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$

Where:
- $b$ = samples where Model 1 is correct and Model 2 is wrong
- $c$ = samples where Model 2 is correct and Model 1 is wrong

### Interpretation

| p-value | Conclusion |
|---|---|
| `< 0.05` | Statistically significant difference (reject null hypothesis) |
| `≥ 0.05` | No significant difference detected |

> Requires ≥25 disagreements between models for reliable results. Result may be unreliable with fewer discordant pairs.

### Usage

```powershell
# Standalone (from JSONL logs)
python mcnemar_test.py temp_eval/model1.jsonl temp_eval/model2.jsonl "Model 1" "Model 2"

# Integrated (from result JSON files + auto-detected JSONL)
python run_benchmark.py --compare "bech mark\result1.json" "bech mark\result2.json"
```

### Example Output

```
================================================================================
Statistical Significance Test (McNemar's Test)
================================================================================
Common samples evaluated: 500
Samples where models disagree: 68
  Model 1 correct, Model 2 wrong: 42
  Model 2 correct, Model 1 wrong: 26

Test Statistic: 3.5647
P-value: 0.0590
Significant at α=0.05: No
→ No statistically significant difference in error rates (p=0.0590)
```

---

## Error Analysis (`analyze_errors.py`)

Categorizes all failures from a JSONL log into 8 types:

| Category | Description |
|---|---|
| `empty` | Prediction is empty or whitespace-only |
| `execution` | Runtime error during code execution |
| `format` | Invalid output format (wrong letter, unexpected structure) |
| `timeout` | Code execution exceeded time limit |
| `test_failed` | Code ran but test assertions failed |
| `output_mismatch` | stdout did not match expected output |
| `syntax_error` | Code has a Python syntax error |
| `other` | Uncategorized failure |

**Usage**:

```powershell
python analyze_errors.py temp_eval/raw_outputs.jsonl
```

**Output**: Per-domain frequency table of each error type and actionable recommendations.
