#!/usr/bin/env python3
"""
Error categorization and analysis script.

Reads raw JSONL output log and groups failures by type per domain.
Provides statistical breakdown of error patterns for debugging.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class ErrorStats:
    domain: str
    error_type: str
    count: int
    percentage: float
    sample_ids: list[str]


def categorize_error(error_msg: str | None) -> str:
    """Categorize error types for better analysis."""
    if not error_msg:
        return "no_error"
    
    error_lower = error_msg.lower()
    
    if "execution-error" in error_lower or "test-failed" in error_lower:
        return "execution_error"
    elif "invalid-output-format" in error_lower or "format" in error_lower:
        return "invalid_format"
    elif "timeout" in error_lower or "timed out" in error_lower:
        return "timeout"
    elif "empty" in error_lower:
        return "empty_response"
    elif any(x in error_lower for x in ["refused", "cannot assist", "cannot help", "can't assist"]):
        return "model_refusal"
    elif "typeerror" in error_lower or "indexerror" in error_lower or "keyerror" in error_lower:
        return "type_error"
    else:
        return "other_error"


def analyze_jsonl(jsonl_path: str | Path) -> dict:
    """Analyze JSONL raw output log and return error statistics."""
    jsonl_path = Path(jsonl_path)
    
    if not jsonl_path.exists():
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return {}
    
    # Stats structures
    errors_by_domain: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    error_counts_by_domain: dict[str, Counter] = defaultdict(Counter)
    total_by_domain: dict[str, int] = Counter()
    
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
                
                domain = record.get("domain", "unknown")
                error = record.get("error")
                sample_id = record.get("sample_id", f"unknown_{line_num}")
                
                total_by_domain[domain] += 1
                
                if error:
                    error_category = categorize_error(error)
                    error_counts_by_domain[domain][error_category] += 1
                    errors_by_domain[domain][error_category].append({
                        "sample_id": sample_id,
                        "error_msg": error,
                    })
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return {}
    
    # Build report
    report = {
        "file": str(jsonl_path),
        "total_records": sum(total_by_domain.values()),
        "by_domain": {},
    }
    
    for domain in sorted(total_by_domain.keys()):
        domain_total = total_by_domain[domain]
        domain_errors = error_counts_by_domain.get(domain, Counter())
        
        error_breakdown = []
        for error_type, count in domain_errors.most_common():
            percentage = (count / domain_total * 100) if domain_total > 0 else 0
            sample_ids = [e["sample_id"] for e in errors_by_domain[domain][error_type]][:5]  # First 5 samples
            error_messages = [e["error_msg"] for e in errors_by_domain[domain][error_type]][:2]  # First 2 messages
            
            error_breakdown.append({
                "type": error_type,
                "count": count,
                "percentage": round(percentage, 2),
                "sample_count": len(errors_by_domain[domain][error_type]),
                "example_samples": sample_ids,
                "example_messages": error_messages,
            })
        
        total_errors = sum(domain_errors.values())
        report["by_domain"][domain] = {
            "total_samples": domain_total,
            "total_errors": total_errors,
            "success_count": domain_total - total_errors,
            "success_rate": round((domain_total - total_errors) / domain_total * 100, 2) if domain_total > 0 else 0,
            "error_breakdown": error_breakdown,
        }
    
    return report


def print_report(report: dict) -> None:
    """Pretty-print error analysis report."""
    if not report:
        print("No data to report.")
        return
    
    print(f"\n{'='*80}")
    print(f"Error Analysis Report")
    print(f"{'='*80}")
    print(f"File: {report.get('file')}")
    print(f"Total Records: {report.get('total_records')}")
    print()
    
    for domain in sorted(report.get("by_domain", {}).keys()):
        stats = report["by_domain"][domain]
        print(f"\n{'='*60}")
        print(f"Domain: {domain}")
        print(f"{'='*60}")
        print(f"  Total Samples:   {stats['total_samples']}")
        print(f"  Success Count:   {stats['success_count']}")
        print(f"  Success Rate:    {stats['success_rate']}%")
        print(f"  Total Errors:    {stats['total_errors']}")
        print()
        print(f"  Error Breakdown:")
        
        for error in stats["error_breakdown"]:
            print(f"    - {error['type']:20s} | Count: {error['count']:4d} ({error['percentage']:5.1f}%) | Samples: {error['sample_count']}")
            
            # Show example messages if available
            if error["example_messages"]:
                first_msg = error["example_messages"][0]
                if len(first_msg) > 60:
                    first_msg = first_msg[:57] + "..."
                print(f"      Example: {first_msg}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python analyze_errors.py <path_to_raw_outputs.jsonl>")
        print()
        print("Example:")
        print("  python analyze_errors.py temp_eval/raw_outputs.jsonl")
        sys.exit(1)
    
    jsonl_path = sys.argv[1]
    
    report = analyze_jsonl(jsonl_path)
    print_report(report)
    
    # Optionally save report to JSON
    if len(sys.argv) > 2 and sys.argv[2] == "--save":
        output_path = Path(jsonl_path).stem + "_error_report.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n✓ Report saved to {output_path}")


if __name__ == "__main__":
    main()
