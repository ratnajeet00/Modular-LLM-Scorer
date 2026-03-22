# Sampling and Difficulty

Sampling implementation: `benchmark_lib/engine/sampler.py`

## Mode sizes

- quick: 100
- half: 1500
- full: 6000

Actual target is `min(mode_size, total_available_samples_after_filtering)`.

When running with a restricted dataset root (for focused domain checks), effective sample count can be lower than global defaults.

## Domain set

Target domains:

- code
- logic
- knowledge
- math

## Exactly 2 datasets per domain

The sampler:

1. counts normalized samples per dataset inside each domain
2. ranks by descending sample count (tie-breaker: dataset name)
3. picks top 2 datasets per domain
4. discards all other datasets for the run

If fewer than 2 datasets exist in a domain, it uses what is available.

## Distinct dataset guarantee

Because selection is by dataset name and capped at top two unique names, selected pair per domain is always distinct.

## Allocation hierarchy

Sampling balance is applied in this order:

1. distribute total requested questions across available domains
2. split each domain quota across the two selected datasets
3. within each selected dataset, stratify by difficulty ratios

## Difficulty ratios

Target ratios inside each selected dataset:

- easy: 30%
- medium: 50%
- hard: 20%

If one bucket is short, remaining slots are filled from other remaining samples in that selected dataset.

## Practical behavior

Observed in logs:

- selected datasets by domain are printed
- final easy/medium/hard counts are printed
