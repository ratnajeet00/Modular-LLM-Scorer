# Limitations and Notes

## Known limitations

1. `dm-code_contests` raw riegeli shards are skipped unless converted.
2. Some folded datasets don't yield normalized rows without schema mappings.
3. Difficulty balancing is ratio-targeted, not exact.
4. Code evaluation is subprocess-isolated but not fully sandboxed.
5. OpenAI/costs are placeholders in some API integrations.
6. Knowledge evaluation allows lenient alias/overlap matching, not strict exact-string.
7. Local models may vary significantly in performance; run with `--batch-size 4` or lower if OOM/timeouts occur.
8. Groq adapter includes throttling but provider quotas still apply.
9. Prompt cache can suppress API traffic; clear `.benchmark_cache` if testing live behavior.

## Validation behavior

Runtime logging includes:

- selected datasets by domain
- easy/medium/hard sampled mix

## Data source policy

The project is built to use local datasets from `data/raw_datasets` and does not require dataset download at benchmark time.

## Compatibility note

There is a path compatibility fallback from `rawdatasets` to `raw_datasets` in the benchmark initializer.
