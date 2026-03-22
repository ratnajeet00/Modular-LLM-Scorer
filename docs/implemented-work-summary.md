# Implemented Work Summary

This file summarizes what has been implemented in the project.

## Completed capabilities

1. Full benchmark package scaffold under `benchmark_lib`.
2. Dataset validation and normalization from mixed formats.
3. Domain-specific difficulty tagging heuristics.
4. Deterministic sampler with mode sizing.
5. Enforced selection of two distinct datasets per domain.
6. Easy/medium/hard stratified sampling within selected datasets.
7. Prompt templating by domain.
8. Inference loop with timeout, retry, cache, and cost hooks.
9. Strict rule-based evaluators for math, logic, knowledge, and code.
10. Weighted scoring with per-dataset and per-domain metrics.
11. Provider-agnostic model interface plus OpenAI, OpenRouter, Gemini, Together, and Groq adapters.
12. Local model adapter with OpenAI-compatible and Ollama-native endpoint support.
13. Knowledge evaluator with alias/paraphrase tolerance and strict numeric checks.
14. Code evaluator with robust exec-based test harness and output-based fallback execution.
15. CLI for benchmark execution.
16. Project-level README and full docs folder.
17. Task-specific prompt policy updates for code/math/knowledge datasets.
18. Output cleaning and output-format validation before evaluation.
19. Retry-on-invalid-output handling in inference loop.
20. Raw output JSONL logging for debugging and analysis.
21. Cache reuse hardened by cleaning/validating cached responses before scoring.
22. Groq local rate-window throttling for RPM/TPM constraints.
23. CLI extensions for `--max-workers` and `--raw-output-log`.
24. Enhanced logic evaluation with boolean normalization and single-letter extraction.
25. Strict prompt enforcement for math final answers and knowledge conciseness.
26. Local model optimizations (auto-timeout adjustment, retry increase, batch size caps).

## Current high-level execution flow

1. Validate dataset root and folder set.
2. Normalize to canonical sample schema.
3. Pick exactly two datasets per domain and filter all others out.
4. Allocate sample budget across domains and selected datasets.
5. Stratify selected datasets by easy/medium/hard.
6. Build prompts and call model adapter with timeout/retry/cache.
7. Evaluate predictions with deterministic rules.
8. Aggregate metrics and compute weighted final score.

## Verification status

Quick-mode smoke benchmark has been run successfully after the two-datasets-per-domain changes and documentation updates.
