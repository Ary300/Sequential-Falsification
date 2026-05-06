#!/usr/bin/env python3
"""Run a small Track B capacity pilot from YAML configs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment_registry import load_expanded_experiments  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Track B capacity pilot experiments.")
    parser.add_argument("--config", default="src/configs/capacity_experiments.yaml")
    parser.add_argument("--output-root", default="results/capacity_pilot")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiments = load_expanded_experiments(ROOT / args.config)
    output_root = ROOT / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    manifest = []
    for experiment in experiments:
        run_name = experiment["name"]
        output_dir = output_root / run_name
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "estimate_capacity.py"),
            "--benchmarks",
            ",".join(experiment.get("benchmarks", [])),
            "--verifiers",
            ",".join(experiment.get("verifiers", [])),
            "--backend",
            experiment.get("backend", "mock"),
            "--model",
            experiment.get("model", "mock-model"),
            "--n-candidates",
            str(experiment.get("n_candidates", 16)),
            "--temperature",
            str(experiment.get("temperature", 0.7)),
            "--max-tokens",
            str(experiment.get("max_tokens", 512)),
            "--seed",
            str(experiment.get("seed", 42)),
            "--timeout",
            str(experiment.get("timeout", 10)),
            "--max-problems",
            str(experiment.get("max_problems", 32)),
            "--data-root",
            experiment.get("data_root", "data"),
            "--output-dir",
            str(output_dir),
        ]
        manifest.append({"name": run_name, "output_dir": str(output_dir), "command": cmd})
        if not args.dry_run:
            subprocess.run(cmd, check=True, cwd=ROOT)

    dump_json({"runs": manifest}, output_root / "manifest.json")
    print(json.dumps({"runs": manifest, "dry_run": args.dry_run}, indent=2))


if __name__ == "__main__":
    main()
