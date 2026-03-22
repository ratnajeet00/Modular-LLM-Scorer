# Models and CLI

## Model interface

Base abstraction: `benchmark_lib/models/base_model.py`

- Required: `generate(prompt: str, max_tokens: int | None = None) -> str`
- Optional: `get_last_cost() -> float`

All adapters run with `temperature=0.2` and accept domain/token limits from the runner.

## Implemented adapters

### OpenAI

File: `benchmark_lib/models/openai_model.py`

- requires `OPENAI_API_KEY`
- chat completions

### OpenRouter

File: `benchmark_lib/models/openrouter_model.py`

- requires `OPENROUTER_API_KEY`
- chat completions over HTTP
- retries token-pressure errors by reducing `max_tokens`

### Local (OpenAI-compatible + Ollama-native fallback)

File: `benchmark_lib/models/local_model.py`

- supports OpenAI-style local endpoints and native Ollama fallback
- default URL: `http://localhost:11434/v1`
- falls back to `/api/chat` when OpenAI route is unavailable
- **automatic optimizations**:
  - increases timeout to 120s
  - increases retries to 3
  - caps batch size at 4 for stability

### Hugging Face

File: `benchmark_lib/models/huggingface_model.py`

- local transformers mode (`--hf-device cpu|cuda|mps`)
- Inference API mode (`--hf-use-inference-api`)
- automatic fallback to chat completions for providers that do not support `text_generation`

### Gemini

File: `benchmark_lib/models/gemini_model.py`

- requires `GEMINI_API_KEY`
- endpoint probe and retry behavior for stable/preview API versions

### Together

File: `benchmark_lib/models/together_model.py`

- requires `TOGETHER_API_KEY`
- OpenAI-compatible chat completions with retry/backoff

### Groq

File: `benchmark_lib/models/groq_model.py`

- requires `GROQ_API_KEY`
- local throttling to enforce rate windows
  - `GROQ_RPM_LIMIT` (default 30)
  - `GROQ_TPM_LIMIT` (default 6000)

## CLI

Entrypoint: `run_benchmark.py`

### Main args

- `--dataset-path` (default `data/raw_datasets`)
- `--model` (`echo`, `openai`, `openrouter`, `local`, `huggingface`, `gemini`, `together`, `groq`)
- `--model-name` (explicit model id)
- `--mode` (`quick`, `half`, `full`)
- `--seed` / `--seeds`
- `--batch-size`
- `--max-workers`
- `--timeout-seconds`
- `--retries`
- `--raw-output-log`
- `--env-file`
- local/HF specific args (`--local-base-url`, `--local-api-key`, `--hf-api-token`, `--hf-use-inference-api`, `--hf-device`)

## Provider testing commands (3 per provider)

### OpenAI

```powershell
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick --max-workers 2 --seed 7
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick --raw-output-log temp_eval/openai_quick.jsonl
```

### OpenRouter

```powershell
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick
python run_benchmark.py --model openrouter --model-name anthropic/claude-3.5-sonnet --mode quick --max-workers 2
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick --raw-output-log temp_eval/openrouter_quick.jsonl
```

### Local

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --local-base-url http://localhost:11434/v1 --mode quick
python run_benchmark.py --model local --model-name llama3.1:8b --local-base-url http://localhost:11434 --mode quick
python run_benchmark.py --model local --model-name llama3.1:8b --mode quick --max-workers 1 --raw-output-log temp_eval/local_quick.jsonl
```

### Hugging Face

```powershell
python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-7b --hf-device cpu --mode quick
python run_benchmark.py --model huggingface --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --hf-use-inference-api --mode quick
python run_benchmark.py --model huggingface --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --hf-use-inference-api --mode quick --raw-output-log temp_eval/hf_quick.jsonl
```

### Gemini

```powershell
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick
python run_benchmark.py --model gemini --model-name gemini-1.5-flash --mode quick --max-workers 2
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick --raw-output-log temp_eval/gemini_quick.jsonl
```

### Together

```powershell
python run_benchmark.py --model together --model-name mistralai/Mistral-7B-Instruct-v0.3 --mode quick
python run_benchmark.py --model together --model-name meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo --mode quick --max-workers 2
python run_benchmark.py --model together --model-name mistralai/Mistral-7B-Instruct-v0.3 --mode quick --raw-output-log temp_eval/together_quick.jsonl
```

### Groq

```powershell
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant --mode quick --max-workers 1
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant --mode quick --max-workers 1 --batch-size 2
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant --mode quick --max-workers 1 --raw-output-log temp_eval/groq_quick.jsonl
```

## Troubleshooting notes

- If dashboard usage looks missing, ensure shell key and `.env` key point to the same account.
- Clear cache for live-call verification: remove `.benchmark_cache/prompt_cache.json`.
- For local models, use exact tag from `ollama list`.
