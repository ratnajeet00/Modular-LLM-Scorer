# Before & After: Benchmark Enhancements

## Results JSON Structure

### BEFORE (Minimal)
```json
{
  "model": "local:llama3.1:8b",
  "mode": "quick",
  "accuracy": 0.19,
  "per_dataset": {
    "gsm8k_main": 0.153846,
    "mbpp_full": 0.307692,
    ...
  },
  "per_domain": {
    "code": 0.4,
    "knowledge": 0.08,
    "logic": 0.2,
    "math": 0.08
  },
  "per_domain_timing": {
    "code": {
      "mean_seconds": 33.601,
      "sample_count": 25
    },
    ...
  },
  "final_score": 0.158,
  "total_questions": 100,
  "correct_count": 19,
  "error_rate": 0.81,
  "failure_rate": 0.15,
  "cost": 0.0
}
```

### AFTER (Publication-Ready)
```json
{
  "model": "local:llama3.1:8b",
  "mode": "quick",
  "accuracy": 0.19,
  
  // ✅ NEW: Statistical confidence intervals
  "confidence_intervals_95": {
    "overall_accuracy": {
      "lower": 0.116,
      "upper": 0.270,
      "accuracy": 0.19
    },
    "per_domain": {
      "code": {"lower": 0.220, "upper": 0.600},
      "knowledge": {"lower": 0.013, "upper": 0.252},
      "logic": {"lower": 0.060, "upper": 0.397},
      "math": {"lower": 0.013, "upper": 0.252}
    }
  },
  
  // ✅ NEW: Performance breakdown by difficulty
  "difficulty_breakdown": {
    "easy": {
      "count": 30,
      "correct": 6,
      "accuracy": 0.2,
      "confidence_interval_95": {
        "lower": 0.082,
        "upper": 0.383
      }
    },
    "medium": {
      "count": 50,
      "correct": 10,
      "accuracy": 0.2,
      "confidence_interval_95": {
        "lower": 0.097,
        "upper": 0.330
      }
    },
    "hard": {
      "count": 20,
      "correct": 3,
      "accuracy": 0.15,
      "confidence_interval_95": {
        "lower": 0.022,
        "upper": 0.425
      }
    }
  },
  
  // ✅ NEW: Summary table for easy visualization
  "summary_table": {
    "overall_accuracy": 0.19,
    "overall_samples": 100,
    "overall_correct": 19,
    "domain_breakdown": [
      {
        "domain": "code",
        "accuracy": 0.4,
        "sample_count": 25,
        "weight": 0.15,
        "weighted_score": 0.06
      },
      {
        "domain": "math",
        "accuracy": 0.08,
        "sample_count": 25,
        "weight": 0.25,
        "weighted_score": 0.02
      },
      {
        "domain": "logic",
        "accuracy": 0.2,
        "sample_count": 25,
        "weight": 0.25,
        "weighted_score": 0.05
      },
      {
        "domain": "knowledge",
        "accuracy": 0.08,
        "sample_count": 25,
        "weight": 0.35,
        "weighted_score": 0.028
      }
    ]
  },
  
  // ✅ NEW: Token usage for cost analysis
  "token_usage": {
    "total_input_tokens": 4500,
    "total_output_tokens": 1200,
    "total_tokens": 5700,
    "by_domain": {
      "code": {"input_tokens": 2000, "output_tokens": 500, "total_tokens": 2500},
      "math": {"input_tokens": 1000, "output_tokens": 300, "total_tokens": 1300},
      "logic": {"input_tokens": 900, "output_tokens": 200, "total_tokens": 1100},
      "knowledge": {"input_tokens": 600, "output_tokens": 200, "total_tokens": 800}
    }
  },
  
  // ✅ NEW: Error categorization
  "per_domain_errors": {
    "code": {
      "invalid-output-format": 5,
      "execution-error:test-failed": 3,
      "empty-output": 2
    },
    "math": {
      "invalid-output-format": 2
    },
    "logic": {
      "invalid-output-format": 8
    },
    "knowledge": {
      "empty-output": 1
    }
  },
  
  // ✅ NEW: Failure breakdown
  "failure_breakdown": {
    "empty_predictions": 5,
    "execution_errors": 3,
    "format_errors": 7,
    "other_errors": 0,
    "total_failures": 15
  },
  
  // ✅ NEW: Git commit for reproducibility
  "git_commit_hash": "a1b2c3d4e5f*",
  
  // ✅ NEW: Datasets used per domain
  "selected_datasets_by_domain": {
    "code": ["mbpp_full", "mbpp_sanitized"],
    "knowledge": ["natural_questions", "squad"],
    "logic": ["proofwriter", "reclor"],
    "math": ["gsm8k_main", "gsm8k_socratic"]
  },
  
  // EXISTING FIELDS (unchanged)
  "per_dataset": {
    "gsm8k_main": 0.153846,
    "gsm8k_socratic": 0.0,
    "mbpp_full": 0.307692,
    "mbpp_sanitized": 0.5,
    "natural_questions": 0.076923,
    "proofwriter": 0.153846,
    "reclor": 0.25,
    "squad": 0.083333
  },
  "per_domain": {
    "code": 0.4,
    "knowledge": 0.08,
    "logic": 0.2,
    "math": 0.08
  },
  "per_domain_timing": {
    "code": {
      "mean_seconds": 33.601,
      "min_seconds": 5.088,
      "max_seconds": 107.536,
      "total_seconds": 840.036,
      "sample_count": 25
    },
    ...
  },
  "final_score": 0.158,
  "total_questions": 100,
  "correct_count": 19,
  "wrong_count": 81,
  "error_rate": 0.81,
  "failure_rate": 0.15,
  "non_empty_predictions": 85,
  "empty_predictions": 15,
  "call_error_count": 15,
  "call_error_examples": ["empty-output", "execution-error"],
  "error_count": 15,
  "error_examples": ["execution-error", "invalid-output-format"],
  "cost": 0.0
}
```

## Raw JSONL Format

### BEFORE (Minimal)
```jsonl
{"sample_id": "gsm8k_main-1", "dataset": "gsm8k_main", "domain": "math", "question": "...", "prediction": "42", "error": null, "elapsed_seconds": 0.5}
{"sample_id": "mbpp_full-1", "dataset": "mbpp_full", "domain": "code", "question": "...", "prediction": "def foo(): ...", "error": null, "elapsed_seconds": 2.3}
```

### AFTER (Complete)
```jsonl
{
  "sample_id": "gsm8k_main-1",
  "dataset": "gsm8k_main",
  "domain": "math",
  "difficulty": "medium",
  "question": "If a cat costs $50, how much do 3 cats cost?",
  "prompt": "You are a helpful AI assistant...\n\n...\n\nQuestion:\nIf a cat costs $50, how much do 3 cats cost?\n\n==MANDATORY==\nAnswer with ONLY a number...",
  "prediction": "150",
  "expected": "150",
  "correct": true,
  "error": null,
  "elapsed_seconds": 0.523,
  "input_tokens": 87,
  "output_tokens": 5
}
{
  "sample_id": "mbpp_full-1",
  "dataset": "mbpp_full",
  "domain": "code",
  "difficulty": "hard",
  "question": "Write a function that sorts a list",
  "prompt": "You are a helpful AI assistant...\n\n...\n\nQuestion:\nWrite a function that sorts a list",
  "prediction": "def sort_list(lst):\n    return sorted(lst)",
  "expected": "def sort_list(lst):\n    return sorted(lst)",
  "correct": true,
  "error": null,
  "elapsed_seconds": 1.234,
  "input_tokens": 156,
  "output_tokens": 23
}
```

## CLI Interface

### BEFORE (Run only)
```bash
# Only option: run benchmarks
python run_benchmark.py --model echo --mode quick
# Output: Saved to bech mark/model_TIMESTAMP.json
```

### AFTER (Enhanced tools)
```bash
# Run benchmarks (same as before, but with enhancements)
python run_benchmark.py --model echo --mode quick

# NEW: Preview sample selection without API calls
python run_benchmark.py --dry-run --mode quick

# NEW: Compare two model results
python run_benchmark.py --compare result1.json result2.json

# NEW: Validate evaluator correctness
python validate_pipeline.py

# NEW: Analyze errors from JSONL
python analyze_errors.py temp_eval/raw_outputs.jsonl --save

# NEW: Extract exact sample list
python save_sample_list.py temp_eval/raw_outputs.jsonl samples.json

# NEW: Generate markdown report
python generate_report.py bech\ mark/model_*.json report.md
```

## Key Improvements Summary

| Feature | Before | After |
|---------|--------|-------|
| Statistical rigor | ❌ None | ✅ 95% CI (Wilson score) |
| Error categorization | ❌ Mixed | ✅ Categorized by type |
| Reproducibility | ❌ Manual | ✅ Git hash, requirements.txt |
| Token tracking | ❌ None | ✅ Input/output per sample |
| Failure breakdown | ❌ Single count | ✅ 4-category breakdown |
| Model comparison | ❌ Manual diff | ✅ Automated CLI tool |
| Cost analysis | ❌ Not possible | ✅ Token usage tracking |
| Difficulty tracking | ❌ Not logged | ✅ Per-tier statistics |
| Dataset tracking | ❌ Console only | ✅ Saved in results |
| Markdown reports | ❌ None | ✅ Auto-generated |
| Validation tools | ❌ None | ✅ Evaluator tests |
| Dry-run preview | ❌ None | ✅ Zero-cost preview |

## Data Size Impact

```
BEFORE:
- results.json: ~2 KB (basic metrics)
- raw_outputs.jsonl: ~50 KB (100 samples)

AFTER:
- results.json: ~8 KB (enhanced metrics, ~4x larger but still small)
- raw_outputs.jsonl: ~200 KB (prompts + tokens + full data, ~4x larger)
- sample_list.json: ~20 KB (if generated)
- report.md: ~5 KB (if generated)

Total space increase: ~180 KB for 100 samples
==> ~1.8 KB per sample (mostly prompts and full data)
==> Negligible for datasets up to 10,000 samples (~18 MB)
```

## Backward Compatibility

✅ **Fully backward compatible:**
- All new fields are additions only
- Existing results still load fine
- Old results can be compared with --compare flag
- No breaking changes to existing functionality
- All existing scripts continue to work

## Next Steps

1. Install updated packages: `pip install -r requirements.txt`
2. Validate setup: `python validate_pipeline.py`
3. Try new features: `python run_benchmark.py --dry-run`
4. Run benchmarks: `python run_benchmark.py --model [your_model]`
5. Generate reports: `python generate_report.py bech\ mark/model_*.json`
