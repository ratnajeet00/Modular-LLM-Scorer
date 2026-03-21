# Modular LLM Scorer

Detailed project documentation is available in [docs/README.md](docs/README.md).

Deterministic, model-agnostic benchmark library for LLM evaluation across four domains:
- math
- logic
- knowledge
- code

The project is designed to run only on datasets already available in `data/raw_datasets` and uses strict rule-based scoring (no AI judge).

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

You can select the exact model to test at runtime with `--model-name`.

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
LOCAL_BASE_URL=http://localhost:11434/v1
LOCAL_API_KEY=
```

Model IDs are selected only in CLI via `--model-name`.

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
python run_benchmark.py --model local --model-name llama3.1 --local-base-url http://localhost:11434/v1 --mode quick
```

## Environment variables

### OpenAI
- OPENAI_API_KEY
- OPENAI_MODEL (default: gpt-4o-mini)

### OpenRouter
- OPENROUTER_API_KEY
- OPENROUTER_MODEL (default: openai/gpt-4o-mini)

## Validation logs

At run time, logs include:
- selected datasets by domain
- sampled difficulty mix (easy/medium/hard)

These logs let you verify that only 2 distinct datasets per domain are used and that easy/mid/hard stratification is active.
