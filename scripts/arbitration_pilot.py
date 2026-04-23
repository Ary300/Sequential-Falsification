#!/usr/bin/env python3
"""Build manifests for the Bayes-optimal knowledge arbitration project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from knowledge_arbitration.benchmarks import ARBITRATION_BENCHMARKS, benchmark_table  # noqa: E402
from knowledge_arbitration.synthetic import synthetic_grid  # noqa: E402
from utils.io import dump_json, load_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build arbitration pilot manifests.")
    parser.add_argument("--config", default="src/configs/knowledge_arbitration_experiments.yaml")
    parser.add_argument("--output-dir", default="results/arbitration_pilot")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def estimate_run_count(experiment: dict) -> int:
    return (
        max(1, len(experiment.get("benchmarks", [])))
        * max(1, len(experiment.get("models", [])) + len(experiment.get("checkpoint_families", [])))
        * max(1, len(experiment.get("conditions", [])))
        * max(1, len(experiment.get("cot_budgets", [])))
    )


def main() -> None:
    args = parse_args()
    config = load_config(ROOT / args.config)
    experiments = config.get("experiments", [])
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for experiment in experiments:
        manifest.append(
            {
                "name": experiment["name"],
                "priority": experiment.get("priority", "P0"),
                "benchmarks": experiment.get("benchmarks", []),
                "models": experiment.get("models", []),
                "checkpoint_families": experiment.get("checkpoint_families", []),
                "conditions": experiment.get("conditions", []),
                "cot_budgets": experiment.get("cot_budgets", []),
                "metrics": experiment.get("metrics", []),
                "estimated_runs": estimate_run_count(experiment),
            }
        )

    payload = {
        "project": "bayes_optimal_knowledge_arbitration",
        "manifest": manifest,
        "benchmark_registry": benchmark_table(),
        "synthetic_preview": synthetic_grid()[:5],
    }
    dump_json(payload, output_dir / "manifest.json")
    print(json.dumps(payload if args.dry_run else {"output_dir": str(output_dir), "num_experiments": len(manifest)}, indent=2))


if __name__ == "__main__":
    main()
