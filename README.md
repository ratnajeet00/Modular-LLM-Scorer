# Modular LLM Scorer

Detailed project documentation is available in [docs/README.md](docs/README.md).

Deterministic, model-agnostic benchmark library for LLM evaluation across four domains:
- math
- logic
- knowledge
- code

The project is designed to run only on datasets already available in `data/raw_datasets` and uses deterministic rule-based scoring (no AI judge).

## Key behavior

### 1) Exactly 2 datasets per domain are used
During sampling, the runner:
- groups samples by domain and dataset
- ranks datasets by available normalized sample count (largest first)
- selects exactly 2 datasets per domain when available
- discards all other datasets for that run

Domains targeted:
- code
- logic
- knowledge
- math

If a domain has fewer than 2 usable datasets, all available datasets for that domain are used.

### 2) Selected datasets are distinct
The two datasets selected for a domain are always different dataset names.

### 3) Difficulty-aware sampling
Within each selected dataset, sampling is stratified by difficulty:
- easy: 30%
- medium (mid): 50%
- hard: 20%

If a bucket is short (for example, not enough hard examples), remaining slots are filled from the remaining samples in that selected dataset.

### 4) Mode sizes
- quick: 500 questions
- half: 1500 questions
- full: 6000 questions

The final sample is balanced first by domain, then by selected datasets within each domain, then by difficulty within each dataset.

## Installation

From project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Optional dataset reader stack (recommended for Hugging Face disk datasets):

```powershell
pip install -e .[datasets]
```

Optional OpenAI model support:

```powershell
pip install -e .[openai]
```

## Run benchmark

Quick smoke run with echo model:

```powershell
python run_benchmark.py \
  --dataset-path data/raw_datasets \
  --model echo \
  --mode quick \
  --batch-size 16 \
  --timeout-seconds 5 \
  --retries 0
```

Supported models:
- echo
- openai
- openrouter
- local
- huggingface
- gemini
- together
- groq

You can select the exact model to test at runtime with `--model-name`.

## Recent updates

- Prompting is now task-specific with stricter output constraints for code, math, and QA tasks.
- Output cleaning and validation are applied before evaluation.
- Invalid outputs are retried (empty/malformed/invalid code patterns).
- Generation temperature is set to `0.2` across adapters.
- Domain max token budget is capped at `200`.
- Raw output logging is available with `--raw-output-log` (JSONL).
- CLI now supports `--max-workers` to control concurrency.
- Groq includes built-in local throttling for RPM/TPM windows (defaults: 30 RPM, 6000 TPM).
- Cache entries are normalized/validated before reuse to avoid stale malformed outputs.

### Local model endpoint compatibility

The local adapter first tries OpenAI-compatible chat completions and then falls back to Ollama native chat when needed.

Supported local endpoint styles:
- `http://localhost:11434/v1` (OpenAI-compatible)
- `http://localhost:11434` (Ollama native)

If you see `model not found`, check installed models and use the exact tag:

```powershell
ollama list
```

### Hugging Face model support

Two modes available:

1. **Local inference** (requires `transformers` + `torch`)
   ```powershell
   python run_benchmark.py --model huggingface --model-name meta-llama/Llama-2-7b --mode quick
   ```

2. **HF Inference API** (cloud-based, requires HF token)
   ```powershell
   python run_benchmark.py --model huggingface --model-name deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --hf-use-inference-api --mode quick
   ```

## .env setup

Create a `.env` file (you can copy `.env.example`) and place your keys/default model names there.

```powershell
Copy-Item .env.example .env
```

The CLI loads `.env` automatically by default (override with `--env-file`).

Example:

```env
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
HF_API_TOKEN=hf_your_token_here
HF_USE_INFERENCE_API=false
HF_DEVICE=cpu
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_API_KEY=
GEMINI_API_KEY=...
TOGETHER_API_KEY=...
GROQ_API_KEY=...
GROQ_RPM_LIMIT=30
GROQ_TPM_LIMIT=6000
```

Model IDs are selected only in CLI via `--model-name`. For HuggingFace, you can also pass arguments via `--hf-api-token`, `--hf-use-inference-api`, `--hf-device`.

## Test specific model names

OpenAI with explicit model:

```powershell
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick
```

OpenRouter with explicit model:

```powershell
python run_benchmark.py --model openrouter --model-name anthropic/claude-3.5-sonnet --mode quick
```

Local model testing (OpenAI-compatible local endpoint):

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --local-base-url http://localhost:11434/v1 --mode quick
```

If your local server is Ollama native only:

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --local-base-url http://localhost:11434 --mode quick
```

## Environment variables

### OpenAI
- OPENAI_API_KEY
- OPENAI_MODEL (default: gpt-4o-mini)

### OpenRouter
- OPENROUTER_API_KEY
- OPENROUTER_MODEL (default: openai/gpt-4o-mini)

### Gemini
- GEMINI_API_KEY

### Together
- TOGETHER_API_KEY

### Groq
- GROQ_API_KEY
- GROQ_RPM_LIMIT (default 30)
- GROQ_TPM_LIMIT (default 6000)

## CLI additions

- `--max-workers`: controls concurrent model requests.
- `--raw-output-log`: writes per-sample JSONL (`question`, `prediction`, `error`).

## Model testing commands (3 per provider)

### OpenAI

```powershell
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick --seed 7 --batch-size 4 --max-workers 2
python run_benchmark.py --model openai --model-name gpt-4o-mini --mode quick --raw-output-log temp_eval/openai_quick.jsonl
```

### OpenRouter

```powershell
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick
python run_benchmark.py --model openrouter --model-name anthropic/claude-3.5-sonnet --mode quick --max-workers 2
python run_benchmark.py --model openrouter --model-name openai/gpt-4o-mini --mode quick --raw-output-log temp_eval/openrouter_quick.jsonl
```

### Local (Ollama/OpenAI-compatible)

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

## Validation logs

At run time, logs include:
- selected datasets by domain
- sampled difficulty mix (easy/medium/hard)

These logs let you verify that only 2 distinct datasets per domain are used and that easy/mid/hard stratification is active.

## Evaluator highlights

- Knowledge answers are evaluated with exact match first, then controlled leniency (aliases, short-span containment, token overlap), with strict numeric handling for numeric targets.
- Code answers execute provided tests when available.
- For code samples with expected output but no tests, generated code is executed and stdout is compared with expected output.
