#!/usr/bin/env python3
"""Analyze closed-book vs aligned-context vs conflict-context theorem-3 controls."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze theorem-3 control conditions from raw generation rows.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", required=True)
    return parser.parse_args()


def _mean(items: list[float]) -> float:
    return sum(items) / len(items) if items else 0.0


def _group(rows: list[dict[str, Any]]) -> dict[tuple[str, str, int], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["benchmark"]), str(row["condition"]), int(row["cot_length"]))].append(row)
    return grouped


def _metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    outcomes = [float(row.get("outcome", 0.0)) for row in rows]
    confidences = [float(row.get("confidence", 0.5)) for row in rows]
    accuracy = _mean(outcomes)
    mean_confidence = _mean(confidences)
    return {
        "count": len(rows),
        "accuracy": accuracy,
        "mean_confidence": mean_confidence,
        "gap": mean_confidence - accuracy,
    }


def build_analysis(rows: list[dict[str, Any]], *, model: str) -> dict[str, Any]:
    grouped = _group(rows)
    condition_rows = []
    for (benchmark, condition, cot_length), values in sorted(grouped.items()):
        if condition not in {"closed_book", "aligned_context", "conflict_context"}:
            continue
        metrics = _metrics(values)
        condition_rows.append(
            {
                "benchmark": benchmark,
                "condition": condition,
                "cot_length": cot_length,
                **{k: round(v, 4) if isinstance(v, float) else v for k, v in metrics.items()},
            }
        )

    by_benchmark: dict[str, dict[str, dict[int, dict[str, Any]]]] = defaultdict(lambda: defaultdict(dict))
    for row in condition_rows:
        by_benchmark[row["benchmark"]][row["condition"]][int(row["cot_length"])] = row

    trajectories = []
    for benchmark in sorted(by_benchmark):
        row = {"benchmark": benchmark}
        for condition in ("closed_book", "aligned_context", "conflict_context"):
            series = by_benchmark[benchmark].get(condition, {})
            if 0 in series and 128 in series and 1024 in series:
                row[condition] = {
                    "gap_cot_0": series[0]["gap"],
                    "gap_cot_128": series[128]["gap"],
                    "gap_cot_1024": series[1024]["gap"],
                    "delta_0_128": round(series[128]["gap"] - series[0]["gap"], 4),
                    "delta_128_1024": round(series[1024]["gap"] - series[128]["gap"], 4),
                    "delta_0_1024": round(series[1024]["gap"] - series[0]["gap"], 4),
                }
        trajectories.append(row)

    return {
        "model": model,
        "num_rows": len(rows),
        "condition_rows": condition_rows,
        "trajectories": trajectories,
    }


def main() -> None:
    args = parse_args()
    rows = []
    with Path(args.rows_jsonl).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            rows.append(json.loads(stripped))
    analysis = build_analysis(rows, model=args.model)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output_path), "num_rows": len(rows)}, indent=2))


if __name__ == "__main__":
    main()
