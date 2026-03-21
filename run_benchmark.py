import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime
from statistics import mean, stdev

from benchmark_lib import Benchmark
from benchmark_lib.models.base_model import BaseModel
from benchmark_lib.models.local_model import LocalModel
from benchmark_lib.models.openai_model import OpenAIModel
from benchmark_lib.models.openrouter_model import OpenRouterModel
from benchmark_lib.models.huggingface_model import HuggingFaceModel
from benchmark_lib.models.gemini_model import GeminiModel
from benchmark_lib.models.together_model import TogetherModel
from benchmark_lib.models.groq_model import GroqModel


class EchoModel(BaseModel):
    model_name = "echo-model"

    def generate(self, prompt: str, max_tokens: int | None = None) -> str:
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
    hf_api_token: str | None = None,
    hf_use_inference_api: bool = False,
    hf_device: str = "cpu",
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
    if name == "huggingface":
        if not model_name_override:
            raise ValueError("--model-name is required when --model huggingface")
        model_id = model_name_override
        token = hf_api_token or os.getenv("HF_API_TOKEN", "")
        use_api = hf_use_inference_api or os.getenv("HF_USE_INFERENCE_API", "").lower() in ("true", "1", "yes")
        device = hf_device or os.getenv("HF_DEVICE", "cpu")

        # Log token source for debugging
        token_source = "CLI argument" if hf_api_token else "HF_API_TOKEN env variable" if token else "not set"
        print(f"[HF] Model: {model_id}, Token: {token_source}, Mode: {'API' if use_api else 'local'}, Device: {device}")

        return HuggingFaceModel(
            model=model_id,
            api_token=token,
            use_inference_api=use_api,
            device=device,
        )
    if name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "")
        model_id = model_name_override or "gemini-2.0-flash"
        print(f"[Gemini] Using model: {model_id}")
        return GeminiModel(api_key=api_key, model=model_id)
    if name == "together":
        api_key = os.getenv("TOGETHER_API_KEY", "")
        model_id = model_name_override or "mistralai/Mistral-7B-Instruct-v0.3"
        print(f"[Together] Using model: {model_id}")
        return TogetherModel(api_key=api_key, model=model_id)
    if name == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        model_id = model_name_override or "llama-3.1-8b-instant"
        print(f"[Groq] Using model: {model_id}")
        return GroqModel(api_key=api_key, model=model_id)
    if name == "echo":
        return EchoModel()
    raise ValueError(f"Unsupported model: {name}")


def _sanitize_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or "model"


def _parse_seeds(seeds_arg: str | None, seed_fallback: int) -> list[int]:
    if not seeds_arg:
        return [seed_fallback]
    items = [x.strip() for x in seeds_arg.split(",") if x.strip()]
    if not items:
        return [seed_fallback]
    return [int(x) for x in items]


def _mean_std(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "std": 0.0}
    if len(values) == 1:
        return {"mean": round(values[0], 6), "std": 0.0}
    return {"mean": round(mean(values), 6), "std": round(stdev(values), 6)}


def _aggregate_runs(model_name: str, mode: str, seeds: list[int], runs: list[dict]) -> dict:
    metric_names = ["accuracy", "final_score", "error_rate", "failure_rate", "cost"]
    aggregate_metrics: dict[str, dict[str, float]] = {}
    for metric_name in metric_names:
        values = [float(r.get(metric_name, 0.0) or 0.0) for r in runs]
        aggregate_metrics[metric_name] = _mean_std(values)

    domains: set[str] = set()
    for r in runs:
        domains.update((r.get("per_domain") or {}).keys())
    per_domain_agg: dict[str, dict[str, float]] = {}
    for domain in sorted(domains):
        values = [float((r.get("per_domain") or {}).get(domain, 0.0) or 0.0) for r in runs]
        per_domain_agg[domain] = _mean_std(values)

    return {
        "model": model_name,
        "mode": mode,
        "seeds": seeds,
        "run_count": len(runs),
        "aggregate": {
            **aggregate_metrics,
            "per_domain": per_domain_agg,
        },
        "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LLM benchmark")
    parser.add_argument("--dataset-path", default="data/raw_datasets", help="Root path containing datasets")
    parser.add_argument(
        "--model",
        default="echo",
        choices=["echo", "openai", "openrouter", "local", "huggingface", "gemini", "together", "groq"],
    )
    parser.add_argument("--model-name", default=None, help="Model identifier to test (overrides provider env default)")
    parser.add_argument("--env-file", default=".env", help="Path to env file with API keys and model defaults")
    parser.add_argument("--local-base-url", default=None, help="Local provider base URL (e.g. http://localhost:11434/v1)")
    parser.add_argument("--local-api-key", default=None, help="Optional API key for local OpenAI-compatible endpoint")
    parser.add_argument("--hf-api-token", default=None, help="Hugging Face API token (from https://huggingface.co/settings/tokens)")
    parser.add_argument("--hf-use-inference-api", action="store_true", help="Use HF Inference API instead of local transformers")
    parser.add_argument("--hf-device", default="cpu", choices=["cpu", "cuda", "mps"], help="Device for local HF inference (cpu, cuda, mps)")
    parser.add_argument("--mode", default="half", choices=["quick", "half", "full"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seeds", default=None, help="Comma-separated seeds for multi-seed runs, e.g. 42,43,44")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-workers", type=int, default=None, help="Max concurrent model requests")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--raw-output-log",
        default="temp_eval/raw_outputs.jsonl",
        help="JSONL path for per-sample raw outputs (question, prediction, error)",
    )
    args = parser.parse_args()

    _load_env_file(args.env_file)

    model = build_model(
        args.model,
        model_name_override=args.model_name,
        local_base_url=args.local_base_url,
        local_api_key=args.local_api_key,
        hf_api_token=args.hf_api_token,
        hf_use_inference_api=args.hf_use_inference_api,
        hf_device=args.hf_device,
    )

    seeds = _parse_seeds(args.seeds, args.seed)
    runs: list[dict] = []
    for seed in seeds:
        benchmark = Benchmark(dataset_path=args.dataset_path, seed=seed)
        run_result = benchmark.run(
            model=model,
            mode=args.mode,
            batch_size=args.batch_size,
            max_workers=args.max_workers,
            timeout_seconds=args.timeout_seconds,
            retries=args.retries,
            raw_output_log_path=args.raw_output_log,
        )
        run_result["seed"] = seed
        runs.append(run_result)

    if len(runs) == 1:
        results = runs[0]
    else:
        results = _aggregate_runs(model_name=model.model_name, mode=args.mode, seeds=seeds, runs=runs)

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
