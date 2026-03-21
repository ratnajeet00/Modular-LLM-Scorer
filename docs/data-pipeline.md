# Data Pipeline

## 1) Dataset validation

`DatasetValidator` checks the dataset root and reports:

- hard errors: missing/invalid dataset root path
- warnings:
: unknown dataset folders
: missing supported folders
: unsupported raw shard format warning for `dm-code_contests`

Validator file: `benchmark_lib/dataset/validator.py`

## 2) Normalization to canonical schema

`DatasetNormalizer` transforms heterogeneous sources into `NormalizedSample`:

- Hugging Face disk datasets (`dataset_dict.json` + Arrow)
- JSON / JSONL
- CSV
- SQuAD v2 JSON

Normalizer file: `benchmark_lib/dataset/normalizer.py`

Canonical output fields:

- id
- dataset
- domain
- question
- answer
- options (optional)
- difficulty
- metadata

Important metadata used by evaluators:
- knowledge aliases (for acceptable answer variants)
- code test artifacts (`test`, `tests`, `test_list`)
- code execution hints (`entry_point`, `input`, `output`, `expected_output`)

## 3) Dataset-specific extractors

Examples currently implemented:

- math:
: `gsm8k_main`, `gsm8k_socratic`, `hendrycks_math_*`, `svamp`
- logic:
: `proofwriter`, `reclor`
- knowledge:
: `squad`, `natural_questions`, `trivia_qa`
- code:
: `openai_humaneval`, `mbpp_full`, `mbpp_sanitized`

## 4) Difficulty tagging

After extraction, each sample is tagged easy/medium/hard by domain-specific heuristics from `benchmark_lib/dataset/difficulty.py`.

SQuAD and TriviaQA normalization preserves additional answer variants in metadata for knowledge evaluator alias matching.

## 5) Hand-off to sampler

The full normalized sample list is passed into `stratified_sample(...)` for domain/dataset/difficulty constrained selection.

## Notes on source path

Primary default root is:

- `data/raw_datasets`

There is compatibility handling that maps `rawdatasets` to `raw_datasets` if needed.
