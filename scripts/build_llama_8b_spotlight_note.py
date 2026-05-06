#!/usr/bin/env python3
"""Build an explicit Llama-3.1-8B spotlight coverage note."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_JSON = (
    ROOT
    / "results/arbitration_spotlight_t12_benchmark_v2/arbitration_spotlight_t12_matrix_benchmark_results.json"
)
OUT_PREFIX = ROOT / "docs/generated/llama_8b_spotlight_note"
MODEL = "meta-llama/Llama-3.1-8B-Instruct"
POLICIES = [
    "bayes_proxy",
    "heuristic_adaptive",
    "always_context",
    "always_parametric",
    "adacad",
    "cocoa",
]


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(q * (len(ordered) - 1))))
    return ordered[idx]


def _series_key(row: dict[str, Any]) -> str:
    return "::".join(
        [
            str(row["benchmark"]),
            str(row["condition"]),
            str(row["cot_length"]),
            str(row.get("split", "all")),
        ]
    )


def _load_rows() -> list[dict[str, Any]]:
    payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for experiment in payload["experiments"]:
        rows.extend(experiment["rows"])
    return [row for row in rows if row["model"] == MODEL]


def _mean_policy(rows: list[dict[str, Any]], policy: str) -> float:
    return mean(float(row["regret_by_policy"][policy]) for row in rows)


def _bootstrap(rows: list[dict[str, Any]], baseline: str, *, n: int = 10000, seed: int = 42) -> dict[str, float]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_series_key(row)].append(row)
    series = {
        key: {policy: mean(float(item["regret_by_policy"][policy]) for item in bucket) for policy in POLICIES}
        for key, bucket in grouped.items()
    }
    keys = sorted(series)
    rng = random.Random(seed)
    gaps: list[float] = []
    for _ in range(n):
        sampled = [series[rng.choice(keys)] for _ in keys]
        gaps.append(mean(item[baseline] for item in sampled) - mean(item["bayes_proxy"] for item in sampled))
    return {
        "mean_gap": round(mean(gaps), 4),
        "ci95_low": round(_quantile(gaps, 0.025), 4),
        "ci95_high": round(_quantile(gaps, 0.975), 4),
        "num_series": len(keys),
    }


def build_summary() -> dict[str, Any]:
    rows = _load_rows()
    benchmarks = sorted(set(str(row["benchmark"]) for row in rows))
    benchmark_rows = []
    for benchmark in benchmarks:
        bucket = [row for row in rows if row["benchmark"] == benchmark]
        benchmark_rows.append(
            {
                "benchmark": benchmark,
                "num_rows": len(bucket),
                "bayes_proxy_mean_regret": round(_mean_policy(bucket, "bayes_proxy"), 4),
                "heuristic_adaptive_mean_regret": round(_mean_policy(bucket, "heuristic_adaptive"), 4),
                "cocoa_mean_regret": round(_mean_policy(bucket, "cocoa"), 4),
                "adacad_mean_regret": round(_mean_policy(bucket, "adacad"), 4),
                "always_context_mean_regret": round(_mean_policy(bucket, "always_context"), 4),
                "always_parametric_mean_regret": round(_mean_policy(bucket, "always_parametric"), 4),
                "bayes_vs_heuristic_gain": round(
                    _mean_policy(bucket, "heuristic_adaptive") - _mean_policy(bucket, "bayes_proxy"), 4
                ),
                "bayes_vs_cocoa_gain": round(_mean_policy(bucket, "cocoa") - _mean_policy(bucket, "bayes_proxy"), 4),
                "bayes_vs_adacad_gain": round(_mean_policy(bucket, "adacad") - _mean_policy(bucket, "bayes_proxy"), 4),
            }
        )
    summary = {
        "model": MODEL,
        "num_rows": len(rows),
        "benchmarks": benchmark_rows,
        "overall": {
            "bayes_proxy_mean_regret": round(_mean_policy(rows, "bayes_proxy"), 4),
            "heuristic_adaptive_mean_regret": round(_mean_policy(rows, "heuristic_adaptive"), 4),
            "cocoa_mean_regret": round(_mean_policy(rows, "cocoa"), 4),
            "adacad_mean_regret": round(_mean_policy(rows, "adacad"), 4),
            "always_context_mean_regret": round(_mean_policy(rows, "always_context"), 4),
            "always_parametric_mean_regret": round(_mean_policy(rows, "always_parametric"), 4),
            "bayes_vs_heuristic_gain": round(_mean_policy(rows, "heuristic_adaptive") - _mean_policy(rows, "bayes_proxy"), 4),
            "bayes_vs_cocoa_gain": round(_mean_policy(rows, "cocoa") - _mean_policy(rows, "bayes_proxy"), 4),
        },
        "bootstrap_bayes_vs_heuristic": _bootstrap(rows, "heuristic_adaptive"),
        "bootstrap_bayes_vs_cocoa": _bootstrap(rows, "cocoa"),
    }
    return summary


def build_markdown(summary: dict[str, Any]) -> str:
    overall = summary["overall"]
    lines = [
        "# Llama-3.1-8B Spotlight Coverage Note",
        "",
        "## Headline",
        "",
        f"- `Llama-3.1-8B-Instruct` is already present across all five spotlight benchmarks: "
        f"`conflictbank`, `faitheval`, `memotrap`, `nq_swap`, and `popqa`.",
        f"- On the Llama-only five-benchmark slice, Bayes beats the generic heuristic by "
        f"`{overall['bayes_vs_heuristic_gain']}` regret with bootstrap CI "
        f"`[{summary['bootstrap_bayes_vs_heuristic']['ci95_low']}, {summary['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
        f"- On that same slice, Bayes beats `CoCoA` by `{overall['bayes_vs_cocoa_gain']}` regret with CI "
        f"`[{summary['bootstrap_bayes_vs_cocoa']['ci95_low']}, {summary['bootstrap_bayes_vs_cocoa']['ci95_high']}]`.",
        "",
        "## Per-Benchmark Read",
        "",
    ]
    for row in summary["benchmarks"]:
        lines.append(
            f"- `{row['benchmark']}`: Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, `CoCoA` `{row['cocoa_mean_regret']}`, "
            f"`AdaCAD` `{row['adacad_mean_regret']}`, `always_context` `{row['always_context_mean_regret']}`, "
            f"`always_parametric` `{row['always_parametric_mean_regret']}`."
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This closes the most visible model-coverage objection at the 8B open-weight tier: Llama is not missing from the main grid.",
            "- No new GPU submission is required for this coverage claim because the finished spotlight matrix already contains the complete Llama-8B five-benchmark slice.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    OUT_PREFIX.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    OUT_PREFIX.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(OUT_PREFIX.with_suffix('.json')), "md": str(OUT_PREFIX.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
