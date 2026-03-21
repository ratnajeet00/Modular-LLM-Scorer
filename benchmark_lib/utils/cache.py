from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


class PromptCache:
    def __init__(self, cache_path: str | None = None) -> None:
        default_path = Path(".benchmark_cache") / "prompt_cache.json"
        self.path = Path(cache_path) if cache_path else default_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, str] = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    @staticmethod
    def key(model_name: str, prompt: str) -> str:
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        return f"{model_name}:{digest}"

    def get(self, model_name: str, prompt: str) -> str | None:
        return self._data.get(self.key(model_name, prompt))

    def set(self, model_name: str, prompt: str, answer: str) -> None:
        self._data[self.key(model_name, prompt)] = answer

    def flush(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)
