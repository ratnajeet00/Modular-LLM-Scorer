# Evaluation and Scoring

## Rule-based evaluators

Evaluator implementation: `benchmark_lib/engine/evaluator.py`

### Math

- normalized text exact match first
- numeric fallback by extracting numeric value
- tolerant comparison via `math.isclose` (default tolerance `1e-3`)

### Logic

- direct answer text normalization
- supports option-letter predictions (A-E) when options exist

### Knowledge

- normalized text exact match

### Code

- extracts fenced Python block when present
- if tests exist, executes candidate code + tests in temp script
- subprocess timeout for code execution
- test pass/fail decides correctness
- if no tests available, falls back to normalized exact code match

### Error signaling

Evaluator returns `(correct: bool, error: str | None)` where applicable.

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
- per-call timeout
- retry loop
- prompt-level cache
- per-record cost capture

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
