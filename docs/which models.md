# Model Selection Justification

This document outlines the rationale for selecting specific open-source models for benchmarking the Modular LLM Scorer.

## Selection Criteria

Models were chosen to maximize:

1. **Architectural diversity** — different organizations and pre-training approaches (Meta, Mistral AI, Alibaba, DeepSeek)
2. **Capability diversity** — general-purpose, reasoning-focused, knowledge-rich, and code-specialized
3. **Reproducibility** — fully open-source weights, locally runnable via Ollama at no cost
4. **Accessibility** — compatible with consumer-grade hardware (8–16 GB VRAM or CPU inference)

---

## Recommended Models

### 🟢 `llama3.1:8b` — General Purpose Baseline

- **Provider**: Meta AI (Ollama tag: `llama3.1:8b`)
- **Strengths**: Strong instruction following across all domains; widely used reference model
- **Role**: Establishes a general-purpose 8B-class baseline for cross-domain comparison
- **Best for**: Math, knowledge; reasonable across all domains
- **Limitations**: Not specialized for code or complex reasoning

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b --mode half
```

---

### 🟡 `mistral:7b-instruct` — Reasoning Specialist

- **Provider**: Mistral AI (Ollama tag: `mistral:7b-instruct`)
- **Strengths**: Strong multi-step reasoning and instruction following; efficient at 7B parameters
- **Role**: Lightweight reasoning benchmark; particularly useful for math and logic evaluation
- **Best for**: Math, logic
- **Limitations**: Smaller knowledge base than larger models

```powershell
python run_benchmark.py --model local --model-name mistral:7b-instruct --mode half
```

---

### 🔵 `qwen2:7b-instruct` — Knowledge Specialist

- **Provider**: Alibaba (Ollama tag: `qwen2:7b-instruct`)
- **Strengths**: Strong performance in knowledge retrieval and comprehension; diverse multilingual training data
- **Role**: Evaluates state-of-the-art 7B knowledge models
- **Best for**: Knowledge domain
- **Limitations**: May underperform on complex code tasks

```powershell
python run_benchmark.py --model local --model-name qwen2:7b-instruct --mode half
```

---

### 🔴 `deepseek-coder:6.7b` — Code Specialist

- **Provider**: DeepSeek (Ollama tag: `deepseek-coder:6.7b`)
- **Strengths**: Specialized for code generation; trained heavily on programming data; strong HumanEval/MBPP performance
- **Role**: Tests whether domain specialization yields measurably better code scores vs. generalist models
- **Best for**: Code domain; useful for isolating specialization effects
- **Limitations**: Weaker on knowledge and math outside programming contexts

```powershell
python run_benchmark.py --model local --model-name deepseek-coder:6.7b --mode half
```

---

## Comparison Strategy

Running all four models with the same seed allows direct comparison:

```powershell
# Run all four
python run_benchmark.py --model local --model-name llama3.1:8b --mode half --seed 42
python run_benchmark.py --model local --model-name mistral:7b-instruct --mode half --seed 42
python run_benchmark.py --model local --model-name qwen2:7b-instruct --mode half --seed 42
python run_benchmark.py --model local --model-name deepseek-coder:6.7b --mode half --seed 42

# Compare any two statistically
python run_benchmark.py --compare "bech mark\llama3.1_8b_*.json" "bech mark\deepseek-coder_6.7b_*.json"
```

Using the same `--seed` ensures identical sample selection for fair paired comparison and valid McNemar's test results.

---

## API Models for Publication-Quality Results

For publication, consider running higher-capacity API-based models as upper-bound comparisons:

| Model | Provider | `--model` | `--model-name` |
|---|---|---|---|
| GPT-4o | OpenAI | `openai` | `gpt-4o` |
| GPT-4o-mini | OpenAI | `openai` | `gpt-4o-mini` |
| Claude 3.5 Sonnet | OpenRouter | `openrouter` | `anthropic/claude-3.5-sonnet` |
| Gemini 2.0 Flash | Google | `gemini` | `gemini-2.0-flash` |
| Llama 3.1 70B | Groq | `groq` | `llama-3.1-70b-versatile` |