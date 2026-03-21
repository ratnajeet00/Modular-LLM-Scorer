# Configuration

## Python and packaging

Defined in `pyproject.toml`.

Core dependency:

- `requests`

Optional extras:

- `datasets` extra:
: `datasets`, `pyarrow`
- `openai` extra:
: `openai`

## Environment variables

The CLI can load variables from an env file (`--env-file`, default `.env`).

Example setup file is provided at `.env.example`.

### OpenAI

- `OPENAI_API_KEY`

### OpenRouter

- `OPENROUTER_API_KEY`

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

## Cache

Prompt cache file defaults to:

- `.benchmark_cache/prompt_cache.json`

Implementation: `benchmark_lib/utils/cache.py`

Cache key is SHA-256 hash of prompt + model name namespace.

## Logging

Logger utility: `benchmark_lib/utils/logging.py`

Current logger setup:

- level: INFO
- stream handler with timestamp/name formatting

## Supported datasets list

Canonical supported folder names are declared in:

- `benchmark_lib/dataset/validator.py`

Unknown folders are ignored with warnings.
