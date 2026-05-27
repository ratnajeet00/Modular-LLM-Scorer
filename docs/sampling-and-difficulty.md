# Sampling and Difficulty

## Overview

Stratified sampling ensures each benchmark run evaluates a representative mix of domains, datasets, and difficulty levels. The sampler is deterministic given the same `--seed`.

**Implementation**: `benchmark_lib/engine/sampler.py`

---

## Mode Sizes

| Mode | Target Samples |
|---|---|
| `quick` | 500 |
| `half` | 1500 |
| `full` | 6000 |

Actual count = `min(mode_target, total_available_samples_after_filtering)`.

When running with `--domain` (single-domain filter), effective sample count is proportionally lower.

---

## Sampling Algorithm

### Step 1 — Dataset Selection (Per Domain)

For each domain:

1. Count normalized samples per dataset within the domain
2. Rank datasets by descending sample count (tie-breaker: alphabetical dataset name)
3. **Select the top 2 datasets** — all other datasets are excluded from the run

If fewer than 2 datasets exist in a domain, all available datasets are used.

**Why top-2?** Ensures domain coverage is consistent and reproducible across providers; prevents one very large dataset from dominating.

Selected datasets are recorded in results JSON under `selected_datasets_by_domain`.

### Step 2 — Budget Allocation (Across Domains)

The total sample budget (mode size) is distributed across active domains proportionally to domain weights:

| Domain | Weight |
|---|---|
| Math | 0.25 |
| Logic | 0.25 |
| Knowledge | 0.35 |
| Code | 0.15 |

Each domain's budget is then split evenly across its two selected datasets.

### Step 3 — Stratified Sampling (Within Each Dataset)

Within each selected dataset, samples are drawn according to difficulty ratios:

| Difficulty | Target ratio |
|---|---|
| Easy | 30% |
| Medium | 50% |
| Hard | 20% |

If one difficulty bucket is under-populated (fewer samples than the target), remaining slots are filled from other available samples in the same dataset (maintaining domain identity).

---

## Difficulty Tiers

Each sample is tagged `easy`, `medium`, or `hard` by `benchmark_lib/dataset/difficulty.py` using domain-specific heuristics applied during normalization.

These are approximate — the actual difficulty distribution seen in logs depends on what each dataset contains. The sampler does a best-effort allocation toward the 30/50/20 target.

---

## Verification with `--dry-run`

Preview exactly which samples would be selected without making any API calls:

```powershell
python run_benchmark.py --dry-run --mode quick --seed 42
```

Example output:
```
================================================================================
Dry Run: Sample Selection
================================================================================
Mode: quick
Seed: 42
Total samples selected: 500

Samples by Domain and Difficulty:
Domain            Easy   Medium     Hard    Total
--------------------------------------------------
code                25        0        0       25
knowledge           17        8        0       25
logic               17        6        2       25
math                 8       12        5       25

Datasets used: 8
  gsm8k_main: 13 samples
  gsm8k_socratic: 12 samples
  ...

✓ Dry run complete. No API calls made.
```

---

## Multi-Seed Averaging

Run the same benchmark with multiple seeds to get averaged results with standard deviation:

```powershell
python run_benchmark.py --model local --model-name llama3.1:8b \
    --mode half --seeds 42,43,44
```

The aggregated result JSON includes:
```json
{
  "seeds": [42, 43, 44],
  "run_count": 3,
  "aggregate": {
    "accuracy": {"mean": 0.423, "std": 0.018},
    "final_score": {"mean": 0.352, "std": 0.021},
    "per_domain": {
      "math": {"mean": 0.381, "std": 0.014},
      "code": {"mean": 0.271, "std": 0.031}
    }
  },
  "runs": [...]
}
```

---

## Practical Notes

- Selected dataset names per domain are logged at the start of each run and stored in `selected_datasets_by_domain` in the results JSON
- Easy/medium/hard counts per domain are also logged when `--dry-run` is used
- For single-domain runs (`--domain code`), only that domain's budget and datasets are used; mode sizes remain the same targets but only one domain is sampled
