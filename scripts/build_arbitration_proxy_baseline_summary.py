#!/usr/bin/env python3
"""Summarize Bayes proxy against named comparator baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMPARATORS = [
    "cocoa",
    "adacad",
    "cad",
    "astute_rag",
    "crag",
    "self_rag",
    "heuristic_adaptive",
    "simulated_model",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build named-comparator summary for arbitration reports.")
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def _pretty(policy: str) -> str:
    mapping = {
        "bayes_proxy": "Bayes proxy",
        "cocoa": "CoCoA",
        "adacad": "AdaCAD",
        "cad": "CAD",
        "astute_rag": "Astute RAG",
        "crag": "CRAG",
        "self_rag": "Self-RAG",
        "heuristic_adaptive": "Heuristic adaptive",
        "simulated_model": "Simulated model",
    }
    return mapping.get(policy, policy.replace("_", " ").title())


def build_summary(report: dict) -> dict:
    overall_rows = list((report.get("regret") or {}).get("overall", []))
    by_policy = {row["policy"]: row for row in overall_rows}
    bayes = by_policy["bayes_proxy"]
    comparator_rows = []
    for name in COMPARATORS:
        row = by_policy.get(name)
        if row is None:
            continue
        comparator_rows.append(
            {
                "policy": name,
                "pretty_policy": _pretty(name),
                "mean_regret": round(float(row["mean_regret"]), 4),
                "num_series": int(row["num_series"]),
                "bayes_advantage": round(float(row["mean_regret"]) - float(bayes["mean_regret"]), 4),
            }
        )

    named_rows = [row for row in comparator_rows if row["policy"] != "simulated_model"]
    strongest_named = min(named_rows, key=lambda row: row["mean_regret"]) if named_rows else None

    return {
        "bayes_proxy": {
            "mean_regret": round(float(bayes["mean_regret"]), 4),
            "num_series": int(bayes["num_series"]),
        },
        "headline": {
            "strongest_named_comparator": None if strongest_named is None else strongest_named["policy"],
            "strongest_named_comparator_regret": None if strongest_named is None else strongest_named["mean_regret"],
            "bayes_advantage_vs_strongest_named": None
            if strongest_named is None
            else strongest_named["bayes_advantage"],
        },
        "comparators": comparator_rows,
    }


def build_markdown(summary: dict) -> str:
    headline = summary["headline"]
    lines = [
        "# Arbitration Proxy Baseline Summary",
        "",
        f"- Bayes proxy mean regret: `{summary['bayes_proxy']['mean_regret']}`",
        f"- Strongest named comparator: `{_pretty(headline['strongest_named_comparator']) if headline['strongest_named_comparator'] else 'n/a'}`",
        f"- Strongest named comparator regret: `{headline['strongest_named_comparator_regret']}`",
        f"- Bayes advantage vs strongest named comparator: `{headline['bayes_advantage_vs_strongest_named']}`",
        "",
        "## Comparator Table",
        "",
        "| Policy | Mean regret | Bayes advantage | Series |",
        "|---|---:|---:|---:|",
    ]
    for row in summary["comparators"]:
        lines.append(
            f"| {row['pretty_policy']} | {row['mean_regret']:.4f} | {row['bayes_advantage']:.4f} | {row['num_series']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = json.loads((ROOT / args.report_json).read_text(encoding="utf-8"))
    summary = build_summary(report)
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
