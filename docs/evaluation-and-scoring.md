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

### Knowledge

- normalized text exact match first
- strict numeric equivalence for number-only targets
- alias acceptance from sample metadata (`aliases`)
- short-span containment check for short factual answers
- token-overlap F1 acceptance for paraphrase tolerance
- prompt instructs short, exact phrases (max 10 words) excluding "I don't know"

### Code

- extracts fenced Python block when present
- automatically retries on `empty-code`, `test-failed`, `timeout`, and syntax errors
- if tests exist, executes candidate code and tests via `exec(compile(...))` in a shared namespace
- supports HumanEval-style `entry_point` binding to `candidate`
- subprocess timeout for code execution
- test pass/fail decides correctness
- if tests are absent but expected output exists, executes generated code and compares stdout to expected output
- if no executable checks are available, falls back to normalized exact code match

### Error signaling

Evaluator returns `(correct: bool, error: str | None)` where applicable.

Common code-eval error reasons include `empty-code`, `code-timeout`, `test-failed`, and `output-mismatch`.

## Inference orchestration

Runner implementation: `benchmark_lib/engine/runner.py`

Per sample:

1. build prompt
2. check cache
3. call model with timeout/retries if cache miss
4. evaluate prediction
5. append `EvalRecord`

Features:

- batch iteration
- no timeout enforcement - models run to completion
- timing tracking per sample (`elapsed_seconds`)
- per-domain timing aggregates (mean/min/max/total seconds)
- per-call timeout
- retry loop
- prompt-level cache
- per-record cost capture
- output cleaning before evaluation
- output format validation with retry on invalid responses
- raw output JSONL logging (`question`, `prediction`, `error`)

Current behavior details:

- math outputs can be normalized from simple expression-style replies to numeric values
- code outputs are kept as full runnable code; fenced wrappers are removed when present
- malformed or stale cached answers are ignored and refreshed

## Scoring

Scorer implementation: `benchmark_lib/engine/scorer.py`

Outputs:

- per_dataset accuracy
- per_domain accuracy
- weighted final score
- total question count
- total cost

Domain weights:

- math: 0.25
- logic: 0.25
- knowledge: 0.35
- code: 0.15

Final score formula:

`sum(domain_accuracy[domain] * domain_weight[domain])`
