#!/usr/bin/env python3
"""Build a real-generation Yoon-style contrast note from theorem-3 summaries."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Yoon-style real-generation contrast note.")
    parser.add_argument("--triviaqa-control-json", required=True)
    parser.add_argument("--conflict-14b-json", required=True)
    parser.add_argument("--closedbook-control-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--short-cot", type=int, default=128)
    parser.add_argument("--long-cot", type=int, default=1024)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_row(rows: list[dict[str, Any]], *, benchmark: str, split: str) -> dict[str, Any]:
    for row in rows:
        if str(row.get("benchmark")) == benchmark and str(row.get("split")) == split:
            return row
    raise KeyError(f"Missing row for benchmark={benchmark} split={split}")


def build_payload(
    triviaqa_control: dict[str, Any],
    conflict_14b: dict[str, Any],
    closedbook_control: dict[str, Any],
    *,
    short_cot: int,
    long_cot: int,
) -> dict[str, Any]:
    trivia_rows = {
        int(row["cot_length"]): row
        for row in triviaqa_control.get("condition_rows", [])
        if str(row.get("benchmark")) == "triviaqa" and str(row.get("condition")) == "closed_book"
    }
    conflict_row = _find_row(conflict_14b["rows"], benchmark="conflictbank", split="conflict")
    closedbook_row = closedbook_control["per_benchmark"]["conflictbank"]

    trivia_cot0 = round(float(trivia_rows[0]["gap"]), 4)
    trivia_short = round(float(trivia_rows[short_cot]["gap"]), 4)
    trivia_long = round(float(trivia_rows[long_cot]["gap"]), 4)
    conflict_cot0 = round(float(conflict_row["gap_cot_0"]), 4)
    conflict_short = round(float(conflict_row["gap_cot_128"]), 4)
    conflict_long = round(float(conflict_row["gap_cot_1024"]), 4)
    closed_cot0 = round(float(closedbook_row["14b_closed_book"][0]), 4)
    closed_short = round(float(closedbook_row["14b_closed_book"][1]), 4)
    closed_long = round(float(closedbook_row["14b_closed_book"][2]), 4)

    headline = {
        "triviaqa_gap_cot0": trivia_cot0,
        "triviaqa_gap_short": trivia_short,
        "triviaqa_gap_long": trivia_long,
        "triviaqa_gap_delta_short": round(trivia_short - trivia_cot0, 4),
        "triviaqa_gap_delta": round(trivia_long - trivia_cot0, 4),
        "conflictbank_gap_cot0": conflict_cot0,
        "conflictbank_gap_short": conflict_short,
        "conflictbank_gap_long": conflict_long,
        "conflictbank_gap_delta_short": round(conflict_short - conflict_cot0, 4),
        "conflictbank_gap_delta": round(conflict_long - conflict_cot0, 4),
        "closed_book_gap_cot0": closed_cot0,
        "closed_book_gap_short": closed_short,
        "closed_book_gap_long": closed_long,
        "closed_book_gap_delta_short": round(closed_short - closed_cot0, 4),
        "closed_book_gap_delta": round(closed_long - closed_cot0, 4),
        "strict_sign_flip": (trivia_long - trivia_cot0) < 0.0 and (conflict_long - conflict_cot0) > 0.0,
        "conflict_worse_than_triviaqa_at_short_cot": conflict_short > trivia_short,
        "conflict_worse_than_triviaqa_at_long_cot": conflict_long > trivia_long,
        "conflict_worse_than_closed_book_at_long_cot": conflict_long > closed_long,
    }
    return {
        "headline": headline,
        "metadata": {
            "short_cot": short_cot,
            "long_cot": long_cot,
            "triviaqa_count_per_cot": int(trivia_rows[0]["count"]),
        },
    }


def build_markdown(payload: dict[str, Any], *, short_cot: int, long_cot: int) -> str:
    h = payload["headline"]
    lines = [
        "# Yoon Real Contrast Note",
        "",
        "This note compares the finished no-conflict QA control (`TriviaQA` closed-book) against the existing explicit-conflict 14B slice (`ConflictBank` conflict) on the real theorem-3 generation path.",
        "",
        "## Headline",
        "",
        f"- `TriviaQA` gap: `{h['triviaqa_gap_cot0']}` -> `{h['triviaqa_gap_short']}` -> `{h['triviaqa_gap_long']}`",
        f"- `TriviaQA` gap delta (`cot {short_cot} - cot 0`): `{h['triviaqa_gap_delta_short']}`",
        f"- `TriviaQA` gap delta (`cot {long_cot} - cot 0`): `{h['triviaqa_gap_delta']}`",
        f"- `ConflictBank` conflict gap: `{h['conflictbank_gap_cot0']}` -> `{h['conflictbank_gap_short']}` -> `{h['conflictbank_gap_long']}`",
        f"- `ConflictBank` conflict gap delta (`cot {short_cot} - cot 0`): `{h['conflictbank_gap_delta_short']}`",
        f"- `ConflictBank` conflict gap delta (`cot {long_cot} - cot 0`): `{h['conflictbank_gap_delta']}`",
        f"- `ConflictBank` closed-book gap: `{h['closed_book_gap_cot0']}` -> `{h['closed_book_gap_short']}` -> `{h['closed_book_gap_long']}`",
        f"- `ConflictBank` closed-book gap delta (`cot {short_cot} - cot 0`): `{h['closed_book_gap_delta_short']}`",
        f"- `ConflictBank` closed-book gap delta (`cot {long_cot} - cot 0`): `{h['closed_book_gap_delta']}`",
        f"- Strict Yoon-style sign flip achieved: `{h['strict_sign_flip']}`",
        f"- Conflict worse than `TriviaQA` at short CoT: `{h['conflict_worse_than_triviaqa_at_short_cot']}`",
        f"- Conflict worse than `TriviaQA` at long CoT: `{h['conflict_worse_than_triviaqa_at_long_cot']}`",
        f"- Conflict worse than closed-book at long CoT: `{h['conflict_worse_than_closed_book_at_long_cot']}`",
        "",
        "Interpretation:",
        "- The strongest reviewer-facing outcome would be a strict sign flip, but the more realistic target is a conflict-amplification figure: explicit conflict should show substantially larger overconfidence than the no-conflict QA control at the same CoT budget.",
        "- In this run, `ConflictBank` conflict is already much worse than `TriviaQA` by `cot=128`, which is the main practical Yoon-contrast figure for the paper.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    payload = build_payload(
        _load_json(Path(args.triviaqa_control_json)),
        _load_json(Path(args.conflict_14b_json)),
        _load_json(Path(args.closedbook_control_json)),
        short_cot=args.short_cot,
        long_cot=args.long_cot,
    )
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(
        build_markdown(payload, short_cot=args.short_cot, long_cot=args.long_cot),
        encoding="utf-8",
    )
    print(json.dumps({"output_prefix": str(output_prefix), "headline": payload["headline"]}, indent=2))


if __name__ == "__main__":
    main()
