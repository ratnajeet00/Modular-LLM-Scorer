# Configuration

## Python and packaging

Defined in `pyproject.toml`.

Core dependency:

- `requests`
- `scipy>=1.8.0` (required for statistical methods)

Optional extras:

- `datasets` extra:
: `datasets`, `pyarrow`
- `openai` extra:
: `openai`
- `groq` extra:
: `groq`

See `requirements.txt` for locked dependency versions.

## Environment variables

The CLI can load variables from an env file (`--env-file`, default `.env`).

Example setup file is provided at `.env.example`.

### OpenAI

- `OPENAI_API_KEY`

### OpenRouter

- `OPENROUTER_API_KEY`

### Gemini

- `GEMINI_API_KEY`

### Together

- `TOGETHER_API_KEY`

### Groq

- `GROQ_API_KEY`
- `GROQ_RPM_LIMIT` (default `30`)
- `GROQ_TPM_LIMIT` (default `6000`)

### Hugging Face

- `HF_API_TOKEN` - API token from https://huggingface.co/settings/tokens (required for Inference API)
- `HF_USE_INFERENCE_API` - Set to `true` to use cloud Inference API, `false` for local inference (default: `false`)
- `HF_DEVICE` - Device for local inference: `cpu`, `cuda`, or `mps` (default: `cpu`)

### Local provider

- `LOCAL_BASE_URL` (default: `http://localhost:11434/v1`)
- `LOCAL_API_KEY` (optional)

Local adapter endpoint behavior:
- tries OpenAI-compatible `chat/completions`
- falls back to Ollama-native `/api/chat` when route is unavailable

Model names are not read from env. Select models only via CLI using `--model-name`.

For Ollama, use the exact installed tag from `ollama list` (for example, `llama3.1:8b`).

## Feature Configuration

### Sandboxed Code Evaluation (Production Safety)
In `benchmark_lib/engine/evaluator.py`:
```python
ENABLE_SANDBOXED_EVAL = True   # Sandbox protection is enabled by default
SANDBOX_STRICT_MODE = False    # Set to True for maximum security (only allows basic operations)
```

### Knowledge Evaluator F1 Threshold
In `benchmark_lib/engine/evaluator.py`:
```python
F1_THRESHOLD_KNOWLEDGE = 0.75  # Adjustable (default: 0.75, range: 0.0-1.0)
```
- Lower threshold: accepts more paraphrase variations
- Higher threshold: stricter exact matching

### Code Execution Timeout
Configurable per invocation:
```python
timeout_sec = 10  # seconds, adjustable in evaluator.py or runner.py
```

## Cache

Prompt cache file defaults to:

- `.benchmark_cache/prompt_cache.json`

Implementation: `benchmark_lib/utils/cache.py`

Cache key is SHA-256 hash of prompt + model name namespace.

Cached responses are cleaned/validated before reuse; invalid cached entries are ignored and regenerated.

## CLI Arguments

### Main Benchmark Flags
- `--dataset-path` (default `data/raw_datasets`) - Root dataset directory
- `--model` (required) - Provider: `echo`, `openai`, `openrouter`, `local`, `huggingface`, `gemini`, `together`, `groq`
- `--model-name` (required) - Explicit model ID (e.g., `gpt-4o-mini`, `llama3.1:8b`)
- `--mode` (default `quick`) - Sample size: `quick` (10%), `half` (50%), `full` (100%)
- `--seed` / `--seeds` - Determinism control (single seed or comma-separated list for multiple runs)
- `--batch-size` (default 4) - Samples per API call
- `--max-workers` (default 8) - Concurrent inference threads
- `--retries` (default 2) - Retry attempts on failure
- `--timeout-seconds` - DISABLED (accepted for compatibility, models run without time limits)
- `--env-file` (default `.env`) - Environment variable file

### Analysis & Comparison Flags
- `--dry-run` - **NEW** Preview sample selection without API calls
- `--raw-output-log` - Output JSONL records with question, prediction, error, and timing per sample
- `--compare` - **NEW** Side-by-side comparison of two model result files (runs McNemar's test)

Example:
```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --mode quick --seed 42
python run_benchmark.py --dry-run --mode quick  # Preview sampling without inference
python run_benchmark.py --compare result1.Json result2.json  # Statistical comparison
```

### Local/HF Specific Args
- `--local-base-url` (default `http://localhost:11434/v1`) - Ollama endpoint
- `--local-api-key` (optional) - API key for local endpoint
- `--hf-api-token` - Hugging Face API token (for Inference API)
- `--hf-use-inference-api` - Use cloud Inference API (default: local)
- `--hf-device` - Local device: `cpu`, `cuda`, or `mps` (default: `cpu`)

## Logging

Logger utility: `benchmark_lib/utils/logging.py`

Current logger setup:

- level: INFO
- stream handler with timestamp/name formatting
- file output to `benchmark.log` (optional, via config)

## Supported datasets list

Canonical supported folder names are declared in:

- `benchmark_lib/dataset/validator.py`

## Output Files Generated

### Results JSON
Located in `bech mark/` directory:
- Filename: `{model}_{timestamp}.json`
- Contains: accuracy, final_score, confidence_intervals_95, per_domain metrics, error breakdown, git_commit, timing data

### Raw Output JSONL
Located in `temp_eval/` directory (when --raw-output-log specified):
- Filename: `{model}_{timestamp}_raw_outputs.jsonl`
- Per-sample records: question, prediction, expected, correct, error, difficulty, dataset, tokens, elapsed_seconds

### Markdown Report
Generated by `generate_report.py`:
- Format: Professional Markdown with tables and statistics
- Sections: Executive summary, per-domain breakdown, reproducibility metadata
