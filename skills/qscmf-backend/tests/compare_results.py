#!/usr/bin/env python3
"""
Compare current test results with baseline.

Usage:
    python compare_results.py [--create-baseline]

Options:
    --create-baseline    Create new baseline from current results
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path


def get_current_metrics(skill_root: Path) -> dict:
    """Calculate current skill metrics."""
    skill_file = skill_root / "SKILL.md"
    skill_content = skill_file.read_text(encoding='utf-8') if skill_file.exists() else ""

    rules_dir = skill_root / "rules"
    rule_files = [f for f in rules_dir.rglob("*.md") if not f.name.startswith('_')]

    return {
        'skill_md_lines': skill_content.count('\n') + 1,
        'rule_file_count': len(rule_files),
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    }


def load_baseline(results_dir: Path) -> dict:
    """Load baseline results."""
    baseline_file = results_dir / "baseline.json"
    if baseline_file.exists():
        with open(baseline_file, 'r') as f:
            return json.load(f)
    return None


def save_baseline(results_dir: Path, metrics: dict):
    """Save baseline results."""
    results_dir.mkdir(parents=True, exist_ok=True)
    baseline_file = results_dir / "baseline.json"
    with open(baseline_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Baseline saved to {baseline_file}")


def compare_with_baseline(current: dict, baseline: dict) -> dict:
    """Compare current metrics with baseline."""
    comparison = {
        'skill_md_lines': {
            'baseline': baseline.get('skill_md_lines', 'N/A'),
            'current': current['skill_md_lines'],
            'delta': current['skill_md_lines'] - baseline.get('skill_md_lines', current['skill_md_lines']),
            'status': '✅' if current['skill_md_lines'] <= baseline.get('skill_md_lines', float('inf')) * 1.1 else '❌'
        },
        'rule_file_count': {
            'baseline': baseline.get('rule_file_count', 'N/A'),
            'current': current['rule_file_count'],
            'delta': current['rule_file_count'] - baseline.get('rule_file_count', current['rule_file_count']),
            'status': '✅' if current['rule_file_count'] >= baseline.get('rule_file_count', 0) else '❌'
        }
    }
    return comparison


def generate_report(comparison: dict) -> str:
    """Generate comparison report."""
    report = []
    report.append("# QSCMF Skill Test Report\n")
    report.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("\n## Summary\n")
    report.append("| Metric | Baseline | Current | Delta | Status |")
    report.append("|--------|----------|---------|-------|--------|")

    for metric, data in comparison.items():
        delta_str = f"+{data['delta']}" if data['delta'] > 0 else str(data['delta'])
        report.append(f"| {metric} | {data['baseline']} | {data['current']} | {delta_str} | {data['status']} |")

    report.append("\n## Regression Check\n")

    all_passed = all(d['status'] == '✅' for d in comparison.values())

    if all_passed:
        report.append("- ✅ All metrics within acceptable range")
        report.append("\n## Recommendations\n")
        report.append("No issues detected. Safe to merge.")
    else:
        report.append("- ❌ Some metrics outside acceptable range")
        report.append("\n## Recommendations\n")
        report.append("Review changes before merging.")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Compare skill test results')
    parser.add_argument('--create-baseline', action='store_true',
                       help='Create new baseline from current results')
    args = parser.parse_args()

    # Paths
    script_dir = Path(__file__).parent
    skill_root = script_dir.parent
    results_dir = skill_root / "tests" / "results"

    # Get current metrics
    current = get_current_metrics(skill_root)

    if args.create_baseline:
        save_baseline(results_dir, current)
        return 0

    # Load baseline
    baseline = load_baseline(results_dir)

    if baseline is None:
        print("⚠️  No baseline found. Creating initial baseline...")
        save_baseline(results_dir, current)
        print("\nRun again to compare with baseline.")
        return 0

    # Compare
    comparison = compare_with_baseline(current, baseline)
    report = generate_report(comparison)

    # Print report
    print(report)

    # Save report
    report_file = results_dir / "comparison_report.md"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to {report_file}")

    # Save current results
    current_file = results_dir / "current.json"
    with open(current_file, 'w') as f:
        json.dump(current, f, indent=2)

    # Return exit code
    all_passed = all(d['status'] == '✅' for d in comparison.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
