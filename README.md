# Modular LLM Scorer

A modular, production-ready benchmarking framework for evaluating large language models (LLMs) across **math**, **logic**, **knowledge**, and **code** — with statistical rigor, reproducibility, and sandboxed code evaluation.

**Python**: 3.10+ · **Model providers**: 8 · **Datasets**: 10+ · **Validation tests**: 43/43 (100%)

---

## Overview

Modular LLM Scorer runs rule-based, deterministic evaluation on stratified samples and produces comparable scores across any supported provider. It supports multiple API providers plus local models, tracks exact prompts and token usage, and reports 95% Wilson score confidence intervals and McNemar's statistical tests.

Key capabilities:

- **Statistical rigor** — 95% Wilson score confidence intervals, McNemar's test for model comparison
- **Reproducibility** — Git commit tracking, exact prompt logging, per-sample token counts
- **Code safety** — Multi-layer sandboxed execution (pattern validation, subprocess isolation, timeout)
- **Professional reporting** — Markdown reports, per-domain breakdown, error categorization
- **Multi-provider support** — OpenAI, OpenRouter, Gemini, Together, Groq, Hugging Face, local (Ollama)

---

## Installation

### Prerequisites

- Python 3.10+
- `scipy>=1.8.0` (for confidence intervals and statistical tests)

### Quick Start

```powershell
# Configure API keys (never commit .env)
Copy-Item .env.example .env

# Preview sample selection (no API calls)
python run_benchmark.py --dry-run --mode quick --seed 42

# Run a benchmark
python run_benchmark.py --model local --model-name llama3.1:8b --mode half --seed 42
```

On Windows, run `$env:PYTHONIOENCODING = "utf-8"` first if you hit Unicode errors.

---

## Project Structure

```
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
│
├── run_benchmark.py            # Main CLI entry point
├── analyze_errors.py           # Error categorization
├── generate_report.py          # Markdown report generation
├── save_sample_list.py         # Sample extraction with metadata
├── mcnemar_test.py             # Standalone McNemar's statistical test
├── validate_pipeline.py        # Evaluator correctness test suite (43 tests)
│
├── requirements.txt            # Locked dependency versions
├── pyproject.toml              # Project metadata and build config
└── .env.example                # API key template (copy to `.env`, never commit `.env`)
```

---

## Usage

### Running Benchmarks

```powershell
python run_benchmark.py --dry-run --mode quick --seed 42          # preview, no API calls
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode full
python run_benchmark.py --model local --model-name deepseek-coder:6.7b --mode half --seeds 42,43,44
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant --mode quick --domain code
python run_benchmark.py --compare "bech mark/model1.json" "bech mark/model2.json"
```

### Model Providers

| Provider | `--model` | `--model-name` examples | Required env var |
|---|---|---|---|
| OpenAI | `openai` | `gpt-4o-mini`, `gpt-4o` | `OPENAI_API_KEY` |
| OpenRouter | `openrouter` | `openai/gpt-4o-mini`, `anthropic/claude-3.5-sonnet` | `OPENROUTER_API_KEY` |
| Google Gemini | `gemini` | `gemini-2.0-flash`, `gemini-1.5-flash` | `GEMINI_API_KEY` |
| Together | `together` | `mistralai/Mistral-7B-Instruct-v0.3` | `TOGETHER_API_KEY` |
| Groq | `groq` | `llama-3.1-8b-instant` | `GROQ_API_KEY` |
| Hugging Face | `huggingface` | `meta-llama/Llama-2-7b` | `HF_API_TOKEN` (API only) |
| Local (Ollama) | `local` | `llama3.1:8b`, `deepseek-coder:6.7b` | None |
| Echo (test) | `echo` | *(auto)* | None |

### Analysis Tools

```powershell
python analyze_errors.py temp_eval/raw_outputs.jsonl                 # categorize failures
python save_sample_list.py temp_eval/raw_outputs.jsonl samples.json  # export sample metadata
python generate_report.py "bech mark/model.json" report.md           # Markdown report
python mcnemar_test.py a.jsonl b.jsonl "Model 1" "Model 2"           # statistical test
python validate_pipeline.py                                          # 43 test cases
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
  "per_domain": {"math": 0.38, "logic": 0.51, "knowledge": 0.44, "code": 0.27},
  "confidence_intervals_95": {
    "overall_accuracy": {"lower": 0.39, "upper": 0.45, "accuracy": 0.42},
    "per_domain": {"math": {"lower": 0.31, "upper": 0.45}}
  },
  "difficulty_breakdown": {
    "easy":   {"count": 600, "correct": 310, "accuracy": 0.517},
    "medium": {"count": 750, "correct": 315, "accuracy": 0.42},
    "hard":   {"count": 150, "correct": 45,  "accuracy": 0.30}
  },
  "failure_breakdown": {"generation_failures": 12, "format_errors": 8, "wrong_answers": 830, "execution_errors": 25},
  "token_usage": {"total_input_tokens": 245000, "total_output_tokens": 18000, "total_tokens": 263000},
  "git_commit_hash": "abc123def*",
  "cost": 0.0,
  "timestamp": "2026-05-26T09:00:00"
}
```

Full schema also includes per-domain error/elapsed-time breakdowns and selected datasets.

### Raw JSONL Log (`temp_eval/raw_outputs.jsonl`)

One line per evaluated sample:

```json
{
  "sample_id": "gsm8k_main-2522",
  "dataset": "gsm8k_main",
  "domain": "math",
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

Copy `.env.example` to `.env`, fill in your keys, and keep `.env` **out of version control** (it is ignored via `.gitignore`):

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

> **Security**: Never commit your real `.env`. If a credential is pushed to a public repository, it must be considered compromised — rotate it immediately even after removing the file from history. Use `git filter-repo` to scrub secrets from history and Dependabot/secret-scanning alerts to stay on top of leaks.

### Feature Toggles (in `benchmark_lib/engine/evaluator.py`)

```python
ENABLE_SANDBOXED_EVAL = True        # Sandboxed code evaluation (default on)
SANDBOX_STRICT_MODE = False         # True = maximum restrictions
F1_THRESHOLD_KNOWLEDGE = 0.75       # 0.0–1.0; lower = more lenient
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

### Domains and Datasets

| Domain | Weight | Datasets |
|---|---|---|
| Math | 25% | `gsm8k_main`, `gsm8k_socratic`, `hendrycks_math_*`, `svamp` |
| Logic | 25% | `proofwriter`, `reclor` |
| Knowledge | 35% | `squad`, `natural_questions`, `trivia_qa` |
| Code | 15% | `openai_humaneval`, `mbpp_full`, `mbpp_sanitized` |

### Final Score

`final_score = Σ domain_accuracy[d] × domain_weight[d]` over {math, logic, knowledge, code}

### Sampling Strategy

- **Mode sizes**: `quick`=500, `half`=1500, `full`=6000 samples
- **Top-2 datasets per domain**: ranked by sample count (tie-break: name)
- **Difficulty split** within each dataset: 30% easy / 50% medium / 20% hard
- **Deterministic**: seeded RNG, reproducible with the same `--seed`

---

## Evaluation Logic

- **Math** — normalized text exact match → numeric extraction → `math.isclose` (tolerance `1e-3`)
- **Logic** — answer letter (A–E), option text matching, boolean normalization (True/False/Yes/No/T/F)
- **Knowledge** — exact match → numeric equivalence → alias matching → short-span containment → token F1 ≥ 0.75
- **Code** — extract fenced Python block → sandboxed execution → test assertion or stdout comparison → exact match fallback. Errors: `empty-code`, `syntax-error`, `test-failed`, `timeout`, `output-mismatch`, `execution-error`, `format-error`, `other`

---

## Statistical Methods

### Wilson Score Confidence Intervals (95%)

Applied per domain, difficulty tier, and dataset (z = 1.96):

$$\text{CI} = \frac{1}{1 + \frac{z^2}{n}}\left(\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}\right)$$

### McNemar's Test for Model Comparison

$$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$

Where `b` = samples M1 correct / M2 wrong, `c` = samples M2 correct / M1 wrong. The difference is statistically significant when the p-value < 0.05 (α = 0.05).

---

## Troubleshooting

- **`scipy` not installed** → `pip install "scipy>=1.8.0"`
- **Empty predictions** → raise `max_tokens` in `benchmark_lib/engine/prompt_builder.py`; verify connectivity and `LOCAL_BASE_URL`
- **Unicode errors (Windows)** → `$env:PYTHONIOENCODING = "utf-8"`
- **Local model timeouts** → use `--batch-size 1` / `--max-workers 1`; ensure Ollama is running (`ollama serve`); verify tags with `ollama list`
- **Stale results / no API calls** → delete the cache: `Remove-Item .benchmark_cache\prompt_cache.json`
- **Verify evaluators** → `python validate_pipeline.py` (expect 43/43 passing)

---

## Contributing

- **New model provider** — subclass `BaseModel` (implement `generate()` + `get_last_cost()`), register it in `run_benchmark.py` → `build_model()`
- **New dataset** — handle the folder in `benchmark_lib/dataset/normalizer.py` and register it in `validator.py`
- **Tune evaluation** — adjust `F1_THRESHOLD_KNOWLEDGE` / `ENABLE_SANDBOXED_EVAL` in `benchmark_lib/engine/evaluator.py`

---

## Known Limitations

- `dm-code_contests` raw shards skipped unless converted from Riegeli format
- Some logic MCQ variants (`Option A` vs `A`) not recognized (~6/43 edge cases)
- Cost tracking is a placeholder in some adapters; actual charges depend on provider
- Groq adapter throttles locally, but provider quotas still apply
- Code sandboxing is pattern-based (not fully hardened like RestrictedPython)
- GSM8K external validation and Qwen2 sampling comparison deferred

---

## Summary

| Metric | Value |
|---|---|
| Domains Covered | 4 (math, logic, knowledge, code) |
| Model Providers | 8 |
| Supported Datasets | 10+ |
| Validation Tests | 43/43 (100%) |
| Statistical Methods | 2 (Wilson CI, McNemar's) |
| Code Security Layers | 3 (pattern, subprocess, timeout) |

---

**Repository**: [ratnajeet00/Modular-LLM-Scorer](https://github.com/ratnajeet00/Modular-LLM-Scorer)  
**License**: See `LICENSE`