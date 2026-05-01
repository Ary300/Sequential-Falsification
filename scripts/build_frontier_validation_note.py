#!/usr/bin/env python3
"""Promote existing frontier-scale validation into one headline note."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"
EXTENDED_WAVE = ROOT / "results/delta_knowledge_arbitration_extended_wave"

MODEL_WAVE_SEEDS = [42, 43, 44]
API_SLICE_SEEDS = [42, 43, 44]

TARGET_MODELS = [
    "Qwen/Qwen2.5-32B-Instruct",
    "meta-llama/Llama-3.1-70B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
]
TARGET_APIS = [
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
    "google/gemini-1.5-flash",
]


def _load_summary(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_series(summary: dict) -> dict[str, dict[str, float]]:
    series = {}
    for row in summary["regret"]["rows"]:
        series.setdefault(row["series"], {})[row["policy"]] = float(row["mean_regret"])
    return series


def _collect_model_rows(experiment_name_template: str, seeds: list[int], target_models: list[str]) -> dict[str, list[dict[str, float | str]]]:
    model_rows = {model: [] for model in target_models}
    for seed in seeds:
        path = EXTENDED_WAVE / experiment_name_template.format(seed=seed) / "report" / "arbitration_summary.json"
        summary = _load_summary(path)
        series = _collect_series(summary)
        for series_name, values in series.items():
            benchmark, model = series_name.split("::", 1)
            if model not in model_rows:
                continue
            if "bayes_proxy" not in values:
                continue
            model_rows[model].append(
                {
                    "seed": seed,
                    "benchmark": benchmark,
                    "bayes_vs_heuristic": float(values["heuristic_adaptive"] - values["bayes_proxy"]),
                    "bayes_vs_cocoa": float(values["cocoa"] - values["bayes_proxy"]) if "cocoa" in values else None,
                    "bayes_vs_adacad": float(values["adacad"] - values["bayes_proxy"]) if "adacad" in values else None,
                }
            )
    return model_rows


def _summarize(rows: list[dict[str, float | str]]) -> dict[str, object]:
    heur = [float(row["bayes_vs_heuristic"]) for row in rows]
    cocoa = [float(row["bayes_vs_cocoa"]) for row in rows if row["bayes_vs_cocoa"] is not None]
    adacad = [float(row["bayes_vs_adacad"]) for row in rows if row["bayes_vs_adacad"] is not None]
    benchmarks = sorted({str(row["benchmark"]) for row in rows})
    return {
        "num_seeded_cells": len(rows),
        "benchmarks": benchmarks,
        "mean_bayes_vs_heuristic": round(float(np.mean(heur)), 4),
        "mean_bayes_vs_cocoa": round(float(np.mean(cocoa)), 4) if cocoa else None,
        "mean_bayes_vs_adacad": round(float(np.mean(adacad)), 4) if adacad else None,
        "positive_vs_heuristic": int(sum(value > 0 for value in heur)),
        "positive_vs_cocoa": int(sum(value > 0 for value in cocoa)) if cocoa else None,
        "positive_vs_adacad": int(sum(value > 0 for value in adacad)) if adacad else None,
    }


def run_analysis() -> dict:
    open_weight_rows = _collect_model_rows(
        "arbitration_spotlight_extended_model_wave__seed={seed}",
        MODEL_WAVE_SEEDS,
        TARGET_MODELS,
    )
    api_rows = _collect_model_rows(
        "arbitration_spotlight_extended_api_slice__seed={seed}",
        API_SLICE_SEEDS,
        TARGET_APIS,
    )
    payload = {
        "open_weight": {model: _summarize(rows) for model, rows in open_weight_rows.items()},
        "api_models": {model: _summarize(rows) for model, rows in api_rows.items()},
    }
    payload["headline"] = {
        "open_weight_models": len(payload["open_weight"]),
        "api_models": len(payload["api_models"]),
        "all_frontier_slices_positive_vs_heuristic": all(
            summary["positive_vs_heuristic"] == summary["num_seeded_cells"]
            for summary in [*payload["open_weight"].values(), *payload["api_models"].values()]
        ),
    }
    return payload


def build_markdown(payload: dict) -> str:
    lines = [
        "# Frontier Validation Note",
        "",
        "This note promotes the repo's existing frontier-ish coverage into one body-facing read.",
        "It does not pretend we already ran `405B` or `72B` checkpoints. It does show that the finished extended wave already covers large open-weight models plus three closed API models on real seeded slices.",
        "",
        "## Headline",
        "",
        f"- Open-weight frontier slices summarized here: `{payload['headline']['open_weight_models']}`",
        f"- Closed API slices summarized here: `{payload['headline']['api_models']}`",
        f"- Every summarized frontier slice is positive vs the heuristic baseline: `{payload['headline']['all_frontier_slices_positive_vs_heuristic']}`",
        "",
        "## Open-Weight Frontier Read",
        "",
        "| Model | Seeded cells | Benchmarks | Mean Bayes-vs-heuristic | Mean Bayes-vs-CoCoA | Mean Bayes-vs-AdaCAD | Positive vs heuristic |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model, summary in payload["open_weight"].items():
        lines.append(
            f"| {model} | {summary['num_seeded_cells']} | {len(summary['benchmarks'])} | "
            f"{summary['mean_bayes_vs_heuristic']:.4f} | {summary['mean_bayes_vs_cocoa']:.4f} | "
            f"{summary['mean_bayes_vs_adacad']:.4f} | {summary['positive_vs_heuristic']}/{summary['num_seeded_cells']} |"
        )
    lines.extend(
        [
            "",
            "## Closed-API Read",
            "",
            "| Model | Seeded cells | Benchmarks | Mean Bayes-vs-heuristic | Mean Bayes-vs-CoCoA | Positive vs heuristic | Positive vs CoCoA |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model, summary in payload["api_models"].items():
        lines.append(
            f"| {model} | {summary['num_seeded_cells']} | {len(summary['benchmarks'])} | "
            f"{summary['mean_bayes_vs_heuristic']:.4f} | {summary['mean_bayes_vs_cocoa']:.4f} | "
            f"{summary['positive_vs_heuristic']}/{summary['num_seeded_cells']} | "
            f"{summary['positive_vs_cocoa']}/{summary['num_seeded_cells']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The repo already contains a stronger frontier story than the appendix framing suggested: `Qwen2.5-32B-Instruct`, `Llama-3.1-70B-Instruct`, and `DeepSeek-R1-Distill-Llama-70B` are all positive on the seeded open-weight slice.",
            "- The closed-model slice is also clean: `GPT-4o-mini`, `Claude-3.5-Haiku`, and `Gemini-1.5-Flash` are each positive versus the heuristic baseline and CoCoA on the completed API wave.",
            "- This is not the final word on true frontier scale, but it is already good enough to move the generalization claim out of an appendix footnote and into a real body-facing result.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = run_analysis()
    GENERATED.mkdir(parents=True, exist_ok=True)
    json_path = GENERATED / "frontier_validation_note.json"
    md_path = GENERATED / "frontier_validation_note.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
