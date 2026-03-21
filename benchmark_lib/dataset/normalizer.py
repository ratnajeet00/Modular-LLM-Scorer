from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

from .difficulty import code_difficulty, knowledge_difficulty, logic_difficulty, math_difficulty
from ..utils.types import NormalizedSample


DOMAIN_MAP = {
	"gsm8k_main": "math",
	"gsm8k_socratic": "math",
	"hendrycks_math_algebra": "math",
	"hendrycks_math_counting_and_probability": "math",
	"hendrycks_math_geometry": "math",
	"svamp": "math",
	"proofwriter": "logic",
	"logiqa": "logic",
	"reclor": "logic",
	"natural_questions": "knowledge",
	"trivia_qa": "knowledge",
	"squad": "knowledge",
	"openai_humaneval": "code",
	"mbpp_full": "code",
	"mbpp_sanitized": "code",
	"dm-code_contests": "code",
}


class DatasetNormalizer:
	def __init__(self, dataset_root: str, max_records_per_dataset: int = 6000) -> None:
		self.root = Path(dataset_root)
		self.max_records_per_dataset = max_records_per_dataset

	def normalize_all(self) -> list[NormalizedSample]:
		samples: list[NormalizedSample] = []
		for ds_dir in sorted([p for p in self.root.iterdir() if p.is_dir()]):
			dataset_name = ds_dir.name
			domain = DOMAIN_MAP.get(dataset_name)
			if not domain:
				continue
			if dataset_name == "squad":
				samples.extend(self._normalize_squad(ds_dir, domain))
				continue
			if dataset_name == "natural_questions":
				samples.extend(self._normalize_nq_csv(ds_dir, domain))
				continue
			if dataset_name == "dm-code_contests":
				continue
			samples.extend(self._normalize_generic_hf_or_json(ds_dir, domain, dataset_name))
		return samples

	def _normalize_generic_hf_or_json(self, ds_dir: Path, domain: str, dataset_name: str) -> list[NormalizedSample]:
		records = self._read_records(ds_dir)
		out: list[NormalizedSample] = []
		for idx, row in enumerate(records):
			sample = self._row_to_sample(row=row, dataset_name=dataset_name, domain=domain, idx=idx)
			if sample:
				out.append(sample)
			if len(out) >= self.max_records_per_dataset:
				break
		return out

	def _read_records(self, ds_dir: Path) -> list[dict[str, Any]]:
		dataset_dict = ds_dir / "dataset_dict.json"
		if dataset_dict.exists():
			try:
				from datasets import load_from_disk  # type: ignore

				ds = load_from_disk(str(ds_dir))
				all_rows: list[dict[str, Any]] = []
				for split_name in ds.keys():
					split = ds[split_name]
					cap = min(len(split), self.max_records_per_dataset)
					if cap == 0:
						continue
					for row in split.select(range(cap)):
						all_rows.append(dict(row))
					if len(all_rows) >= self.max_records_per_dataset:
						break
				return all_rows[: self.max_records_per_dataset]
			except Exception:
				pass

		rows: list[dict[str, Any]] = []
		for p in sorted(ds_dir.rglob("*.jsonl")):
			with p.open("r", encoding="utf-8") as f:
				for line in f:
					line = line.strip()
					if not line:
						continue
					rows.append(json.loads(line))
					if len(rows) >= self.max_records_per_dataset:
						return rows

		for p in sorted(ds_dir.rglob("*.json")):
			if p.name in {"dataset_info.json", "state.json", "dataset_dict.json"}:
				continue
			payload = json.loads(p.read_text(encoding="utf-8"))
			if isinstance(payload, list):
				rows.extend([x for x in payload if isinstance(x, dict)])
			elif isinstance(payload, dict):
				nested = payload.get("data")
				if isinstance(nested, list):
					rows.extend([x for x in nested if isinstance(x, dict)])
			if len(rows) >= self.max_records_per_dataset:
				return rows[: self.max_records_per_dataset]

		for p in sorted(ds_dir.rglob("*.csv")):
			with p.open("r", encoding="utf-8", newline="") as f:
				reader = csv.DictReader(f)
				for row in reader:
					rows.append(dict(row))
					if len(rows) >= self.max_records_per_dataset:
						return rows
		return rows[: self.max_records_per_dataset]

	def _row_to_sample(
		self,
		row: dict[str, Any],
		dataset_name: str,
		domain: str,
		idx: int,
	) -> NormalizedSample | None:
		q, a, options, meta = self._extract_qa(row, dataset_name)
		if not q or not a:
			return None

		if domain == "math":
			difficulty = math_difficulty(q, a)
		elif domain == "logic":
			difficulty = logic_difficulty(q, len(options or []))
		elif domain == "knowledge":
			difficulty = knowledge_difficulty(q, str(meta.get("context", "")))
		else:
			test_count = len(meta.get("tests", [])) if isinstance(meta.get("tests"), list) else 0
			difficulty = code_difficulty(q, test_count, str(meta.get("canonical_solution", "")))

		sid = str(
			row.get("id")
			or row.get("task_id")
			or row.get("id_string")
			or row.get("qid")
			or f"{dataset_name}-{idx}"
		)

		return NormalizedSample(
			id=sid,
			dataset=dataset_name,
			domain=domain,
			question=q,
			answer=a,
			options=options,
			difficulty=difficulty,
			metadata=meta,
		)

	def _extract_qa(self, row: dict[str, Any], dataset_name: str) -> tuple[str, str, list[str] | None, dict[str, Any]]:
		# Dataset-specific handling first.
		if dataset_name in {"gsm8k_main", "gsm8k_socratic"}:
			return str(row.get("question", "")), str(row.get("answer", "")), None, {}

		if dataset_name.startswith("hendrycks_math"):
			return str(row.get("problem", "")), str(row.get("solution", "")), None, {}

		if dataset_name == "svamp":
			q = str(row.get("Question", "") or row.get("question", ""))
			a = str(row.get("Answer", "") or row.get("answer", ""))
			return q, a, None, {}

		if dataset_name == "proofwriter":
			q = str(row.get("question", ""))
			a = str(row.get("answer", ""))
			context = str(row.get("theory", ""))
			return q, a, None, {"context": context}

		if dataset_name == "reclor":
			q = str(row.get("question", ""))
			answers = row.get("answers") or row.get("options") or []
			options = [str(x) for x in answers] if isinstance(answers, list) else None
			label = row.get("label")
			a = ""
			if isinstance(label, int) and options and 0 <= label < len(options):
				a = options[label]
			elif isinstance(label, str) and options:
				letter_idx = ord(label.strip().upper()[:1]) - ord("A")
				if 0 <= letter_idx < len(options):
					a = options[letter_idx]
			return q, a, options, {"context": str(row.get("context", "")), "label": label}

		if dataset_name == "openai_humaneval":
			q = str(row.get("prompt", ""))
			tests = row.get("test", "")
			entry_point = row.get("entry_point", "")
			a = str(row.get("canonical_solution", ""))
			return q, a, None, {"test": str(tests), "entry_point": str(entry_point), "canonical_solution": a}

		if dataset_name in {"mbpp_full", "mbpp_sanitized"}:
			q = str(row.get("text", "") or row.get("prompt", ""))
			a = str(row.get("code", ""))
			tests = row.get("test_list") if isinstance(row.get("test_list"), list) else []
			return q, a, None, {"tests": tests, "canonical_solution": a}

		if dataset_name == "trivia_qa":
			q = str(row.get("question", ""))
			a = self._coerce_trivia_answer(row.get("answer"))
			meta: dict[str, Any] = {}
			ans_obj = row.get("answer")
			if isinstance(ans_obj, dict) and isinstance(ans_obj.get("aliases"), list):
				meta["aliases"] = [str(x) for x in ans_obj.get("aliases", []) if str(x).strip()]
			return q, a, None, meta

		# Generic fallback.
		question = str(
			row.get("question")
			or row.get("problem")
			or row.get("prompt")
			or row.get("text")
			or ""
		)
		answer = str(
			row.get("answer")
			or row.get("target")
			or row.get("solution")
			or row.get("output")
			or ""
		)
		options: list[str] | None = None
		if isinstance(row.get("options"), list):
			options = [str(x) for x in row["options"]]

		meta: dict[str, Any] = {}
		for key in ["test", "tests", "test_list", "input", "output", "expected_output", "entry_point", "aliases"]:
			if key in row and row.get(key) is not None:
				meta[key] = row.get(key)
		return question, answer, options, meta

	def _normalize_squad(self, ds_dir: Path, domain: str) -> list[NormalizedSample]:
		out: list[NormalizedSample] = []
		idx = 0
		for file_name in ["train-v2.0.json", "dev-v2.0.json"]:
			p = ds_dir / file_name
			if not p.exists():
				continue
			payload = json.loads(p.read_text(encoding="utf-8"))
			for article in payload.get("data", []):
				for paragraph in article.get("paragraphs", []):
					context = paragraph.get("context", "")
					for qa in paragraph.get("qas", []):
						answers = qa.get("answers", [])
						if not answers:
							continue
						all_answers = [str(x.get("text", "")) for x in answers if str(x.get("text", "")).strip()]
						answer = all_answers[0] if all_answers else ""
						question = str(qa.get("question", ""))
						if not question or not answer:
							continue
						difficulty = knowledge_difficulty(question, context)
						aliases = list(dict.fromkeys(all_answers))
						out.append(
							NormalizedSample(
								id=str(qa.get("id", f"squad-{idx}")),
								dataset="squad",
								domain=domain,
								question=question,
								answer=answer,
								options=None,
								difficulty=difficulty,
								metadata={"context": context, "aliases": aliases},
							)
						)
						idx += 1
						if len(out) >= self.max_records_per_dataset:
							return out
		return out

	def _normalize_nq_csv(self, ds_dir: Path, domain: str) -> list[NormalizedSample]:
		out: list[NormalizedSample] = []
		idx = 0
		# Natural Questions CSV rows can contain very large contexts.
		csv.field_size_limit(min(2**31 - 1, sys.maxsize))
		for p in sorted(ds_dir.glob("*.csv")):
			with p.open("r", encoding="utf-8", newline="") as f:
				reader = csv.DictReader(f)
				for row in reader:
					q = str(
						row.get("Question")
						or row.get("question")
						or row.get("question_text")
						or row.get("Query")
						or ""
					)
					a = str(
						row.get("Answer")
						or row.get("answer")
						or row.get("short_answers")
						or row.get("short_answer")
						or row.get("long_answers")
						or row.get("long_answer")
						or row.get("Short Answer")
						or ""
					)
					if not q or not a:
						continue
					diff = knowledge_difficulty(q, "")
					out.append(
						NormalizedSample(
							id=str(row.get("id", f"nq-{idx}")),
							dataset="natural_questions",
							domain=domain,
							question=q,
							answer=a,
							options=None,
							difficulty=diff,
							metadata={},
						)
					)
					idx += 1
					if len(out) >= self.max_records_per_dataset:
						return out
		return out

	@staticmethod
	def _coerce_trivia_answer(answer: Any) -> str:
		if isinstance(answer, str):
			return answer
		if isinstance(answer, dict):
			if isinstance(answer.get("value"), str):
				return answer["value"]
			aliases = answer.get("aliases")
			if isinstance(aliases, list) and aliases:
				return str(aliases[0])
		return ""
