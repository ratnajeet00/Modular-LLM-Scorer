from __future__ import annotations

from pathlib import Path


SUPPORTED_DATASETS = {
    "gsm8k_main",
    "gsm8k_socratic",
    "hendrycks_math_algebra",
    "hendrycks_math_counting_and_probability",
    "hendrycks_math_geometry",
    "svamp",
    "proofwriter",
    "logiqa",
    "reclor",
    "natural_questions",
    "trivia_qa",
    "squad",
    "openai_humaneval",
    "mbpp_full",
    "mbpp_sanitized",
    "dm-code_contests",
}


class DatasetValidator:
    def __init__(self, dataset_root: str) -> None:
        self.root = Path(dataset_root)

    def validate(self) -> tuple[list[str], list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        if not self.root.exists() or not self.root.is_dir():
            errors.append(f"Dataset root does not exist: {self.root}")
            return errors, warnings

        present = {p.name for p in self.root.iterdir() if p.is_dir()}
        unsupported = sorted([name for name in present if name not in SUPPORTED_DATASETS])
        if unsupported:
            warnings.append(f"Unknown dataset folders found and ignored: {unsupported}")

        missing = sorted([name for name in SUPPORTED_DATASETS if name not in present])
        if missing:
            warnings.append(f"Some supported dataset folders are missing: {missing}")

        if "dm-code_contests" in present:
            warnings.append(
                "dm-code_contests appears to use riegeli shards. Parsing is skipped unless converted to JSON/Arrow/HF disk format."
            )

        return errors, warnings
