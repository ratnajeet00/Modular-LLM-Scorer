# Modular LLM Scorer

A modular, production-ready benchmarking framework for evaluating large language models (LLMs) across multiple domains with statistical rigor, reproducibility, and code safety.

**Version**: 1.0 | **Python**: 3.10+ | **Status**: Publication Ready  
**Validation**: 43/43 tests passing (100%) | **Tasks Completed**: 21/23 (91%)

---

## Overview

Modular LLM Scorer evaluates LLMs across four domains — **math**, **logic**, **knowledge**, and **code** — using rule-based, deterministic evaluation. It supports 8 model providers, stratified sampling, sandboxed code execution, 95% Wilson score confidence intervals, and McNemar's statistical testing.

Key capabilities:

- **Statistical rigor** — 95% Wilson score confidence intervals, McNemar's test for model comparison
- **Full reproducibility** — Git commit tracking, exact prompt logging, per-sample token counts
- **Code safety** — Multi-layer sandboxed execution (pattern validation, subprocess isolation, timeout)
- **Professional reporting** — Markdown reports, per-domain breakdown, error categorization
- **Multi-provider support** — OpenAI, OpenRouter, Gemini, Together, Groq, Hugging Face, local (Ollama)

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- `scipy>=1.8.0` (for confidence intervals and statistical tests)

### Quick Start

```powershell
# Activate virtual environment (Windows)
.venv\Scripts\activate.ps1

# Preview sample selection (no API calls)
python run_benchmark.py --dry-run --mode quick --seed 42

# Run benchmark with a local model
python run_benchmark.py --model local --model-name llama3.1:8b --mode half --seed 42

# Run benchmark with Gemini
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick

# Compare two result files
python run_benchmark.py --compare "bech mark/model1_result.json" "bech mark/model2_result.json"
```

### Windows Encoding Fix

If you see Unicode errors, run before benchmarking:

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

---

## Project Structure

```
Modular LLM Tester/
├── benchmark_lib/              # Core library
│   ├── benchmark.py            # Main orchestration entry point
│   ├── dataset/
│   │   ├── validator.py        # Dataset folder/structure validation
│   │   ├── normalizer.py       # Multi-format data loading & normalization
│   │   └── difficulty.py       # Domain-specific difficulty tagging heuristics
│   ├── engine/
│   │   ├── sampler.py          # Deterministic stratified sampling
│   │   ├── prompt_builder.py   # Domain-specific prompts with refusal prevention
│   │   ├── runner.py           # Inference loop (cache, retry, timing, logging)
│   │   ├── evaluator.py        # Rule-based grading for all 4 domains
│   │   ├── scorer.py           # Results aggregation + 95% Wilson score CIs
│   │   └── sandboxed_eval.py   # Multi-layer code execution sandbox
│   ├── models/
│   │   ├── base_model.py       # Abstract model interface
│   │   ├── openai_model.py     # OpenAI API adapter
│   │   ├── openrouter_model.py # OpenRouter API adapter
│   │   ├── local_model.py      # Local (Ollama) adapter with native fallback
│   │   ├── huggingface_model.py# HF local + Inference API adapter
│   │   ├── gemini_model.py     # Google Gemini adapter with preflight check
│   │   ├── together_model.py   # Together API adapter
│   │   ├── groq_model.py       # Groq adapter with local rate throttling
│   │   └── _rate_limit.py      # Shared rate limiting utilities
│   └── utils/
│       ├── types.py            # NormalizedSample, EvalRecord dataclasses
│       ├── cache.py            # SHA-256 prompt cache
│       └── logging.py          # Logger configuration
│
├── data/raw_datasets/          # Local dataset root (HF disk, CSV, JSON)
├── bech mark/                  # Benchmark result JSONs (auto-generated)
├── temp_eval/                  # Raw JSONL output logs (auto-generated)
├── docs/                       # Full documentation
│
├── run_benchmark.py            # Main CLI entry point
├── analyze_errors.py           # Error categorization into 8 types
├── generate_report.py          # Markdown report generation
├── save_sample_list.py         # Sample extraction with metadata
├── mcnemar_test.py             # Standalone McNemar's statistical test
├── validate_pipeline.py        # Evaluator correctness test suite (43 tests)
│
├── requirements.txt            # Locked dependency versions
├── pyproject.toml              # Project metadata and build config
└── .env                        # API keys (copy from .env.example)
```

---

## Usage Guide

### Running Benchmarks

```powershell
# Dry run — preview sample selection (no API calls)
python run_benchmark.py --dry-run --mode quick --seed 42

# Quick benchmark (10% of samples, ~500)
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick

# Half benchmark (50% of samples, ~1500)
python run_benchmark.py --model local --model-name llama3.1:8b --mode half --seed 42

# Full benchmark (100% of samples, ~6000)
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode full

# Multi-seed run for statistical averaging
python run_benchmark.py --model local --model-name deepseek-coder:6.7b --mode half --seeds 42,43,44

# Single domain only
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant --mode quick --domain code
```

### Model Providers

| Provider | `--model` | `--model-name` examples | Required env var |
|---|---|---|---|
| OpenAI | `openai` | `gpt-4o-mini`, `gpt-4o` | `OPENAI_API_KEY` |
| OpenRouter | `openrouter` | `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet` | `OPENROUTER_API_KEY` |
| Google Gemini | `gemini` | `gemini-2.0-flash`, `gemini-1.5-flash` | `GEMINI_API_KEY` |
| Together | `together` | `mistralai/Mistral-7B-Instruct-v0.3` | `TOGETHER_API_KEY` |
| Groq | `groq` | `llama-3.1-8b-instant` | `GROQ_API_KEY` |
| Hugging Face | `huggingface` | `meta-llama/Llama-2-7b` | `HF_API_TOKEN` (for API) |
| Local (Ollama) | `local` | `llama3.1:8b`, `deepseek-coder:6.7b` | None |
| Echo (test) | `echo` | *(auto)* | None |

### Analysis Tools

```powershell
# Analyze failure types from raw JSONL log
python analyze_errors.py temp_eval/raw_outputs.jsonl

# Extract sample list with metadata
python save_sample_list.py temp_eval/raw_outputs.jsonl samples.json

# Generate professional Markdown report
python generate_report.py "bech mark/model_result.json" report.md

# Standalone McNemar's statistical test
python mcnemar_test.py temp_eval/model1.jsonl temp_eval/model2.jsonl "Model 1" "Model 2"

# Compare two benchmark results (includes McNemar's test)
python run_benchmark.py --compare result1.json result2.json

# Validate evaluator pipeline (43 test cases)
python validate_pipeline.py
```

---

## Output Files

### Results JSON (`bech mark/{model}_{timestamp}.json`)

```json
{
  "model": "llama3.1:8b",
  "mode": "half",
  "accuracy": 0.42,
  "final_score": 0.35,
  "per_domain": {
    "math": 0.38,
    "logic": 0.51,
    "knowledge": 0.44,
    "code": 0.27
  },
  "confidence_intervals_95": {
    "overall_accuracy": {"lower": 0.39, "upper": 0.45, "accuracy": 0.42},
    "per_domain": {
      "math": {"lower": 0.31, "upper": 0.45},
      "code": {"lower": 0.19, "upper": 0.36}
    }
  },
  "difficulty_breakdown": {
    "easy":   {"count": 600, "correct": 310, "accuracy": 0.517},
    "medium": {"count": 750, "correct": 315, "accuracy": 0.42},
    "hard":   {"count": 150, "correct": 45,  "accuracy": 0.30}
  },
  "failure_breakdown": {
    "generation_failures": 12,
    "format_errors": 8,
    "wrong_answers": 830,
    "execution_errors": 25
  },
  "per_domain_errors": {
    "code": {"test-failed": 15, "code-timeout": 6, "empty-code": 4}
  },
  "token_usage": {
    "total_input_tokens": 245000,
    "total_output_tokens": 18000,
    "total_tokens": 263000
  },
  "per_domain_timing": {
    "code": {"mean_seconds": 4.23, "min_seconds": 1.15, "max_seconds": 8.92}
  },
  "git_commit_hash": "abc123def*",
  "selected_datasets_by_domain": {
    "math": ["gsm8k_main", "gsm8k_socratic"],
    "code": ["mbpp_sanitized", "openai_humaneval"]
  },
  "cost": 0.0,
  "timestamp": "2026-05-26T09:00:00"
}
```

### Raw JSONL Log (`temp_eval/raw_outputs.jsonl`)

Each line is one evaluated sample:

```json
{
  "sample_id": "gsm8k_main-2522",
  "dataset": "gsm8k_main",
  "domain": "math",
  "question": "Janet sells 16 eggs...",
  "prediction": "18",
  "expected": "18",
  "correct": true,
  "error": null,
  "difficulty": "medium",
  "prompt": "[full prompt sent to model]",
  "input_tokens": 127,
  "output_tokens": 12,
  "elapsed_seconds": 0.48
}
```

---

## Configuration

### Environment Variables (`.env`)

```ini
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=...
TOGETHER_API_KEY=...
GROQ_API_KEY=gsk_...
GROQ_RPM_LIMIT=30
GROQ_TPM_LIMIT=6000
HF_API_TOKEN=hf_...
HF_USE_INFERENCE_API=false
HF_DEVICE=cpu
LOCAL_BASE_URL=http://localhost:11434/v1
```

### Feature Toggles (in `benchmark_lib/engine/evaluator.py`)

```python
# Sandboxed code evaluation (enabled by default)
ENABLE_SANDBOXED_EVAL = True
SANDBOX_STRICT_MODE = False  # Set True for maximum restrictions

# Knowledge domain F1 matching threshold
F1_THRESHOLD_KNOWLEDGE = 0.75  # Range 0.0–1.0; lower = more lenient
```

### CLI Flags

| Flag | Default | Description |
|---|---|---|
| `--model` | `echo` | Provider: `openai`, `gemini`, `groq`, `local`, `huggingface`, `together`, `openrouter` |
| `--model-name` | *(varies)* | Exact model identifier |
| `--mode` | `half` | Sample size: `quick` (500), `half` (1500), `full` (6000) |
| `--seed` | `42` | Random seed for reproducibility |
| `--seeds` | *(none)* | Comma-separated seeds for multi-run averaging |
| `--domain` | *(all)* | Filter to one domain: `math`, `logic`, `knowledge`, `code` |
| `--dry-run` | `false` | Preview sampling without API calls |
| `--compare` | *(none)* | Compare two result JSONs with McNemar's test |
| `--raw-output-log` | `temp_eval/raw_outputs.jsonl` | Per-sample JSONL log path |
| `--batch-size` | `8` | Samples per batch |
| `--max-workers` | *(auto)* | Concurrent inference threads |
| `--retries` | `2` | Retry attempts on model failure |
| `--env-file` | `.env` | Path to environment variable file |

---

## Domains & Scoring

### Supported Domains and Datasets

| Domain | Weight | Datasets |
|---|---|---|
| Math | 25% | `gsm8k_main`, `gsm8k_socratic`, `hendrycks_math_*`, `svamp` |
| Logic | 25% | `proofwriter`, `reclor` |
| Knowledge | 35% | `squad`, `natural_questions`, `trivia_qa` |
| Code | 15% | `openai_humaneval`, `mbpp_full`, `mbpp_sanitized` |

### Final Score Formula

```
final_score = Σ (domain_accuracy[d] × domain_weight[d])
              for d in {math, logic, knowledge, code}
```

### Sampling Strategy

- **Mode sizes**: `quick`=500, `half`=1500, `full`=6000 samples
- **Top-2 datasets per domain**: ranked by sample count (tie-break: name)
- **Difficulty split** within each dataset: 30% easy / 50% medium / 20% hard
- **Deterministic**: seeded RNG, reproducible across runs with the same `--seed`

---

## Evaluation Logic

### Math
- Normalized text exact match → numeric extraction → `math.isclose` (tolerance `1e-3`)

### Logic
- Answer letter (A–E) extraction, option text matching, boolean normalization (True/False/Yes/No/T/F)

### Knowledge
- Exact match → numeric equivalence → alias list matching → short-span containment → token F1 ≥ 0.75

### Code
- Extract fenced Python block → sandboxed execution → test assertion or stdout comparison → exact match fallback
- **Error types**: `empty-code`, `syntax-error`, `test-failed`, `timeout`, `output-mismatch`, `execution-error`, `format-error`, `other`

---

## Statistical Methods

### Wilson Score Confidence Intervals (95%)

Applied per domain, difficulty tier, and dataset:

$$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

Where: $\hat{p}$ = accuracy, $n$ = sample count, $z = 1.96$

### McNemar's Test for Model Comparison

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$

Where $b$ = samples M1 correct / M2 wrong, $c$ = samples M2 correct / M1 wrong. P-value < 0.05 indicates a statistically significant difference (α = 0.05).

---

## Troubleshooting

**`scipy not installed`**:
```powershell
pip install "scipy>=1.8.0"
```

**Empty predictions from model**:
- Increase `max_tokens` in `benchmark_lib/engine/prompt_builder.py`
- Verify model availability and connectivity
- Check `LOCAL_BASE_URL` is correct for local models

**Unicode errors (Windows)**:
```powershell
$env:PYTHONIOENCODING = "utf-8"
```

**Local model timeouts**:
- Use `--batch-size 1` or `--max-workers 1` to reduce load
- Ensure Ollama is running: `ollama serve`
- Verify model tag: `ollama list`

**Validate evaluators**:
```powershell
python validate_pipeline.py
# Expected: 43/43 tests passing
```

**Clear prompt cache** (force live API calls):
```powershell
Remove-Item .benchmark_cache\prompt_cache.json
```

---

## Contributing

### Adding a New Model Provider

```python
# benchmark_lib/models/my_provider.py
from .base_model import BaseModel

class MyModel(BaseModel):
    model_name = "my-model-id"

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        # Call your API here
        return response_text

    def get_last_cost(self) -> float:
        return 0.0  # optional
```

Register it in `run_benchmark.py` inside `build_model()`.

### Adding a New Dataset

Extend `benchmark_lib/dataset/normalizer.py` to handle the new folder name and produce `NormalizedSample` objects. Register the dataset name in `benchmark_lib/dataset/validator.py`.

### Adjusting Evaluation Thresholds

```python
# benchmark_lib/engine/evaluator.py
F1_THRESHOLD_KNOWLEDGE = 0.75   # Raise for stricter matching
ENABLE_SANDBOXED_EVAL = True    # Disable for local testing only
```

---

## Known Limitations

- **Riegeli format**: `dm-code_contests` raw shards skipped unless converted
- **Logic MCQ variants**: Some "Option A" vs "A" formats not recognized (~6/43 edge cases)
- **Cost tracking**: Placeholder in some adapters; actual charges depend on provider
- **Groq rate limits**: Adapter throttles locally but provider quotas still apply
- **Code sandboxing**: Pattern-based, not RestrictedPython — not fully hardened
- **Task 3** (deferred): GSM8K external validation requires Meta reference scores
- **Task 10** (deferred): Qwen2 sampling comparison (general mechanism already validated)

---

## Publication Checklist

- [x] 95% Wilson score confidence intervals
- [x] McNemar's test for statistical significance
- [x] Multiple-seed averaging support
- [x] Git commit hash versioning with uncommitted indicator
- [x] Full prompt text logging (exact reproducibility)
- [x] Per-sample token count tracking
- [x] Per-domain error categorization (8 types)
- [x] Code safety via sandboxed execution
- [x] Professional Markdown report generation
- [x] Evaluator validation suite (43/43 tests, 100%)
- [x] Stratified sampling verification (`--dry-run`)
- [x] Locked `requirements.txt` for environment reproducibility

---

## Summary Statistics

| Metric | Value |
|---|---|
| Domains Covered | 4 (math, logic, knowledge, code) |
| Model Providers | 8 |
| Supported Datasets | 10+ |
| Validation Tests | 43/43 (100%) |
| Statistical Methods | 2 (Wilson CI, McNemar's) |
| Code Security Layers | 3 (pattern, subprocess, timeout) |
| Tasks Completed | 21/23 (91%) |

---

**Repository**: [ratnajeet00/Modular-LLM-Scorer](https://github.com/ratnajeet00/Modular-LLM-Scorer)  
**License**: See `LICENSE`  
**Last Updated**: May 2026
