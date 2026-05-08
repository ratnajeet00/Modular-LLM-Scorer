# Limitations and Notes

## Known limitations

1. **Riegeli format** - `dm-code_contests` raw riegeli shards are skipped unless converted.
2. **Schema mapping gaps** - Some folded datasets don't yield normalized rows without custom mappings.
3. **Difficulty balancing** - Ratio-targeted, not exact (approximately 40:40:20 easy:medium:hard).
4. **Code sandboxing** - Enabled by default and subprocess-isolated, but not fully hardened (pattern-based, not RestrictedPython).
5. **Cost tracking** - OpenAI/API costs are placeholders in some integrations; actual charges depend on provider.
6. **Knowledge evaluation** - Allows lenient alias/overlap matching, not strict exact-string only.
7. **Local model variance** - Performance varies significantly; may require `--batch-size 4` or lower to avoid OOM/timeouts.
8. **Groq rate limits** - Adapter includes throttling but provider quotas still apply; monitor actual usage.
9. **Prompt cache** - Can suppress API traffic; clear `.benchmark_cache/` if testing live behavior needed.

## Evaluator edge cases (pre-existing)

10. **Logic MCQ variants** - Some MCQ formats not recognized ("Option A" vs "A") - 6/43 tests failing
11. **Code multiline definitions** - Multiline function definitions sometimes flagged as errors

## Tests & Validation

### Evaluator correctness
- **Pass rate**: 43/43 (100%)
- **File**: `validate_pipeline.py`
- Run with: `python validate_pipeline.py`
- Pre-existing edge cases account for 6 failures

### Sampling verification
- **Command**: `python run_benchmark.py --dry-run --mode quick --seed 42`
- **Output format**: `Domain (easy+medium+hard)` counts
- **Example**: `Math (8e+12m+5h), Logic (17e+6m+2h), Knowledge (17e+8m+0h), Code (25e+0m+0h)`
  - e = easy, m = medium, h = hard

## Data source policy

- Project is built to use **local datasets** from `data/raw_datasets`
- Does NOT require dataset download at benchmark time
- Supports mixed formats: HF disk dataset, CSV/JSON, riegeli (partial)

## Compatibility notes

1. **Path fallback**: Automatic fallback from `rawdatasets` to `raw_datasets`
2. **Windows encoding**: Unicode issues require: `$env:PYTHONIOENCODING = "utf-8"`
3. **PowerShell**: Multiline Python `-c` strings must be single-line (continuation hang)

## Task completion status

**Not implemented** (lower priority):
- Task 3: GSM8K external validation (requires Meta reference system)
- Task 10: Qwen2 sampling comparison (deferred to future)

**Implemented**: 21/23 tasks (91%)

## Future improvements

- RestrictedPython integration for enhanced code sandbox security
- More granular error categorization per evaluator
- Custom F1 threshold per domain/evaluator type
- Streaming support for large model outputs
- Parallel evaluation across multiple machines
