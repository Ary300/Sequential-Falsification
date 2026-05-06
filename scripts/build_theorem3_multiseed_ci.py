#!/usr/bin/env python3
"""Aggregate theorem-3 summary JSONs across seeds and report a bootstrap CI."""

from __future__ import annotations

import argparse
import glob
import json
import random
import re
from pathlib import Path
from statistics import mean, median


HEADLINE_KEYS = (
    "conflict_minus_no_conflict_ece_delta",
    "mean_conflict_ece_delta",
    "mean_no_conflict_ece_delta",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--glob",
        required=True,
        help="Glob for theorem3_summary.json files, for example 'results/e1_llama8b_grpo_s*/**/theorem3_summary.json'.",
    )
    parser.add_argument(
        "--seed-regex",
        default=r"(?:^|[/_])s(?P<seed>\d+)(?:[/_]|$)",
        help="Regex used to extract the seed from the matched path.",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Human-readable label for the run family.",
    )
    parser.add_argument(
        "--num-bootstrap",
        type=int,
        default=10000,
        help="Number of bootstrap resamples over seeds.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for bootstrap resampling.",
    )
    parser.add_argument(
        "--output-prefix",
        required=True,
        help="Output prefix; writes both .json and .md files.",
    )
    return parser.parse_args()


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    idx = max(0, min(len(sorted_values) - 1, int(q * (len(sorted_values) - 1))))
    return sorted_values[idx]


def bootstrap_ci(values: list[float], *, num_bootstrap: int, seed: int) -> dict[str, float]:
    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(num_bootstrap):
        sample = [values[rng.randrange(len(values))] for _ in values]
        draws.append(mean(sample))
    draws.sort()
    return {
        "ci95_low": round(percentile(draws, 0.025), 4),
        "ci95_high": round(percentile(draws, 0.975), 4),
    }


def extract_seed(path: Path, pattern: re.Pattern[str]) -> int | None:
    match = pattern.search(str(path))
    if not match:
        return None
    seed_text = match.groupdict().get("seed")
    if seed_text is None:
        return None
    return int(seed_text)


def load_rows(glob_pattern: str, seed_regex: str) -> list[dict]:
    seed_pattern = re.compile(seed_regex)
    rows: list[dict] = []
    for raw_path in sorted(glob.glob(glob_pattern, recursive=True)):
        path = Path(raw_path)
        try:
            payload = json.loads(path.read_text())
        except Exception:
            continue
        headline = payload.get("headline") or {}
        seed = extract_seed(path, seed_pattern)
        rows.append(
            {
                "path": str(path),
                "seed": seed,
                "coverage_rows": (payload.get("coverage") or {}).get("num_rows"),
                **{key: headline.get(key) for key in HEADLINE_KEYS},
            }
        )
    return [row for row in rows if row["seed"] is not None]


def build_summary(rows: list[dict], *, label: str, num_bootstrap: int, seed: int) -> dict:
    metrics: dict[str, dict] = {}
    for key in HEADLINE_KEYS:
        values = [float(row[key]) for row in rows if row.get(key) is not None]
        if not values:
            continue
        metrics[key] = {
            "mean": round(mean(values), 4),
            "median": round(median(values), 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "bootstrap": bootstrap_ci(values, num_bootstrap=num_bootstrap, seed=seed),
        }
    return {
        "label": label,
        "num_complete_seed_runs": len(rows),
        "seeds": sorted(int(row["seed"]) for row in rows),
        "rows": rows,
        "metrics": metrics,
    }


def render_markdown(summary: dict) -> str:
    def fmt(value: float | None) -> str:
        if value is None:
            return "-"
        return f"{float(value):+.4f}"

    lines = [
        f"# {summary['label']} Multiseed Theorem-3 CI",
        "",
        f"- complete seed runs: `{summary['num_complete_seed_runs']}`",
        f"- seeds: `{summary['seeds']}`",
        "",
        "## Headline",
        "",
    ]
    metric_names = {
        "conflict_minus_no_conflict_ece_delta": "Conflict minus no-conflict ECE delta",
        "mean_conflict_ece_delta": "Mean conflict ECE delta",
        "mean_no_conflict_ece_delta": "Mean no-conflict ECE delta",
    }
    for key in HEADLINE_KEYS:
        metric = summary["metrics"].get(key)
        if not metric:
            continue
        ci = metric["bootstrap"]
        lines.extend(
            [
                f"- {metric_names[key]}: mean `{metric['mean']:+.4f}`, 95% bootstrap CI `[{ci['ci95_low']:+.4f}, {ci['ci95_high']:+.4f}]`",
                f"  median `{metric['median']:+.4f}`, range `[{metric['min']:+.4f}, {metric['max']:+.4f}]`",
            ]
        )
    lines.extend(
        [
            "",
            "## Per-Seed Rows",
            "",
            "| Seed | Conflict minus no-conflict | Conflict | No-conflict | Rows |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in sorted(summary["rows"], key=lambda item: int(item["seed"])):
        lines.append(
            f"| {row['seed']} | {fmt(row['conflict_minus_no_conflict_ece_delta'])} | "
            f"{fmt(row['mean_conflict_ece_delta'])} | {fmt(row['mean_no_conflict_ece_delta'])} | "
            f"{int(row['coverage_rows']) if row['coverage_rows'] is not None else '-'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    rows = load_rows(args.glob, args.seed_regex)
    summary = build_summary(rows, label=args.label, num_bootstrap=args.num_bootstrap, seed=args.seed)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    output_prefix.with_suffix(".md").write_text(render_markdown(summary) + "\n")
    print(json.dumps({"output_json": str(output_prefix.with_suffix('.json')), "output_md": str(output_prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
