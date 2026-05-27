# Data Pipeline

## Overview

The data pipeline transforms raw dataset files into canonical `NormalizedSample` objects ready for sampling and evaluation. It runs automatically at benchmark startup.

**Implementation files**:
- `benchmark_lib/dataset/validator.py` — structure validation
- `benchmark_lib/dataset/normalizer.py` — multi-format normalization
- `benchmark_lib/dataset/difficulty.py` — difficulty tagging

---

## Step 1: Dataset Validation (`DatasetValidator`)

`DatasetValidator` inspects the dataset root directory and reports:

**Hard errors** (halt execution):
- Dataset root path does not exist or is not a directory

**Warnings** (logged but execution continues):
- Unknown folder names not in the supported dataset list
- Missing supported dataset folders
- `dm-code_contests` raw Riegeli shards (unsupported format)

**Supported canonical folder names** (declared in `validator.py`):

| Domain | Dataset Folders |
|---|---|
| Math | `gsm8k_main`, `gsm8k_socratic`, `hendrycks_math_*` (8 variants), `svamp` |
| Logic | `proofwriter`, `reclor` |
| Knowledge | `squad`, `natural_questions`, `trivia_qa` |
| Code | `openai_humaneval`, `mbpp_full`, `mbpp_sanitized` |

---

## Step 2: Normalization (`DatasetNormalizer`)

`DatasetNormalizer` reads each dataset folder and emits `NormalizedSample` objects with a canonical schema.

### Supported Source Formats

| Format | Detected by |
|---|---|
| **Hugging Face disk dataset** | `dataset_dict.json` + Apache Arrow files present |
| **JSON** | `.json` files with a list or dict structure |
| **JSONL** | `.jsonl` files (one JSON object per line) |
| **CSV** | `.csv` files |
| **SQuAD v2 JSON** | `.json` with `"data"[*].paragraphs[*].qas` structure |

### Canonical Output Schema (`NormalizedSample`)

| Field | Type | Description |
|---|---|---|
| `id` | `str` | `{dataset}-{index}` |
| `dataset` | `str` | Source dataset name |
| `domain` | `str` | `math`, `logic`, `knowledge`, or `code` |
| `question` | `str` | Question / problem text |
| `answer` | `str` | Ground-truth expected answer |
| `options` | `list[str] \| None` | MCQ answer options (logic domain only) |
| `difficulty` | `str` | `easy`, `medium`, or `hard` (set in step 3) |
| `metadata` | `dict` | Domain-specific extras (see below) |

### Important Metadata Fields

| Key | Used by | Description |
|---|---|---|
| `aliases` | Knowledge evaluator | Alternative correct answer strings (SQuAD, TriviaQA) |
| `test` | Code evaluator | Test assertions as a string |
| `tests` | Code evaluator | Test assertions as a list of strings |
| `test_list` | Code evaluator | Alternative test list format (MBPP) |
| `entry_point` | Code evaluator | Function name expected in candidate code |
| `input` | Code evaluator | stdin to provide when running code |
| `output` / `expected_output` | Code evaluator | Expected stdout |

---

## Step 3: Dataset-Specific Extractors

The normalizer contains per-dataset extraction logic:

### Math
- `gsm8k_main`, `gsm8k_socratic` — question/answer pairs; answer is the final numeric value
- `hendrycks_math_*` — problem/solution pairs; solution is extracted to the final boxed value
- `svamp` — equation word problems with numeric answers

### Logic
- `proofwriter` — natural language reasoning; answer is `true`, `false`, or `unknown`
- `reclor` — reading comprehension with MCQ options (A–E)

### Knowledge
- `squad` — extractive QA; preserves all `answers.text` variants as `aliases`
- `natural_questions` — question/answer pairs; short answer extracted
- `trivia_qa` — trivia QA; alternative answer variants preserved as `aliases`

### Code
- `openai_humaneval` — function signature + docstring as question; test assertions in metadata; `entry_point` required
- `mbpp_full`, `mbpp_sanitized` — programming tasks; test list in `test_list` metadata field

---

## Step 4: Difficulty Tagging (`difficulty.py`)

After extraction, each sample is tagged `easy`, `medium`, or `hard` using domain-specific heuristics:

| Domain | Heuristic |
|---|---|
| Math | Question length, presence of multi-step keywords, answer magnitude |
| Logic | Depth of reasoning chain, number of premises, question complexity |
| Knowledge | Answer length, number of answer aliases, question specificity |
| Code | Function complexity, number of test cases, presence of edge cases |

These are heuristic-based labels, not guaranteed ground truth. The actual difficulty distribution in a run depends on what the dataset contains.

---

## Step 5: Hand-Off to Sampler

The full normalized sample list (all domains, all datasets, all difficulties) is passed to `stratified_sample(samples, mode, seed)` in `benchmark_lib/engine/sampler.py`.

The sampler selects a representative subset according to the configured mode and seed. See [Sampling and Difficulty](./sampling-and-difficulty.md) for details.

---

## Notes on Dataset Root Path

- **Default**: `data/raw_datasets`
- **Override**: `--dataset-path /path/to/root`
- **Path compatibility**: Automatic fallback from `rawdatasets` → `raw_datasets` if the non-underscore path is not found
- **Data policy**: The framework uses **pre-downloaded local datasets** — no internet download occurs at benchmark time
- **Mixed formats**: A single run can use datasets in different formats from the same root directory
