"""Merge single-seed results.json files into one multi-seed results payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evaluate import summarize


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_results_path(path: Path) -> Path:
    if path.is_file():
        return path
    candidates = [
        path / "results.json",
        path / "results_from_progress.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No results file found under {path}")


def _stderr(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return (variance**0.5) / (len(values) ** 0.5)


def _merge_seed_shards(benchmark: str, seed: int, shard_runs: list[dict[str, Any]]) -> dict[str, Any]:
    shard_runs = sorted(
        shard_runs,
        key=lambda row: (
            row.get("metadata", {}).get("problem_offset", row.get("problem_offset", 0)),
            row.get("num_problems", 0),
        ),
    )
    merged_results: list[dict[str, Any]] = []
    methods: list[str] = []
    for run in shard_runs:
        merged_results.extend(run.get("results", []))
        if not methods:
            methods = list(run.get("summary", {}).get("methods", {}).keys())
    merged_summary = summarize(merged_results, methods) if merged_results and methods else {"methods": {}, "difficulty": {}, "calibration": {}}
    total_num_problems = sum(run.get("num_problems", 0) for run in shard_runs)
    return {
        "benchmark": benchmark,
        "seed": seed,
        "num_problems": total_num_problems,
        "results": merged_results,
        "summary": merged_summary,
        "merged_from_shards": len(shard_runs),
        "problem_offset_min": min(run.get("metadata", {}).get("problem_offset", run.get("problem_offset", 0)) for run in shard_runs),
    }


def _merge_benchmark_runs(benchmark: str, seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    seed_runs = sorted(seed_runs, key=lambda row: row.get("seed", 0))
    methods = sorted(
        {
            method
            for run in seed_runs
            for method in run.get("summary", {}).get("methods", {}).keys()
        }
    )
    summary_across_seeds: dict[str, Any] = {"methods": {}, "calibration": {}}
    for method in methods:
        accuracies = [
            run["summary"]["methods"][method]["accuracy"]
            for run in seed_runs
            if method in run.get("summary", {}).get("methods", {})
        ]
        if not accuracies:
            continue
        summary_across_seeds["methods"][method] = {
            "accuracy_mean": sum(accuracies) / len(accuracies),
            "accuracy_stderr": _stderr(accuracies),
            "accuracy_by_seed": accuracies,
        }

    for metric_name in ["ece", "mce", "brier", "auroc"]:
        values = [
            run.get("summary", {}).get("calibration", {}).get(metric_name, 0.0)
            for run in seed_runs
        ]
        if values:
            summary_across_seeds["calibration"][metric_name] = {
                "mean": sum(values) / len(values),
                "stderr": _stderr(values),
                "by_seed": values,
            }

    return {
        "benchmark": benchmark,
        "num_problems": seed_runs[0].get("num_problems", 0),
        "num_complete_seed_runs": len(seed_runs),
        "num_seed_runs": len(seed_runs),
        "seed_runs": seed_runs,
        "summary_across_seeds": summary_across_seeds,
        "partial": False,
    }


def merge_results_files(results_files: list[Path]) -> dict[str, Any]:
    by_benchmark_seed: dict[tuple[str, int], list[dict[str, Any]]] = {}
    model = "unknown-model"
    metadata_samples: list[dict[str, Any]] = []
    resolved_files = [resolve_results_path(path) for path in results_files]
    for results_file in resolved_files:
        payload = load_json(results_file)
        metadata = payload.get("metadata", {})
        if metadata.get("model") and metadata.get("model") != "unknown-model":
            model = metadata["model"]
        metadata_samples.append(metadata)
        for benchmark_result in payload.get("benchmarks", []):
            benchmark = benchmark_result["benchmark"]
            if "seed_runs" in benchmark_result:
                runs = benchmark_result["seed_runs"]
            else:
                runs = [benchmark_result]
            for run in runs:
                seed = int(run.get("seed", 0))
                run = dict(run)
                run["metadata"] = dict(payload.get("metadata", {}))
                by_benchmark_seed.setdefault((benchmark, seed), []).append(run)

    by_benchmark: dict[str, list[dict[str, Any]]] = {}
    for (benchmark, seed), shard_runs in sorted(by_benchmark_seed.items()):
        merged_seed_run = _merge_seed_shards(benchmark, seed, shard_runs)
        by_benchmark.setdefault(benchmark, []).append(merged_seed_run)

    merged_benchmarks = [
        _merge_benchmark_runs(benchmark, runs)
        for benchmark, runs in sorted(by_benchmark.items())
    ]
    return {
        "benchmarks": merged_benchmarks,
        "metadata": {
            "source": "merged_seed_results",
            "model": model,
            "results_files": [str(path) for path in resolved_files],
            "num_source_files": len(resolved_files),
            "samples": metadata_samples,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge multiple single-seed results.json files.")
    parser.add_argument(
        "--results-file",
        action="append",
        default=[],
        help="Path to a results-like JSON file. May be passed multiple times.",
    )
    parser.add_argument(
        "--run-dir",
        action="append",
        default=[],
        help="Run directory containing results.json or results_from_progress.json. May be passed multiple times.",
    )
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    results_files = [Path(item) for item in args.results_file] + [Path(item) for item in args.run_dir]
    if not results_files:
        raise SystemExit("Provide at least one --results-file or --run-dir.")
    payload = merge_results_files(results_files)
    output_file = Path(args.output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Merged {len(results_files)} files into {output_file}")


if __name__ == "__main__":
    main()
