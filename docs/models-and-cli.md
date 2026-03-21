# Models and CLI

## Model interface

Base abstraction: `benchmark_lib/models/base_model.py`

Required method:

- `generate(prompt: str) -> str`

Optional cost hook:

- `get_last_cost() -> float`

## Implemented adapters

### OpenAI adapter

File: `benchmark_lib/models/openai_model.py`

- requires `OPENAI_API_KEY`
- uses chat completions API
- fixed `temperature=0`

### OpenRouter adapter

File: `benchmark_lib/models/openrouter_model.py`

- requires `OPENROUTER_API_KEY`
- uses HTTP endpoint `/chat/completions`
- fixed `temperature=0`
- reads `usage.cost` when provided

### Local adapter

File: `benchmark_lib/models/local_model.py`

- supports local OpenAI-compatible endpoints and Ollama-native fallback
- default base URL: `http://localhost:11434/v1`
- optional local API key support
- endpoint strategy:
  - try `<base_url>/chat/completions`
  - on route-miss, fall back to `<base_without_v1>/api/chat`

### Echo model (CLI smoke model)

Defined in `run_benchmark.py`.

Behavior: returns prompt text as prediction (used for deterministic pipeline smoke testing).

## CLI

Entrypoint: `run_benchmark.py`

### Main args

- `--dataset-path` (default `data/raw_datasets`)
- `--model` (`echo`, `openai`, `openrouter`, `local`)
- `--model-name` (explicit model id to test; required for `openai`, `openrouter`, and `local`)
- `--env-file` (default `.env`)
- `--local-base-url` (for local model endpoint)
- `--local-api-key` (optional local endpoint key)
- `--mode` (`quick`, `half`, `full`)
- `--seed`
- `--batch-size`
- `--timeout-seconds`
- `--retries`

### Example

```powershell
python run_benchmark.py \
  --dataset-path data/raw_datasets \
  --model echo \
  --mode quick \
  --batch-size 16 \
  --timeout-seconds 5 \
  --retries 0
```

Result is printed as JSON.

## Runtime model selection

`--model-name` is the only way to choose model IDs at runtime for provider/local models.

Examples:

```powershell
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick
python run_benchmark.py --model local --model-name llama3.1:8b --local-base-url http://localhost:11434/v1 --mode quick
```

## Local model troubleshooting

1. Route not found (404):
  - Keep `--local-base-url http://localhost:11434/v1` for OpenAI-compatible gateways.
  - For native Ollama, `http://localhost:11434` also works via fallback.

2. Model not found:
  - Check installed model tags with `ollama list`.
  - Use exact model tag in `--model-name` (for example `llama3.1:8b`, not `llama3.1`).
