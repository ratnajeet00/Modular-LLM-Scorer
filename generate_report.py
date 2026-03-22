#!/usr/bin/env python3
"""
Generate human-readable markdown report from benchmark results JSON.

Takes a benchmark result JSON file and generates a formatted markdown report
suitable for publication and sharing.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_markdown_report(result_json_path: str | Path) -> str:
    """Generate markdown report from result JSON."""
    result_json_path = Path(result_json_path)
    
    if not result_json_path.exists():
        raise FileNotFoundError(f"Result file not found: {result_json_path}")
    
    with open(result_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Start building markdown
    md = []
    
    md.append(f"# Benchmark Report: {results.get('model', 'Unknown Model')}\n")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Executive Summary
    md.append("## Executive Summary\n")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Mode | {results.get('mode', 'N/A')} |")
    md.append(f"| Overall Accuracy | {results.get('accuracy', 0.0):.2%} |")
    md.append(f"| Final Score (Weighted) | {results.get('final_score', 0.0):.6f} |")
    md.append(f"| Total Questions | {results.get('total_questions', 0)} |")
    md.append(f"| Correct Answers | {results.get('correct_count', 0)} |")
    md.append(f"| Failure Rate | {results.get('failure_rate', 0.0):.2%} |")
    md.append(f"| Total Cost | ${results.get('cost', 0.0):.2f} |")
    md.append("")
    
    # Per-Domain Performance
    md.append("## Per-Domain Performance\n")
    md.append(f"| Domain | Accuracy | Samples | Weight | Weighted Score |")
    md.append(f"|--------|----------|---------|--------|-----------------|")
    
    summary_table = results.get("summary_table", {})
    for domain_stats in summary_table.get("domain_breakdown", []):
        domain = domain_stats.get("domain", "N/A")
        accuracy = domain_stats.get("accuracy", 0.0)
        count = domain_stats.get("sample_count", 0)
        weight = domain_stats.get("weight", 0.0)
        weighted = domain_stats.get("weighted_score", 0.0)
        md.append(f"| {domain} | {accuracy:.2%} | {count} | {weight:.0%} | {weighted:.6f} |")
    md.append("")
    
    # Confidence Intervals
    conf_int = results.get("confidence_intervals_95", {})
    if conf_int:
        md.append("## Confidence Intervals (95%)\n")
        overall_ci = conf_int.get("overall_accuracy")
        if overall_ci:
            md.append(f"**Overall Accuracy CI:** [{overall_ci['lower']:.4f}, {overall_ci['upper']:.4f}]\n")
        
        per_domain_ci = conf_int.get("per_domain", {})
        if per_domain_ci:
            md.append("| Domain | Lower Bound | Upper Bound |")
            md.append("|--------|-------------|-------------|")
            for domain, ci_data in sorted(per_domain_ci.items()):
                lower = ci_data.get("lower", 0.0)
                upper = ci_data.get("upper", 0.0)
                md.append(f"| {domain} | {lower:.4f} | {upper:.4f} |")
            md.append("")
    
    # Difficulty Breakdown
    difficulty_stats = results.get("difficulty_breakdown", {})
    if difficulty_stats:
        md.append("## Difficulty Breakdown\n")
        md.append(f"| Tier | Count | Correct | Accuracy |")
        md.append(f"|------|-------|---------|----------|")
        
        for tier in ["easy", "medium", "hard"]:
            if tier in difficulty_stats:
                stats = difficulty_stats[tier]
                count = stats.get("count", 0)
                correct = stats.get("correct", 0)
                accuracy = stats.get("accuracy", 0.0)
                md.append(f"| {tier} | {count} | {correct} | {accuracy:.2%} |")
        md.append("")
    
    # Per-Dataset Performance
    per_dataset = results.get("per_dataset", {})
    if per_dataset:
        md.append("## Per-Dataset Performance\n")
        md.append(f"| Dataset | Accuracy |")
        md.append(f"|---------|----------|")
        
        for dataset, accuracy in sorted(per_dataset.items()):
            md.append(f"| {dataset} | {accuracy:.2%} |")
        md.append("")
    
    # Error Analysis
    md.append("## Error Analysis\n")
    md.append(f"- **Total Errors:** {results.get('error_count', 0)}")
    md.append(f"- **Call Errors (failed API):** {results.get('call_error_count', 0)}")
    md.append(f"- **Empty Predictions:** {results.get('empty_predictions', 0)}")
    
    failure_breakdown = results.get("failure_breakdown", {})
    if failure_breakdown:
        md.append(f"\n**Failure Breakdown:**")
        md.append(f"- Empty predictions: {failure_breakdown.get('empty_predictions', 0)}")
        md.append(f"- Execution errors: {failure_breakdown.get('execution_errors', 0)}")
        md.append(f"- Format errors: {failure_breakdown.get('format_errors', 0)}")
        md.append(f"- Other errors: {failure_breakdown.get('other_errors', 0)}")
        md.append("")
    
    error_examples = results.get("error_examples", [])
    if error_examples:
        md.append(f"\n**Example Errors:**")
        for i, error in enumerate(error_examples[:3], 1):
            error_short = error[:80] + ("..." if len(error) > 80 else "")
            md.append(f"- {error_short}")
        md.append("")
    
    # Per-Domain Error Breakdown
    per_domain_errors = results.get("per_domain_errors", {})
    if per_domain_errors:
        md.append("## Per-Domain Error Breakdown\n")
        for domain in sorted(per_domain_errors.keys()):
            errors = per_domain_errors[domain]
            md.append(f"### {domain.capitalize()}\n")
            for error_type, count in list(errors.items())[:5]:
                md.append(f"- {error_type}: {count}")
            md.append("")
    
    # Performance Timing
    timing = results.get("per_domain_timing", {})
    if timing:
        md.append("## Performance Timing\n")
        md.append(f"| Domain | Mean (s) | Min (s) | Max (s) | Total (s) | Samples |")
        md.append(f"|--------|----------|---------|---------|-----------|---------|")
        
        for domain, times in sorted(timing.items()):
            mean_s = times.get("mean_seconds", 0.0)
            min_s = times.get("min_seconds", 0.0)
            max_s = times.get("max_seconds", 0.0)
            total_s = times.get("total_seconds", 0.0)
            count = times.get("sample_count", 0)
            md.append(f"| {domain} | {mean_s:.3f} | {min_s:.3f} | {max_s:.3f} | {total_s:.3f} | {count} |")
        md.append("")
    
    # Reproducibility Info
    md.append("## Reproducibility\n")
    
    git_hash = results.get("git_commit_hash")
    if git_hash:
        md.append(f"- **Git Commit:** `{git_hash}`")
    
    selected_datasets = results.get("selected_datasets_by_domain", {})
    if selected_datasets:
        md.append(f"- **Selected Datasets:**")
        for domain, datasets in sorted(selected_datasets.items()):
            md.append(f"  - {domain}: {', '.join(datasets)}")
    md.append("")
    
    return "\n".join(md)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <result.json> [output.md]")
        print()
        print("Example:")
        print("  python generate_report.py bech\\ mark/model_20260322_212321.json")
        sys.exit(1)
    
    result_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else Path(result_path).stem + ".md"
    
    try:
        markdown = generate_markdown_report(result_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print(f"✓ Markdown report generated: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
