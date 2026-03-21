import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime

from benchmark_lib import Benchmark
from benchmark_lib.models.base_model import BaseModel
from benchmark_lib.models.local_model import LocalModel
from benchmark_lib.models.openai_model import OpenAIModel
from benchmark_lib.models.openrouter_model import OpenRouterModel


class EchoModel(BaseModel):
    model_name = "echo-model"

    def generate(self, prompt: str) -> str:
        return prompt


def _load_env_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists() or not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def build_model(
    name: str,
    model_name_override: str | None = None,
    local_base_url: str | None = None,
    local_api_key: str | None = None,
) -> BaseModel:
    if name == "openai":
        if not model_name_override:
            raise ValueError("--model-name is required when --model openai")
        api_key = os.getenv("OPENAI_API_KEY", "")
        model_id = model_name_override
        return OpenAIModel(api_key=api_key, model=model_id)
    if name == "openrouter":
        if not model_name_override:
            raise ValueError("--model-name is required when --model openrouter")
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model_id = model_name_override
        return OpenRouterModel(api_key=api_key, model=model_id)
    if name == "local":
        if not model_name_override:
            raise ValueError("--model-name is required when --model local")
        model_id = model_name_override
        base_url = local_base_url or os.getenv("LOCAL_BASE_URL", "http://localhost:11434/v1")
        api_key = local_api_key if local_api_key is not None else os.getenv("LOCAL_API_KEY", "")
        return LocalModel(model=model_id, base_url=base_url, api_key=api_key)
    if name == "echo":
        return EchoModel()
    raise ValueError(f"Unsupported model: {name}")


def _sanitize_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or "model"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LLM benchmark")
    parser.add_argument("--dataset-path", default="data/raw_datasets", help="Root path containing datasets")
    parser.add_argument("--model", default="echo", choices=["echo", "openai", "openrouter", "local"])
    parser.add_argument("--model-name", default=None, help="Model identifier to test (overrides provider env default)")
    parser.add_argument("--env-file", default=".env", help="Path to env file with API keys and model defaults")
    parser.add_argument("--local-base-url", default=None, help="Local provider base URL (e.g. http://localhost:11434/v1)")
    parser.add_argument("--local-api-key", default=None, help="Optional API key for local OpenAI-compatible endpoint")
    parser.add_argument("--mode", default="half", choices=["quick", "half", "full"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    _load_env_file(args.env_file)

    benchmark = Benchmark(dataset_path=args.dataset_path, seed=args.seed)
    model = build_model(
        args.model,
        model_name_override=args.model_name,
        local_base_url=args.local_base_url,
        local_api_key=args.local_api_key,
    )

    results = benchmark.run(
        model=model,
        mode=args.mode,
        batch_size=args.batch_size,
        timeout_seconds=args.timeout_seconds,
        retries=args.retries,
    )

    out_dir = Path("bech mark")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_part = _sanitize_filename(model.model_name)
    out_path = out_dir / f"{model_part}_{stamp}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"Saved benchmark report: {out_path}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
