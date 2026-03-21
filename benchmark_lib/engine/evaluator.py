from __future__ import annotations

from collections import Counter
import json
import math
import re
import subprocess
import tempfile
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
        return _eval_knowledge(sample, prediction), None
    if sample.domain == "code":
        ok, err = _eval_code(sample, prediction)
        return ok, err
    return False, "unknown-domain"


def _is_pure_number_text(s: str) -> bool:
    return bool(re.fullmatch(r"\s*-?\d+(?:\.\d+)?\s*", s.replace(",", "")))


def _token_f1(a: str, b: str) -> float:
    a_tokens = a.split()
    b_tokens = b.split()
    if not a_tokens or not b_tokens:
        return 0.0
    a_counter = Counter(a_tokens)
    b_counter = Counter(b_tokens)
    overlap = sum((a_counter & b_counter).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(b_tokens)
    recall = overlap / len(a_tokens)
    return (2 * precision * recall) / (precision + recall)


def _eval_knowledge(sample: NormalizedSample, prediction: str) -> bool:
    answer_norm = _norm_text(sample.answer)
    pred_norm = _norm_text(prediction)
    if answer_norm == pred_norm:
        return True

    # Keep strict numeric handling for number-only targets.
    if _is_pure_number_text(sample.answer):
        if not _is_pure_number_text(prediction):
            return False
        a_num = _extract_number(sample.answer)
        p_num = _extract_number(prediction)
        if a_num is None or p_num is None:
            return False
        return math.isclose(a_num, p_num, rel_tol=1e-9, abs_tol=1e-9)

    aliases = sample.metadata.get("aliases", [])
    if isinstance(aliases, list):
        for alias in aliases:
            if _norm_text(str(alias)) == pred_norm:
                return True

    # Accept short-answer containment for span-like answers.
    if answer_norm and pred_norm and len(answer_norm.split()) <= 5:
        if len(pred_norm) >= 3 and (answer_norm in pred_norm or pred_norm in answer_norm):
            return True

    return _token_f1(answer_norm, pred_norm) >= 0.8


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


def _stringify_expected(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "\n".join(str(x) for x in value)
    return str(value)


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

    with tempfile.TemporaryDirectory(prefix="bench_eval_") as tmp:
        candidate_path = Path(tmp) / "candidate.py"
        candidate_path.write_text(code, encoding="utf-8")

        if test_source:
            tests_path = Path(tmp) / "tests.py"
            tests_path.write_text(test_source, encoding="utf-8")
            runner_path = Path(tmp) / "runner.py"
            runner_path.write_text(
                "\n".join(
                    [
                        "import json",
                        "import sys",
                        "import traceback",
                        "from pathlib import Path",
                        "",
                        "entry_point = sys.argv[1] if len(sys.argv) > 1 else ''",
                        "namespace = {}",
                        "",
                        "try:",
                        "    candidate_src = Path('candidate.py').read_text(encoding='utf-8')",
                        "    tests_src = Path('tests.py').read_text(encoding='utf-8')",
                        "    exec(compile(candidate_src, 'candidate.py', 'exec'), namespace, namespace)",
                        "    if entry_point and entry_point in namespace and 'candidate' not in namespace:",
                        "        namespace['candidate'] = namespace[entry_point]",
                        "    exec(compile(tests_src, 'tests.py', 'exec'), namespace, namespace)",
                        "    print(json.dumps({'ok': True}))",
                        "except Exception as exc:",
                        "    print(json.dumps({'ok': False, 'error': str(exc), 'trace': traceback.format_exc()}))",
                    ]
                ),
                encoding="utf-8",
            )

            try:
                proc = subprocess.run(
                    ["python", str(runner_path), str(sample.metadata.get("entry_point", ""))],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                    cwd=tmp,
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

        expected_output = sample.metadata.get("expected_output")
        if expected_output is None:
            expected_output = sample.metadata.get("output")

        if expected_output is not None:
            stdin_payload = _stringify_expected(sample.metadata.get("input"))
            if stdin_payload and not stdin_payload.endswith("\n"):
                stdin_payload += "\n"

            try:
                proc = subprocess.run(
                    ["python", str(candidate_path)],
                    input=stdin_payload,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                    cwd=tmp,
                )
            except subprocess.TimeoutExpired:
                return False, "code-timeout"

            if proc.returncode != 0:
                return False, (proc.stderr or "code-exec-failed")[:500]

            actual_norm = _norm_text(proc.stdout)
            expected_norm = _norm_text(_stringify_expected(expected_output))
            if actual_norm == expected_norm:
                return True, None

            # Tolerate trailing explanations by checking output containment.
            if expected_norm and expected_norm in actual_norm:
                return True, None

            return False, "output-mismatch"

    # Last resort fallback when no executable checks are available.
    return _norm_text(sample.answer) == _norm_text(code), None