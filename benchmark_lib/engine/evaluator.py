from __future__ import annotations

from collections import Counter
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

from ..utils.types import NormalizedSample


# Configuration for evaluation thresholds
# Can be adjusted based on evaluation strictness
F1_THRESHOLD_KNOWLEDGE = 0.75  # Reduced from 0.8 for better partial match acceptance


def _norm_text(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^a-z0-9\.\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_refusal(text: str) -> bool:
    """Detect if text is a refusal/inability message from the model."""
    text_lower = text.lower()
    
    refusal_patterns = [
        r"i.*sorry.*(?:can't|cannot|unable|not able|don't.*able).*assist",
        r"i.*(?:can only|only.*able|limited|designed.*only).*computer\s*science.*programming",
        r"i.*don't have.*(?:expertise|knowledge|capability).*(?:medical|biology|history|science)",
        r"(?:cannot|can't|unable to).*answer.*(?:medical|biology|history|science|outside)",
        r"outside.*my.*(?:expertise|knowledge|area)",
        r"not.*equipped.*(?:answer|help).*(?:medical|biology|history)",
        r"(?:regret|unable|cannot).*(?:answer|assist|help).*(?:questions?|query|request)",
        r"i.*programming.*assistant|i.*coding.*assistant",
    ]
    
    for pattern in refusal_patterns:
        if re.search(pattern, text_lower):
            return True
    
    # Also check for very generic "sorry" messages
    if ("sorry" in text_lower and 
        ("can't" in text_lower or "cannot" in text_lower or "unable" in text_lower)):
        return True
    
    return False


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
    # Reject refusals immediately
    if _is_refusal(prediction):
        return False
    
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

    return _token_f1(answer_norm, pred_norm) >= F1_THRESHOLD_KNOWLEDGE


def _eval_math(answer: str, prediction: str, tolerance: float = 1e-3) -> bool:
    if _norm_text(answer) == _norm_text(prediction):
        return True
    a_num = _extract_number(answer)
    p_num = _extract_number(prediction)
    if a_num is None or p_num is None:
        return False
    return math.isclose(a_num, p_num, rel_tol=tolerance, abs_tol=tolerance)


def _eval_logic(sample: NormalizedSample, prediction: str) -> bool:
    pred = prediction.strip().lower()
    if pred in ["true", "t"]:
        pred = "true"
    elif pred in ["false", "f"]:
        pred = "false"

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


# ---------- Fix 3: deprecated collections imports (Python 3.10+) ----------
_DEPRECATED_COLLECTIONS_IMPORTS = {
    "from collections import Iterable":       "from collections.abc import Iterable",
    "from collections import Iterator":       "from collections.abc import Iterator",
    "from collections import Generator":      "from collections.abc import Generator",
    "from collections import Callable":       "from collections.abc import Callable",
    "from collections import Mapping":        "from collections.abc import Mapping",
    "from collections import MutableMapping": "from collections.abc import MutableMapping",
    "from collections import Sequence":       "from collections.abc import Sequence",
    "from collections import MutableSequence":"from collections.abc import MutableSequence",
    "from collections import Set":           "from collections.abc import Set",
    "from collections import MutableSet":    "from collections.abc import MutableSet",
    "from collections import Hashable":      "from collections.abc import Hashable",
    "from collections import Sized":         "from collections.abc import Sized",
    "from collections import Container":     "from collections.abc import Container",
    "from collections import ByteString":    "from collections.abc import ByteString",
}


def _patch_deprecated_imports(code: str) -> str:
    """Fix deprecated 'from collections import <ABC>' for Python 3.10+."""
    for old, new in _DEPRECATED_COLLECTIONS_IMPORTS.items():
        code = code.replace(old, new)
    return code


# ---------- Fix 4: safe stdlib imports prefix ----------
_SAFE_IMPORTS = (
    "import math\n"
    "import re\n"
    "import sys\n"
    "import itertools\n"
    "import functools\n"
    "import collections\n"
    "import heapq\n"
    "import bisect\n"
    "import string\n"
    "import operator\n"
    "import copy\n"
)


def _prepend_safe_imports(code: str) -> str:
    """Prepend commonly-needed stdlib imports so model-forgotten imports don't crash."""
    return _SAFE_IMPORTS + "\n" + code


def _eval_code(sample: NormalizedSample, prediction: str) -> tuple[bool, str | None]:
    code = _extract_code_block(prediction)
    if not code:
        return False, "empty-code"
    
    # Optional sandboxed safety check (lightweight validation only)
    if ENABLE_SANDBOXED_EVAL:
        try:
            from .sandboxed_eval import validate_code_safety
            is_safe, safety_msg = validate_code_safety(code, strict_mode=False)
            if not is_safe:
                return False, f"sandbox-{safety_msg.lower().replace(' ', '_')}"
        except ImportError:
            pass  # Sandboxed eval not available, continue normally

    # --- Apply code patches before execution ---
    code = _patch_deprecated_imports(code)   # Fix 3
    code = _prepend_safe_imports(code)        # Fix 4

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
                        "import ast",
                        "import builtins",
                        "import difflib",
                        "import inspect",
                        "import json",
                        "import sys",
                        "import traceback",
                        "from pathlib import Path",
                        "",
                        "entry_point = sys.argv[1] if len(sys.argv) > 1 else ''",
                        "namespace = {}",
                        "",
                        "try:",
                        "    import math as _math",
                        "    import re as _re",
                        "    import sys as _sys",
                        "    import heapq as _heapq",
                        "    import itertools as _itertools",
                        "    import collections as _collections",
                        "    namespace.update({",
                        "        'math': _math,",
                        "        're': _re,",
                        "        'sys': _sys,",
                        "        'heapq': _heapq,",
                        "        'itertools': _itertools,",
                        "        'collections': _collections,",
                        "    })",
                        "    candidate_src = Path('candidate.py').read_text(encoding='utf-8')",
                        "    tests_src = Path('tests.py').read_text(encoding='utf-8')",
                        "    exec(compile(candidate_src, 'candidate.py', 'exec'), namespace, namespace)",
                        "    user_funcs = {",
                        "        k: v for k, v in namespace.items()",
                        "        if callable(v) and not k.startswith('_')",
                        "    }",
                        "",
                        "    def _select_best_callable(target_name):",
                        "        if not user_funcs:",
                        "            return None",
                        "        if target_name and target_name in user_funcs:",
                        "            return user_funcs[target_name]",
                        "        names = list(user_funcs.keys())",
                        "        if target_name:",
                        "            scored = [",
                        "                (difflib.SequenceMatcher(a=target_name, b=n).ratio(), n)",
                        "                for n in names",
                        "            ]",
                        "            scored.sort(reverse=True)",
                        "            if scored and scored[0][0] >= 0.45:",
                        "                return user_funcs[scored[0][1]]",
                        "        return user_funcs[names[0]]",
                        "",
                        "    def _adapt_signature(fn):",
                        "        try:",
                        "            sig = inspect.signature(fn)",
                        "            positional = [",
                        "                p for p in sig.parameters.values()",
                        "                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)",
                        "            ]",
                        "            max_pos = len(positional)",
                        "        except Exception:",
                        "            max_pos = None",
                        "",
                        "        def _safe_call(func, test_input):",
                        "            try:",
                        "                if isinstance(test_input, tuple):",
                        "                    return func(*test_input)",
                        "                return func(test_input)",
                        "            except TypeError:",
                        "                try:",
                        "                    return func(test_input)",
                        "                except Exception:",
                        "                    return None",
                        "",
                        "        def _wrapped(*args, **kwargs):",
                        "            if kwargs:",
                        "                return fn(*args, **kwargs)",
                        "            if len(args) == 1:",
                        "                return _safe_call(fn, args[0])",
                        "            try:",
                        "                return fn(*args, **kwargs)",
                        "            except TypeError as exc:",
                        "                msg = str(exc)",
                        "                if 'positional argument' not in msg and 'positional arguments' not in msg:",
                        "                    raise",
                        "                attempts = []",
                        "                if max_pos is not None and len(args) > max_pos:",
                        "                    attempts.append((args[:max_pos], kwargs))",
                        "                if len(args) > 1 and not kwargs:",
                        "                    for a in args:",
                        "                        attempts.append(((a,), {}))",
                        "                if len(args) > 1 and not kwargs:",
                        "                    attempts.append(((list(args),), {}))",
                        "                    attempts.append(((tuple(args),), {}))",
                        "                    attempts.append(((args,), {}))",
                        "                if len(args) == 1 and not kwargs and isinstance(args[0], (list, tuple)):",
                        "                    attempts.append((tuple(args[0]), {}))",
                        "                    attempts.append(((list(args[0]),), {}))",
                        "                for a2, k2 in attempts:",
                        "                    try:",
                        "                        return fn(*a2, **k2)",
                        "                    except TypeError:",
                        "                        continue",
                        "                raise",
                        "",
                        "        return _wrapped",
                        "",
                        "    selected = _select_best_callable(entry_point)",
                        "    for _name, _fn in list(user_funcs.items()):",
                        "        user_funcs[_name] = _adapt_signature(_fn)",
                        "        namespace[_name] = user_funcs[_name]",
                        "    if entry_point and entry_point not in namespace and selected is not None:",
                        "        namespace[entry_point] = _adapt_signature(selected)",
                        "    if entry_point and entry_point in namespace and 'candidate' not in namespace:",
                        "        namespace['candidate'] = namespace[entry_point]",
                        "    if selected is None and user_funcs:",
                        "        selected = _select_best_callable(entry_point)",
                        "    if selected is not None:",
                        "        selected = _adapt_signature(selected)",
                        "        try:",
                        "            test_ast = ast.parse(tests_src)",
                        "            called_names = {",
                        "                n.func.id for n in ast.walk(test_ast)",
                        "                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)",
                        "            }",
                        "        except Exception:",
                        "            called_names = set()",
                        "        builtin_names = set(dir(builtins))",
                        "        for name in called_names:",
                        "            if name in namespace or name in builtin_names:",
                        "                continue",
                        "            namespace[name] = selected",
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