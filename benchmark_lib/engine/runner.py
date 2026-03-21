from __future__ import annotations

import ast
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError, as_completed

from ..models.base_model import BaseModel
from ..utils.cache import PromptCache
from ..utils.logging import get_logger
from ..utils.types import EvalRecord, NormalizedSample
from .evaluator import evaluate
from .prompt_builder import build_prompt, get_max_tokens


logger = get_logger(__name__)


RETRIABLE_CODE_ERROR_MARKERS = (
    "invalid-output-format",
    "missing",
    "typeerror",
    "list index out of range",
    "test-failed",
)


def _is_empty_response(res: str | None) -> bool:
    if res is None:
        return True
    stripped = res.strip()
    return stripped == "" or stripped == "```"


class _RenameFunctionSymbol(ast.NodeTransformer):
    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.old_name:
            return ast.copy_location(ast.Name(id=self.new_name, ctx=node.ctx), node)
        return node


def _extract_and_clean_code(text: str, expected_name: str | None) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""

    # Remove fenced markdown wrappers.
    if "```" in raw:
        fenced = []
        in_fence = False
        for line in raw.splitlines():
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                fenced.append(line)
        if fenced:
            raw = "\n".join(fenced).strip()

    lines = []
    for line in raw.splitlines():
        stripped = line.lstrip()
        if re.match(r"^print\s*\(", stripped):
            continue
        if stripped.startswith("if __name__"):
            break
        lines.append(line)
    raw = "\n".join(lines).strip()

    try:
        module = ast.parse(raw)
    except Exception:
        # Fallback: recover def-blocks from mixed prose + code outputs.
        lines = raw.splitlines()
        recovered: list[str] = []
        i = 0
        while i < len(lines):
            if re.match(r"^\s*(async\s+def|def)\s+\w+\s*\(", lines[i]):
                block = [lines[i]]
                i += 1
                while i < len(lines):
                    ln = lines[i]
                    if not ln.strip():
                        block.append(ln)
                        i += 1
                        continue
                    if ln.startswith((" ", "\t")):
                        block.append(ln)
                        i += 1
                        continue
                    break
                recovered.append("\n".join(block).rstrip())
                continue
            i += 1

        if recovered:
            raw = "\n\n".join(recovered).strip()
            try:
                module = ast.parse(raw)
            except Exception:
                return raw
        else:
            return raw
        return raw

    # Keep only imports + function defs; ignore examples/tests/explanations.
    kept_nodes: list[ast.stmt] = []
    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef)):
            kept_nodes.append(node)

    if not kept_nodes:
        return raw

    # Rename first function to expected function name when required.
    if expected_name:
        expected = expected_name.strip()
        funcs = [n for n in kept_nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        has_expected = any(getattr(fn, "name", "") == expected for fn in funcs)
        if funcs and not has_expected:
            old_name = funcs[0].name
            funcs[0].name = expected
            renamer = _RenameFunctionSymbol(old_name=old_name, new_name=expected)
            for idx, node in enumerate(kept_nodes):
                kept_nodes[idx] = renamer.visit(node)  # type: ignore[assignment]
            for node in kept_nodes:
                ast.fix_missing_locations(node)

    new_module = ast.Module(body=kept_nodes, type_ignores=[])
    ast.fix_missing_locations(new_module)
    try:
        return ast.unparse(new_module).strip()
    except Exception:
        return raw


def _safe_eval_arithmetic(expr: str) -> float | None:
    """Evaluate a simple arithmetic expression safely and return a number."""
    try:
        tree = ast.parse(expr, mode="eval")
    except Exception:
        return None

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.FloorDiv,
        ast.USub,
        ast.UAdd,
        ast.Constant,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            return None
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            return None

    try:
        result = eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, {})
    except Exception:
        return None
    return float(result) if isinstance(result, (int, float)) else None


def clean_output(sample: NormalizedSample, text: str) -> str:
    domain = sample.domain
    raw = (text or "").strip()
    if not raw:
        return ""

    # Normalize fenced outputs early for all domains.
    if raw.startswith("```"):
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        if len(lines) >= 2 and lines[-1].strip() == "```":
            body = lines[1:-1]
            raw = "\n".join(body).strip()

    if domain == "code":
        expected_name = sample.metadata.get("entry_point")
        if not isinstance(expected_name, str):
            expected_name = None
        return _extract_and_clean_code(raw, expected_name)

    if domain == "math":
        # Try to simplify expression-style answers into final numeric value.
        expr_candidate = raw.split("\n")[-1].strip()
        simplified = _safe_eval_arithmetic(expr_candidate)
        if simplified is not None:
            if simplified.is_integer():
                return str(int(simplified))
            return str(simplified)

    # For non-code tasks keep the final line to reduce extra narration.
    lines = [ln.strip() for ln in raw.split("\n") if ln.strip()]
    if not lines:
        return ""
    return lines[-1]


def valid_output(sample: NormalizedSample, text: str) -> bool:
    if not text or not text.strip():
        return False

    normalized = text.strip()
    if sample.domain == "code":
        if len(normalized) > 8000:
            return False
        if "def " not in normalized:
            return False
        try:
            ast.parse(normalized)
        except SyntaxError:
            return False
        return True

    # Non-code answers should stay concise and avoid giant irrelevant outputs.
    if len(normalized) > 1000:
        return False
    return True


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


def _call_with_timeout(model: BaseModel, prompt: str, timeout_seconds: float, max_tokens: int | None = None) -> str:
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(model.generate, prompt, max_tokens)
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
    raw_output_log_path: str | None = "temp_eval/raw_outputs.jsonl",
) -> list[EvalRecord]:
    cache = cache or PromptCache()
    records: list[EvalRecord | None] = [None] * len(samples)
    total = len(samples)
    started_at = time.monotonic()
    cache_lock = threading.Lock()
    progress_lock = threading.Lock()
    raw_log_lock = threading.Lock()
    completed = 0

    raw_output_file = None
    if raw_output_log_path:
        os.makedirs(os.path.dirname(raw_output_log_path), exist_ok=True)
        raw_output_file = open(raw_output_log_path, "a", encoding="utf-8")
    
    # Auto-adjust timeout and retries for local models (slower inference)
    # This applies to both Ollama (local:) and local Hugging Face (huggingface:) models
    is_local_model = model.model_name.startswith("local:") or (
        model.model_name.startswith("huggingface:") and not getattr(model, "use_inference_api", False)
    )
    is_groq_model = model.model_name.startswith("groq:")
    if is_local_model:
        # Local models are typically much slower (CPU inference)
        # Increase timeout and retry count for better reliability
        timeout_seconds = max(timeout_seconds, 120.0)  # Min 120s for local
        retries = max(retries, 3)  # Min 3 retries for flaky local connections
        logger.info(
            "Local model detected: adjusted timeout=%s retries=%s",
            timeout_seconds,
            retries,
        )

    if total == 0:
        return []

    if max_workers is None:
        if is_groq_model:
            # Groq free-tier is strict on RPM/TPM; keep defaults conservative.
            max_workers = 1
        else:
            # Reduced concurrency to 4-6 workers to prevent API failures
            cpu_count = os.cpu_count() or 4
            max_workers = min(6, max(4, cpu_count))
    max_workers = max(1, int(max_workers))
    worker_count = min(max_workers, total)
    logger.info("Inference concurrency: workers=%s", worker_count)
    
    # Reduce batch_size for local models to avoid memory and latency issues
    if is_local_model:
        batch_size = min(batch_size, 4)  # Cap at 4 for local models
        logger.info("Local model: reduced batch_size to %s", batch_size)

    def _run_one(sample: NormalizedSample) -> EvalRecord:
        prompt = build_prompt(sample)
        with cache_lock:
            cached = cache.get(model.model_name, prompt)
        prediction = None
        error: str | None = None
        cost = 0.0

        if cached is not None:
            cleaned_cached = clean_output(sample, cached)
            if valid_output(sample, cleaned_cached):
                prediction = cleaned_cached
                if cleaned_cached != cached:
                    with cache_lock:
                        cache.set(model.model_name, prompt, cleaned_cached)
            else:
                # Stale or malformed cache entry: force a fresh model response.
                prediction = None
        
        # Get domain-specific max_tokens (reduced for local models)
        max_tokens = get_max_tokens(sample.domain, is_local_model=is_local_model)

        if prediction is None:
            attempt = 0
            max_retry_for_sample = retries
            if sample.domain == "code":
                max_retry_for_sample = max(retries, 3)
            while True:
                try:
                    raw_prediction = _call_with_timeout(model, prompt, timeout_seconds, max_tokens)
                    if sample.domain == "code" and _is_empty_response(raw_prediction):
                        raise ValueError("empty-output")
                    prediction = clean_output(sample, raw_prediction)
                    if sample.domain == "code" and _is_empty_response(prediction):
                        raise ValueError("empty-output")
                    if not valid_output(sample, prediction):
                        raise ValueError("invalid-output-format")

                    if sample.domain == "code":
                        ok_code, err_code = evaluate(sample, prediction)
                        if not ok_code:
                            raise ValueError(f"execution-error:{err_code or 'unknown'}")

                    cost = float(model.get_last_cost())
                    with cache_lock:
                        cache.set(model.model_name, prompt, prediction)
                    break
                except Exception as exc:
                    attempt += 1
                    error_text = str(exc)
                    should_retry = True
                    if sample.domain == "code":
                        lower_error = error_text.lower()
                        should_retry = any(marker in lower_error for marker in RETRIABLE_CODE_ERROR_MARKERS)
                        if "empty-output" in lower_error:
                            should_retry = True
                    if not should_retry:
                        prediction = ""
                        error = error_text
                        break
                    if attempt > max_retry_for_sample:
                        prediction = ""
                        error = error_text
                        break

        correct, eval_error = evaluate(sample, prediction or "")
        if raw_output_file is not None:
            payload = {
                "sample_id": sample.id,
                "dataset": sample.dataset,
                "domain": sample.domain,
                "question": sample.question,
                "prediction": prediction or "",
                "error": error or eval_error,
            }
            with raw_log_lock:
                raw_output_file.write(json.dumps(payload, ensure_ascii=False) + "\n")
                raw_output_file.flush()

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
    if raw_output_file is not None:
        raw_output_file.close()
    return [r for r in records if r is not None]
