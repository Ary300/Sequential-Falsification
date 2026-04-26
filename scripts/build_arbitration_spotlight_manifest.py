#!/usr/bin/env python3
"""Build and validate a spotlight-scale arbitration campaign manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment_registry import load_expanded_experiments  # noqa: E402
from knowledge_arbitration.benchmarks import ARBITRATION_BENCHMARKS  # noqa: E402
from utils.io import dump_json  # noqa: E402


SPOTLIGHT_FLOOR = {
    "min_models": 5,
    "min_benchmarks": 5,
    "min_baselines": 6,
    "min_ablations": 4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a spotlight-scale arbitration campaign manifest.")
    parser.add_argument("--config", default="src/configs/knowledge_arbitration_spotlight.yaml")
    parser.add_argument("--output-dir", default="results/arbitration_spotlight_manifest")
    return parser.parse_args()


def _experiment_summary(experiment: dict[str, Any]) -> dict[str, Any]:
    benchmarks = list(experiment.get("benchmarks", []))
    models = list(experiment.get("models", []))
    baselines = list(experiment.get("baseline_methods", []))
    ablations = list(experiment.get("ablations", []))
    conditions = list(experiment.get("conditions", []))
    cot_lengths = list(experiment.get("cot_lengths", []))
    self_consistency = list(experiment.get("self_consistency", []))
    grid_values = experiment.get("grid", {})

    grid_multiplier = 1
    for values in grid_values.values():
        grid_multiplier *= max(1, len(values))

    total_cells = (
        max(1, len(benchmarks))
        * max(1, len(models))
        * max(1, len(conditions))
        * max(1, len(cot_lengths))
        * max(1, len(self_consistency))
        * grid_multiplier
    )

    benchmark_specs = []
    for benchmark in benchmarks:
        spec = ARBITRATION_BENCHMARKS.get(benchmark)
        benchmark_specs.append(
            {
                "key": benchmark,
                "known": spec is not None,
                "status": None if spec is None else spec.status,
                "family": None if spec is None else spec.family,
                "role": None if spec is None else spec.role,
            }
        )

    return {
        "name": experiment["name"],
        "priority": experiment.get("priority", "unspecified"),
        "benchmarks": benchmark_specs,
        "models": models,
        "baseline_methods": baselines,
        "ablations": ablations,
        "conditions": conditions,
        "cot_lengths": cot_lengths,
        "self_consistency": self_consistency,
        "grid": grid_values,
        "max_examples": int(experiment.get("max_examples", 0)),
        "total_cells": total_cells,
        "notes": experiment.get("notes", ""),
    }


def _readiness(summary_rows: list[dict[str, Any]]) -> dict[str, Any]:
    union_models = {model for row in summary_rows for model in row["models"]}
    union_benchmarks = {item["key"] for row in summary_rows for item in row["benchmarks"]}
    union_baselines = {method for row in summary_rows for method in row["baseline_methods"]}
    union_ablations = {item for row in summary_rows for item in row["ablations"]}

    readiness = {
        "unique_models": len(union_models),
        "unique_benchmarks": len(union_benchmarks),
        "unique_baselines": len(union_baselines),
        "unique_ablations": len(union_ablations),
        "meets_model_floor": len(union_models) >= SPOTLIGHT_FLOOR["min_models"],
        "meets_benchmark_floor": len(union_benchmarks) >= SPOTLIGHT_FLOOR["min_benchmarks"],
        "meets_baseline_floor": len(union_baselines) >= SPOTLIGHT_FLOOR["min_baselines"],
        "meets_ablation_floor": len(union_ablations) >= SPOTLIGHT_FLOOR["min_ablations"],
    }
    readiness["spotlight_floor_ready"] = all(
        readiness[key]
        for key in (
            "meets_model_floor",
            "meets_benchmark_floor",
            "meets_baseline_floor",
            "meets_ablation_floor",
        )
    )
    return readiness


def main() -> None:
    args = parse_args()
    experiments = load_expanded_experiments(ROOT / args.config)
    summary_rows = [_experiment_summary(experiment) for experiment in experiments]
    payload = {
        "config": args.config,
        "num_experiments": len(summary_rows),
        "spotlight_floor": SPOTLIGHT_FLOOR,
        "readiness": _readiness(summary_rows),
        "experiments": summary_rows,
    }
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_dir / "manifest.json")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

