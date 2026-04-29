#!/usr/bin/env python3
"""Build a compact statistical-strength note for the finished spotlight matrices."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build spotlight statistical strength note.")
    parser.add_argument("--t12-report-json", required=True)
    parser.add_argument("--t3-report-json", required=True)
    parser.add_argument("--t12-bootstrap-json", required=True)
    parser.add_argument("--t3-bootstrap-json", required=True)
    parser.add_argument("--family-note-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def _load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _exact_sign_pvalue(num_positive: int, n: int) -> float:
    if n <= 0:
        return 1.0
    return sum(comb(n, k) for k in range(num_positive, n + 1)) / (2**n)


def _fixed_lambda_evalue(signs: list[int], lam: float = 0.5) -> float:
    value = 1.0
    for sign in signs:
        if sign > 0:
            value *= 1.0 + lam
        elif sign < 0:
            value *= 1.0 - lam
    return value


def _series_gaps(report: dict[str, Any], *, baseline: str) -> list[dict[str, Any]]:
    per_series: dict[str, dict[str, float]] = defaultdict(dict)
    for row in report["regret"]["rows"]:
        per_series[str(row["series"])][str(row["policy"])] = float(row["mean_regret"])

    rows = []
    for series, policies in sorted(per_series.items()):
        benchmark, model = series.split("::", 1)
        gap = float(policies[baseline]) - float(policies["bayes_proxy"])
        rows.append(
            {
                "series": series,
                "benchmark": benchmark,
                "model": model,
                "gap": round(gap, 4),
                "sign": 1 if gap > 0 else -1 if gap < 0 else 0,
            }
        )
    return rows


def _stopping_summary(rows: list[dict[str, Any]], *, thresholds: list[float]) -> dict[str, Any]:
    value = 1.0
    path = []
    crossings: dict[str, int | None] = {str(threshold): None for threshold in thresholds}
    for index, row in enumerate(rows, start=1):
        sign = int(row["sign"])
        if sign > 0:
            value *= 1.5
        elif sign < 0:
            value *= 0.5
        path.append(
            {
                "index": index,
                "series": row["series"],
                "benchmark": row["benchmark"],
                "model": row["model"],
                "gap": row["gap"],
                "evalue": round(value, 4),
            }
        )
        for threshold in thresholds:
            key = str(threshold)
            if crossings[key] is None and value >= threshold:
                crossings[key] = index
    return {
        "final_evalue": round(value, 4),
        "crossings": crossings,
        "path_preview": path[:10] + ([] if len(path) <= 12 else [{"index": -1, "series": "...", "benchmark": "...", "model": "...", "gap": 0.0, "evalue": 0.0}]) + path[-2:],
    }


def _matrix_summary(
    report: dict[str, Any],
    bootstrap: dict[str, Any],
    *,
    baseline: str,
    comparator: str,
) -> dict[str, Any]:
    baseline_rows = _series_gaps(report, baseline=baseline)
    comparator_rows = _series_gaps(report, baseline=comparator)
    baseline_signs = [int(row["sign"]) for row in baseline_rows]
    comparator_signs = [int(row["sign"]) for row in comparator_rows]
    baseline_wins = sum(sign > 0 for sign in baseline_signs)
    comparator_wins = sum(sign > 0 for sign in comparator_signs)
    n = len(baseline_rows)
    return {
        "num_series": n,
        "wins_vs_baseline": baseline_wins,
        "wins_vs_comparator": comparator_wins,
        "sign_test_p_vs_baseline": _exact_sign_pvalue(baseline_wins, n),
        "sign_test_p_vs_comparator": _exact_sign_pvalue(comparator_wins, n),
        "evalue_vs_baseline": _fixed_lambda_evalue(baseline_signs),
        "evalue_vs_comparator": _fixed_lambda_evalue(comparator_signs),
        "sequential_vs_baseline": _stopping_summary(baseline_rows, thresholds=[10.0, 20.0, 100.0]),
        "sequential_vs_comparator": _stopping_summary(comparator_rows, thresholds=[10.0, 20.0, 100.0]),
        "bootstrap": bootstrap["bootstrap"],
    }


def build_summary(
    t12_report: dict[str, Any],
    t3_report: dict[str, Any],
    t12_bootstrap: dict[str, Any],
    t3_bootstrap: dict[str, Any],
    family_note: dict[str, Any],
) -> dict[str, Any]:
    return {
        "t12_matrix": _matrix_summary(
            t12_report,
            t12_bootstrap,
            baseline="heuristic_adaptive",
            comparator=str(t12_bootstrap["bootstrap"]["bayes_vs_strongest_named"]["baseline"]),
        ),
        "t3_matrix": _matrix_summary(
            t3_report,
            t3_bootstrap,
            baseline="heuristic_adaptive",
            comparator=str(t3_bootstrap["bootstrap"]["bayes_vs_strongest_named"]["baseline"]),
        ),
        "family_note": family_note,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    t12 = summary["t12_matrix"]
    t3 = summary["t3_matrix"]
    lines = [
        "# Spotlight Statistical Strength Note",
        "",
        "This note consolidates the strongest already-finished statistical support for the spotlight-scale matrices.",
        "",
        "## T1/T2 Matrix",
        "",
        f"- Series wins vs heuristic: `{t12['wins_vs_baseline']}/{t12['num_series']}`",
        f"- Exact one-sided sign-test p vs heuristic: `{t12['sign_test_p_vs_baseline']:.6f}`",
        f"- Fixed-lambda e-value vs heuristic: `{t12['evalue_vs_baseline']:.4f}`",
        f"- Bootstrap Bayes-vs-heuristic CI: `[{t12['bootstrap']['bayes_vs_heuristic']['ci95_low']}, {t12['bootstrap']['bayes_vs_heuristic']['ci95_high']}]`",
        f"- Series wins vs strongest named comparator: `{t12['wins_vs_comparator']}/{t12['num_series']}`",
        f"- Exact one-sided sign-test p vs strongest named comparator: `{t12['sign_test_p_vs_comparator']:.6f}`",
        f"- Fixed-lambda e-value vs strongest named comparator: `{t12['evalue_vs_comparator']:.4f}`",
        f"- Sequential e-value crosses `10` after `{t12['sequential_vs_baseline']['crossings']['10.0']}` series, `20` after `{t12['sequential_vs_baseline']['crossings']['20.0']}` series, and `100` after `{t12['sequential_vs_baseline']['crossings']['100.0']}` series against the heuristic.",
        "",
        "## T3 Proxy Matrix",
        "",
        f"- Series wins vs heuristic: `{t3['wins_vs_baseline']}/{t3['num_series']}`",
        f"- Exact one-sided sign-test p vs heuristic: `{t3['sign_test_p_vs_baseline']:.6f}`",
        f"- Fixed-lambda e-value vs heuristic: `{t3['evalue_vs_baseline']:.4f}`",
        f"- Bootstrap Bayes-vs-heuristic CI: `[{t3['bootstrap']['bayes_vs_heuristic']['ci95_low']}, {t3['bootstrap']['bayes_vs_heuristic']['ci95_high']}]`",
        f"- Series wins vs strongest named comparator: `{t3['wins_vs_comparator']}/{t3['num_series']}`",
        f"- Exact one-sided sign-test p vs strongest named comparator: `{t3['sign_test_p_vs_comparator']:.6f}`",
        f"- Fixed-lambda e-value vs strongest named comparator: `{t3['evalue_vs_comparator']:.4f}`",
        f"- Sequential e-value crosses `10` after `{t3['sequential_vs_baseline']['crossings']['10.0']}` series, `20` after `{t3['sequential_vs_baseline']['crossings']['20.0']}` series, and `100` after `{t3['sequential_vs_baseline']['crossings']['100.0']}` series against the heuristic.",
        "",
        "## Read",
        "",
        "- The theorem-1/theorem-2 spotlight matrix is not just a positive mean-gap result; it is directionally positive on almost every benchmark-model series and crosses strong e-value thresholds quickly.",
        "- The theorem-3 proxy matrix is weaker than the theorem-1/theorem-2 matrix, but it still reaches a clean positive bootstrap interval and decisive series-level directional support against the heuristic.",
        "- The strongest named-comparator story remains more mixed than the heuristic story, which is exactly why the paper should headline Bayes-vs-heuristic plus benchmark-family consistency rather than over-selling every comparator.",
        "- This note complements, rather than replaces, the benchmark-family Holm-Bonferroni tables in the family-consistency artifact.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(
        _load(args.t12_report_json),
        _load(args.t3_report_json),
        _load(args.t12_bootstrap_json),
        _load(args.t3_bootstrap_json),
        _load(args.family_note_json),
    )
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
