#!/usr/bin/env python3
"""Build paper-facing eta-tempered decoding note artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 eta-tempered decoding note.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-prefix", default="docs/generated/theorem3_eta_tempered_method_result")
    return parser.parse_args()


def build_markdown(summary: dict) -> str:
    meta = summary["metadata"]
    selection = summary["selection"]
    calibration = summary["calibration"]
    evaluation = summary["evaluation"]
    lines = [
        "# Theorem 3 Eta-Tempered Decoding Result",
        "",
        "This is the method result implied by the theorem-3 rewrite: we rescore the saved long-CoT trace against a closed-book prior and choose `eta` on a held-out calibration split.",
        "",
        "## Headline",
        "",
        f"- Model: `{meta['model']}`",
        f"- Benchmark: `{meta['benchmark']}`",
        f"- Condition: `{meta['condition']}`",
        f"- CoT length: `{meta['cot_length']}`",
        f"- Selected eta: `{selection['selected_eta']}`",
        f"- Oracle eta on calibration split: `{selection['oracle_eta']}`",
        f"- Calibration baseline Brier at eta=1: `{calibration['baseline_metrics']['brier']}`",
        f"- Calibration selected Brier: `{calibration['selected_metrics']['brier']}`",
        f"- Eval baseline accuracy / confidence / gap at eta=1: `{evaluation['baseline']['accuracy']}` / `{evaluation['baseline']['mean_confidence']}` / `{evaluation['baseline']['overconfidence_gap']}`",
        f"- Eval tempered accuracy / confidence / gap: `{evaluation['selected']['accuracy']}` / `{evaluation['selected']['mean_confidence']}` / `{evaluation['selected']['overconfidence_gap']}`",
        "",
        "## Eta Sweep",
        "",
        "| Eta | Count | Accuracy | ECE | Brier | Mean confidence |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in calibration["per_eta"]:
        lines.append(
            f"| {row['eta']:.2f} | {row['count']} | {row['accuracy']:.4f} | {row['ece']:.4f} | {row['brier']:.4f} | {row['mean_confidence']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = json.loads(Path(args.source).read_text(encoding="utf-8"))
    output_prefix = ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "json": str(output_prefix.with_suffix(".json")),
                "md": str(output_prefix.with_suffix(".md")),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
