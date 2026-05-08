# Documentation Index

This folder contains comprehensive documentation for **Modular LLM Scorer** — a production-ready benchmarking framework with statistical rigor, code safety, and professional reporting.

**Status**: 21/23 tasks complete (91%) — Ready for academic publication.

## Contents

1. [Architecture](./architecture.md) - System design with modular components
2. [Data Pipeline](./data-pipeline.md) - Dataset validation and normalization
3. [Sampling and Difficulty](./sampling-and-difficulty.md) - Stratified sampling strategy
4. [Evaluation and Scoring](./evaluation-and-scoring.md) - Rule-based grading with statistical analysis
5. [Models and CLI](./models-and-cli.md) - Model adapters and command-line interface
6. [Configuration](./configuration.md) - Environment setup, CLI flags, feature toggles
7. [Limitations and Notes](./limitations-and-notes.md) - Known limitations and edge cases
8. [Implemented Work Summary](./implemented-work-summary.md) - Task completion status and changes
9. [Reference Models](./which%20models.md) - Selected open-source models and rationale

## Key Features Documented Here

### Statistical Rigor
- **95% Confidence Intervals** (Wilson Score method) - See [Evaluation and Scoring](./evaluation-and-scoring.md)
- **McNemar's Statistical Test** for model comparison - See [Models and CLI](./models-and-cli.md)
- **Error Categorization** into 8 failure types - See [Evaluation and Scoring](./evaluation-and-scoring.md)

### Code Safety & Reproducibility
- **Sandboxed Code Execution** with pattern validation, subprocess isolation, and timeouts enabled by default - See [Evaluation and Scoring](./evaluation-and-scoring.md)
- **Full Prompt Logging** for exact reproducibility - See [Configuration](./configuration.md)
- **Token Counting** for cost tracking - See [Configuration](./configuration.md)
- **Git Versioning** with commit hash tracking - See [Configuration](./configuration.md)

### Professional Workflow
- **Analysis Tools**: Error analysis, sample extraction, statistical testing - See [Implemented Work Summary](./implemented-work-summary.md)
- **Markdown Report Generation** with per-domain breakdown - See [Implemented Work Summary](./implemented-work-summary.md)
- **Evaluator Validation Pipeline** (100% test pass rate, 43/43) - See [Implemented Work Summary](./implemented-work-summary.md)

## CLI Quick Reference

```bash
# Preview sampling without API calls
python run_benchmark.py --dry-run --mode quick --seed 42

# Run benchmark
python run_benchmark.py --model local --model-name llama3.1:8b --mode half

# Compare two models with statistics
python run_benchmark.py --compare result1.json result2.json

# Statistical test (standalone)
python mcnemar_test.py log1.jsonl log2.jsonl

# Error analysis
python analyze_errors.py temp_eval/raw_outputs.jsonl

# Generate professional report
python generate_report.py result.json report.md
```

See [Models and CLI](./models-and-cli.md) for detailed argument reference.

## Recent Additions (Latest Release)

- **95% Wilson Score Confidence Intervals** for all domain/difficulty breakdowns
- **McNemar's Statistical Test Tool** for rigorous model comparison
- **Sandboxed Code Evaluation** with multi-layer protection
- **Error Categorization & Analysis** (8 failure types)
- **Markdown Report Generation** with domain breakdown and metadata
- **CLI Enhancements**: `--compare`, `--dry-run` flags
- **Evaluator Testing**: 43/43 validation tests passing
- **Git Tracking**: Commit hash + uncommitted indicator in results
- **Token Counting**: Per-sample input/output token tracking

See [Evaluation and Scoring](./evaluation-and-scoring.md) and [Configuration](./configuration.md) for implementation details.

## Additional Guides

- [**Hugging Face Model Integration**](../HUGGINGFACE_GUIDE.md) - Local and API-based Hugging Face model support with automatic fallback
- [**Environment Setup**](../ENV_SETUP.md) - Complete guide to API tokens and environment variables
- [**Local Model Optimization**](../LOCAL_MODEL_OPTIMIZATION.md) - Performance tuning for Ollama and Hugging Face

## Quick Map of Key Source Files

### Core Pipeline
- Orchestration: `benchmark_lib/benchmark.py`
- Dataset validation: `benchmark_lib/dataset/validator.py`
- Dataset normalization: `benchmark_lib/dataset/normalizer.py`
- Difficulty tagging: `benchmark_lib/dataset/difficulty.py`
- Stratified sampling: `benchmark_lib/engine/sampler.py`
- Prompt templating: `benchmark_lib/engine/prompt_builder.py`
- Inference loop: `benchmark_lib/engine/runner.py`
- Rule-based evaluation: `benchmark_lib/engine/evaluator.py`
- **Sandboxed execution** (NEW): `benchmark_lib/engine/sandboxed_eval.py`
- Scoring & statistics: `benchmark_lib/engine/scorer.py`

### Model Providers
- Abstract base: `benchmark_lib/models/base_model.py`
- OpenAI: `benchmark_lib/models/openai_model.py`
- OpenRouter: `benchmark_lib/models/openrouter_model.py`
- Local (Ollama): `benchmark_lib/models/local_model.py`
- Hugging Face: `benchmark_lib/models/huggingface_model.py`
- Gemini: `benchmark_lib/models/gemini_model.py`
- Together: `benchmark_lib/models/together_model.py`
- Groq: `benchmark_lib/models/groq_model.py`

### Utilities & Tools
- Data types: `benchmark_lib/utils/types.py`
- Prompt caching: `benchmark_lib/utils/cache.py`
- Logging setup: `benchmark_lib/utils/logging.py`
- **Error analysis** (NEW): `analyze_errors.py`
- **Report generation** (NEW): `generate_report.py`
- **Sample extraction** (NEW): `save_sample_list.py`
- **Statistical testing** (NEW): `mcnemar_test.py`
- **Evaluator validation** (NEW): `validate_pipeline.py`

## Publication Readiness

All requirements for academic publication are implemented:
- ✅ Confidence intervals with proper statistical methods
- ✅ Multiple-run averaging support via seeds parameter
- ✅ Full reproducibility (prompts, commits, tokens)
- ✅ Statistical significance testing (McNemar's)
- ✅ Error categorization and analysis
- ✅ Code safety (sandboxed execution)
- ✅ Professional reporting
- ✅ Domain breakdown per standard ML benchmarks
- ✅ Requirements lock file

See [Implemented Work Summary](./implemented-work-summary.md) for complete checklist.
- CLI entrypoint: `run_benchmark.py`
