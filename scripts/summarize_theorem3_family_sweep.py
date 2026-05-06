#!/usr/bin/env python3
"""Summarize theorem-3 family sweeps across multiple result JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate theorem-3 result JSONs into a family-sweep summary.")
    parser.add_argument("--results-file", action="append", required=True, help="Path to a theorem3 *_final.json file.")
    parser.add_argument("--label", default="family_sweep", help="Summary label.")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def load_rows(path: Path) -> dict:
    payload = json.loads(path.read_text())
    return {
        "path": str(path),
        "model": payload["model"],
        "source_job": payload.get("source_job"),
        "rows": payload.get("rows", []),
        "headline": payload.get("headline", {}),
    }


def build_summary(loaded: list[dict], label: str) -> dict:
    rows = []
    for item in loaded:
        for row in item["rows"]:
            rows.append(
                {
                    "model": item["model"],
                    "source_job": item.get("source_job"),
                    "benchmark": row["benchmark"],
                    "split": row["split"],
                    "gap_cot_0": row["gap_cot_0"],
                    "gap_cot_128": row["gap_cot_128"],
                    "gap_cot_1024": row["gap_cot_1024"],
                    "gap_delta_0_128": row["gap_delta_0_128"],
                    "gap_delta_128_1024": row["gap_delta_128_1024"],
                }
            )
    return {"label": label, "models": loaded, "rows": rows}


def write_markdown(summary: dict, path: Path) -> None:
    lines = [
        f"# Theorem 3 Family Sweep: {summary['label']}",
        "",
        "| Model | Benchmark | Split | `cot=0` | `cot=128` | `cot=1024` | `0->128` | `128->1024` |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {row['model']} | {row['benchmark']} | {row['split']} | "
            f"{row['gap_cot_0']:.4f} | {row['gap_cot_128']:.4f} | {row['gap_cot_1024']:.4f} | "
            f"{row['gap_delta_0_128']:.4f} | {row['gap_delta_128_1024']:.4f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    loaded = [load_rows(Path(item)) for item in args.results_file]
    summary = build_summary(loaded, args.label)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_markdown(summary, output_md)

    print(
        json.dumps(
            {
                "label": args.label,
                "output_json": str(output_json),
                "output_md": str(output_md),
                "num_models": len(loaded),
                "num_rows": len(summary["rows"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
