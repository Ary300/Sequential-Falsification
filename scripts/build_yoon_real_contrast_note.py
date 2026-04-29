#!/usr/bin/env python3
"""Build a real-generation Yoon-style contrast note from theorem-3 rows."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Yoon-style real-generation contrast note.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--long-cot", type=int, default=1024)
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _gap(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    mean_conf = sum(float(row.get("confidence", 0.5)) for row in rows) / len(rows)
    accuracy = sum(float(row.get("outcome", 0.0)) for row in rows) / len(rows)
    return round(mean_conf - accuracy, 4)


def build_payload(rows: list[dict[str, Any]], *, long_cot: int) -> dict[str, Any]:
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        benchmark = str(row.get("benchmark"))
        condition = str(row.get("condition"))
        cot_length = int(row.get("cot_length", -1))
        grouped[(benchmark, condition, cot_length)].append(row)

    trivia_cot0 = _gap(grouped[("triviaqa", "aligned_context", 0)])
    trivia_long = _gap(grouped[("triviaqa", "aligned_context", long_cot)])
    conflict_cot0 = _gap(grouped[("conflictbank", "conflict_context", 0)])
    conflict_long = _gap(grouped[("conflictbank", "conflict_context", long_cot)])
    closed_cot0 = _gap(grouped[("conflictbank", "closed_book", 0)])
    closed_long = _gap(grouped[("conflictbank", "closed_book", long_cot)])

    headline = {
        "triviaqa_gap_cot0": trivia_cot0,
        "triviaqa_gap_long": trivia_long,
        "triviaqa_gap_delta": round(trivia_long - trivia_cot0, 4),
        "conflictbank_gap_cot0": conflict_cot0,
        "conflictbank_gap_long": conflict_long,
        "conflictbank_gap_delta": round(conflict_long - conflict_cot0, 4),
        "closed_book_gap_cot0": closed_cot0,
        "closed_book_gap_long": closed_long,
        "closed_book_gap_delta": round(closed_long - closed_cot0, 4),
        "strict_sign_flip": (trivia_long - trivia_cot0) < 0.0 and (conflict_long - conflict_cot0) > 0.0,
        "conflict_worse_than_closed_book_at_long_cot": conflict_long > closed_long,
    }
    return {"headline": headline}


def build_markdown(payload: dict[str, Any], *, long_cot: int) -> str:
    h = payload["headline"]
    lines = [
        "# Yoon Real Contrast Note",
        "",
        "This note compares a no-conflict QA control (`TriviaQA` aligned-context) against the explicit conflict slice (`ConflictBank` conflict-context) on the real theorem-3 generation path.",
        "",
        "## Headline",
        "",
        f"- `TriviaQA` gap: `{h['triviaqa_gap_cot0']}` -> `{h['triviaqa_gap_long']}`",
        f"- `TriviaQA` gap delta (`cot {long_cot} - cot 0`): `{h['triviaqa_gap_delta']}`",
        f"- `ConflictBank` conflict gap: `{h['conflictbank_gap_cot0']}` -> `{h['conflictbank_gap_long']}`",
        f"- `ConflictBank` conflict gap delta (`cot {long_cot} - cot 0`): `{h['conflictbank_gap_delta']}`",
        f"- `ConflictBank` closed-book gap: `{h['closed_book_gap_cot0']}` -> `{h['closed_book_gap_long']}`",
        f"- `ConflictBank` closed-book gap delta (`cot {long_cot} - cot 0`): `{h['closed_book_gap_delta']}`",
        f"- Strict Yoon-style sign flip achieved: `{h['strict_sign_flip']}`",
        f"- Conflict worse than closed-book at long CoT: `{h['conflict_worse_than_closed_book_at_long_cot']}`",
        "",
        "Interpretation:",
        "- The strongest reviewer-facing outcome is a strict sign flip: flat-or-improving no-conflict QA paired with worsening explicit conflict.",
        "- Even if the strict sign flip fails, `ConflictBank` can still support the theorem-3 story if conflict ends up worse than the closed-book baseline at long CoT.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = _load_rows(Path(args.rows_jsonl))
    payload = build_payload(rows, long_cot=args.long_cot)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(build_markdown(payload, long_cot=args.long_cot), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "output_prefix": str(output_prefix)}, indent=2))


if __name__ == "__main__":
    main()
