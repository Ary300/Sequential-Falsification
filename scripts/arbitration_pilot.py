#!/usr/bin/env python3
"""Build manifests and optionally run synthetic arbitration pilots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge_arbitration.benchmarks import ARBITRATION_BENCHMARKS  # noqa: E402
from knowledge_arbitration.experiment import run_benchmark_experiment, run_synthetic_experiment  # noqa: E402
from utils.io import dump_json, load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build manifests and synthetic results for arbitration pilots.")
    parser.add_argument("--config", default="src/configs/knowledge_arbitration_experiments.yaml")
    parser.add_argument("--output-dir", default="results/arbitration_pilot")
    parser.add_argument("--experiment-name", action="append", default=[])
    parser.add_argument("--run-synthetic", action="store_true")
    parser.add_argument("--run-benchmarks", action="store_true")
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Optional benchmark override in the form benchmark=/path/to/local.jsonl",
    )
    return parser.parse_args()


def estimate_condition_count(experiment: dict) -> int:
    return (
        max(1, len(experiment.get("benchmarks", [])))
        * max(1, len(experiment.get("models", [])))
        * max(1, len(experiment.get("conditions", [])))
        * max(1, len(experiment.get("cot_lengths", [])))
        * max(1, len(experiment.get("self_consistency", [])))
    )


def build_manifest(config: dict, selected_names: set[str]) -> dict:
    runs = []
    for experiment in config.get("experiments", []):
        if selected_names and experiment["name"] not in selected_names:
            continue
        max_examples = int(experiment.get("max_examples", 0))
        grid_cells = estimate_condition_count(experiment)
        estimated_examples = max_examples * grid_cells
        benchmark_specs = []
        for benchmark in experiment.get("benchmarks", []):
            spec = ARBITRATION_BENCHMARKS.get(benchmark)
            benchmark_specs.append(
                {
                    "key": benchmark,
                    "known": spec is not None,
                    "role": spec.role if spec else "unknown",
                    "status": spec.status if spec else "unknown",
                }
            )
        runs.append(
            {
                "name": experiment["name"],
                "priority": experiment.get("priority", "unspecified"),
                "benchmarks": benchmark_specs,
                "models": experiment.get("models", []),
                "conditions": experiment.get("conditions", []),
                "cot_lengths": experiment.get("cot_lengths", []),
                "self_consistency": experiment.get("self_consistency", []),
                "max_examples": max_examples,
                "grid_cells": grid_cells,
                "estimated_examples": estimated_examples,
            }
        )
    return {"runs": runs}


def main() -> None:
    args = parse_args()
    config = load_config(ROOT / args.config)
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_names = set(args.experiment_name)
    manifest = build_manifest(config, selected_names)
    dump_json(manifest, output_dir / "manifest.json")

    synthetic_results = []
    benchmark_results = []
    dataset_overrides = {}
    for item in args.dataset:
        if "=" not in item:
            raise ValueError(f"Expected benchmark override as benchmark=/path, got: {item}")
        benchmark, path = item.split("=", 1)
        dataset_overrides[benchmark.strip()] = path.strip()

    if args.run_synthetic:
        experiments = {experiment["name"]: experiment for experiment in config.get("experiments", [])}
        for run in manifest["runs"]:
            result = run_synthetic_experiment(experiments[run["name"]])
            synthetic_results.append(result["experiment_name"])
            dump_json(result, output_dir / f"{run['name']}_synthetic_results.json")
    if args.run_benchmarks:
        experiments = {experiment["name"]: experiment for experiment in config.get("experiments", [])}
        for run in manifest["runs"]:
            result = run_benchmark_experiment(experiments[run["name"]], dataset_overrides=dataset_overrides)
            benchmark_results.append(result["experiment_name"])
            dump_json(result, output_dir / f"{run['name']}_benchmark_results.json")

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "num_runs": len(manifest["runs"]),
                "runs": manifest["runs"],
                "synthetic_results": synthetic_results,
                "benchmark_results": benchmark_results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
