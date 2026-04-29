#!/usr/bin/env python3
"""Run expanded knowledge-arbitration benchmark configs and render reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from experiment_registry import filter_experiments, load_expanded_experiments  # noqa: E402
from knowledge_arbitration.experiment import run_benchmark_experiment  # noqa: E402
from knowledge_arbitration.reporting import write_report  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run benchmark-backed knowledge-arbitration experiments from an expanded config."
    )
    parser.add_argument("--config", default="src/configs/knowledge_arbitration_spotlight_extended.yaml")
    parser.add_argument("--output-dir", default="results/knowledge_arbitration_extended_wave")
    parser.add_argument("--experiment-name", action="append", default=[], help="Exact expanded or base experiment name.")
    parser.add_argument(
        "--experiment-prefix",
        action="append",
        default=[],
        help="Expanded or base experiment prefix. May be repeated.",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Optional benchmark override in the form benchmark=/path/to/local.jsonl",
    )
    parser.add_argument("--max-examples-override", type=int, default=None)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--report-subdir",
        default="report",
        help="Per-experiment report directory name placed under each experiment output directory.",
    )
    return parser.parse_args()


def parse_dataset_overrides(items: list[str]) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Expected benchmark override as benchmark=/path, got: {item}")
        benchmark, path = item.split("=", 1)
        overrides[benchmark.strip()] = path.strip()
    return overrides


def _result_stub(result: dict[str, Any], result_file: Path, report_dir: Path) -> dict[str, Any]:
    summary = result.get("summary", {})
    metadata = result.get("metadata", {})
    bayes = summary.get("bayes_proxy", {})
    heuristic = summary.get("heuristic_adaptive", {})
    return {
        "name": result.get("experiment_name"),
        "result_file": str(result_file),
        "report_dir": str(report_dir),
        "num_rows": metadata.get("num_rows"),
        "num_groups": metadata.get("num_groups"),
        "bayes_proxy_mean_regret": bayes.get("mean_regret"),
        "heuristic_adaptive_mean_regret": heuristic.get("mean_regret"),
        "bayes_vs_heuristic_gain": (
            None
            if bayes.get("mean_regret") is None or heuristic.get("mean_regret") is None
            else float(heuristic["mean_regret"]) - float(bayes["mean_regret"])
        ),
    }


def main() -> None:
    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_overrides = parse_dataset_overrides(args.dataset)

    experiments = filter_experiments(
        load_expanded_experiments(ROOT / args.config),
        names=args.experiment_name,
        prefixes=args.experiment_prefix,
    )
    if not experiments:
        raise SystemExit("No experiments matched the provided filters.")

    manifest_rows: list[dict[str, Any]] = []
    for experiment in experiments:
        run_config = dict(experiment)
        if args.max_examples_override is not None:
            run_config["max_examples"] = args.max_examples_override

        experiment_slug = str(run_config["name"])
        experiment_output_dir = output_dir / experiment_slug
        experiment_output_dir.mkdir(parents=True, exist_ok=True)
        result_file = experiment_output_dir / f"{experiment_slug}_benchmark_results.json"
        report_dir = experiment_output_dir / args.report_subdir

        if args.skip_existing and result_file.exists():
            payload = json.loads(result_file.read_text(encoding="utf-8"))
            manifest_rows.append(_result_stub(payload, result_file, report_dir))
            continue

        result = run_benchmark_experiment(run_config, dataset_overrides=dataset_overrides)
        dump_json(result, result_file)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_manifest = write_report(result, report_dir)

        manifest_row = _result_stub(result, result_file, report_dir)
        manifest_row["report_manifest"] = report_manifest
        manifest_rows.append(manifest_row)

    manifest = {
        "config": args.config,
        "output_dir": str(output_dir),
        "num_experiments": len(manifest_rows),
        "experiments": manifest_rows,
    }
    dump_json(manifest, output_dir / "manifest.json")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
