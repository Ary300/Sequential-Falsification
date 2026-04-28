#!/usr/bin/env python3
"""Build an explicit 5x5 spotlight-grid coverage note."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = (
    ROOT
    / "results/arbitration_spotlight_t12_benchmark_v2/arbitration_spotlight_t12_matrix_benchmark_results.json"
)
OUT_PREFIX = ROOT / "docs/generated/spotlight_5x5_grid_note"


def _load_rows() -> list[dict[str, Any]]:
    payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for experiment in payload["experiments"]:
        rows.extend(experiment["rows"])
    return rows


def _mean_policy(rows: list[dict[str, Any]], policy: str) -> float:
    return mean(float(row["regret_by_policy"][policy]) for row in rows)


def build_summary() -> dict[str, Any]:
    rows = _load_rows()
    models = sorted(set(str(row["model"]) for row in rows))
    benchmarks = sorted(set(str(row["benchmark"]) for row in rows))
    coverage = []
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_model[str(row["model"])].append(row)
    for model in models:
        model_rows = by_model[model]
        coverage.append(
            {
                "model": model,
                "num_rows": len(model_rows),
                "num_benchmarks": len(set(str(r["benchmark"]) for r in model_rows)),
                "bayes_proxy_mean_regret": round(_mean_policy(model_rows, "bayes_proxy"), 4),
                "heuristic_adaptive_mean_regret": round(_mean_policy(model_rows, "heuristic_adaptive"), 4),
                "cocoa_mean_regret": round(_mean_policy(model_rows, "cocoa"), 4),
                "adacad_mean_regret": round(_mean_policy(model_rows, "adacad"), 4),
                "bayes_vs_heuristic_gain": round(
                    _mean_policy(model_rows, "heuristic_adaptive") - _mean_policy(model_rows, "bayes_proxy"), 4
                ),
            }
        )
    cells = []
    for model in models:
        for benchmark in benchmarks:
            subset = [row for row in rows if row["model"] == model and row["benchmark"] == benchmark]
            cells.append(
                {
                    "model": model,
                    "benchmark": benchmark,
                    "num_rows": len(subset),
                    "bayes_proxy_mean_regret": round(_mean_policy(subset, "bayes_proxy"), 4),
                    "heuristic_adaptive_mean_regret": round(_mean_policy(subset, "heuristic_adaptive"), 4),
                    "bayes_vs_heuristic_gain": round(
                        _mean_policy(subset, "heuristic_adaptive") - _mean_policy(subset, "bayes_proxy"), 4
                    ),
                }
            )
    return {
        "num_models": len(models),
        "num_benchmarks": len(benchmarks),
        "num_rows": len(rows),
        "models": models,
        "benchmarks": benchmarks,
        "coverage_by_model": coverage,
        "cells": cells,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Spotlight 5x5 Grid Note",
        "",
        "## Headline",
        "",
        f"- The completed spotlight matrix already covers `{summary['num_models']}` models x `{summary['num_benchmarks']}` benchmarks = `{summary['num_models'] * summary['num_benchmarks']}` model-benchmark cells.",
        f"- Total parsed rows in the finished matrix: `{summary['num_rows']}`.",
        "",
        "## Model Coverage",
        "",
    ]
    for row in summary["coverage_by_model"]:
        lines.append(
            f"- `{row['model']}`: `{row['num_benchmarks']}` benchmarks, Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, `CoCoA` `{row['cocoa_mean_regret']}`, "
            f"`AdaCAD` `{row['adacad_mean_regret']}`, Bayes gain `{row['bayes_vs_heuristic_gain']}`."
        )
    lines.extend(["", "## Cell Table", "", "| Model | Benchmark | Rows | Bayes | Heuristic | Bayes gain |", "|---|---|---:|---:|---:|---:|"])
    for row in summary["cells"]:
        lines.append(
            f"| {row['model']} | {row['benchmark']} | {row['num_rows']} | {row['bayes_proxy_mean_regret']:.4f} | "
            f"{row['heuristic_adaptive_mean_regret']:.4f} | {row['bayes_vs_heuristic_gain']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    OUT_PREFIX.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    OUT_PREFIX.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(OUT_PREFIX.with_suffix('.json')), "md": str(OUT_PREFIX.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
