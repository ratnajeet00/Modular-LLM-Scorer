import argparse
import json
import os
import re
import sys
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


def _compare_results(result1_path: str, result2_path: str) -> None:
    """Compare two benchmark result JSONs and show diff table."""
    try:
        with open(result1_path, encoding="utf-8") as f:
            r1 = json.load(f)
        with open(result2_path, encoding="utf-8") as f:
            r2 = json.load(f)
    except Exception as e:
        print(f"Error loading results: {e}", file=sys.stderr)
        return
    
    print(f"\n{'='*80}")
    print(f"Benchmark Comparison")
    print(f"{'='*80}")
    print(f"Model 1: {r1.get('model')} ({result1_path})")
    print(f"Model 2: {r2.get('model')} ({result2_path})")
    print()
    
    # Overall metrics
    print(f"{'Metric':<30} {'Model 1':>15} {'Model 2':>15} {'Diff':>15}")
    print("=" * 80)
    
    metrics = ["accuracy", "final_score", "failure_rate", "cost"]
    for metric in metrics:
        v1 = r1.get(metric, 0.0)
        v2 = r2.get(metric, 0.0)
        diff = v2 - v1
        diff_str = f"{diff:+.6f}"
        print(f"{metric:<30} {v1:>15.6f} {v2:>15.6f} {diff_str:>15}")
    
    # Per-domain breakdown
    print(f"\n{'Per-Domain Accuracy':<30} {'Model 1':>15} {'Model 2':>15} {'Diff':>15}")
    print("=" * 80)
    
    per_domain_1 = r1.get("per_domain", {})
    per_domain_2 = r2.get("per_domain", {})
    all_domains = set(per_domain_1.keys()) | set(per_domain_2.keys())
    
    for domain in sorted(all_domains):
        v1 = per_domain_1.get(domain, 0.0)
        v2 = per_domain_2.get(domain, 0.0)
        diff = v2 - v1
        diff_str = f"{diff:+.6f}"
        print(f"{domain:<30} {v1:>15.6f} {v2:>15.6f} {diff_str:>15}")
    
    # Try to perform McNemar's test if JSONL logs are available
    _try_mcnemar_test(result1_path, result2_path, r1, r2)


def _try_mcnemar_test(json1_path: str, json2_path: str, r1: dict, r2: dict) -> None:
    """Try to perform McNemar's test using raw JSONL logs if available."""
    try:
        from scipy.stats import chi2
    except ImportError:
        return  # scipy not available, skip
    
    # Try to locate JSONL files - they're typically in temp_eval or bech mark directories
    json1_parent = Path(json1_path).parent
    json2_parent = Path(json2_path).parent
    
    # Look for raw_outputs.jsonl or similar files
    possible_dirs = [
        json1_parent,
        json1_parent.parent / "temp_eval",
        Path("temp_eval"),
        Path("bech mark"),
    ]
    
    jsonl1 = None
    jsonl2 = None
    
    # Try to match with filename patterns from result files
    model1_name = r1.get("model", "model1")
    model2_name = r2.get("model", "model2")
    
    for d in possible_dirs:
        if not d.exists():
            continue
        # Look for files containing model names or dated output files
        for f in d.glob("*raw_outputs*.jsonl"):
            if jsonl1 is None and (model1_name.lower() in f.name.lower() or 
                                  f.name.startswith("raw_outputs")):
                jsonl1 = str(f)
            elif jsonl2 is None and (model2_name.lower() in f.name.lower() or
                                    f.name.startswith("raw_outputs")):
                jsonl2 = str(f)
            
            if jsonl1 and jsonl2:
                break
    
    if not jsonl1 or not jsonl2:
        return  # Couldn't find JSONL files
    
    try:
        # Extract predictions from JSONL
        m1_preds = {}
        m2_preds = {}
        
        with open(jsonl1) as f:
            for line in f:
                rec = json.loads(line)
                m1_preds[rec.get("sample_id")] = rec.get("correct", False)
        
        with open(jsonl2) as f:
            for line in f:
                rec = json.loads(line)
                m2_preds[rec.get("sample_id")] = rec.get("correct", False)
        
        # Find common samples
        common = set(m1_preds.keys()) & set(m2_preds.keys())
        if not common or len(common) < 10:
            return  # Not enough common samples
        
        # Build contingency table for discordant pairs
        m1_correct_m2_wrong = 0
        m1_wrong_m2_correct = 0
        
        for sid in common:
            m1_correct = m1_preds[sid]
            m2_correct = m2_preds[sid]
            
            if m1_correct and not m2_correct:
                m1_correct_m2_wrong += 1
            elif not m1_correct and m2_correct:
                m1_wrong_m2_correct += 1
        
        # Perform McNemar's test
        b = m1_correct_m2_wrong
        c = m1_wrong_m2_correct
        total_disagreement = b + c
        
        if total_disagreement == 0:
            stat = 0.0
            p_value = 1.0
        else:
            stat = (b - c) ** 2 / total_disagreement
            from scipy.stats import chi2
            p_value = 1 - chi2.cdf(stat, df=1)
        
        print(f"\n{'='*80}")
        print(f"Statistical Significance Test (McNemar's Test)")
        print(f"{'='*80}")
        print(f"Common samples evaluated: {len(common)}")
        print(f"Samples where models disagree: {m1_correct_m2_wrong + m1_wrong_m2_correct}")
        print(f"  Model 1 correct, Model 2 wrong: {m1_correct_m2_wrong}")
        print(f"  Model 2 correct, Model 1 wrong: {m1_wrong_m2_correct}")
        print(f"\nTest Statistic: {stat:.4f}")
        print(f"P-value: {p_value:.6f}")
        print(f"Significant at α=0.05: {'Yes' if p_value < 0.05 else 'No'}")
        if p_value < 0.05:
            print(f"→ The models have SIGNIFICANTLY different error rates (p={p_value:.4f})")
        else:
            print(f"→ No statistically significant difference in error rates (p={p_value:.4f})")
        
    except Exception:
        pass  # Silently fail if JSONL analysis doesn't work


def _dry_run(dataset_path: str, mode: str, seed: int) -> None:
    """Show sample selection without calling model."""
    from benchmark_lib import Benchmark
    from benchmark_lib.engine.sampler import stratified_sample
    
    try:
        benchmark = Benchmark(dataset_path=dataset_path, seed=seed)
        selected = stratified_sample(benchmark.samples, mode=mode, seed=seed)
        
        print(f"\n{'='*80}")
        print(f"Dry Run: Sample Selection")
        print(f"{'='*80}")
        print(f"Mode: {mode}")
        print(f"Seed: {seed}")
        print(f"Total samples selected: {len(selected)}")
        print()
        
        # Group by domain and difficulty
        from collections import defaultdict
        by_domain_diff = defaultdict(lambda: defaultdict(int))
        by_dataset = defaultdict(int)
        
        for s in selected:
            by_domain_diff[s.domain][s.difficulty] += 1
            by_dataset[s.dataset] += 1
        
        print("Samples by Domain and Difficulty:")
        print(f"{'Domain':<15} {'Easy':>8} {'Medium':>8} {'Hard':>8} {'Total':>8}")
        print("-" * 50)
        
        for domain in ["math", "logic", "knowledge", "code"]:
            easy = by_domain_diff[domain]["easy"]
            med = by_domain_diff[domain]["medium"]
            hard = by_domain_diff[domain]["hard"]
            total = easy + med + hard
            if total > 0:
                print(f"{domain:<15} {easy:>8} {med:>8} {hard:>8} {total:>8}")
        
        print(f"\nDatasets used: {len(by_dataset)}")
        for dataset, count in sorted(by_dataset.items()):
            print(f"  {dataset}: {count} samples")
        
        print(f"\n✓ Dry run complete. No API calls made.")
    except Exception as e:
        print(f"Error during dry run: {e}", file=sys.stderr)





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
    parser.add_argument("--domain", default=None, choices=["math", "logic", "knowledge", "code"], 
                        help="Filter to only run a specific domain (math, logic, knowledge, or code)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seeds", default=None, help="Comma-separated seeds for multi-seed runs, e.g. 42,43,44")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-workers", type=int, default=None, help="Max concurrent model requests")
    parser.add_argument("--timeout-seconds", type=float, default=30.0, help="(DISABLED - models run without time limits)")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--raw-output-log",
        default="temp_eval/raw_outputs.jsonl",
        help="JSONL path for per-sample raw outputs (question, prediction, error)",
    )
    # New CLI flags
    parser.add_argument("--compare", nargs=2, metavar=("RESULT1", "RESULT2"), 
                        help="Compare two benchmark result JSONs and show diff table")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show sample selection without calling model")
    args = parser.parse_args()

    # Handle special CLI modes
    if args.compare:
        _compare_results(args.compare[0], args.compare[1])
        return
    
    if args.dry_run:
        _dry_run(args.dataset_path, args.mode, args.seed)
        return

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

    if args.model == "gemini" and isinstance(model, GeminiModel):
        ok, message = model.preflight_model_check()
        print(message)
        if not ok:
            raise RuntimeError("Gemini preflight failed. Fix model/API access and retry.")

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
            domain_filter=args.domain,
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
