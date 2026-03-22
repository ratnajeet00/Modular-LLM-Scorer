from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .dataset.normalizer import DatasetNormalizer
from .dataset.validator import DatasetValidator
from .engine.runner import run_inference
from .engine.sampler import stratified_sample
from .engine.scorer import score
from .models.base_model import BaseModel
from .utils.cache import PromptCache
from .utils.logging import get_logger


logger = get_logger(__name__)


class Benchmark:
    def __init__(
        self,
        dataset_path: str,
        seed: int = 42,
        max_records_per_dataset: int = 6000,
    ) -> None:
        path = Path(dataset_path)
        if not path.exists() and "rawdatasets" in dataset_path:
            candidate = Path(dataset_path.replace("rawdatasets", "raw_datasets"))
            if candidate.exists():
                path = candidate
        self.dataset_path = str(path)
        self.seed = seed
        self.max_records_per_dataset = max_records_per_dataset

        validator = DatasetValidator(self.dataset_path)
        errors, warnings = validator.validate()
        if errors:
            raise ValueError("; ".join(errors))
        for w in warnings:
            logger.warning(w)

        normalizer = DatasetNormalizer(self.dataset_path, max_records_per_dataset=max_records_per_dataset)
        self.samples = normalizer.normalize_all()
        if not self.samples:
            raise ValueError(f"No benchmarkable samples found in {self.dataset_path}")
        logger.info("Loaded %s normalized samples", len(self.samples))

    def run(
        self,
        model: BaseModel,
        mode: str = "half",
        batch_size: int = 8,
        retries: int = 2,
        timeout_seconds: float = 30.0,
        cache_path: str | None = None,
        max_workers: int | None = None,
        raw_output_log_path: str | None = "temp_eval/raw_outputs.jsonl",
    ) -> dict:
        selected = stratified_sample(self.samples, mode=mode, seed=self.seed)
        logger.info("Running benchmark on %s samples in mode=%s", len(selected), mode)

        per_domain_ds: dict[str, set[str]] = defaultdict(set)
        diff_counts: Counter[str] = Counter()
        for s in selected:
            per_domain_ds[s.domain].add(s.dataset)
            diff_counts[s.difficulty] += 1
        logger.info(
            "Selected datasets by domain: %s",
            {k: sorted(v) for k, v in per_domain_ds.items()},
        )
        logger.info(
            "Difficulty mix: easy=%s medium=%s hard=%s",
            diff_counts.get("easy", 0),
            diff_counts.get("medium", 0),
            diff_counts.get("hard", 0),
        )

        import time as time_module
        inference_start = time_module.monotonic()
        records = run_inference(
            model=model,
            samples=selected,
            retries=retries,
            timeout_seconds=timeout_seconds,
            batch_size=batch_size,
            cache=PromptCache(cache_path),
            max_workers=max_workers,
            raw_output_log_path=raw_output_log_path,
        )
        inference_elapsed = time_module.monotonic() - inference_start

        non_empty_predictions = sum(1 for r in records if r.prediction.strip())
        call_error_records = [r for r in records if r.error and not r.prediction.strip()]
        call_error_count = len(call_error_records)

        if non_empty_predictions == 0 and records:
            example_errors = sorted({(r.error or "unknown-error") for r in call_error_records})[:3]
            raise RuntimeError(
                "No model outputs were captured. This usually means API/provider calls failed. "
                f"Examples: {example_errors}"
            )

        if call_error_count:
            logger.warning(
                "Model call failures detected: %s/%s (%.1f%%)",
                call_error_count,
                len(records),
                (100.0 * call_error_count / max(1, len(records))),
            )

        return score(records, model_name=model.model_name, mode=mode, selected_datasets_by_domain=per_domain_ds)
