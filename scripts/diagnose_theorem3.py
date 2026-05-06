#!/usr/bin/env python3
"""Diagnose theorem-3 calibration behavior on arbitration result files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose theorem-3 disagreement in arbitration results.")
    parser.add_argument("--results-file", required=True, help="Path to arbitration result JSON.")
    parser.add_argument("--output-dir", required=True, help="Directory for diagnosis artifacts.")
    parser.add_argument("--low", type=float, default=0.2, help="Lower bound for genuine-conflict parametric score.")
    parser.add_argument("--high", type=float, default=0.8, help="Upper bound for genuine-conflict parametric score.")
    parser.add_argument("--short-cot", default="0", help="Short-CoT bucket to compare.")
    parser.add_argument("--long-cot", default="4096", help="Long-CoT bucket to compare.")
    parser.add_argument("--max-samples", type=int, default=10, help="Max sampled examples per benchmark bucket.")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for group in payload.get("experiments", []):
        rows.extend(group.get("rows", []))
    return rows


def ece(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    probs = [float(row["policies"]["simulated_model"]["probability"]) for row in rows]
    labels = [int(row["label"]) for row in rows]
    pairs = sorted(zip(probs, labels), key=lambda item: item[0])
    n = len(pairs)
    bucket = max(1, n // 15)
    total = 0.0
    for index in range(0, n, bucket):
        chunk = pairs[index : index + bucket]
        mean_prob = sum(prob for prob, _ in chunk) / len(chunk)
        mean_label = sum(label for _, label in chunk) / len(chunk)
        total += len(chunk) / n * abs(mean_prob - mean_label)
    return total


def ambiguity_bucket(row: dict[str, Any], low: float, high: float) -> str:
    parametric = float(row["features"].get("parametric_score", 0.5))
    if low <= parametric <= high:
        return "genuine_conflict"
    if parametric > high:
        return "easy_high_confidence"
    return "easy_low_confidence"


def family_key(row: dict[str, Any]) -> str:
    return str(row.get("metadata", {}).get("conflict_family") or "all")


def summarize_delta(short_rows: list[dict[str, Any]], long_rows: list[dict[str, Any]]) -> dict[str, Any]:
    short_ece = ece(short_rows)
    long_ece = ece(long_rows)
    return {
        "count_short": len(short_rows),
        "count_long": len(long_rows),
        "ece_short": round(short_ece, 4),
        "ece_long": round(long_ece, 4),
        "ece_delta": round(long_ece - short_ece, 4),
        "mean_parametric_score": round(
            statistics.mean(float(row["features"].get("parametric_score", 0.5)) for row in short_rows),
            4,
        )
        if short_rows
        else None,
        "mean_context_reliability": round(
            statistics.mean(float(row["features"].get("context_reliability", 0.5)) for row in short_rows),
            4,
        )
        if short_rows
        else None,
    }


def sample_wrong_way_examples(
    rows: list[dict[str, Any]],
    *,
    benchmark: str,
    long_cot: str,
    bucket: str,
    low: float,
    high: float,
    max_samples: int,
) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in rows
        if row["benchmark"] == benchmark
        and row["condition"] == "conflict_context"
        and str(row["cot_length"]) == long_cot
        and ambiguity_bucket(row, low, high) == bucket
    ]
    candidates.sort(
        key=lambda row: abs(float(row["model_context_probability"]) - float(row["oracle_context_probability"])),
        reverse=True,
    )
    sampled = []
    for row in candidates[:max_samples]:
        sampled.append(
            {
                "id": row.get("id"),
                "question": row.get("question"),
                "benchmark": row["benchmark"],
                "model": row["model"],
                "condition": row["condition"],
                "split": row["split"],
                "cot_length": row["cot_length"],
                "oracle_context_probability": round(float(row["oracle_context_probability"]), 4),
                "model_context_probability": round(float(row["model_context_probability"]), 4),
                "parametric_score": round(float(row["features"].get("parametric_score", 0.5)), 4),
                "contextual_score": round(float(row["features"].get("contextual_score", 0.5)), 4),
                "conflict_magnitude": round(float(row["features"].get("conflict_magnitude", 0.5)), 4),
                "context_correct": bool(row["features"].get("context_correct", False)),
                "parametric_correct": bool(row["features"].get("parametric_correct", False)),
                "conflict_family": row.get("metadata", {}).get("conflict_family"),
                "conflict_claim": row.get("metadata", {}).get("conflict_claim"),
                "default_claim": row.get("metadata", {}).get("default_claim"),
            }
        )
    return sampled


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(Path(args.results_file))
    low = float(args.low)
    high = float(args.high)
    short_cot = str(args.short_cot)
    long_cot = str(args.long_cot)

    by_benchmark: dict[str, Any] = {}
    for benchmark in sorted({row["benchmark"] for row in rows}):
        benchmark_rows = [row for row in rows if row["benchmark"] == benchmark]
        benchmark_summary: dict[str, Any] = {"overall": {}, "by_ambiguity": {}, "by_family": {}}

        short_rows = [
            row
            for row in benchmark_rows
            if row["condition"] == "conflict_context" and str(row["cot_length"]) == short_cot
        ]
        long_rows = [
            row
            for row in benchmark_rows
            if row["condition"] == "conflict_context" and str(row["cot_length"]) == long_cot
        ]
        benchmark_summary["overall"] = summarize_delta(short_rows, long_rows)

        for bucket in ["genuine_conflict", "easy_high_confidence", "easy_low_confidence"]:
            short_bucket = [row for row in short_rows if ambiguity_bucket(row, low, high) == bucket]
            long_bucket = [row for row in long_rows if ambiguity_bucket(row, low, high) == bucket]
            if short_bucket and long_bucket:
                benchmark_summary["by_ambiguity"][bucket] = summarize_delta(short_bucket, long_bucket)

        for conflict_family in sorted({family_key(row) for row in benchmark_rows if row["condition"] == "conflict_context"}):
            short_family = [row for row in short_rows if family_key(row) == conflict_family]
            long_family = [row for row in long_rows if family_key(row) == conflict_family]
            if short_family and long_family:
                benchmark_summary["by_family"][conflict_family] = summarize_delta(short_family, long_family)

        by_benchmark[benchmark] = benchmark_summary

    samples = {
        benchmark: sample_wrong_way_examples(
            rows,
            benchmark=benchmark,
            long_cot=long_cot,
            bucket="genuine_conflict",
            low=low,
            high=high,
            max_samples=args.max_samples,
        )
        for benchmark in sorted({row["benchmark"] for row in rows})
    }

    summary = {
        "results_file": str(args.results_file),
        "short_cot": short_cot,
        "long_cot": long_cot,
        "ambiguity_interval": [low, high],
        "by_benchmark": by_benchmark,
        "samples": samples,
        "notes": [
            "This diagnosis uses proxy arbitration rows, not raw generated reasoning traces.",
            "A positive theorem-3 result requires conflict-context ECE to increase on genuinely ambiguous rows.",
            "If a benchmark stays negative after ambiguity filtering, it likely behaves more like detectable corruption than genuine source ambiguity.",
        ],
    }

    lines = [
        "# Theorem 3 Diagnosis",
        "",
        f"- Results file: `{args.results_file}`",
        f"- Genuine-conflict filter: `parametric_score in [{low:.2f}, {high:.2f}]`",
        f"- CoT comparison: `{short_cot}` -> `{long_cot}`",
        "",
        "## Benchmark Summary",
        "",
        "| Benchmark | Overall delta | Genuine-conflict delta | Notes |",
        "| --- | ---: | ---: | --- |",
    ]
    for benchmark, benchmark_summary in by_benchmark.items():
        overall_delta = benchmark_summary["overall"].get("ece_delta")
        genuine_delta = benchmark_summary["by_ambiguity"].get("genuine_conflict", {}).get("ece_delta")
        note_parts = []
        family_summary = benchmark_summary["by_family"]
        if family_summary:
            family_note = ", ".join(f"{name}: {values['ece_delta']:+.4f}" for name, values in family_summary.items())
            note_parts.append(f"families {family_note}")
        lines.append(
            f"| `{benchmark}` | `{overall_delta:+.4f}` | "
            f"`{genuine_delta:+.4f}` | {'; '.join(note_parts) if note_parts else 'n/a'} |"
        )
    lines.extend(["", "## Sampled Wrong-Way Examples", ""])
    for benchmark, sampled_rows in samples.items():
        lines.append(f"### `{benchmark}`")
        if not sampled_rows:
            lines.append("")
            lines.append("No sampled rows available.")
            lines.append("")
            continue
        for row in sampled_rows:
            lines.append(
                f"- `{row['id']}`: oracle `{row['oracle_context_probability']:.4f}` vs model "
                f"`{row['model_context_probability']:.4f}`, param `{row['parametric_score']:.4f}`, "
                f"family `{row.get('conflict_family')}`"
            )
            lines.append(f"  question: {row['question']}")
        lines.append("")
    markdown = "\n".join(lines)

    dump_json(summary, output_dir / "theorem3_diagnosis.json")
    (output_dir / "summary.md").write_text(markdown, encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "json": str(output_dir / 'theorem3_diagnosis.json')}, indent=2))


if __name__ == "__main__":
    main()
