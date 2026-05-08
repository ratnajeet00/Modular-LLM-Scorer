# Evaluation and Scoring

## Rule-based evaluators

Evaluator implementation: `benchmark_lib/engine/evaluator.py`

### Math

- normalized text exact match first
- numeric fallback by extracting numeric value
- tolerant comparison via `math.isclose` (default tolerance `1e-3`)
- strict prompt enforcement for final numeric answers only (no explanation)

### Logic

- direct answer text normalization
- supports option-letter predictions (A-E) when options exist
- **robust boolean normalization**: handles True/False, T/F, Yes/No, and case iterations
- Configurable via prompt templates

### Knowledge

- normalized text exact match first
- strict numeric equivalence for number-only targets
- alias acceptance from sample metadata (`aliases`)
- short-span containment check for short factual answers
- token-overlap F1 acceptance for paraphrase tolerance
- **Configurable F1 threshold**: `F1_THRESHOLD_KNOWLEDGE` (default 0.75)
  - Lower = more lenient (0.5), upper = stricter (0.9)
- Prompt instructs short, exact phrases (max 10 words) excluding "I don't know"

### Code

- extracts fenced Python block when present
- automatically retries on `empty-code`, `test-failed`, `timeout`, and syntax errors
- **Sandboxed execution** via `benchmark_lib/engine/sandboxed_eval.py`:
  - Pattern validation: blocks `exec`, `eval`, file operations, system commands
  - Subprocess isolation: separate process with configurable timeout (default 10s)
  - Output truncation and monitoring for safety
- If tests exist, executes candidate code and tests
- Supports HumanEval-style `entry_point` binding to `candidate`
- Test pass/fail decides correctness
- If tests absent but expected output exists, executes generated code and compares stdout
- Falls back to normalized exact code match if no executable checks available

### Error signaling

Evaluator returns `(correct: bool, error: str | None)` where applicable.

**Code evaluation error categories** (8 types):
- `empty-code`: No code generated
- `syntax-error`: Code fails to parse
- `test-failed`: Code runs but test assertions fail
- `timeout`: Code execution exceeded time limit
- `output-mismatch`: stdout does not match expected
- `execution-error`: Runtime exception (NameError, TypeError, etc.)
- `format-error`: Invalid output format
- `other`: Unexpected failure

## Inference orchestration

Runner implementation: `benchmark_lib/engine/runner.py`

Per sample:

1. Build prompt (domain-specific with refusal prevention)
2. Check cache
3. Call model with timeout/retries if cache miss
4. Evaluate prediction (rule-based, potentially sandboxed)
5. Append `EvalRecord` with timing data

Features:

- Batch iteration with configurable batch size
- **No timeout enforcement** - models run to completion (timeout arg for compatibility only)
- **Timing tracking** per sample: `elapsed_seconds`
- **Per-domain aggregates**: mean/min/max/total seconds and sample count
- Per-call timeout configurable (default 10s for code execution)
- Retry loop with exponential backoff
- Prompt-level SHA-256 cache with validation
- Per-record cost capture (where applicable)
- Output cleaning before evaluation (whitespace normalization, etc.)
- Output format validation with retry on invalid responses
- Raw output JSONL logging: `question`, `prediction`, `error`, `elapsed_seconds`

Current behavior details:

- **Math outputs**: Normalized from simple expression-style replies to numeric values
- **Code outputs**: Kept as full runnable code; fenced wrappers removed
- **Knowledge outputs**: Trimmed to max 10 words for consistency
- Cache: Malformed or stale cached answers ignored and refreshed

## Scoring & Statistical Analysis

Scorer implementation: `benchmark_lib/engine/scorer.py`

### Outputs

- **Per-dataset accuracy**: Raw correctness rate per dataset
- **Per-domain accuracy**: Weighted accuracy within domain (if multiple datasets)
- **Per-domain confidence intervals**: 95% Wilson score method
- **Per-difficulty breakdown**: Accuracy by (easy/medium/hard)
- Per-difficulty confidence intervals
- **Weighted final score**: Domain-weighted sum
- **Error breakdown**: Count of each error category
- **Timing aggregates**: Per-domain timing statistics
- **Total question count** and **total cost** (where tracked)

### Domain Weights

- Math: 0.25
- Logic: 0.25
- Knowledge: 0.35
- Code: 0.15

### Final Score Formula

```
score = Σ(domain_accuracy[domain] × domain_weight[domain]) 
        for domain in {math, logic, knowledge, code}
```

### Confidence Interval Calculation

**Wilson Score method** (recommended for small samples):

$$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Where:
- $\hat{p}$ = accuracy (proportion correct)
- $n$ = sample count
- $z$ = 1.96 (95% confidence level)

Benefits: Handles edge cases (0% and 100% accuracy) gracefully.

## Model Comparison: McNemar's Test

Located in: `mcnemar_test.py` (standalone utility) and integrated into `run_benchmark.py --compare`

### Purpose

Test whether two models have **statistically significant differences** on the same evaluation set.

### Test Statistic

$$\chi^2 = \frac{(|b-c| - 1)^2}{b + c}$$

Where:
- $b$ = samples Model 1 correct, Model 2 wrong
- $c$ = samples Model 2 correct, Model 1 wrong

### Interpretation

- **p-value < 0.05**: Statistically significant difference (reject null hypothesis)
- **p-value ≥ 0.05**: No significant difference
- Requires minimum 25+ disagreements for reliable result

### Example Usage

```powershell
# Standalone McNemar's test
python mcnemar_test.py log1.jsonl log2.jsonl "Model 1" "Model 2"

# Via benchmark --compare
python run_benchmark.py --compare result1.json result2.json
```

### Output Interpretation

```
McNemar's χ² = 4.2, p-value = 0.04
Result: Models are SIGNIFICANTLY DIFFERENT (p < 0.05)
Accuracy delta: Model 1 is +2.5% more accurate
```

## Error Analysis

Tool: `analyze_errors.py`

Categorizes failures into:
1. Empty predictions
2. Execution errors
3. Format errors
4. Timeout errors
5. Test failures
6. Output mismatches
7. Syntax errors
8. Other/unknown

Usage:
```powershell
python analyze_errors.py temp_eval/raw_outputs.jsonl
```

Output: Per-domain error frequency table and recommendations.
