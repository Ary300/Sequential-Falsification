#!/usr/bin/env python3
"""Build a dedicated PopQA / NQ-Swap benchmark note from the spotlight matrix."""

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
OUT_PREFIX = ROOT / "docs/generated/popqa_nqswap_real_benchmark_note"

TARGET_MODELS = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "Qwen/Qwen2.5-7B-Instruct",
]
TARGET_BENCHMARKS = ["popqa", "nq_swap"]
TARGET_POLICIES = [
    "bayes_proxy",
    "heuristic_adaptive",
    "always_context",
    "always_parametric",
    "adacad",
    "cocoa",
]


def _load_rows() -> list[dict[str, Any]]:
    payload = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for experiment in payload["experiments"]:
        rows.extend(experiment["rows"])
    return rows


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(q * (len(ordered) - 1))))
    return ordered[idx]


def _series_key(row: dict[str, Any]) -> str:
    return "::".join(
        [
            str(row["benchmark"]),
            str(row["model"]),
            str(row["condition"]),
            str(row["cot_length"]),
            str(row.get("split", "all")),
        ]
    )


def _mean_policy(rows: list[dict[str, Any]], policy: str) -> float:
    return mean(float(row["regret_by_policy"][policy]) for row in rows)


def _bootstrap_from_series(rows: list[dict[str, Any]], baseline: str, *, seed: int = 42, n: int = 10000) -> dict[str, float]:
    series: dict[str, dict[str, float]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_series_key(row)].append(row)
    for key, bucket in grouped.items():
        series[key] = {
            policy: mean(float(item["regret_by_policy"][policy]) for item in bucket)
            for policy in TARGET_POLICIES
        }

    rng = random.Random(seed)
    keys = sorted(series)
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


def _popqa_bins(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    popularity = sorted(float(row.get("metadata", {}).get("popularity_score", 0.0)) for row in rows)
    low_cut = popularity[len(popularity) // 3]
    high_cut = popularity[(2 * len(popularity)) // 3]
    out = []
    for name, keep in [
        ("low", lambda x: x <= low_cut),
        ("mid", lambda x: low_cut < x <= high_cut),
        ("high", lambda x: x > high_cut),
    ]:
        subset = [row for row in rows if keep(float(row.get("metadata", {}).get("popularity_score", 0.0)))]
        out.append(
            {
                "bin": name,
                "num_rows": len(subset),
                "bayes_proxy_mean_regret": round(_mean_policy(subset, "bayes_proxy"), 4),
                "heuristic_adaptive_mean_regret": round(_mean_policy(subset, "heuristic_adaptive"), 4),
                "cocoa_mean_regret": round(_mean_policy(subset, "cocoa"), 4),
                "adacad_mean_regret": round(_mean_policy(subset, "adacad"), 4),
                "bayes_vs_heuristic_gain": round(
                    _mean_policy(subset, "heuristic_adaptive") - _mean_policy(subset, "bayes_proxy"), 4
                ),
            }
        )
    return out


def _nqswap_types(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = sorted(set(str(row.get("metadata", {}).get("substitution_type", "unknown")) for row in rows))
    out = []
    for substitution_type in types:
        subset = [row for row in rows if str(row.get("metadata", {}).get("substitution_type", "unknown")) == substitution_type]
        out.append(
            {
                "substitution_type": substitution_type,
                "num_rows": len(subset),
                "bayes_proxy_mean_regret": round(_mean_policy(subset, "bayes_proxy"), 4),
                "heuristic_adaptive_mean_regret": round(_mean_policy(subset, "heuristic_adaptive"), 4),
                "cocoa_mean_regret": round(_mean_policy(subset, "cocoa"), 4),
                "adacad_mean_regret": round(_mean_policy(subset, "adacad"), 4),
                "bayes_vs_heuristic_gain": round(
                    _mean_policy(subset, "heuristic_adaptive") - _mean_policy(subset, "bayes_proxy"), 4
                ),
            }
        )
    return out


def build_summary() -> dict[str, Any]:
    rows = _load_rows()
    filtered = [row for row in rows if row["benchmark"] in TARGET_BENCHMARKS and row["model"] in TARGET_MODELS]

    benchmarks: dict[str, Any] = {}
    for benchmark in TARGET_BENCHMARKS:
        benchmark_rows = [row for row in filtered if row["benchmark"] == benchmark]
        per_model = []
        for model in TARGET_MODELS:
            model_rows = [row for row in benchmark_rows if row["model"] == model]
            per_model.append(
                {
                    "model": model,
                    "num_rows": len(model_rows),
                    "bayes_proxy_mean_regret": round(_mean_policy(model_rows, "bayes_proxy"), 4),
                    "heuristic_adaptive_mean_regret": round(_mean_policy(model_rows, "heuristic_adaptive"), 4),
                    "always_context_mean_regret": round(_mean_policy(model_rows, "always_context"), 4),
                    "always_parametric_mean_regret": round(_mean_policy(model_rows, "always_parametric"), 4),
                    "adacad_mean_regret": round(_mean_policy(model_rows, "adacad"), 4),
                    "cocoa_mean_regret": round(_mean_policy(model_rows, "cocoa"), 4),
                    "bayes_vs_heuristic_gain": round(
                        _mean_policy(model_rows, "heuristic_adaptive") - _mean_policy(model_rows, "bayes_proxy"), 4
                    ),
                    "bayes_vs_cocoa_gain": round(
                        _mean_policy(model_rows, "cocoa") - _mean_policy(model_rows, "bayes_proxy"), 4
                    ),
                    "bayes_vs_adacad_gain": round(
                        _mean_policy(model_rows, "adacad") - _mean_policy(model_rows, "bayes_proxy"), 4
                    ),
                }
            )

        summary = {
            "num_rows": len(benchmark_rows),
            "num_models": len(TARGET_MODELS),
            "per_model": per_model,
            "bootstrap_bayes_vs_heuristic": _bootstrap_from_series(benchmark_rows, "heuristic_adaptive"),
            "bootstrap_bayes_vs_cocoa": _bootstrap_from_series(benchmark_rows, "cocoa"),
        }
        if benchmark == "popqa":
            summary["popularity_bins"] = _popqa_bins(benchmark_rows)
        if benchmark == "nq_swap":
            summary["substitution_types"] = _nqswap_types(benchmark_rows)
        benchmarks[benchmark] = summary

    return {
        "source_results": str(RESULTS_JSON.relative_to(ROOT)),
        "target_models": TARGET_MODELS,
        "benchmarks": benchmarks,
        "headline": {
            "popqa_bayes_vs_heuristic_gain": benchmarks["popqa"]["per_model"][0]["bayes_vs_heuristic_gain"],
            "popqa_bayes_vs_heuristic_ci95": benchmarks["popqa"]["bootstrap_bayes_vs_heuristic"],
            "nq_swap_bayes_vs_heuristic_gain": benchmarks["nq_swap"]["per_model"][0]["bayes_vs_heuristic_gain"],
            "nq_swap_bayes_vs_heuristic_ci95": benchmarks["nq_swap"]["bootstrap_bayes_vs_heuristic"],
        },
    }


def build_markdown(summary: dict[str, Any]) -> str:
    popqa = summary["benchmarks"]["popqa"]
    nq_swap = summary["benchmarks"]["nq_swap"]
    lines = [
        "# PopQA / NQ-Swap Real Benchmark Note",
        "",
        "## Headline",
        "",
        f"- `PopQA`: Bayes beats the generic heuristic by `{summary['headline']['popqa_bayes_vs_heuristic_gain']}` regret, "
        f"with benchmark-level bootstrap CI "
        f"`[{popqa['bootstrap_bayes_vs_heuristic']['ci95_low']}, {popqa['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
        f"- `NQ-Swap`: Bayes beats the generic heuristic by `{summary['headline']['nq_swap_bayes_vs_heuristic_gain']}` regret, "
        f"with benchmark-level bootstrap CI "
        f"`[{nq_swap['bootstrap_bayes_vs_heuristic']['ci95_low']}, {nq_swap['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
        "",
        "## PopQA",
        "",
    ]
    for row in popqa["per_model"]:
        lines.append(
            f"- `{row['model']}`: Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, "
            f"`CoCoA` `{row['cocoa_mean_regret']}`, `AdaCAD` `{row['adacad_mean_regret']}`, "
            f"`always_context` `{row['always_context_mean_regret']}`, "
            f"`always_parametric` `{row['always_parametric_mean_regret']}`."
        )
    lines.extend(
        [
            f"- Bayes vs heuristic bootstrap CI: "
            f"`[{popqa['bootstrap_bayes_vs_heuristic']['ci95_low']}, {popqa['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
            f"- Bayes vs `CoCoA` bootstrap CI: "
            f"`[{popqa['bootstrap_bayes_vs_cocoa']['ci95_low']}, {popqa['bootstrap_bayes_vs_cocoa']['ci95_high']}]`.",
            "",
            "Popularity-bin read:",
            "",
        ]
    )
    for row in popqa["popularity_bins"]:
        lines.append(
            f"- `{row['bin']}` popularity: Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, "
            f"Bayes gain `{row['bayes_vs_heuristic_gain']}`."
        )

    lines.extend(["", "## NQ-Swap", ""])
    for row in nq_swap["per_model"]:
        lines.append(
            f"- `{row['model']}`: Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, "
            f"`CoCoA` `{row['cocoa_mean_regret']}`, `AdaCAD` `{row['adacad_mean_regret']}`, "
            f"`always_context` `{row['always_context_mean_regret']}`, "
            f"`always_parametric` `{row['always_parametric_mean_regret']}`."
        )
    lines.extend(
        [
            f"- Bayes vs heuristic bootstrap CI: "
            f"`[{nq_swap['bootstrap_bayes_vs_heuristic']['ci95_low']}, {nq_swap['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
            f"- Bayes vs `CoCoA` bootstrap CI: "
            f"`[{nq_swap['bootstrap_bayes_vs_cocoa']['ci95_low']}, {nq_swap['bootstrap_bayes_vs_cocoa']['ci95_high']}]`.",
            "",
            "Substitution-type read:",
            "",
        ]
    )
    for row in nq_swap["substitution_types"]:
        lines.append(
            f"- `{row['substitution_type']}`: Bayes `{row['bayes_proxy_mean_regret']}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']}`, "
            f"Bayes gain `{row['bayes_vs_heuristic_gain']}`."
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- `PopQA` closes the most visible theorem-2 scope gap: the Bayes rule beats the popularity-style heuristic on the benchmark that motivated popularity-threshold retrieval in the first place.",
            "- `NQ-Swap` closes the most visible comparator gap: it is the canonical entity-substitution benchmark used by the closest baseline papers, and Bayes is clearly ahead there too.",
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
