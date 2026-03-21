from __future__ import annotations

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed

from ..models.base_model import BaseModel
from ..utils.cache import PromptCache
from ..utils.logging import get_logger
from ..utils.types import EvalRecord, NormalizedSample
from .evaluator import evaluate
from .prompt_builder import build_prompt


logger = get_logger(__name__)


def _print_progress(done: int, total: int, started_at: float) -> None:
    if total <= 0:
        return
    width = 30
    ratio = done / total
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    elapsed = max(0.0, time.monotonic() - started_at)
    rate = done / elapsed if elapsed > 0 else 0.0
    remaining = total - done
    eta = remaining / rate if rate > 0 else 0.0
    line = (
        f"\rProgress [{bar}] {done}/{total} "
        f"({ratio * 100:5.1f}%) | {rate:5.2f} q/s | ETA {eta:6.1f}s"
    )
    sys.stderr.write(line)
    sys.stderr.flush()


def _call_with_timeout(model: BaseModel, prompt: str, timeout_seconds: float) -> str:
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(model.generate, prompt)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeoutError as exc:
            raise TimeoutError("Model call timed out") from exc


def run_inference(
    model: BaseModel,
    samples: list[NormalizedSample],
    retries: int = 2,
    timeout_seconds: float = 30.0,
    batch_size: int = 8,
    cache: PromptCache | None = None,
    show_progress: bool = True,
    max_workers: int | None = None,
) -> list[EvalRecord]:
    cache = cache or PromptCache()
    records: list[EvalRecord | None] = [None] * len(samples)
    total = len(samples)
    started_at = time.monotonic()
    cache_lock = threading.Lock()
    progress_lock = threading.Lock()
    completed = 0

    if total == 0:
        return []

    if max_workers is None:
        max_workers = min(16, max(4, (os.cpu_count() or 4) * 2))
    max_workers = max(1, int(max_workers))
    worker_count = min(max_workers, total)
    logger.info("Inference concurrency: workers=%s", worker_count)

    def _run_one(sample: NormalizedSample) -> EvalRecord:
        prompt = build_prompt(sample)
        with cache_lock:
            cached = cache.get(model.model_name, prompt)
        prediction = cached
        error: str | None = None
        cost = 0.0

        if prediction is None:
            attempt = 0
            while True:
                try:
                    prediction = _call_with_timeout(model, prompt, timeout_seconds)
                    cost = float(model.get_last_cost())
                    with cache_lock:
                        cache.set(model.model_name, prompt, prediction)
                    break
                except Exception as exc:
                    attempt += 1
                    if attempt > retries:
                        prediction = ""
                        error = str(exc)
                        break

        correct, eval_error = evaluate(sample, prediction or "")
        return EvalRecord(
            sample_id=sample.id,
            dataset=sample.dataset,
            domain=sample.domain,
            difficulty=sample.difficulty,
            prompt=prompt,
            prediction=prediction or "",
            expected=sample.answer,
            correct=correct,
            error=error or eval_error,
            cost=cost,
        )

    if show_progress:
        _print_progress(0, total, started_at)

    # Keep memory bounded by feeding work in chunks while still processing each chunk concurrently.
    chunk_size = max(worker_count, batch_size)
    for start in range(0, total, chunk_size):
        end = min(total, start + chunk_size)
        chunk = samples[start:end]
        with ThreadPoolExecutor(max_workers=worker_count) as pool:
            future_to_index = {
                pool.submit(_run_one, sample): idx for idx, sample in enumerate(chunk, start=start)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                records[idx] = future.result()
                if show_progress:
                    with progress_lock:
                        completed += 1
                        _print_progress(completed, total, started_at)

    if show_progress:
        sys.stderr.write("\n")
        sys.stderr.flush()

    cache.flush()
    return [r for r in records if r is not None]
