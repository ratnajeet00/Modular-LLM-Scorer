# Limitations and Notes

## Known limitations

1. `dm-code_contests` raw riegeli shards are detected but skipped unless converted to parseable format.
2. Some datasets may exist in folder form but not yield normalized rows unless schema mappings are present.
3. Difficulty balancing is ratio-targeted, not exact, and may drift if one bucket is sparse.
4. Code evaluation executes Python code/tests in a subprocess with timeout but no dedicated sandbox beyond temp-dir process isolation.
5. OpenAI adapter currently reports zero cost (cost hook placeholder), while OpenRouter adapter uses response usage when present.
6. Knowledge evaluator allows bounded leniency (aliases and overlap checks), so it is not strict exact-string-only matching.
7. Local adapter supports endpoint fallback, but valid local model tags are still required.

## Validation behavior

Runtime logging includes:

- selected datasets by domain
- easy/medium/hard sampled mix

## Data source policy

The project is built to use local datasets from `data/raw_datasets` and does not require dataset download at benchmark time.

## Compatibility note

There is a path compatibility fallback from `rawdatasets` to `raw_datasets` in the benchmark initializer.
