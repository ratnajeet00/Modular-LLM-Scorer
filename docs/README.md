# Documentation Index

This folder contains comprehensive technical documentation for **Modular LLM Scorer** — a production-ready benchmarking framework for evaluating large language models with statistical rigor, code safety, and professional reporting.

**Status**: 21/23 tasks complete (91%) — Publication Ready  
**Validation**: 43/43 evaluator tests passing (100%)

---

## Contents

1. [Architecture](./architecture.md) — System design, component diagram, data contracts, statistical methods
2. [Data Pipeline](./data-pipeline.md) — Dataset validation, normalization formats, difficulty tagging
3. [Sampling and Difficulty](./sampling-and-difficulty.md) — Stratified sampling strategy, mode sizes, difficulty ratios
4. [Evaluation and Scoring](./evaluation-and-scoring.md) — Rule-based grading, CIs, McNemar's test, error analysis
5. [Models and CLI](./models-and-cli.md) — All 8 model providers and complete CLI reference
6. [Configuration](./configuration.md) — Environment variables, CLI flags, feature toggles, output files
7. [Limitations and Notes](./limitations-and-notes.md) — Known limitations, edge cases, compatibility notes
8. [Implemented Work Summary](./implemented-work-summary.md) — Full task completion log and capability list
9. [Reference Models](./which%20models.md) — Recommended open-source models and selection rationale
10. [Research References](./Reseach%20paper.md) — Academic citations for datasets and evaluation methodology

---

## Quick CLI Reference

```powershell
# Preview sampling (no API calls)
python run_benchmark.py --dry-run --mode quick --seed 42

# Run benchmark
python run_benchmark.py --model local --model-name llama3.1:8b --mode half

# Compare two models with McNemar's test
python run_benchmark.py --compare result1.json result2.json

# Standalone statistical test
python mcnemar_test.py log1.jsonl log2.jsonl "Model 1" "Model 2"

# Error analysis
python analyze_errors.py temp_eval/raw_outputs.jsonl

# Generate Markdown report
python generate_report.py result.json report.md

# Validate evaluator pipeline
python validate_pipeline.py
```

---

## Key Features

### Statistical Rigor
- **95% Wilson Score Confidence Intervals** — per domain, difficulty tier, and dataset → [Evaluation and Scoring](./evaluation-and-scoring.md)
- **McNemar's Statistical Test** — paired model comparison → [Evaluation and Scoring](./evaluation-and-scoring.md)
- **Error Categorization** — 8 failure types → [Evaluation and Scoring](./evaluation-and-scoring.md)

### Code Safety & Reproducibility
- **Sandboxed Code Execution** — pattern validation, subprocess isolation, configurable timeout → [Evaluation and Scoring](./evaluation-and-scoring.md)
- **Full Prompt Logging** — exact prompt text per sample in JSONL → [Configuration](./configuration.md)
- **Token Counting** — input/output tokens per sample and domain → [Configuration](./configuration.md)
- **Git Commit Tracking** — hash + uncommitted indicator (`*`) in results → [Configuration](./configuration.md)

### Professional Workflow
- **Markdown Report Generation** — domain breakdown, timing, failure analysis → [Implemented Work Summary](./implemented-work-summary.md)
- **Analysis Tools** — error analysis, sample extraction, statistical testing → [Implemented Work Summary](./implemented-work-summary.md)
- **Evaluator Validation Pipeline** — 43 test cases, 100% pass rate → [Limitations and Notes](./limitations-and-notes.md)

---

## Source File Map

### Core Pipeline
| File | Purpose |
|---|---|
| `benchmark_lib/benchmark.py` | Main orchestration entry point |
| `benchmark_lib/dataset/validator.py` | Dataset folder & structure validation |
| `benchmark_lib/dataset/normalizer.py` | Multi-format data loading (HF disk, CSV, JSON, JSONL) |
| `benchmark_lib/dataset/difficulty.py` | Domain-specific difficulty tagging heuristics |
| `benchmark_lib/engine/sampler.py` | Deterministic stratified sampling |
| `benchmark_lib/engine/prompt_builder.py` | Domain-specific prompts with refusal prevention |
| `benchmark_lib/engine/runner.py` | Inference loop (cache, retry, timing, JSONL logging) |
| `benchmark_lib/engine/evaluator.py` | Rule-based grading for all 4 domains |
| `benchmark_lib/engine/sandboxed_eval.py` | Multi-layer code execution sandbox |
| `benchmark_lib/engine/scorer.py` | Results aggregation with 95% Wilson score CIs |

### Model Providers
| File | Provider |
|---|---|
| `benchmark_lib/models/base_model.py` | Abstract base class |
| `benchmark_lib/models/openai_model.py` | OpenAI API |
| `benchmark_lib/models/openrouter_model.py` | OpenRouter API |
| `benchmark_lib/models/local_model.py` | Local (Ollama, OpenAI-compatible) |
| `benchmark_lib/models/huggingface_model.py` | Hugging Face (local + Inference API) |
| `benchmark_lib/models/gemini_model.py` | Google Gemini |
| `benchmark_lib/models/together_model.py` | Together API |
| `benchmark_lib/models/groq_model.py` | Groq (with rate throttling) |

### Utilities & Analysis Tools
| File | Purpose |
|---|---|
| `benchmark_lib/utils/types.py` | `NormalizedSample` and `EvalRecord` dataclasses |
| `benchmark_lib/utils/cache.py` | SHA-256 prompt cache |
| `benchmark_lib/utils/logging.py` | Logger configuration |
| `analyze_errors.py` | Error categorization into 8 types |
| `generate_report.py` | Markdown report generation |
| `save_sample_list.py` | Sample extraction with metadata |
| `mcnemar_test.py` | McNemar's statistical test |
| `validate_pipeline.py` | Evaluator correctness test suite |
| `run_benchmark.py` | Main CLI entry point |

---

## Publication Readiness

All requirements for academic publication are implemented:

- ✅ 95% confidence intervals with Wilson score method
- ✅ Multiple-seed run averaging
- ✅ Full reproducibility (prompts, commits, tokens logged)
- ✅ McNemar's statistical significance testing
- ✅ 8-type error categorization and analysis
- ✅ Code safety via sandboxed subprocess execution
- ✅ Professional Markdown report generation
- ✅ Per-domain breakdown matching standard ML benchmark conventions
- ✅ Locked `requirements.txt` for environment reproducibility
- ✅ 43/43 evaluator validation tests passing

See [Implemented Work Summary](./implemented-work-summary.md) for the full task checklist.
