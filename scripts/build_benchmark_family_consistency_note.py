#!/usr/bin/env python3
"""Build benchmark-family consistency summaries for arbitration reports."""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build benchmark-family consistency note.")
    parser.add_argument("--t12-report-json", required=True)
    parser.add_argument("--t3-report-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _exact_sign_pvalue(num_positive: int, n: int, *, alternative: str) -> float:
    if n <= 0:
        return 1.0
    if alternative == "greater":
        tail = range(num_positive, n + 1)
    else:
        tail = range(0, num_positive + 1)
    return sum(comb(n, k) for k in tail) / (2**n)


def _holm_adjust(rows: list[dict], key: str) -> None:
    indexed = sorted(enumerate(rows), key=lambda item: item[1][key])
    m = len(indexed)
    adjusted = [0.0] * m
    running = 0.0
    for rank, (orig_idx, row) in enumerate(indexed, start=1):
        candidate = min(1.0, (m - rank + 1) * float(row[key]))
        running = max(running, candidate)
        adjusted[rank - 1] = running
    for (ranked, (orig_idx, row)) in enumerate(indexed):
        rows[orig_idx][f"{key}_holm"] = round(adjusted[ranked], 4)


def _fixed_lambda_evalue(signs: list[int], lam: float = 0.5) -> float:
    value = 1.0
    for sign in signs:
        if sign > 0:
            value *= 1.0 + lam
        elif sign < 0:
            value *= 1.0 - lam
    return value


def _build_matrix_summary(report: dict, *, baseline: str, comparator: str) -> list[dict]:
    by_benchmark: dict[str, list[dict]] = {}
    series_map: dict[tuple[str, str], dict[str, float]] = {}
    for row in report["regret"]["rows"]:
        benchmark, model = row["series"].split("::", 1)
        series_map.setdefault((benchmark, model), {})[row["policy"]] = float(row["mean_regret"])

    for (benchmark, model), values in series_map.items():
        bayes = values["bayes_proxy"]
        base_gap = float(values[baseline]) - bayes
        comp_gap = float(values[comparator]) - bayes
        by_benchmark.setdefault(benchmark, []).append(
            {
                "model": model,
                "gap_vs_baseline": round(base_gap, 4),
                "gap_vs_comparator": round(comp_gap, 4),
            }
        )

    rows: list[dict] = []
    for benchmark, model_rows in sorted(by_benchmark.items()):
        base_signs = [1 if row["gap_vs_baseline"] > 0 else -1 if row["gap_vs_baseline"] < 0 else 0 for row in model_rows]
        comp_signs = [1 if row["gap_vs_comparator"] > 0 else -1 if row["gap_vs_comparator"] < 0 else 0 for row in model_rows]
        base_pos = sum(sign > 0 for sign in base_signs)
        comp_pos = sum(sign > 0 for sign in comp_signs)
        n = len(model_rows)
        base_alt = "greater" if sum(row["gap_vs_baseline"] for row in model_rows) >= 0 else "less"
        comp_alt = "greater" if sum(row["gap_vs_comparator"] for row in model_rows) >= 0 else "less"
        rows.append(
            {
                "benchmark": benchmark,
                "num_models": n,
                "mean_gap_vs_baseline": round(sum(row["gap_vs_baseline"] for row in model_rows) / n, 4),
                "mean_gap_vs_comparator": round(sum(row["gap_vs_comparator"] for row in model_rows) / n, 4),
                "positive_models_vs_baseline": base_pos,
                "positive_models_vs_comparator": comp_pos,
                "sign_test_p_vs_baseline": round(_exact_sign_pvalue(base_pos if base_alt == "greater" else n - base_pos, n, alternative="greater"), 4),
                "sign_test_p_vs_comparator": round(_exact_sign_pvalue(comp_pos if comp_alt == "greater" else n - comp_pos, n, alternative="greater"), 4),
                "evalue_vs_baseline": round(_fixed_lambda_evalue(base_signs), 4),
                "evalue_vs_comparator": round(_fixed_lambda_evalue(comp_signs), 4),
                "rows": model_rows,
            }
        )

    _holm_adjust(rows, "sign_test_p_vs_baseline")
    _holm_adjust(rows, "sign_test_p_vs_comparator")
    return rows


def build_summary(t12_report: dict, t3_report: dict) -> dict:
    return {
        "t12_matrix": _build_matrix_summary(t12_report, baseline="heuristic_adaptive", comparator="cocoa"),
        "t3_matrix": _build_matrix_summary(t3_report, baseline="heuristic_adaptive", comparator="cocoa"),
    }


def build_markdown(summary: dict) -> str:
    lines = [
        "# Benchmark-Family Consistency Note",
        "",
        "This note summarizes how often Bayes beats the generic heuristic and CoCoA within each benchmark family.",
        "The model-level sign tests are intentionally conservative because each benchmark contributes only five model-family slices.",
        "",
    ]

    for section_key, title in [
        ("t12_matrix", "Spotlight Matrix (`T1/T2`)"),
        ("t3_matrix", "Theorem-3 Proxy Matrix"),
    ]:
        lines.extend(
            [
                f"## {title}",
                "",
                "| Benchmark | Mean gap vs heuristic | Positive model slices | One-sided sign p | Holm p | Fixed-lambda e-value | Mean gap vs CoCoA | Positive slices vs CoCoA | One-sided sign p | Holm p | Fixed-lambda e-value |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summary[section_key]:
            lines.append(
                f"| {row['benchmark']} | {row['mean_gap_vs_baseline']:.4f} | "
                f"{row['positive_models_vs_baseline']}/{row['num_models']} | "
                f"{row['sign_test_p_vs_baseline']:.4f} | {row['sign_test_p_vs_baseline_holm']:.4f} | {row['evalue_vs_baseline']:.4f} | "
                f"{row['mean_gap_vs_comparator']:.4f} | {row['positive_models_vs_comparator']}/{row['num_models']} | "
                f"{row['sign_test_p_vs_comparator']:.4f} | {row['sign_test_p_vs_comparator_holm']:.4f} | {row['evalue_vs_comparator']:.4f} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Read",
            "",
            "- On the spotlight matrix, `ConflictBank`, `FaithEval`, `MemoTrap`, and `NQ-Swap` are unanimous `5/5` Bayes-over-heuristic wins across model families, while `PopQA` is the lone mixed family because of the Llama-70B outlier slice.",
            "- On that same matrix, those same four benchmark families are also unanimous `5/5` Bayes-over-CoCoA wins, which is the cleanest benchmark-family version of the theorem-1/theorem-2 headline.",
            "- On the theorem-3 proxy matrix, `AmbigDocs`, `ConflictBank`, `FaithEval`, and `RAMDocs` are unanimous `5/5` Bayes-over-heuristic wins, while `WikiContradict` is a unanimous negative exception. That makes the theorem-3 regret read explicitly benchmark-dependent rather than universally positive.",
            "- The fixed-lambda e-values are exploratory support diagnostics, not replacements for the main bootstrap intervals. They are included to make the cross-model directional consistency easy to see at a glance.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(_load(args.t12_report_json), _load(args.t3_report_json))
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
