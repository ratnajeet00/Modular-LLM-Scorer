# Documentation Index

This folder contains project documentation for Modular LLM Scorer.

## Contents

1. [Architecture](./architecture.md)
2. [Data Pipeline](./data-pipeline.md)
3. [Sampling and Difficulty](./sampling-and-difficulty.md)
4. [Evaluation and Scoring](./evaluation-and-scoring.md)
5. [Models and CLI](./models-and-cli.md)
6. [Configuration](./configuration.md)
7. [Limitations and Notes](./limitations-and-notes.md)
8. [Implemented Work Summary](./implemented-work-summary.md)

Recent behavior changes are documented in:
- [Evaluation and Scoring](./evaluation-and-scoring.md)
- [Models and CLI](./models-and-cli.md)

## Quick map of key source files

- Core API: `benchmark_lib/benchmark.py`
- Dataset validation: `benchmark_lib/dataset/validator.py`
- Dataset normalization: `benchmark_lib/dataset/normalizer.py`
- Difficulty heuristics: `benchmark_lib/dataset/difficulty.py`
- Sampling strategy: `benchmark_lib/engine/sampler.py`
- Prompt templates: `benchmark_lib/engine/prompt_builder.py`
- Inference loop: `benchmark_lib/engine/runner.py`
- Evaluators (knowledge aliases/F1, executable code tests/output checks): `benchmark_lib/engine/evaluator.py`
- Scoring: `benchmark_lib/engine/scorer.py`
- Model interface/adapters: `benchmark_lib/models/*.py`
- Cache and logging: `benchmark_lib/utils/*.py`
- CLI entrypoint: `run_benchmark.py`
