#!/usr/bin/env python3
"""Isolate the marginal conflict penalty in theorem-3 gap trajectories."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    conflict = json.loads((ROOT / "docs/generated/theorem3_real_14b_final.json").read_text(encoding="utf-8"))
    yoon = json.loads((ROOT / "docs/generated/yoon_real_contrast_note.json").read_text(encoding="utf-8"))

    conflict_row = next(row for row in conflict["rows"] if row["benchmark"] == "conflictbank" and row["split"] == "conflict")
    noconf_row = next(row for row in conflict["rows"] if row["benchmark"] == "conflictbank" and row["split"] == "no_conflict")
    headline = yoon["headline"]

    payload = {
        "headline": {
            "conflict_minus_no_conflict_gap_cot0": round(conflict_row["gap_cot_0"] - noconf_row["gap_cot_0"], 4),
            "conflict_minus_no_conflict_gap_cot128": round(conflict_row["gap_cot_128"] - noconf_row["gap_cot_128"], 4),
            "conflict_minus_no_conflict_gap_cot1024": round(conflict_row["gap_cot_1024"] - noconf_row["gap_cot_1024"], 4),
            "conflict_minus_triviaqa_gap_cot128": round(headline["conflictbank_gap_short"] - headline["triviaqa_gap_short"], 4),
            "conflict_minus_triviaqa_gap_cot1024": round(headline["conflictbank_gap_long"] - headline["triviaqa_gap_long"], 4),
        }
    }
    output_prefix = ROOT / "docs/generated/theorem3_conflict_bonus_note"
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(
        "\n".join(
            [
                "# Theorem 3 Conflict Bonus Note",
                "",
                "This note isolates the marginal conflict penalty instead of reporting raw overconfidence gaps alone.",
                "",
                "## Headline",
                "",
                f"- `ConflictBank` conflict minus no-conflict gap at `cot=0`: `{payload['headline']['conflict_minus_no_conflict_gap_cot0']}`",
                f"- `ConflictBank` conflict minus no-conflict gap at `cot=128`: `{payload['headline']['conflict_minus_no_conflict_gap_cot128']}`",
                f"- `ConflictBank` conflict minus no-conflict gap at `cot=1024`: `{payload['headline']['conflict_minus_no_conflict_gap_cot1024']}`",
                f"- `ConflictBank` conflict minus `TriviaQA` gap at `cot=128`: `{payload['headline']['conflict_minus_triviaqa_gap_cot128']}`",
                f"- `ConflictBank` conflict minus `TriviaQA` gap at `cot=1024`: `{payload['headline']['conflict_minus_triviaqa_gap_cot1024']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
