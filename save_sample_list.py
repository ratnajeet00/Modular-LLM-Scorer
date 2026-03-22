#!/usr/bin/env python3
"""
Save sampled question list for reproducibility.

Reads a raw JSONL output log and extracts metadata about which exact questions
were evaluated, allowing independent reproduction of the exact evaluation set.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict


def extract_sample_metadata(jsonl_path: str | Path) -> dict:
    """Extract metadata about sampled questions from JSONL."""
    jsonl_path = Path(jsonl_path)
    
    if not jsonl_path.exists():
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return {}
    
    samples = []
    by_domain = defaultdict(list)
    by_dataset = defaultdict(list)
    by_difficulty = Counter()
    
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line {line_num}: {e}", file=sys.stderr)
                    continue
                
                # Extract key fields
                sample_meta = {
                    "sample_id": record.get("sample_id"),
                    "dataset": record.get("dataset"),
                    "domain": record.get("domain"),
                    "difficulty": record.get("difficulty"),
                    "question": record.get("question"),
                }
                
                samples.append(sample_meta)
                
                domain = record.get("domain")
                if domain:
                    by_domain[domain].append(sample_meta)
                
                dataset = record.get("dataset")
                if dataset:
                    by_dataset[dataset].append(sample_meta)
                
                difficulty = record.get("difficulty")
                if difficulty:
                    by_difficulty[difficulty] += 1
    
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return {}
    
    # Build summary
    summary = {
        "file": str(jsonl_path),
        "total_samples": len(samples),
        "samples": samples,
        "summary": {
            "by_domain": {
                domain: len(samples_list) for domain, samples_list in by_domain.items()
            },
            "by_dataset": {
                dataset: len(samples_list) for dataset, samples_list in by_dataset.items()
            },
            "by_difficulty": dict(by_difficulty),
        }
    }
    
    return summary


def save_sample_list(jsonl_path: str | Path, output_path: str | Path | None = None) -> None:
    """Extract and save sample metadata to JSON."""
    metadata = extract_sample_metadata(jsonl_path)
    
    if not metadata:
        print("Failed to extract metadata", file=sys.stderr)
        return
    
    if output_path is None:
        output_path = Path(jsonl_path).stem + "_sample_list.json"
    else:
        output_path = Path(output_path)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print(f"Sample List Extracted")
        print(f"{'='*80}")
        print(f"Source: {jsonl_path}")
        print(f"Output: {output_path}")
        print(f"Total samples: {metadata['total_samples']}")
        print(f"\nBreakdown by domain:")
        for domain, count in sorted(metadata['summary']['by_domain'].items()):
            print(f"  {domain:<15} {count:>4}")
        print(f"\nBreakdown by difficulty:")
        for diff, count in sorted(metadata['summary']['by_difficulty'].items()):
            print(f"  {diff:<15} {count:>4}")
        print(f"\n✓ Sample list saved to {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}", file=sys.stderr)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python save_sample_list.py <path_to_raw_outputs.jsonl> [output_path]")
        print()
        print("Example:")
        print("  python save_sample_list.py temp_eval/raw_outputs.jsonl")
        print("  python save_sample_list.py temp_eval/raw_outputs.jsonl evaluated_samples.json")
        sys.exit(1)
    
    jsonl_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    save_sample_list(jsonl_path, output_path)


if __name__ == "__main__":
    main()
