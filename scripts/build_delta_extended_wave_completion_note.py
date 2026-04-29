#!/usr/bin/env python3
"""Render a compact completion note for the Delta extended arbitration wave."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Markdown note from the Delta extended-wave completion summary.")
    parser.add_argument(
        "--input",
        default="docs/generated/delta_extended_wave_completion_summary.json",
        help="Path to the compact completion summary JSON.",
    )
    parser.add_argument(
        "--output-prefix",
        default="docs/generated/delta_extended_wave_completion_summary",
        help="Output prefix without extension.",
    )
    return parser.parse_args()


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    waves = summary["waves"]
    lines = [
        "# Delta Extended Wave Completion Summary",
        "",
        "## Headline",
        "",
        f"- Completed experiment variants: `{summary['num_results']}`",
        f"- Best gain slice: `{summary['best_gain']['name']}` with Bayes-vs-heuristic gain `{summary['best_gain']['gain']:.4f}`",
        f"- Smallest gain slice: `{summary['worst_gain']['name']}` with Bayes-vs-heuristic gain `{summary['worst_gain']['gain']:.4f}`",
        "",
        "## Wave Summary",
        "",
        "| Wave | Variants | Total rows | Mean gain | Mean Bayes regret | Mean heuristic regret |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for wave_name in ["model_wave", "t3_calibration_wave", "api_slice"]:
        if wave_name not in waves:
            continue
        wave = waves[wave_name]
        lines.append(
            f"| {wave_name} | {wave['count']} | {wave['total_rows']} | "
            f"{wave['mean_gain']:.4f} | {wave['mean_bayes_regret']:.4f} | {wave['mean_heuristic_regret']:.4f} |"
        )

    lines.extend(["", "## Variants", ""])
    for row in payload["rows"]:
        lines.append(
            f"- `{row['name']}`: rows `{row['num_rows']}`, "
            f"Bayes `{row['bayes_proxy_mean_regret']:.4f}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']:.4f}`, "
            f"gain `{row['gain']:.4f}`"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_prefix = Path(args.output_prefix)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_prefix": str(output_prefix)}, indent=2))


if __name__ == "__main__":
    main()
