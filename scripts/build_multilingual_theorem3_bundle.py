#!/usr/bin/env python3
"""Aggregate multilingual theorem-3 run summaries into one bundle."""

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


DEFAULT_RUNS = ",".join(
    [
        "mistral_5lang=results/mistral7b_theorem3_multilingual_v1/theorem3_report/theorem3_summary.json",
        "gemma9_5lang=results/gemma9b_theorem3_multilingual_v1/theorem3_report/theorem3_summary.json",
        "mistral_ja=results/mistral7b_theorem3_multilingual_ja_v1/theorem3_report/theorem3_summary.json",
        "mistral_ar=results/mistral7b_theorem3_multilingual_ar_v1/theorem3_report/theorem3_summary.json",
        "mistral_fr=results/mistral7b_theorem3_multilingual_fr_v1/theorem3_report/theorem3_summary.json",
        "mistral_pt=results/mistral7b_theorem3_multilingual_pt_v1/theorem3_report/theorem3_summary.json",
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a multilingual theorem-3 summary bundle.")
    parser.add_argument("--runs", default=DEFAULT_RUNS)
    parser.add_argument(
        "--output-prefix",
        default=str(ROOT / "docs/generated/multilingual_theorem3_results_bundle"),
    )
    return parser.parse_args()


def parse_runs(spec: str) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for chunk in spec.split(","):
        item = chunk.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Invalid run spec: {item}")
        label, raw_path = item.split("=", 1)
        out.append((label.strip(), ROOT / raw_path.strip()))
    return out


def load_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_run(label: str, payload: dict[str, Any] | None, path: Path) -> dict[str, Any]:
    if payload is None:
        return {
            "label": label,
            "status": "missing",
            "summary_path": str(path.relative_to(ROOT)),
        }
    headline = payload.get("headline", {}) or {}
    coverage = payload.get("coverage", {}) or {}
    metadata = payload.get("metadata", {}) or {}
    screening = metadata.get("screening", {}) or {}
    return {
        "label": label,
        "status": "ready",
        "summary_path": str(path.relative_to(ROOT)),
        "benchmarks": coverage.get("benchmarks", []),
        "num_rows": coverage.get("num_rows"),
        "mean_conflict_ece_delta": headline.get("mean_conflict_ece_delta"),
        "mean_no_conflict_ece_delta": headline.get("mean_no_conflict_ece_delta"),
        "conflict_minus_no_conflict_ece_delta": headline.get("conflict_minus_no_conflict_ece_delta"),
        "mean_conflict_overconfidence_gap_delta": headline.get("mean_conflict_overconfidence_gap_delta"),
        "mean_no_conflict_overconfidence_gap_delta": headline.get("mean_no_conflict_overconfidence_gap_delta"),
        "screening_keys": sorted(screening.keys()),
    }


def build_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ready = [row for row in rows if row.get("status") == "ready"]
    diffs = [
        float(row["conflict_minus_no_conflict_ece_delta"])
        for row in ready
        if row.get("conflict_minus_no_conflict_ece_delta") is not None
    ]
    conflict = [
        float(row["mean_conflict_ece_delta"])
        for row in ready
        if row.get("mean_conflict_ece_delta") is not None
    ]
    no_conflict = [
        float(row["mean_no_conflict_ece_delta"])
        for row in ready
        if row.get("mean_no_conflict_ece_delta") is not None
    ]
    return {
        "headline": {
            "runs_total": len(rows),
            "runs_ready": len(ready),
            "mean_conflict_minus_no_conflict_ece_delta": round(sum(diffs) / len(diffs), 4) if diffs else None,
            "mean_conflict_ece_delta": round(sum(conflict) / len(conflict), 4) if conflict else None,
            "mean_no_conflict_ece_delta": round(sum(no_conflict) / len(no_conflict), 4) if no_conflict else None,
        },
        "runs": rows,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    headline = payload["headline"]
    lines = [
        "# Multilingual Theorem-3 Results Bundle",
        "",
        f"- runs total: `{headline['runs_total']}`",
        f"- runs ready: `{headline['runs_ready']}`",
        f"- mean conflict-minus-no-conflict ECE delta: `{headline['mean_conflict_minus_no_conflict_ece_delta']}`",
        f"- mean conflict ECE delta: `{headline['mean_conflict_ece_delta']}`",
        f"- mean no-conflict ECE delta: `{headline['mean_no_conflict_ece_delta']}`",
        "",
        "| Run | Status | Benchmarks | Rows | Conflict | No-conflict | Delta |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["runs"]:
        lines.append(
            "| "
            f"{row['label']} | {row['status']} | "
            f"{', '.join(row.get('benchmarks', [])) if row.get('benchmarks') else '-'} | "
            f"{row.get('num_rows', '-') if row.get('num_rows') is not None else '-'} | "
            f"{row.get('mean_conflict_ece_delta', '-') if row.get('mean_conflict_ece_delta') is not None else '-'} | "
            f"{row.get('mean_no_conflict_ece_delta', '-') if row.get('mean_no_conflict_ece_delta') is not None else '-'} | "
            f"{row.get('conflict_minus_no_conflict_ece_delta', '-') if row.get('conflict_minus_no_conflict_ece_delta') is not None else '-'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    runs = parse_runs(args.runs)
    rows = [summarize_run(label, load_summary(path), path) for label, path in runs]
    payload = build_payload(rows)
    output_prefix = Path(args.output_prefix)
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_json": str(output_prefix.with_suffix(".json")),
                "output_md": str(output_prefix.with_suffix(".md")),
                "runs_ready": payload["headline"]["runs_ready"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
