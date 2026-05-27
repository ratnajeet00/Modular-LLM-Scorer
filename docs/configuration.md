# Configuration

## Python & Packaging

Defined in `pyproject.toml`:

- **Name**: `benchmark-lib`
- **Version**: `0.1.0`
- **Requires**: Python ≥ 3.10

### Core Dependencies

| Package | Minimum Version | Purpose |
|---|---|---|
| `requests` | `>=2.31.0` | HTTP calls for OpenRouter, Together, Gemini |
| `scipy` | `>=1.8.0` | Wilson score CIs and McNemar's test |
| `groq` | `>=1.1.1` | Groq API client |
| `google-genai` | `>=1.0.0` | Google Gemini client |

### Optional Extras

| Extra | Packages | Install with |
|---|---|---|
| `datasets` | `datasets>=2.18.0`, `pyarrow>=14.0.0` | `pip install -e ".[datasets]"` |
| `openai` | `openai>=1.30.0` | `pip install -e ".[openai]"` |
| `groq` | `groq>=0.9.0` | Included in core |

See `requirements.txt` for locked dependency versions.

---

## Environment Variables

The CLI loads variables from `.env` (or the file specified by `--env-file`). Model names are **never** read from the environment — always pass them via `--model-name`.

### OpenAI

```ini
OPENAI_API_KEY=sk-...
```

### OpenRouter

```ini
OPENROUTER_API_KEY=sk-or-...
```

### Google Gemini

```ini
GEMINI_API_KEY=...
```

### Together AI

```ini
TOGETHER_API_KEY=...
```

### Groq

```ini
GROQ_API_KEY=gsk_...
GROQ_RPM_LIMIT=30      # Requests per minute (default 30)
GROQ_TPM_LIMIT=6000    # Tokens per minute (default 6000)
```

Groq adapter enforces these limits locally via a sliding window. Provider quotas may still apply.

### Hugging Face

```ini
HF_API_TOKEN=hf_...               # Required for Inference API; optional for local
HF_USE_INFERENCE_API=false        # true = cloud API, false = local transformers
HF_DEVICE=cpu                     # cpu | cuda | mps (for local inference)
```

### Local / Ollama

```ini
LOCAL_BASE_URL=http://localhost:11434/v1  # OpenAI-compatible endpoint
LOCAL_API_KEY=                            # Optional; leave empty for Ollama
```

Local adapter behavior:
- First tries OpenAI-compatible `POST /chat/completions`
- Falls back to Ollama-native `POST /api/chat` if the route is unavailable

For Ollama, use the exact model tag shown in `ollama list` (e.g. `llama3.1:8b`, `deepseek-coder:6.7b`).

---

## Feature Configuration

These constants are in `benchmark_lib/engine/evaluator.py` and can be changed directly:

### Sandboxed Code Evaluation

```python
ENABLE_SANDBOXED_EVAL = True   # Enable sandbox safety check before code execution (default: True)
SANDBOX_STRICT_MODE = False    # Set True for maximum restrictions (default: False)
```

- `True` / `False`: enables/disables pattern-based safety validation before subprocess execution
- `SANDBOX_STRICT_MODE = True`: adds additional restriction layer for tighter security

### Knowledge Evaluator F1 Threshold

```python
F1_THRESHOLD_KNOWLEDGE = 0.75  # Token-overlap F1 acceptance threshold (default: 0.75)
```

- Range: 0.0–1.0
- Lower (e.g. 0.5): accepts more paraphrase variations
- Higher (e.g. 0.9): stricter, closer to exact string matching
- Reduced from 0.8 → 0.75 to improve partial-match acceptance

### Code Execution Timeout

Configured in `benchmark_lib/engine/evaluator.py` as the `timeout=` argument to `subprocess.run()`:

```python
timeout=10  # seconds; subprocess is killed if exceeded → returns "code-timeout" error
```

---

## Prompt Cache

- **Default path**: `.benchmark_cache/prompt_cache.json`
- **Cache key**: SHA-256 hash of `prompt + model_name`
- **Validation**: Cached responses are cleaned and re-validated before reuse; malformed or stale entries are silently regenerated
- **Implementation**: `benchmark_lib/utils/cache.py`

To force live API calls (bypass cache):

```powershell
Remove-Item .benchmark_cache\prompt_cache.json
```

---

## CLI Arguments

### Main Benchmark Flags

| Flag | Default | Description |
|---|---|---|
| `--dataset-path` | `data/raw_datasets` | Root directory containing dataset folders |
| `--model` | `echo` | Provider: `echo`, `openai`, `openrouter`, `local`, `huggingface`, `gemini`, `together`, `groq` |
| `--model-name` | *(provider default)* | Explicit model identifier (required for `openai`, `openrouter`, `local`, `huggingface`) |
| `--mode` | `half` | Sample size: `quick` (~500), `half` (~1500), `full` (~6000) |
| `--seed` | `42` | Random seed for deterministic sampling |
| `--seeds` | *(none)* | Comma-separated list for multi-seed runs, e.g. `42,43,44` |
| `--domain` | *(all 4)* | Restrict to a single domain: `math`, `logic`, `knowledge`, `code` |
| `--batch-size` | `8` | Samples per processing batch |
| `--max-workers` | *(auto)* | Concurrent model request threads |
| `--retries` | `2` | Retry attempts per sample on failure |
| `--timeout-seconds` | *(disabled)* | Accepted for backward compatibility; models run without time limits |
| `--raw-output-log` | `temp_eval/raw_outputs.jsonl` | JSONL path for per-sample logs |
| `--env-file` | `.env` | Path to environment variable file |

### Analysis & Comparison Flags

| Flag | Description |
|---|---|
| `--dry-run` | Preview sample selection counts by domain/difficulty — no API calls made |
| `--compare RESULT1 RESULT2` | Side-by-side comparison of two result JSON files, including McNemar's test if JSONL logs are found |

### Local / HF-Specific Flags

| Flag | Default | Description |
|---|---|---|
| `--local-base-url` | `http://localhost:11434/v1` | Ollama or other local endpoint |
| `--local-api-key` | *(empty)* | API key for local endpoint (optional) |
| `--hf-api-token` | *(env)* | Hugging Face token (overrides `HF_API_TOKEN`) |
| `--hf-use-inference-api` | `false` | Use cloud Inference API instead of local `transformers` |
| `--hf-device` | `cpu` | Local inference device: `cpu`, `cuda`, or `mps` |

### Example Invocations

```powershell
# Local Ollama model
python run_benchmark.py --model local --model-name llama3.1:8b --mode quick --seed 42

# Preview sampling (no API calls)
python run_benchmark.py --dry-run --mode quick

# Statistical comparison of two runs
python run_benchmark.py --compare "bech mark\result1.json" "bech mark\result2.json"

# Gemini full benchmark with custom log path
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode full \
    --raw-output-log temp_eval/gemini_full.jsonl

# Multi-seed run for averaging
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant \
    --mode half --seeds 42,43,44 --max-workers 1
```

---

## Output Files

### Results JSON

**Location**: `bech mark/{model}_{timestamp}.json`

Key fields:

| Field | Type | Description |
|---|---|---|
| `model` | `str` | Model name |
| `mode` | `str` | Benchmark mode |
| `accuracy` | `float` | Overall accuracy |
| `final_score` | `float` | Domain-weighted score |
| `per_domain` | `dict` | Accuracy per domain |
| `confidence_intervals_95` | `dict` | Wilson CIs for overall and per-domain accuracy |
| `difficulty_breakdown` | `dict` | Count/accuracy/CI per difficulty tier |
| `failure_breakdown` | `dict` | Counts of generation failures, format errors, wrong answers, execution errors |
| `per_domain_errors` | `dict` | Error type frequency per domain |
| `per_domain_timing` | `dict` | mean/min/max/total seconds per domain |
| `token_usage` | `dict` | Total and per-domain input/output token counts |
| `git_commit_hash` | `str` | Commit hash + `*` if uncommitted changes present |
| `selected_datasets_by_domain` | `dict` | Which 2 datasets were selected per domain |
| `cost` | `float` | Total API cost (where tracked) |

### Raw Output JSONL

**Location**: `temp_eval/raw_outputs.jsonl` (or path from `--raw-output-log`)

Each line is one `EvalRecord`:

```json
{
  "sample_id": "gsm8k_main-2522",
  "dataset": "gsm8k_main",
  "domain": "math",
  "question": "...",
  "prediction": "18",
  "expected": "18",
  "correct": true,
  "error": null,
  "difficulty": "medium",
  "prompt": "[full prompt text]",
  "input_tokens": 127,
  "output_tokens": 12,
  "elapsed_seconds": 0.48
}
```

### Markdown Report

**Generated by**: `generate_report.py result.json report.md`

Sections:
- Executive summary with overall accuracy and final score
- Per-domain accuracy table with confidence intervals
- Difficulty breakdown
- Timing statistics
- Reproducibility metadata (model, seed, git commit, datasets)

---

## Logging

Logger: `benchmark_lib/utils/logging.py`

- Level: `INFO` by default
- Stream handler with `[timestamp] [name] [level]` formatting
- Key log prefixes:
  - `🧪 Testing code for {sample_id}` — code evaluation started
  - `✓ Code test PASSED` / `✗ Code test FAILED` — per-sample code results
  - `✓ Output MATCHED` / `✗ Output MISMATCH` — output comparison results
  - `[timeout]` / `[exec-failure]` — execution errors

---

## Supported Datasets

Canonical dataset folder names are declared in `benchmark_lib/dataset/validator.py`. Unsupported folder names trigger a warning but don't stop execution.

**Math**: `gsm8k_main`, `gsm8k_socratic`, `hendrycks_math_algebra`, `hendrycks_math_counting_and_probability`, `hendrycks_math_geometry`, `hendrycks_math_intermediate_algebra`, `hendrycks_math_number_theory`, `hendrycks_math_prealgebra`, `hendrycks_math_precalculus`, `svamp`

**Logic**: `proofwriter`, `reclor`

**Knowledge**: `squad`, `natural_questions`, `trivia_qa`

**Code**: `openai_humaneval`, `mbpp_full`, `mbpp_sanitized`
