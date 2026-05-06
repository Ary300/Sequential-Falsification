#!/usr/bin/env python3
"""Build a same-family theorem-3 threshold summary from DeepSeek and Qwen runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model_size_b(model: str) -> int:
    lower = model.lower()
    for token in ("32b", "14b", "13b", "8b", "7b"):
        if token in lower:
            return int(token[:-1])
    return 0


def _pretty_model(model: str) -> str:
    if "Qwen/Qwen2.5-" in model:
        return model.replace("Qwen/Qwen2.5-", "Qwen2.5-").replace("-Instruct", "")
    if "deepseek-ai/DeepSeek-R1-Distill-Qwen-" in model:
        return model.replace("deepseek-ai/DeepSeek-R1-Distill-Qwen-", "DeepSeek-R1-Distill-Qwen-")
    return model


def _classify_shape(g0: float, g128: float, g1024: float) -> str:
    if g128 > g0 and g1024 < g128:
        if g1024 < g0:
            return "peak_then_full_recovery"
        return "peak_then_partial_recovery"
    if g128 > g0 and g1024 >= g128:
        return "persistent_or_saturating"
    if g128 <= g0 and g1024 <= g128:
        return "monotone_improving"
    return "mixed"


def _is_recovery_row(row: dict[str, Any], min_drop: float = 0.03) -> bool:
    return (
        row["shape"] in {"peak_then_partial_recovery", "peak_then_full_recovery"}
        and (float(row["gap_cot_128"]) - float(row["gap_cot_1024"])) >= min_drop
    )


def _is_conflict_persistent(row: dict[str, Any], min_long_gap: float = 0.85) -> bool:
    return float(row["gap_cot_1024"]) >= min_long_gap


def _collect_rows() -> list[dict[str, Any]]:
    deepseek = _load_json(ROOT / "docs/generated/theorem3_deepseek_family_sweep.json")
    qwen = _load_json(ROOT / "docs/generated/theorem3_qwen_family_final.json")

    rows: list[dict[str, Any]] = []
    for row in deepseek["rows"]:
        enriched = dict(row)
        enriched["family"] = "DeepSeek-R1-Distill-Qwen"
        enriched["model_pretty"] = _pretty_model(enriched["model"])
        enriched["model_size_b"] = _model_size_b(enriched["model"])
        enriched["status"] = "final"
        enriched["shape"] = _classify_shape(
            float(enriched["gap_cot_0"]),
            float(enriched["gap_cot_128"]),
            float(enriched["gap_cot_1024"]),
        )
        rows.append(enriched)

    for row in qwen["rows"]:
        enriched = dict(row)
        enriched["family"] = "Qwen2.5"
        enriched["model_pretty"] = _pretty_model(enriched["model"])
        enriched["model_size_b"] = _model_size_b(enriched["model"])
        enriched["shape"] = _classify_shape(
            float(enriched["gap_cot_0"]),
            float(enriched["gap_cot_128"]),
            float(enriched["gap_cot_1024"]),
        )
        rows.append(enriched)
    return rows


def _family_rows(rows: list[dict[str, Any]], family: str, benchmark: str, split: str) -> list[dict[str, Any]]:
    return sorted(
        [row for row in rows if row["family"] == family and row["benchmark"] == benchmark and row["split"] == split],
        key=lambda row: int(row["model_size_b"]),
    )


def _recovery_threshold(rows: list[dict[str, Any]], family: str, benchmark: str, split: str) -> int | None:
    for row in _family_rows(rows, family, benchmark, split):
        if _is_recovery_row(row):
            return int(row["model_size_b"])
    return None


def _persistent_models(rows: list[dict[str, Any]], family: str, benchmark: str, split: str) -> list[int]:
    out: list[int] = []
    for row in _family_rows(rows, family, benchmark, split):
        if _is_conflict_persistent(row):
            out.append(int(row["model_size_b"]))
    return out


def build_summary() -> dict[str, Any]:
    rows = _collect_rows()
    headline = {
        "qwen_wikicontradict_conflict_recovery_threshold_b": _recovery_threshold(
            rows, "Qwen2.5", "wikicontradict", "conflict"
        ),
        "qwen_conflictbank_conflict_recovery_threshold_b": _recovery_threshold(
            rows, "Qwen2.5", "conflictbank", "conflict"
        ),
        "qwen_conflictbank_conflict_persistent_models_b": _persistent_models(
            rows, "Qwen2.5", "conflictbank", "conflict"
        ),
        "deepseek_wikicontradict_conflict_recovery_threshold_b": _recovery_threshold(
            rows, "DeepSeek-R1-Distill-Qwen", "wikicontradict", "conflict"
        ),
        "deepseek_conflictbank_conflict_recovery_threshold_b": _recovery_threshold(
            rows, "DeepSeek-R1-Distill-Qwen", "conflictbank", "conflict"
        ),
        "deepseek_conflictbank_conflict_persistent_models_b": _persistent_models(
            rows, "DeepSeek-R1-Distill-Qwen", "conflictbank", "conflict"
        ),
    }
    return {
        "as_of": "2026-04-26",
        "families": sorted({row["family"] for row in rows}),
        "rows": rows,
        "headline": headline,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    h = summary["headline"]
    lines = [
        "# Theorem 3 Same-Family Threshold Summary",
        "",
        "## Headline Read",
        "",
        f"- Same-family `Qwen2.5` naturalistic-contradiction recovery first appears at approximately `{h['qwen_wikicontradict_conflict_recovery_threshold_b']}B` on `WikiContradict` conflict.",
        f"- Same-family `Qwen2.5` controlled-conflict recovery has **not** appeared through the currently observed `32B` scale on `ConflictBank` conflict: threshold = `{h['qwen_conflictbank_conflict_recovery_threshold_b']}`.",
        f"- Same-family `Qwen2.5` controlled-conflict persistence above `0.85` long-CoT gap holds at scales `{h['qwen_conflictbank_conflict_persistent_models_b']}`.",
        f"- `DeepSeek-R1-Distill-Qwen` recovers on `WikiContradict` by `{h['deepseek_wikicontradict_conflict_recovery_threshold_b']}B`, but the `ConflictBank` family splits by scale: recovery at `{h['deepseek_conflictbank_conflict_recovery_threshold_b']}B`, persistence at `{h['deepseek_conflictbank_conflict_persistent_models_b']}`.",
        "",
        "## Per-Slice Shapes",
        "",
        "| Family | Model | Benchmark | Split | `cot=0` | `cot=128` | `cot=1024` | Shape | Status |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in sorted(
        summary["rows"],
        key=lambda row: (row["family"], row["benchmark"], row["split"], int(row["model_size_b"])),
    ):
        lines.append(
            f"| {row['family']} | {row['model_pretty']} | {row['benchmark']} | {row['split']} | "
            f"{row['gap_cot_0']:.4f} | {row['gap_cot_128']:.4f} | {row['gap_cot_1024']:.4f} | "
            f"{row['shape']} | {row['status']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    out_json = ROOT / "docs/generated/theorem3_same_family_threshold_summary.json"
    out_md = ROOT / "docs/generated/theorem3_same_family_threshold_summary.md"
    out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"output_json": str(out_json), "output_md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
