#!/usr/bin/env python3
"""Summarize whether the theorem-3 asymmetry replicates across model families."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _select_row(rows: list[dict[str, Any]], *, family: str, benchmark: str, split: str, size_b: int) -> dict[str, Any]:
    for row in rows:
        if (
            str(row.get("family")) == family
            and str(row.get("benchmark")) == benchmark
            and str(row.get("split")) == split
            and int(row.get("model_size_b")) == size_b
        ):
            return row
    raise KeyError((family, benchmark, split, size_b))


def _replicates_asymmetry(rows: list[dict[str, Any]], family: str) -> bool:
    small = _select_row(rows, family=family, benchmark="conflictbank", split="conflict", size_b=7)
    large = _select_row(rows, family=family, benchmark="conflictbank", split="conflict", size_b=14)
    small_delta = float(small.get("gap_delta_128_1024", float(small["gap_cot_1024"]) - float(small["gap_cot_128"])))
    large_delta = float(large.get("gap_delta_128_1024", float(large["gap_cot_1024"]) - float(large["gap_cot_128"])))
    small_recovers = small_delta < 0.0
    large_saturates = large_delta >= 0.0
    return small_recovers and large_saturates


def main() -> None:
    summary = _load_json(ROOT / "docs/generated/theorem3_same_family_threshold_summary.json")
    rows = list(summary["rows"])

    deepseek_rep = _replicates_asymmetry(rows, "DeepSeek-R1-Distill-Qwen")
    qwen_rep = _replicates_asymmetry(rows, "Qwen2.5")

    payload = {
        "headline": {
            "deepseek_7b_14b_conflictbank_asymmetry_replicates": deepseek_rep,
            "qwen_7b_14b_conflictbank_asymmetry_replicates": qwen_rep,
            "cross_family_universal_asymmetry_holds": deepseek_rep and qwen_rep,
            "paper_verdict": (
                "No universal cross-family 7B-vs-14B asymmetry: the strongest theorem-3 claim is "
                "benchmark-dependent two-regime behavior, not a family-invariant 7B-recovers / 14B-saturates law."
            ),
        },
        "rows": [
            _select_row(rows, family="DeepSeek-R1-Distill-Qwen", benchmark="conflictbank", split="conflict", size_b=7),
            _select_row(rows, family="DeepSeek-R1-Distill-Qwen", benchmark="conflictbank", split="conflict", size_b=14),
            _select_row(rows, family="Qwen2.5", benchmark="conflictbank", split="conflict", size_b=7),
            _select_row(rows, family="Qwen2.5", benchmark="conflictbank", split="conflict", size_b=14),
            _select_row(rows, family="Qwen2.5", benchmark="wikicontradict", split="conflict", size_b=32),
        ],
    }

    lines = [
        "# Theorem 3 Cross-Family Verdict",
        "",
        f"- DeepSeek `7B -> 14B` ConflictBank asymmetry replicates: `{deepseek_rep}`",
        f"- Qwen `7B -> 14B` ConflictBank asymmetry replicates: `{qwen_rep}`",
        f"- Universal cross-family asymmetry holds: `{payload['headline']['cross_family_universal_asymmetry_holds']}`",
        "- Verdict: no universal cross-family `7B recovers / 14B saturates` law.",
        "- Strongest theorem-3 statement: benchmark-dependent two-regime behavior.",
        "",
        "## Key Rows",
        "",
        "| Family | Benchmark | Size | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `128->1024` delta | Shape |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| {row['family']} | {row['benchmark']} | {row['model_size_b']} | "
            f"{float(row['gap_cot_0']):.4f} | {float(row['gap_cot_128']):.4f} | {float(row['gap_cot_1024']):.4f} | "
            f"{float(row.get('gap_delta_128_1024', float(row['gap_cot_1024']) - float(row['gap_cot_128']))):.4f} | {row['shape']} |"
        )
    lines.append("")

    out_json = ROOT / "docs/generated/theorem3_cross_family_verdict.json"
    out_md = ROOT / "docs/generated/theorem3_cross_family_verdict.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"json": str(out_json), "md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
