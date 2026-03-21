from __future__ import annotations

import json
import math
import re
import subprocess
import tempfile
import textwrap
from pathlib import Path

from ..utils.types import NormalizedSample


def _norm_text(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9\.\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_number(s: str) -> float | None:
    matches = re.findall(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
    if not matches:
        return None
    try:
        return float(matches[-1])
    except ValueError:
        return None


def evaluate(sample: NormalizedSample, prediction: str) -> tuple[bool, str | None]:
    if sample.domain == "math":
        return _eval_math(sample.answer, prediction), None
    if sample.domain == "logic":
        return _eval_logic(sample, prediction), None
    if sample.domain == "knowledge":
        return _norm_text(sample.answer) == _norm_text(prediction), None
    if sample.domain == "code":
        ok, err = _eval_code(sample, prediction)
        return ok, err
    return False, "unknown-domain"


def _eval_math(answer: str, prediction: str, tolerance: float = 1e-3) -> bool:
    if _norm_text(answer) == _norm_text(prediction):
        return True
    a_num = _extract_number(answer)
    p_num = _extract_number(prediction)
    if a_num is None or p_num is None:
        return False
    return math.isclose(a_num, p_num, rel_tol=tolerance, abs_tol=tolerance)


def _eval_logic(sample: NormalizedSample, prediction: str) -> bool:
    pred = prediction.strip()
    if sample.options:
        answer_norm = _norm_text(sample.answer)
        if _norm_text(pred) == answer_norm:
            return True
        # Accept answer letters A/B/C/D if options are provided.
        letter_match = re.search(r"\b([A-E])\b", pred.upper())
        if letter_match:
            idx = ord(letter_match.group(1)) - ord("A")
            if 0 <= idx < len(sample.options):
                return _norm_text(sample.options[idx]) == answer_norm
        return False
    return _norm_text(pred) == _norm_text(sample.answer)


def _extract_code_block(prediction: str) -> str:
    fenced = re.findall(r"```(?:python)?\n([\s\S]*?)```", prediction)
    if fenced:
        return fenced[0].strip()
    return prediction.strip()


def _eval_code(sample: NormalizedSample, prediction: str) -> tuple[bool, str | None]:
    code = _extract_code_block(prediction)
    if not code:
        return False, "empty-code"

    test_list = sample.metadata.get("tests", [])
    test_blob = sample.metadata.get("test", "")
    if test_list:
        test_source = "\n".join(str(x) for x in test_list)
    else:
        test_source = str(test_blob)

    if not test_source:
        # Fallback to exact match if no executable tests exist.
        return _norm_text(sample.answer) == _norm_text(code), None

    with tempfile.TemporaryDirectory(prefix="bench_eval_") as tmp:
        script_path = Path(tmp) / "candidate_test.py"
        runner = textwrap.dedent(
            f"""
            import json
            import traceback

            {code}

            try:
                {test_source}
                print(json.dumps({{"ok": True}}))
            except Exception as exc:
                print(json.dumps({{"ok": False, "error": str(exc), "trace": traceback.format_exc()}}))
            """
        )
        script_path.write_text(runner, encoding="utf-8")

        try:
            proc = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return False, "code-timeout"

        if proc.returncode != 0 and not proc.stdout.strip():
            return False, (proc.stderr or "code-exec-failed")[:500]

        last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        try:
            payload = json.loads(last_line)
        except Exception:
            return False, (proc.stderr or proc.stdout or "invalid-test-output")[:500]

        if bool(payload.get("ok")):
            return True, None
        return False, str(payload.get("error") or "test-failed")