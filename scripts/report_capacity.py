#!/usr/bin/env python3
"""Render Track B capacity results into headline tables and figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from utils.io import dump_json  # noqa: E402
from utils.plotting import maybe_plot_grouped_bars, maybe_plot_scaling_curve, maybe_plot_scatter  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Track B capacity figures and summary tables.")
    parser.add_argument("--results-file", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def load_results(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_capacity_bar_payload(payload: dict) -> dict:
    benchmarks = payload.get("benchmarks", [])
    verifier_names = []
    for benchmark in benchmarks:
        for row in benchmark.get("headline_summary", []):
            name = row["verifier"]
            if name not in verifier_names:
                verifier_names.append(name)
    series = []
    for benchmark in benchmarks:
        headline = {row["verifier"]: row for row in benchmark.get("headline_summary", [])}
        series.append(
            {
                "label": benchmark["benchmark"],
                "values": [round(float(headline.get(name, {}).get("capacity", 0.0)), 4) for name in verifier_names],
            }
        )
    return {
        "title": "Verifier Capacity by Benchmark",
        "categories": verifier_names,
        "series": series,
        "x_label": "Verifier",
        "y_label": "Estimated capacity (nats)",
        "rotation": 20,
    }


def build_selector_bar_payload(payload: dict) -> dict:
    benchmarks = payload.get("benchmarks", [])
    categories = [benchmark["benchmark"] for benchmark in benchmarks]
    oracle_values = [round(float(benchmark.get("pool_summary", {}).get("oracle_accuracy", 0.0)) * 100.0, 2) for benchmark in benchmarks]
    majority_values = []
    public_values = []
    sce_values = []
    for benchmark in benchmarks:
        summary = {row["verifier"]: row for row in benchmark.get("headline_summary", [])}
        majority_values.append(round(float(summary.get("majority", {}).get("selector_accuracy", 0.0)) * 100.0, 2))
        public_values.append(round(float(summary.get("public_test", {}).get("selector_accuracy", 0.0)) * 100.0, 2))
        sce_values.append(round(float(summary.get("sce_trace", {}).get("selector_accuracy", 0.0)) * 100.0, 2))
    return {
        "title": "Observed Selector Accuracy vs Oracle",
        "categories": categories,
        "series": [
            {"label": "oracle", "values": oracle_values},
            {"label": "majority", "values": majority_values},
            {"label": "public_test", "values": public_values},
            {"label": "sce_trace", "values": sce_values},
        ],
        "x_label": "Benchmark",
        "y_label": "Accuracy (%)",
        "rotation": 15,
    }


def build_predicted_curve_payload(payload: dict) -> dict:
    series = []
    for benchmark in payload.get("benchmarks", []):
        for verifier_name, verifier_payload in benchmark.get("verifiers", {}).items():
            predicted = verifier_payload.get("predicted_curves", [])
            series.append(
                {
                    "label": f"{benchmark['benchmark']}::{verifier_name}",
                    "x": [int(row["budget"]) for row in predicted],
                    "y": [round(float(row["predicted_accuracy"]) * 100.0, 2) for row in predicted],
                }
            )
    return {
        "title": "Predicted Accuracy Ceilings from Capacity",
        "x_label": "Budget proxy",
        "y_label": "Predicted selective accuracy (%)",
        "x_scale": "log2",
        "series": series,
    }


def build_predicted_vs_observed_payload(payload: dict) -> dict:
    series = []
    n_candidates = int(payload.get("metadata", {}).get("n_candidates", 16))
    for benchmark in payload.get("benchmarks", []):
        xs = []
        ys = []
        annotations = []
        for verifier_name, verifier_payload in benchmark.get("verifiers", {}).items():
            predicted = verifier_payload.get("predicted_curves", [])
            predicted_at_budget = next(
                (row for row in predicted if int(row.get("budget", -1)) == n_candidates),
                predicted[-1] if predicted else {"predicted_accuracy": 0.0},
            )
            xs.append(round(float(predicted_at_budget.get("predicted_accuracy", 0.0)) * 100.0, 2))
            ys.append(round(float(verifier_payload.get("selection_summary", {}).get("selector_accuracy", 0.0)) * 100.0, 2))
            annotations.append(verifier_name)
        series.append({"label": benchmark["benchmark"], "x": xs, "y": ys, "annotations": annotations})
    return {
        "title": "Predicted vs Observed Selector Accuracy",
        "x_label": f"Predicted accuracy at budget={n_candidates} (%)",
        "y_label": "Observed selector accuracy (%)",
        "series": series,
        "diagonal": True,
        "annotate_points": True,
    }


def build_markdown_summary(payload: dict) -> str:
    lines = [
        "# Track B Capacity Summary",
        "",
        f"- Model: `{payload.get('metadata', {}).get('model', 'unknown')}`",
        f"- Backend: `{payload.get('metadata', {}).get('backend', 'unknown')}`",
        f"- Candidates per problem: `{payload.get('metadata', {}).get('n_candidates', 'unknown')}`",
        "",
        "| Benchmark | Oracle | Majority cap. | Public-test cap. | SCE-trace cap. | Majority acc. | Public-test acc. | SCE-trace acc. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for benchmark in payload.get("benchmarks", []):
        summary = {row["verifier"]: row for row in benchmark.get("headline_summary", [])}
        oracle = float(benchmark.get("pool_summary", {}).get("oracle_accuracy", 0.0)) * 100.0
        lines.append(
            "| "
            + " | ".join(
                [
                    benchmark["benchmark"],
                    f"{oracle:.2f}",
                    f"{float(summary.get('majority', {}).get('capacity', 0.0)):.4f}",
                    f"{float(summary.get('public_test', {}).get('capacity', 0.0)):.4f}",
                    f"{float(summary.get('sce_trace', {}).get('capacity', 0.0)):.4f}",
                    f"{float(summary.get('majority', {}).get('selector_accuracy', 0.0)) * 100.0:.2f}",
                    f"{float(summary.get('public_test', {}).get('selector_accuracy', 0.0)) * 100.0:.2f}",
                    f"{float(summary.get('sce_trace', {}).get('selector_accuracy', 0.0)) * 100.0:.2f}",
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = load_results(args.results_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "capacity_bars": build_capacity_bar_payload(payload),
        "selector_bars": build_selector_bar_payload(payload),
        "predicted_curves": build_predicted_curve_payload(payload),
        "predicted_vs_observed": build_predicted_vs_observed_payload(payload),
    }
    dump_json(summary, output_dir / "capacity_report.json")
    (output_dir / "summary.md").write_text(build_markdown_summary(payload), encoding="utf-8")

    maybe_plot_grouped_bars(summary["capacity_bars"], output_dir / "capacity_bars.pdf")
    maybe_plot_grouped_bars(summary["selector_bars"], output_dir / "selector_accuracy_bars.pdf")
    maybe_plot_scaling_curve(summary["predicted_curves"], output_dir / "predicted_curves.pdf")
    maybe_plot_scatter(summary["predicted_vs_observed"], output_dir / "predicted_vs_observed.pdf")

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "artifacts": [
                    "capacity_report.json",
                    "summary.md",
                    "capacity_bars.pdf|json",
                    "selector_accuracy_bars.pdf|json",
                    "predicted_curves.pdf|json",
                    "predicted_vs_observed.pdf|json",
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
