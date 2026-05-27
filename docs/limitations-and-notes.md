# Limitations and Notes

## Known Limitations

### Data & Formats

1. **Riegeli format** (`dm-code_contests`) — Raw Riegeli shards are skipped unless pre-converted to HF disk / JSONL format. A warning is emitted.
2. **Schema mapping gaps** — Some folded or custom dataset structures may not yield normalized rows without adding an explicit extractor in `normalizer.py`.
3. **Difficulty balancing** — Ratio targets (30% easy / 50% medium / 20% hard) are best-effort. If a dataset is skewed toward one difficulty, the actual distribution will differ.

### Evaluation

4. **Logic MCQ variants** — Some MCQ prediction formats not recognized (e.g. "Option A" vs "A"). Accounts for ~6 edge cases in the evaluator test suite (pre-existing, not from enhancements).
5. **Code multiline definitions** — Multiline function definitions sometimes trigger false-positive pattern violations in sandbox mode. Disable `SANDBOX_STRICT_MODE` if this occurs.
6. **Knowledge evaluation leniency** — Alias/overlap matching is intentionally lenient for recall. For strict exact-string evaluation, raise `F1_THRESHOLD_KNOWLEDGE` to 0.9+ in `evaluator.py`.
7. **Code sandbox** — Pattern-based, not bytecode-level (unlike RestrictedPython). Subprocess isolation prevents parent process harm but does not prevent all resource exhaustion (CPU/disk).

### Infrastructure

8. **Cost tracking** — API costs are estimated or placeholder in some adapters. Actual charges depend on the provider's billing.
9. **Local model variance** — Output quality and speed vary significantly by model and hardware. Use `--batch-size 1` or `--max-workers 1` to reduce OOM risk.
10. **Groq rate limits** — Local RPM/TPM throttling is enforced, but provider quotas still apply. Monitor actual usage via the Groq dashboard.
11. **Prompt cache** — The SHA-256 cache can suppress live API calls. Clear `.benchmark_cache/prompt_cache.json` to force fresh inference.

---

## Deferred Tasks (Non-Critical)

| Task | Reason | Workaround |
|---|---|---|
| **Task 3**: GSM8K external validation | Requires Meta reference scores not publicly available in standard benchmark repos | Compare against published leaderboard numbers manually |
| **Task 10**: Qwen2 sampling comparison | General stratified sampling mechanism already proven via `--dry-run` | Run `--dry-run --mode quick` and inspect domain/difficulty counts |

---

## Tests & Validation

### Evaluator Correctness

```powershell
python validate_pipeline.py
```

- **Pass rate**: 43/43 (100% of implemented test cases)
- **Pre-existing edge cases**: 6 logic MCQ format variants (documented above, not from enhancements)

### Sampling Verification

```powershell
python run_benchmark.py --dry-run --mode quick --seed 42
```

Shows domain × difficulty counts for the selected samples without any API calls.

---

## Compatibility Notes

| Issue | Fix |
|---|---|
| Windows Unicode errors | `$env:PYTHONIOENCODING = "utf-8"` before running any script |
| PowerShell multiline `-c` strings | Must be single-line (multiline continuation causes a hang) |
| Path not found: `rawdatasets` | Automatic fallback to `raw_datasets` is applied; no action needed |
| `scipy` not installed | `pip install "scipy>=1.8.0"` |
| Ollama model not found | Run `ollama list` to get exact tag; use that as `--model-name` |

---

## Data Source Policy

- The framework uses **pre-downloaded local datasets** in `data/raw_datasets/`
- No internet download occurs at benchmark time
- Supported formats: HF disk dataset (Arrow), JSON, JSONL, CSV, SQuAD v2 JSON
- Riegeli format is partially supported — conversion to JSONL is recommended

---

## Future Improvements

These are not currently planned but would enhance the framework:

- **RestrictedPython integration** — bytecode-level sandbox for stronger code execution security
- **Custom F1 threshold per domain/dataset** — currently one global threshold for the entire knowledge domain
- **More granular error categories** — per-evaluator sub-type tracking
- **Streaming support** — for models with very long outputs
- **Parallel evaluation across machines** — distributed benchmark mode
- **Automatic dataset download** — optional HF Hub download at first run if dataset folder is missing
