#!/usr/bin/env python3
"""Build camera-ready reaggregations for the outstanding Paper 2 summary asks.

This script only uses artifacts already present in the repo. It is intentionally
explicit about which summaries are exact and which are best-effort because some
reviewer asks refer to larger pools than the currently materialized local files.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs" / "generated"
EXTENDED_WAVE = ROOT / "results" / "delta_knowledge_arbitration_extended_wave"
SEEDS = [42, 43, 44]
BASELINES = ["cocoa", "astute_rag", "self_rag"]
ETA_FILES = [
    GENERATED / "theorem3_eta_tempered_method_result.json",
    GENERATED / "theorem3_eta_tempered_conflictbank_full.json",
    GENERATED / "theorem3_eta_tempered_wikicontradict_full.json",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = (len(ordered) - 1) * q
    lo = int(idx)
    hi = min(len(ordered) - 1, lo + 1)
    frac = idx - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _series_gaps_for_baseline(baseline: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        path = EXTENDED_WAVE / f"arbitration_spotlight_extended_model_wave__seed={seed}" / "report" / "arbitration_summary.json"
        payload = _load_json(path)
        per_series: dict[str, dict[str, float]] = {}
        for row in payload["regret"]["rows"]:
            per_series.setdefault(str(row["series"]), {})[str(row["policy"])] = float(row["mean_regret"])
        for series, policies in sorted(per_series.items()):
            if "bayes_proxy" not in policies or baseline not in policies:
                continue
            gap = float(policies[baseline] - policies["bayes_proxy"])
            rows.append(
                {
                    "seed": seed,
                    "series": series,
                    "benchmark": series.split("::", 1)[0],
                    "model": series.split("::", 1)[1],
                    "baseline_regret": float(policies[baseline]),
                    "bayes_regret": float(policies["bayes_proxy"]),
                    "gap": gap,
                    "positive_gap": max(gap, 0.0),
                }
            )
    return rows


def _head_to_head_positive_subset() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for baseline in BASELINES:
        rows = _series_gaps_for_baseline(baseline)
        positive_rows = [row for row in rows if row["gap"] > 0.0]
        out[baseline] = {
            "total_cells": len(rows),
            "positive_cells": len(positive_rows),
            "mean_gap_all": round(statistics.mean(row["gap"] for row in rows), 4) if rows else 0.0,
            "mean_gap_positive_subset": round(statistics.mean(row["gap"] for row in positive_rows), 4)
            if positive_rows
            else 0.0,
            "mean_positive_part": round(statistics.mean(row["positive_gap"] for row in rows), 4) if rows else 0.0,
            "max_gap": round(max((row["gap"] for row in rows), default=0.0), 4),
            "min_gap": round(min((row["gap"] for row in rows), default=0.0), 4),
        }
    return out


def _eta_distribution_summary() -> dict[str, Any]:
    slice_rows = []
    for path in ETA_FILES:
        payload = _load_json(path)
        meta = payload.get("metadata", {})
        selection = payload.get("selection", {})
        evaluation = payload.get("evaluation", {})
        baseline = evaluation.get("baseline", {})
        selected = evaluation.get("selected", {})
        if not baseline or not selected:
            continue
        slice_rows.append(
            {
                "source_file": path.name,
                "benchmark": str(meta.get("benchmark", "unknown")),
                "condition": str(meta.get("condition", "unknown")),
                "cot_length": int(meta.get("cot_length", 0)),
                "selected_eta": float(selection.get("selected_eta", 1.0)),
                "accuracy_delta": float(selected.get("accuracy", 0.0)) - float(baseline.get("accuracy", 0.0)),
                "ece_delta": float(selected.get("ece", 0.0)) - float(baseline.get("ece", 0.0)),
                "brier_delta": float(selected.get("brier", 0.0)) - float(baseline.get("brier", 0.0)),
                "confidence_delta": float(selected.get("mean_confidence", 0.0)) - float(baseline.get("mean_confidence", 0.0)),
                "gap_delta": float(selected.get("overconfidence_gap", 0.0)) - float(baseline.get("overconfidence_gap", 0.0)),
            }
        )

    summary: dict[str, Any] = {"num_slices_available": len(slice_rows), "metrics": {}, "slice_rows": slice_rows}
    for metric in ["accuracy_delta", "ece_delta", "brier_delta", "confidence_delta", "gap_delta", "selected_eta"]:
        values = [float(row[metric]) for row in slice_rows]
        if not values:
            summary["metrics"][metric] = {}
            continue
        summary["metrics"][metric] = {
            "median": round(statistics.median(values), 4),
            "iqr_low": round(_percentile(values, 0.25), 4),
            "iqr_high": round(_percentile(values, 0.75), 4),
            "max": round(max(values), 4),
            "min": round(min(values), 4),
        }
    return summary


def _finite_difference_second_derivative() -> dict[str, Any]:
    rows = []
    for path in ETA_FILES:
        payload = _load_json(path)
        per_eta = (payload.get("calibration", {}) or {}).get("per_eta", [])
        if len(per_eta) < 3:
            continue
        per_eta = sorted(per_eta, key=lambda row: float(row["eta"]))
        for left, center, right in zip(per_eta, per_eta[1:], per_eta[2:]):
            h1 = float(center["eta"]) - float(left["eta"])
            h2 = float(right["eta"]) - float(center["eta"])
            if abs(h1 - h2) > 1e-9 or h1 <= 0:
                continue
            h = h1
            left_r = float(left["brier"])
            center_r = float(center["brier"])
            right_r = float(right["brier"])
            second = (left_r - 2.0 * center_r + right_r) / (h * h)
            rows.append(
                {
                    "source_file": path.name,
                    "benchmark": str((payload.get("metadata", {}) or {}).get("benchmark", "unknown")),
                    "condition": str((payload.get("metadata", {}) or {}).get("condition", "unknown")),
                    "eta_center": float(center["eta"]),
                    "brier_second_derivative": second,
                }
            )
    values = [row["brier_second_derivative"] for row in rows]
    return {
        "num_estimates": len(rows),
        "median": round(statistics.median(values), 4) if values else 0.0,
        "iqr_low": round(_percentile(values, 0.25), 4) if values else 0.0,
        "iqr_high": round(_percentile(values, 0.75), 4) if values else 0.0,
        "max": round(max(values), 4) if values else 0.0,
        "min": round(min(values), 4) if values else 0.0,
        "rows": rows,
    }


def build_payload() -> dict[str, Any]:
    return {
        "head_to_head_positive_subset": _head_to_head_positive_subset(),
        "eta_tempering_distribution_summary": _eta_distribution_summary(),
        "c_rob_shift_curvature_proxy": _finite_difference_second_derivative(),
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Paper 2 Camera-Ready Reaggregations",
        "",
        "This note packages the remaining low-compute reaggregations from already materialized Paper 2 artifacts.",
        "",
        "## Powered Head-to-Head Positive Subset",
        "",
        "We report both the mean gap over all `210` seeded cells and the positive-only subset mean (`Δ̂_+` here = average Bayes-vs-baseline gap over cells where the gap is positive).",
        "",
        "| Baseline | Mean gap (all) | Positive cells | Δ̂_+ positive subset | Mean positive part | Max gap | Min gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for baseline, row in payload["head_to_head_positive_subset"].items():
        lines.append(
            f"| {baseline} | {row['mean_gap_all']:.4f} | {row['positive_cells']}/{row['total_cells']} | "
            f"{row['mean_gap_positive_subset']:.4f} | {row['mean_positive_part']:.4f} | "
            f"{row['max_gap']:.4f} | {row['min_gap']:.4f} |"
        )

    eta = payload["eta_tempering_distribution_summary"]
    lines.extend(
        [
            "",
            "## Eta-Tempering Distribution Summary",
            "",
            f"- Available local slices: `{eta['num_slices_available']}`",
            "- This is the exact currently materialized local pool, which is smaller than the aspirational `n=30` sweep.",
            "",
            "| Metric | Median | IQR | Max | Min |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for metric, stats in eta["metrics"].items():
        if not stats:
            continue
        lines.append(
            f"| {metric} | {stats['median']:.4f} | [{stats['iqr_low']:.4f}, {stats['iqr_high']:.4f}] | "
            f"{stats['max']:.4f} | {stats['min']:.4f} |"
        )

    curv = payload["c_rob_shift_curvature_proxy"]
    lines.extend(
        [
            "",
            "## Empirical Curvature Proxy",
            "",
            "We approximate `∂²_{ww} R` with a finite-difference second derivative of Brier along the locally available eta grid.",
            "",
            f"- Number of curvature estimates: `{curv['num_estimates']}`",
            f"- Median: `{curv['median']}`",
            f"- IQR: `[{curv['iqr_low']}, {curv['iqr_high']}]`",
            f"- Max: `{curv['max']}`",
            f"- Min: `{curv['min']}`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    json_path = GENERATED / "paper2_camera_ready_reaggregations.json"
    md_path = GENERATED / "paper2_camera_ready_reaggregations.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
