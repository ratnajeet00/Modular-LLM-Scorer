# Model Selection Justification

This document outlines the rationale for selecting specific local models for benchmarking the Modular LLM Scorer.

## Selected Models

### 🟢 llama3.1:8b (General Purpose)
- Serves as a baseline open-source model.
- Represents widely used 8B-class general-purpose LLMs.
- Helps measure minimum expected performance across all domains.

### 🟡 mistral:7b-instruct (Reasoning)
- Known for strong reasoning and instruction-following capabilities.
- Provides a lightweight but capable reasoning benchmark.
- Particularly useful for evaluating **math** and **logic** tasks.

### 🔵 qwen2:7b-instruct (Knowledge)
- Strong performance in knowledge retrieval and comprehension tasks.
- Trained on diverse multilingual and factual data.
- Represents modern high-performing 7B models.

### 🔴 deepseek-coder:6.7b (Code Specialist)
- **Specialized for code generation tasks.**
- Trained heavily on programming data.
- Provides critical insight into domain-specific model performance vs generalists.

## Overall Strategy

These models were selected to ensure:

1. **Architectural diversity** (Meta, Mistral, Alibaba, DeepSeek)
2. **Capability diversity** (general, reasoning, knowledge, code)
3. **Reproducibility**: Fair comparison using fully open-source, locally runnable models.
4. **Accessibility**: Cost-free evaluation setup compatible with consumer hardware.