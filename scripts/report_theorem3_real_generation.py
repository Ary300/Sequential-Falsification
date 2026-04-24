#!/usr/bin/env python3
"""Render headline theorem-3 metrics from real-generation runs."""

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

from utils.io import dump_json  # noqa: E402
from utils.metrics import accuracy, brier_score, expected_calibration_error  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 real-generation summary artifacts.")
    parser.add_argument("--results-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--short-cot", type=int, default=0)
    parser.add_argument("--long-cot", type=int, default=1024)
    parser.add_argument("--max-samples", type=int, default=5)
    return parser.parse_args()


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in payload.get("experiments", []):
        rows.extend(group.get("rows", []))
    return rows


def _metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    confidences = [float(row.get("confidence", 0.5)) for row in rows]
    outcomes = [int(row.get("outcome", 0)) for row in rows]
    reasoning_words = [int(row.get("reasoning_word_count", 0)) for row in rows]
    response_words = [int(row.get("response_word_count", 0)) for row in rows]
    return {
        "count": len(rows),
        "accuracy": accuracy(bool(item) for item in outcomes),
        "ece": expected_calibration_error(confidences, outcomes),
        "brier": brier_score(confidences, outcomes),
        "mean_confidence": (sum(confidences) / len(confidences)) if confidences else 0.0,
        "mean_reasoning_words": (sum(reasoning_words) / len(reasoning_words)) if reasoning_words else 0.0,
        "mean_response_words": (sum(response_words) / len(response_words)) if response_words else 0.0,
    }


def _sample_rows(rows: list[dict[str, Any]], max_samples: int) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            int(row.get("outcome", 0)),
            -float(row.get("confidence", 0.5)),
            -int(row.get("reasoning_word_count", 0)),
        ),
    )
    out = []
    for row in ranked[:max_samples]:
        out.append(
            {
                "benchmark": row.get("benchmark"),
                "id": row.get("id"),
                "condition": row.get("condition"),
                "cot_length": row.get("cot_length"),
                "confidence": round(float(row.get("confidence", 0.5)), 4),
                "outcome": int(row.get("outcome", 0)),
                "answer": row.get("answer"),
                "reasoning_word_count": int(row.get("reasoning_word_count", 0)),
                "screening_confidence": row.get("metadata", {}).get("screening_confidence"),
                "reasoning_preview": str(row.get("reasoning_text", ""))[:400],
            }
        )
    return out


def build_report(payload: dict[str, Any], *, short_cot: int, long_cot: int, max_samples: int) -> dict[str, Any]:
    rows = _rows(payload)
    by_slice: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("benchmark")), str(row.get("split")), int(row.get("cot_length", 0)))
        by_slice.setdefault(key, []).append(row)

    slice_rows = []
    for (benchmark, split, cot_length), slice_values in sorted(by_slice.items()):
        metrics = _metrics(slice_values)
        slice_rows.append(
            {
                "benchmark": benchmark,
                "split": split,
                "cot_length": cot_length,
                **{key: round(value, 4) if isinstance(value, float) else value for key, value in metrics.items()},
            }
        )

    trend_rows = []
    benchmarks = sorted({str(row.get("benchmark")) for row in rows})
    for benchmark in benchmarks:
        for split in ("conflict", "no_conflict"):
            short_rows = [row for row in rows if row.get("benchmark") == benchmark and row.get("split") == split and int(row.get("cot_length", 0)) == short_cot]
            long_rows = [row for row in rows if row.get("benchmark") == benchmark and row.get("split") == split and int(row.get("cot_length", 0)) == long_cot]
            if not short_rows or not long_rows:
                continue
            short_metrics = _metrics(short_rows)
            long_metrics = _metrics(long_rows)
            trend_rows.append(
                {
                    "benchmark": benchmark,
                    "split": split,
                    "short_cot": short_cot,
                    "long_cot": long_cot,
                    "ece_delta": round(long_metrics["ece"] - short_metrics["ece"], 4),
                    "brier_delta": round(long_metrics["brier"] - short_metrics["brier"], 4),
                    "accuracy_delta": round(long_metrics["accuracy"] - short_metrics["accuracy"], 4),
                    "confidence_delta": round(long_metrics["mean_confidence"] - short_metrics["mean_confidence"], 4),
                    "reasoning_word_delta": round(long_metrics["mean_reasoning_words"] - short_metrics["mean_reasoning_words"], 4),
                }
            )

    conflict_deltas = [row["ece_delta"] for row in trend_rows if row["split"] == "conflict"]
    no_conflict_deltas = [row["ece_delta"] for row in trend_rows if row["split"] == "no_conflict"]

    samples = {
        benchmark: _sample_rows(
            [
                row
                for row in rows
                if row.get("benchmark") == benchmark and row.get("split") == "conflict" and int(row.get("cot_length", 0)) == long_cot
            ],
            max_samples=max_samples,
        )
        for benchmark in benchmarks
    }

    return {
        "metadata": payload.get("metadata", {}),
        "coverage": {
            "benchmarks": benchmarks,
            "num_rows": len(rows),
            "num_groups": len(payload.get("experiments", [])),
        },
        "headline": {
            "mean_conflict_ece_delta": round(sum(conflict_deltas) / len(conflict_deltas), 4) if conflict_deltas else None,
            "mean_no_conflict_ece_delta": round(sum(no_conflict_deltas) / len(no_conflict_deltas), 4) if no_conflict_deltas else None,
            "mean_conflict_reasoning_word_delta": round(
                sum(row["reasoning_word_delta"] for row in trend_rows if row["split"] == "conflict")
                / len([row for row in trend_rows if row["split"] == "conflict"]),
                4,
            )
            if any(row["split"] == "conflict" for row in trend_rows)
            else None,
        },
        "slice_rows": slice_rows,
        "trend_rows": trend_rows,
        "samples": samples,
    }


def build_markdown(report: dict[str, Any]) -> str:
    headline = report.get("headline", {})
    lines = [
        "# Theorem 3 Real-Generation Report",
        "",
        f"- Benchmarks: {', '.join(f'`{item}`' for item in report.get('coverage', {}).get('benchmarks', []))}",
        f"- Parsed rows: `{report.get('coverage', {}).get('num_rows', 0)}`",
        f"- Parsed groups: `{report.get('coverage', {}).get('num_groups', 0)}`",
        "",
        "## Headline",
        "",
        f"- Mean conflict ECE delta: `{headline.get('mean_conflict_ece_delta')}`",
        f"- Mean no-conflict ECE delta: `{headline.get('mean_no_conflict_ece_delta')}`",
        f"- Mean conflict reasoning-word delta: `{headline.get('mean_conflict_reasoning_word_delta')}`",
        "",
        "## Slice Metrics",
        "",
        "| Benchmark | Split | CoT | Count | Accuracy | ECE | Brier | Mean conf | Mean reasoning words |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("slice_rows", []):
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['cot_length']} | {row['count']} | "
            f"{row['accuracy']:.4f} | {row['ece']:.4f} | {row['brier']:.4f} | "
            f"{row['mean_confidence']:.4f} | {row['mean_reasoning_words']:.2f} |"
        )

    lines.extend(
        [
            "",
            "## Short-to-Long Deltas",
            "",
            "| Benchmark | Split | ECE delta | Brier delta | Accuracy delta | Confidence delta | Reasoning-word delta |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("trend_rows", []):
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['ece_delta']:.4f} | {row['brier_delta']:.4f} | "
            f"{row['accuracy_delta']:.4f} | {row['confidence_delta']:.4f} | {row['reasoning_word_delta']:.2f} |"
        )

    lines.extend(["", "## Sample Conflict Long-CoT Traces", ""])
    for benchmark, rows in report.get("samples", {}).items():
        lines.append(f"### `{benchmark}`")
        if not rows:
            lines.append("")
            lines.append("No sampled rows.")
            lines.append("")
            continue
        for row in rows:
            lines.append(
                f"- `{row['id']}`: conf `{row['confidence']:.4f}`, outcome `{row['outcome']}`, "
                f"reasoning words `{row['reasoning_word_count']}`, screening `{row['screening_confidence']}`"
            )
            lines.append(f"  answer: {row['answer']}")
            lines.append(f"  reasoning: {row['reasoning_preview']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = json.loads(Path(args.results_file).read_text(encoding="utf-8"))
    report = build_report(payload, short_cot=args.short_cot, long_cot=args.long_cot, max_samples=args.max_samples)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(report, output_dir / "theorem3_summary.json")
    (output_dir / "summary.md").write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "summary_json": str(output_dir / "theorem3_summary.json")}, indent=2))


if __name__ == "__main__":
    main()
