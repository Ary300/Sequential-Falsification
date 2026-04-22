"""Collect per-seed progress JSON files into a reportable results payload."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from utils.io import dump_json
except ModuleNotFoundError:  # pragma: no cover - package import fallback
    from .utils.io import dump_json


PROGRESS_RE = re.compile(r"(?P<benchmark>.+)_seed(?P<seed>\d+)_progress\.json$")


def _stderr(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return (variance ** 0.5) / (len(values) ** 0.5)


def _is_complete(run: dict[str, Any]) -> bool:
    completed = run.get("num_problems_completed")
    total = run.get("num_problems_total", run.get("num_problems"))
    if completed is not None and total is not None:
        return completed >= total
    results = run.get("results", [])
    return bool(total) and len(results) >= total


def _infer_model_name(run: dict[str, Any]) -> str:
    for problem in run.get("results", []):
        for method_result in problem.get("methods", {}).values():
            selected = method_result.get("selected")
            if selected and selected.get("model"):
                return selected["model"]
            for record in method_result.get("records", []):
                if record.get("model"):
                    return record["model"]
    return run.get("model", "unknown-model")


def _combine_seed_runs(benchmark: str, seed_runs: list[dict[str, Any]]) -> dict[str, Any]:
    complete_runs = [run for run in seed_runs if _is_complete(run)]
    runs_for_stats = complete_runs or seed_runs
    methods = sorted(
        {
            method
            for run in runs_for_stats
            for method in run.get("summary", {}).get("methods", {}).keys()
        }
    )
    summary_across_seeds: dict[str, Any] = {"methods": {}, "calibration": {}}
    for method in methods:
        accuracies = [
            run["summary"]["methods"][method]["accuracy"]
            for run in runs_for_stats
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
            for run in runs_for_stats
        ]
        if values:
            summary_across_seeds["calibration"][metric_name] = {
                "mean": sum(values) / len(values),
                "stderr": _stderr(values),
                "by_seed": values,
            }

    return {
        "benchmark": benchmark,
        "num_problems": runs_for_stats[0].get("num_problems_total", runs_for_stats[0].get("num_problems", 0)),
        "num_problems_completed_max": max(
            run.get("num_problems_completed", len(run.get("results", []))) for run in seed_runs
        ),
        "num_complete_seed_runs": len(complete_runs),
        "num_seed_runs": len(seed_runs),
        "seed_runs": seed_runs,
        "summary_across_seeds": summary_across_seeds,
        "partial": len(complete_runs) != len(seed_runs),
    }


def collect_progress(progress_dir: Path) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(progress_dir.glob("*_seed*_progress.json")):
        match = PROGRESS_RE.match(path.name)
        if not match:
            continue
        benchmark = match.group("benchmark")
        seed = int(match.group("seed"))
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.setdefault("benchmark", benchmark)
        payload.setdefault("seed", seed)
        grouped.setdefault(benchmark, []).append(payload)

    benchmarks = []
    for benchmark, runs in sorted(grouped.items()):
        runs.sort(key=lambda item: item.get("seed", 0))
        benchmarks.append(_combine_seed_runs(benchmark, runs))
    model = "unknown-model"
    if benchmarks and grouped:
        first_runs = next(iter(grouped.values()))
        if first_runs:
            model = _infer_model_name(first_runs[0])
    return {
        "benchmarks": benchmarks,
        "metadata": {
            "source": "progress_files",
            "progress_dir": str(progress_dir),
            "partial": any(item.get("partial", False) for item in benchmarks),
            "model": model,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect progress JSON files into a results-like payload.")
    parser.add_argument("--progress-dir", default="results/full_delta")
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    progress_dir = Path(args.progress_dir)
    payload = collect_progress(progress_dir)
    output_file = Path(args.output_file) if args.output_file else progress_dir / "results_from_progress.json"
    dump_json(payload, output_file)
    print(f"Wrote {len(payload['benchmarks'])} benchmark payloads to {output_file}")


if __name__ == "__main__":
    main()
