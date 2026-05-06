"""Summarize Priority-1 falsification-vs-baseline pilot results.

The purpose is deliberately narrow: before launching a broad NeurIPS-scale
matrix, check whether the fixed sequential falsification path separates from
generated-test filtering and self-debug on the rows that previously threatened
the paper's novelty story.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TARGET_METHODS = ["generated_test_filter", "self_debug", "falsification", "oracle"]


def _load_payload(path: Path) -> dict[str, Any] | None:
    if path.is_dir():
        for candidate in [path / "results.json", path / "results_from_progress.json"]:
            if candidate.exists():
                path = candidate
                break
        else:
            progress = sorted(path.glob("*_progress.json"))
            if not progress:
                return None
            path = progress[-1]
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _method_accuracy(summary: dict[str, Any], method: str) -> float | None:
    methods = summary.get("methods", {})
    if method not in methods:
        return None
    value = methods[method]
    if "accuracy_mean" in value:
        return float(value["accuracy_mean"])
    return float(value.get("accuracy", 0.0))


def _iter_benchmark_summaries(payload: dict[str, Any]) -> list[tuple[str, dict[str, Any], int | None]]:
    if "summary" in payload:
        return [(str(payload.get("benchmark", "unknown")), payload["summary"], payload.get("num_problems_completed", payload.get("num_problems")))]
    rows = []
    for benchmark in payload.get("benchmarks", []):
        if "summary_across_seeds" in benchmark:
            rows.append((benchmark.get("benchmark", "unknown"), benchmark["summary_across_seeds"], benchmark.get("num_problems")))
        elif "summary" in benchmark:
            rows.append((benchmark.get("benchmark", "unknown"), benchmark["summary"], benchmark.get("num_problems")))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Result files or run directories to summarize.")
    parser.add_argument("--min-margin", type=float, default=0.02, help="Required falsification margin over generated-test-filter.")
    args = parser.parse_args()

    any_failure = False
    for raw_path in args.paths:
        path = Path(raw_path)
        payload = _load_payload(path)
        if payload is None:
            print(f"{path}: no results found")
            any_failure = True
            continue

        for benchmark, summary, n_problems in _iter_benchmark_summaries(payload):
            values = {method: _method_accuracy(summary, method) for method in TARGET_METHODS}
            fals = values.get("falsification")
            gtf = values.get("generated_test_filter")
            sd = values.get("self_debug")
            oracle = values.get("oracle")
            print(f"\n{path} :: {benchmark} ({n_problems or '?'} problems)")
            for method in TARGET_METHODS:
                value = values.get(method)
                print(f"  {method:22s} {value * 100:6.2f}%" if value is not None else f"  {method:22s}   --")
            if fals is not None and gtf is not None:
                margin = fals - gtf
                print(f"  falsification - generated_test_filter: {margin * 100:+.2f} pp")
                if margin < args.min_margin:
                    any_failure = True
            if fals is not None and sd is not None:
                print(f"  falsification - self_debug:           {(fals - sd) * 100:+.2f} pp")
            if fals is not None and oracle is not None and oracle > 0:
                print(f"  oracle recovered:                      {(fals / oracle) * 100:.1f}%")

    if any_failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
