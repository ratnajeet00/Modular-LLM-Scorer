# LLM Benchmark Enhancement Guide

## Quick Start

This document describes all the enhancements made to prepare the Modular LLM Tester for publication.

### Installation

```bash
# Install pip dependencies (scipy is new)
pip install -r requirements.txt

# Or install via pyproject.toml
pip install -e .
```

## 📊 New Features & Tools

### 1. Enhanced Results JSON Output

Benchmark results now include:

```bash
python run_benchmark.py --model echo --mode quick
# Results saved to: bech mark/echo_YYYYMMDD_HHMMSS.json
```

**New fields in results JSON:**
- `confidence_intervals_95`: 95% confidence intervals (Wilson score method)
- `difficulty_breakdown`: Performance per difficulty tier (easy/medium/hard)
- `summary_table`: Per-domain breakdown with weighted scores
- `per_domain_errors`: Error categorization by type
- `failure_breakdown`: Detailed failure type breakdown
- `token_usage`: Input/output token counts for cost analysis
- `git_commit_hash`: Git commit for reproducibility
- `selected_datasets_by_domain`: Which datasets were used per domain

### 2. CLI Tools

#### A. Compare Two Models
```bash
python run_benchmark.py --compare result1.json result2.json
```
Shows side-by-side accuracy, scores, and failure rates for easy comparison.

#### B. Dry-Run (Preview without API calls)
```bash
python run_benchmark.py --dry-run --mode half --seed 42
```
Preview exactly which samples will be evaluated without incurring API costs.

#### C. Validate Evaluator
```bash
python validate_pipeline.py
```
Tests evaluator correctness with 10 known Q&A pairs across all domains.
Should pass before running expensive benchmarks to verify the evaluation logic.

### 3. Analysis Tools

#### A. Error Analysis
```bash
python analyze_errors.py temp_eval/raw_outputs.jsonl [--save]
```
Categorizes errors from JSONL into:
- execution_error (code test failures)
- invalid_format (output format violations)
- timeout (API timeouts)
- empty_response (no output)
- model_refusal (model refused to answer)
- type_error (Python errors)
- other_error (misc failures)

Provides per-domain success rates and failure patterns.

#### B. Extract Sample List
```bash
python save_sample_list.py temp_eval/raw_outputs.jsonl samples_evaluated.json
```
Extracts metadata about which exact samples were evaluated.
Enables independent reproduction of the exact evaluation set.

#### C. Generate Markdown Report
```bash
python generate_report.py bech\ mark/model_*.json output.md
```
Converts JSON results to human-readable markdown with:
- Executive summary
- Per-domain performance tables
- Confidence intervals
- Difficulty breakdown
- Error analysis
- Timing statistics
- Reproducibility info

## 🔍 Enhanced Raw JSONL Format

Each sample now includes:
```json
{
  "sample_id": "gsm8k_main-123",
  "dataset": "gsm8k_main",
  "domain": "math",
  "difficulty": "medium",
  "question": "What is 2 + 2?",
  "prompt": "You are a helpful AI assistant...\n\nQuestion:\nWhat is 2 + 2?",
  "prediction": "4",
  "expected": "4",
  "correct": true,
  "error": null,
  "elapsed_seconds": 0.5,
  "input_tokens": 45,
  "output_tokens": 10
}
```

## 📈 Statistical Improvements

### Confidence Intervals
```python
# Results now include:
{
  "confidence_intervals_95": {
    "overall_accuracy": {
      "lower": 0.18,
      "upper": 0.22,
      "accuracy": 0.20
    },
    "per_domain": {
      "math": {"lower": 0.15, "upper": 0.25},
      "code": {"lower": 0.35, "upper": 0.45},
      ...
    }
  }
}
```

### Token Usage Tracking
```python
{
  "token_usage": {
    "total_input_tokens": 5000,
    "total_output_tokens": 1200,
    "total_tokens": 6200,
    "by_domain": {
      "code": {
        "input_tokens": 2000,
        "output_tokens": 800,
        "total_tokens": 2800
      },
      ...
    }
  }
}
```

### Failure Breakdown
```python
{
  "failure_breakdown": {
    "empty_predictions": 10,
    "execution_errors": 5,
    "format_errors": 8,
    "other_errors": 2,
    "total_failures": 25
  }
}
```

## 🎯 Usage Examples

### Full Publication Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Validate evaluator works correctly
python validate_pipeline.py

# 3. Preview sample selection for cost estimation
python run_benchmark.py --dry-run --mode half --seed 42

# 4. Run benchmark
python run_benchmark.py --model local --model-name "llama3.1:8b" --mode half --seed 42

# 5. Analyze errors
python analyze_errors.py temp_eval/raw_outputs.jsonl --save

# 6. Generate markdown report
python generate_report.py bech\ mark/llama3.1_*.json llama_report.md

# 7. Compare with other model (optional)
python run_benchmark.py --compare bech\ mark/model_a_*.json bech\ mark/model_b_*.json

# 8. Extract exact sample list for reproducibility
python save_sample_list.py temp_eval/raw_outputs.jsonl samples_used.json
```

### Quick Model Comparison

```bash
# Instead of running each benchmark separately:
# 1. Compare existing results directly
python run_benchmark.py --compare benchmark_a.json benchmark_b.json

# Output shows:
# - Overall accuracy comparison
# - Final score comparison  
# - Failure rate comparison
# - Cost comparison
# - Per-domain breakdown with diffs
```

## 📋 Reproducibility Checklist

When publishing results, include:

✅ **Git commit hash** - Automatically captured in results
✅ **Environment lock file** - `requirements.txt` for exact package versions
✅ **Sample list** - `save_sample_list.py` output showing exact questions
✅ **Raw outputs JSONL** - With full prompts and token counts
✅ **Markdown report** - Human-readable summary
✅ **Confidence intervals** - Statistical uncertainty quantification
✅ **Error analysis** - Detailed failure breakdown
✅ **Model details** - Saved in JSON results

## 🔧 Configuration

### Dependencies

```toml
# From pyproject.toml (now includes scipy)
dependencies = [
  "groq>=1.1.1",
  "google-genai>=1.0.0",
  "requests>=2.31.0",
  "scipy>=1.8.0",  # NEW: For confidence intervals
]
```

### Environment Variables

No new env vars required. Existing ones still work:
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- etc.

## 📊 Results File Structure

```
bech mark/
├── model1_20260322_212321.json      # Main results
├── model2_20260322_183607.json
├── model1_report.md                 # Generated markdown
└── model1_samples.json              # Sample list
```

Corresponding JSONL:
```
temp_eval/
├── raw_outputs.jsonl               # Per-sample logs with prompts & tokens
├── raw_outputs_error_report.json   # Generated error analysis
└── raw_outputs_sample_list.json    # Generated sample metadata
```

## 🐛 Troubleshooting

### "scipy not found"
```bash
pip install scipy>=1.8.0
```

### "JSONL file not found"
Make sure your raw output log path is correct. Default is `temp_eval/raw_outputs.jsonl`

### "Git commit hash shows as None"
The script only captures git info if:
1. You're in a git repository
2. Git is installed and in PATH
This is non-critical - other features work fine.

## 📚 Documentation

- For detailed implementation info: See `IMPLEMENTATION_SUMMARY.md`
- For architecture: See `docs/architecture.md`
- For data pipeline: See `docs/data-pipeline.md`

## 🎓 Key Improvements for Publication

1. **Scientific Rigor**
   - 95% confidence intervals on all metrics
   - Detailed error categorization
   - Token usage tracking

2. **Reproducibility**
   - Git commit tracking
   - Requirements lock file
   - Sample list extraction
   - Full prompt logging

3. **Transparency**
   - Error breakdown per domain
   - Failure type categorization
   - Dataset selection tracking

4. **Usability**
   - Model comparison tool
   - Error analysis dashboard
   - Markdown report generator
   - Evaluator validation

5. **Cost Analysis**
   - Token counting per sample
   - Per-domain token usage
   - Cost tracking

## 🔄 Update Cycle

When running multiple benchmarks:

```bash
# Session 1: Model A
python run_benchmark.py --model local --model-name "model_a" --seed 42
# --> Results in bech mark/model_a_20260322_123456.json

# Session 2: Model B  
python run_benchmark.py --model local --model-name "model_b" --seed 42
# --> Results in bech mark/model_b_20260322_234567.json

# Compare (works with both old & new results)
python run_benchmark.py --compare bech\ mark/model_a_*.json bech\ mark/model_b_*.json

# Generate reports
python generate_report.py bech\ mark/model_a_*.json report_a.md
python generate_report.py bech\ mark/model_b_*.json report_b.md
```

## 📞 Support

For issues or questions:
1. Check `IMPLEMENTATION_SUMMARY.md` for detailed changes
2. Run `python validate_pipeline.py` to verify setup
3. Try `--dry-run` to debug sample selection
4. Use `analyze_errors.py` to understand failures
