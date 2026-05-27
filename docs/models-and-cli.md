# Models and CLI

## Model Interface

All model adapters extend `BaseModel` in `benchmark_lib/models/base_model.py`.

**Required method**:
```python
def generate(self, prompt: str, max_tokens: int | None = None) -> str:
    ...
```

**Optional method**:
```python
def get_last_cost(self) -> float:
    return 0.0
```

All adapters run at `temperature=0.2` by default and accept domain-specific `max_tokens` limits from the runner.

---

## Implemented Adapters

### OpenAI

**File**: `benchmark_lib/models/openai_model.py`  
**Env var**: `OPENAI_API_KEY`  
**Protocol**: OpenAI chat completions  
**Usage**:

```powershell
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick
python run_benchmark.py --model openai --model-name gpt-4o --mode quick --max-workers 2
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick \
    --raw-output-log temp_eval/openai_quick.jsonl
```

---

### OpenRouter

**File**: `benchmark_lib/models/openrouter_model.py`  
**Env var**: `OPENROUTER_API_KEY`  
**Protocol**: OpenAI-compatible chat completions over HTTPS  
**Special behavior**: Automatically retries with reduced `max_tokens` on token-pressure errors  
**Usage**:

```powershell
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick
python run_benchmark.py --model openrouter --model-name anthropic/claude-3.5-sonnet --mode quick
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick \
    --raw-output-log temp_eval/openrouter_quick.jsonl
```

---

### Local (Ollama / OpenAI-compatible)

**File**: `benchmark_lib/models/local_model.py`  
**Env var**: `LOCAL_BASE_URL` (default `http://localhost:11434/v1`), `LOCAL_API_KEY` (optional)  
**Protocol**:
- Primary: OpenAI-compatible `POST /v1/chat/completions`
- Fallback: Ollama-native `POST /api/chat`

**Automatic optimizations** for local models:
- No timeout enforcement (models run to completion)
- Retries increased to 3
- Batch size capped at 4 for stability

**Usage**:

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --mode quick
python run_benchmark.py --model local --model-name deepseek-coder:6.7b --mode half --seed 42
python run_benchmark.py --model local --model-name mistral:7b-instruct --mode quick \
    --max-workers 1 --raw-output-log temp_eval/local_quick.jsonl
```

> **Tip**: Use the exact model tag from `ollama list` (e.g. `llama3.1:8b`, not `llama3.1`).

---

### Hugging Face

**File**: `benchmark_lib/models/huggingface_model.py`  
**Env vars**: `HF_API_TOKEN`, `HF_USE_INFERENCE_API`, `HF_DEVICE`  
**Modes**:
- **Local** (`--hf-device cpu|cuda|mps`): runs the model locally using `transformers`
- **Inference API** (`--hf-use-inference-api`): calls the HF cloud API

**Special behavior**: Automatically falls back to chat completions for providers that don't support `text_generation`.

**Usage**:

```powershell
python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-7b \
    --hf-device cpu --mode quick
python run_benchmark.py --model huggingface \
    --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
    --hf-use-inference-api --mode quick
python run_benchmark.py --model huggingface \
    --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
    --hf-use-inference-api --mode quick \
    --raw-output-log temp_eval/hf_quick.jsonl
```

---

### Gemini

**File**: `benchmark_lib/models/gemini_model.py`  
**Env var**: `GEMINI_API_KEY`  
**Special behavior**: Runs a preflight model check before the benchmark starts; fails fast if the model or API key is invalid.

**Usage**:

```powershell
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode quick
python run_benchmark.py --model gemini --model-name gemini-1.5-flash --mode quick --max-workers 2
python run_benchmark.py --model gemini --model-name gemini-2.0-flash --mode full \
    --raw-output-log temp_eval/gemini_full.jsonl
```

---

### Together AI

**File**: `benchmark_lib/models/together_model.py`  
**Env var**: `TOGETHER_API_KEY`  
**Protocol**: OpenAI-compatible chat completions with retry/backoff  
**Default model**: `mistralai/Mistral-7B-Instruct-v0.3`

**Usage**:

```powershell
python run_benchmark.py --model together \
    --model-name mistralai/Mistral-7B-Instruct-v0.3 --mode quick
python run_benchmark.py --model together \
    --model-name meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo --mode quick --max-workers 2
python run_benchmark.py --model together \
    --model-name mistralai/Mistral-7B-Instruct-v0.3 --mode quick \
    --raw-output-log temp_eval/together_quick.jsonl
```

---

### Groq

**File**: `benchmark_lib/models/groq_model.py`  
**Env vars**: `GROQ_API_KEY`, `GROQ_RPM_LIMIT` (default 30), `GROQ_TPM_LIMIT` (default 6000)  
**Special behavior**: Local sliding-window rate throttling to stay within Groq's free tier limits.  
**Default model**: `llama-3.1-8b-instant`

**Usage**:

```powershell
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant \
    --mode quick --max-workers 1
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant \
    --mode quick --max-workers 1 --batch-size 2
python run_benchmark.py --model groq --model-name llama-3.1-8b-instant \
    --mode quick --max-workers 1 \
    --raw-output-log temp_eval/groq_quick.jsonl
```

---

## CLI Reference

**Entrypoint**: `run_benchmark.py`

### Main Flags

| Flag | Default | Description |
|---|---|---|
| `--dataset-path` | `data/raw_datasets` | Root dataset directory |
| `--model` | `echo` | Provider name (see list above) |
| `--model-name` | *(provider default)* | Exact model ID |
| `--mode` | `half` | `quick` / `half` / `full` |
| `--seed` | `42` | Single random seed |
| `--seeds` | *(none)* | Comma-separated seeds for multi-run averaging |
| `--domain` | *(all)* | Filter: `math`, `logic`, `knowledge`, `code` |
| `--batch-size` | `8` | Samples per batch |
| `--max-workers` | *(auto)* | Concurrent inference threads |
| `--retries` | `2` | Retry attempts per failed sample |
| `--timeout-seconds` | *(disabled)* | Accepted for compatibility; has no effect |
| `--raw-output-log` | `temp_eval/raw_outputs.jsonl` | Per-sample JSONL log path |
| `--env-file` | `.env` | Environment variable file |

### Analysis & Comparison Flags

| Flag | Description |
|---|---|
| `--dry-run` | Preview sample counts by domain + difficulty; no API calls |
| `--compare R1 R2` | Side-by-side table of two result JSONs + McNemar's test |

### Local / HF Flags

| Flag | Default | Description |
|---|---|---|
| `--local-base-url` | `http://localhost:11434/v1` | Ollama / local endpoint URL |
| `--local-api-key` | *(empty)* | Optional API key for local endpoint |
| `--hf-api-token` | *(env)* | Hugging Face token |
| `--hf-use-inference-api` | `false` | Use HF cloud API instead of local inference |
| `--hf-device` | `cpu` | Local inference device: `cpu`, `cuda`, `mps` |

---

## Timing Metrics

All benchmark runs include per-sample and per-domain timing data.

### Per-Sample (in JSONL log)

Each raw output record includes:
```json
"elapsed_seconds": 0.48
```

### Per-Domain (in Results JSON)

```json
"per_domain_timing": {
  "code": {
    "mean_seconds": 4.23,
    "min_seconds": 1.15,
    "max_seconds": 8.92,
    "total_seconds": 84.6,
    "sample_count": 20
  },
  "math": {
    "mean_seconds": 0.85,
    "min_seconds": 0.21,
    "max_seconds": 2.14,
    "total_seconds": 17.0,
    "sample_count": 20
  }
}
```

---

## Adding a New Model Provider

1. Create `benchmark_lib/models/my_provider.py`:

```python
from .base_model import BaseModel

class MyModel(BaseModel):
    model_name = "my-provider/model-id"

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
        # Call your API
        return response_text

    def get_last_cost(self) -> float:
        return 0.0  # optional
```

2. Register it in `run_benchmark.py` inside `build_model()`:

```python
if name == "myprovider":
    api_key = os.getenv("MY_API_KEY", "")
    model_id = model_name_override or "default-model-id"
    return MyModel(api_key=api_key, model=model_id)
```

3. Add `"myprovider"` to the `--model` choices list in `parser.add_argument`.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| API key not found | Check `.env` file and ensure the correct variable name |
| Local model unavailable | Ensure `ollama serve` is running; verify tag with `ollama list` |
| HF token error | Generate a new token at https://huggingface.co/settings/tokens |
| Cache returning stale results | Delete `.benchmark_cache/prompt_cache.json` |
| Groq rate limit errors | Reduce `--max-workers` to 1 and `--batch-size` to 2 |
| Gemini preflight fails | Check `GEMINI_API_KEY` and that the model name exists |
