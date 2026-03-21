# Models and CLI

## Model interface

Base abstraction: `benchmark_lib/models/base_model.py`

Required method:

- `generate(prompt: str, max_tokens: int | None = None) -> str`

Optional cost hook:

- `get_last_cost() -> float`

## Implemented adapters

### OpenAI adapter

File: `benchmark_lib/models/openai_model.py`

- requires `OPENAI_API_KEY`
- uses chat completions API
- fixed `temperature=0`
- domain-specific `max_tokens` (256-512)

### OpenRouter adapter

File: `benchmark_lib/models/openrouter_model.py`

- requires `OPENROUTER_API_KEY`
- uses HTTP endpoint `/chat/completions`
- fixed `temperature=0`
- reads `usage.cost` when provided
- automatic retry on 402 (payment required) with token reduction
- domain-specific `max_tokens` (256-512)

### Local adapter (Ollama)

File: `benchmark_lib/models/local_model.py`

- supports local OpenAI-compatible endpoints and Ollama-native fallback
- default base URL: `http://localhost:11434/v1`
- optional local API key support
- endpoint strategy:
  - try `<base_url>/chat/completions`
  - on route-miss, fall back to `<base_without_v1>/api/chat`
- **Auto-optimization for local models**:
  - Timeout increased to 120+ seconds
  - Retries increased to 3+
  - Batch size capped at 4
  - Tokens reduced 50% for faster inference

### Hugging Face adapter

File: `benchmark_lib/models/huggingface_model.py`

**Two modes:**

1. **Local Inference** (default)
   - Uses `transformers` pipeline for CPU/GPU/MPS inference
   - Device selection: `cpu`, `cuda`, `mps`
   - No internet required
   - Respects auto-optimization for local models

2. **Inference API**
   - Uses HF Inference API for cloud-based hosted inference
   - Requires `HF_API_TOKEN` from https://huggingface.co/settings/tokens
   - **Automatic fallback for custom providers**:
     - Attempts standard `text_generation` task first
     - Falls back to `chat.completions` API when provider doesn't support text_generation
     - Enables support for models like DeepSeek on nscale provider
   - Domain-specific `max_tokens` (256-512)

**Examples:**

```bash
# Local inference on CPU
python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-7b --hf-device cpu --mode quick

# Local inference on GPU
python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-13b --hf-device cuda --mode quick

# HF Inference API
python run_benchmark.py --model huggingface --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --hf-use-inference-api --mode quick
```

### Echo model (CLI smoke model)

Defined in `run_benchmark.py`.

Behavior: returns prompt text as prediction (used for deterministic pipeline smoke testing).

## CLI

Entrypoint: `run_benchmark.py`

### Main args

- `--dataset-path` (default `data/raw_datasets`)
- `--model` (`echo`, `openai`, `openrouter`, `local`, `huggingface`)
- `--model-name` (explicit model id to test; required for `openai`, `openrouter`, `local`, and `huggingface`)
- `--env-file` (default `.env`)
- `--local-base-url` (for local model endpoint, Ollama)
- `--local-api-key` (optional local endpoint key)
- `--hf-api-token` (Hugging Face API token for Inference API)
- `--hf-use-inference-api` (use HF Inference API instead of local inference for HuggingFace models)
- `--hf-device` (device for local HF inference: `cpu`, `cuda`, `mps`)
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
python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-7b --hf-device cpu --mode quick
python run_benchmark.py --model huggingface --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --hf-use-inference-api --mode quick
```

## Local model troubleshooting

1. Route not found (404):
  - Keep `--local-base-url http://localhost:11434/v1` for OpenAI-compatible gateways.
  - For native Ollama, `http://localhost:11434` also works via fallback.

2. Model not found:
  - Check installed model tags with `ollama list`.
  - Use exact model tag in `--model-name` (for example `llama3.1:8b`, not `llama3.1`).

## Hugging Face troubleshooting

1. **401 Unauthorized / Invalid username or password**:
   - Ensure `HF_API_TOKEN` is set correctly from https://huggingface.co/settings/tokens
   - Token must be a **Pro or user-tier token with API access**
   - Either set in `.env` or pass via CLI: `--hf-api-token your_token`

2. **Task not supported** (for custom providers):
   - System automatically detects and falls back to `chat.completions` API
   - Works for models like DeepSeek on nscale provider
   - No user action required

3. **CUDA/GPU not available**:
   - Use `--hf-device cpu` for CPU-only inference
   - Or install CUDA-enabled PyTorch for `--hf-device cuda`

4. **Model not found**:
   - Use exact HF model ID format: `owner/model` (e.g., `meta-llama/Llama-2-7b`)
   - Check model page on https://huggingface.co/models
