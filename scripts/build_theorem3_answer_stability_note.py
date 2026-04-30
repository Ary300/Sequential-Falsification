#!/usr/bin/env python3
"""Build an appendix-ready answer-stability note for theorem 3."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 answer-stability note from row-level traces.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--cot-lengths", default="0,128,1024")
    parser.add_argument("--benchmarks", default="conflictbank,wikicontradict")
    parser.add_argument("--splits", default="conflict,no_conflict")
    return parser.parse_args()


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _build_summary(
    rows: list[dict[str, Any]],
    *,
    model_name: str,
    cot_lengths: tuple[int, int, int],
    benchmarks: list[str],
    splits: list[str],
) -> dict[str, Any]:
    cot0, cot1, cot2 = cot_lengths
    sections: list[dict[str, Any]] = []
    for benchmark in benchmarks:
        for split in splits:
            by_id_answers: dict[str, dict[int, str]] = defaultdict(dict)
            by_id_conf: dict[str, dict[int, float]] = defaultdict(dict)
            by_id_outcome: dict[str, dict[int, int]] = defaultdict(dict)
            for row in rows:
                if str(row.get("benchmark")) != benchmark or str(row.get("split")) != split:
                    continue
                example_id = str(row.get("id"))
                cot_length = int(row.get("cot_length", 0))
                by_id_answers[example_id][cot_length] = str(row.get("answer", ""))
                by_id_conf[example_id][cot_length] = float(row.get("confidence", 0.5))
                by_id_outcome[example_id][cot_length] = int(row.get("outcome", 0))

            valid_ids = [
                example_id
                for example_id, answer_map in by_id_answers.items()
                if all(cot in answer_map for cot in cot_lengths)
            ]
            if not valid_ids:
                continue

            stable_all_ids = [
                example_id
                for example_id in valid_ids
                if by_id_answers[example_id][cot0] == by_id_answers[example_id][cot1] == by_id_answers[example_id][cot2]
            ]
            stable_pre_ids = [
                example_id
                for example_id in valid_ids
                if by_id_answers[example_id][cot0] == by_id_answers[example_id][cot1]
            ]
            stable_post_ids = [
                example_id
                for example_id in valid_ids
                if by_id_answers[example_id][cot1] == by_id_answers[example_id][cot2]
            ]

            def _stable_payload(example_ids: list[str], *, left: int, right: int) -> dict[str, float]:
                if not example_ids:
                    return {
                        "fraction": 0.0,
                        "count": 0,
                        "mean_confidence_delta": 0.0,
                        "mean_accuracy_delta": 0.0,
                        "mean_gap_delta": 0.0,
                    }
                confidence_delta = [
                    by_id_conf[example_id][right] - by_id_conf[example_id][left]
                    for example_id in example_ids
                ]
                accuracy_delta = [
                    float(by_id_outcome[example_id][right] - by_id_outcome[example_id][left])
                    for example_id in example_ids
                ]
                gap_delta = [
                    (by_id_conf[example_id][right] - by_id_outcome[example_id][right])
                    - (by_id_conf[example_id][left] - by_id_outcome[example_id][left])
                    for example_id in example_ids
                ]
                return {
                    "fraction": len(example_ids) / len(valid_ids),
                    "count": len(example_ids),
                    "mean_confidence_delta": _mean(confidence_delta),
                    "mean_accuracy_delta": _mean(accuracy_delta),
                    "mean_gap_delta": _mean(gap_delta),
                }

            sections.append(
                {
                    "benchmark": benchmark,
                    "split": split,
                    "count": len(valid_ids),
                    "cot_lengths": list(cot_lengths),
                    "stable_all": _stable_payload(stable_all_ids, left=cot0, right=cot2),
                    "stable_pre": _stable_payload(stable_pre_ids, left=cot0, right=cot1),
                    "stable_post": _stable_payload(stable_post_ids, left=cot1, right=cot2),
                }
            )

    headline = {}
    conflictbank_conflict = next(
        (
            section
            for section in sections
            if section["benchmark"] == "conflictbank" and section["split"] == "conflict"
        ),
        None,
    )
    if conflictbank_conflict is not None:
        headline = {
            "conflictbank_conflict_count": conflictbank_conflict["count"],
            "conflictbank_conflict_stable_all_fraction": round(conflictbank_conflict["stable_all"]["fraction"], 4),
            "conflictbank_conflict_stable_pre_fraction": round(conflictbank_conflict["stable_pre"]["fraction"], 4),
            "conflictbank_conflict_stable_post_fraction": round(conflictbank_conflict["stable_post"]["fraction"], 4),
            "conflictbank_conflict_stable_pre_gap_delta": round(conflictbank_conflict["stable_pre"]["mean_gap_delta"], 4),
            "conflictbank_conflict_stable_all_gap_delta": round(conflictbank_conflict["stable_all"]["mean_gap_delta"], 4),
        }

    return {
        "metadata": {
            "model_name": model_name,
            "cot_lengths": list(cot_lengths),
            "benchmarks": benchmarks,
            "splits": splits,
            "num_rows": len(rows),
        },
        "headline": headline,
        "sections": sections,
    }


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Theorem 3 Answer-Stability Note",
        "",
        "This note quantifies the empirical scope of the answer-stability condition used in the theorem-3 proof.",
        "",
        f"- Model: `{payload['metadata']['model_name']}`",
        f"- CoT lengths: `{payload['metadata']['cot_lengths']}`",
        f"- Total source rows: `{payload['metadata']['num_rows']}`",
        "",
    ]
    headline = payload.get("headline", {})
    if headline:
        lines.extend(
            [
                "## Headline",
                "",
                f"- `ConflictBank` conflict examples with all three CoT checkpoints: `{headline['conflictbank_conflict_count']}`",
                f"- Stable across `0/128/1024`: `{headline['conflictbank_conflict_stable_all_fraction']}`",
                f"- Stable across the pre-saturation window `0/128`: `{headline['conflictbank_conflict_stable_pre_fraction']}`",
                f"- Stable across `128/1024`: `{headline['conflictbank_conflict_stable_post_fraction']}`",
                f"- On the pre-saturation stable subset, mean gap delta `0 -> 128`: `{headline['conflictbank_conflict_stable_pre_gap_delta']}`",
                f"- On the fully stable subset, mean gap delta `0 -> 1024`: `{headline['conflictbank_conflict_stable_all_gap_delta']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Per-Slice Detail",
            "",
            "| Benchmark | Split | Count | Stable `0/128/1024` | Stable `0/128` | Stable `128/1024` | Stable `0/128` gap delta | Stable `0/128` acc delta | Stable `0/1024` gap delta |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for section in payload["sections"]:
        lines.append(
            "| {benchmark} | {split} | {count} | {stable_all} | {stable_pre} | {stable_post} | {pre_gap} | {pre_acc} | {all_gap} |".format(
                benchmark=section["benchmark"],
                split=section["split"],
                count=section["count"],
                stable_all=round(section["stable_all"]["fraction"], 4),
                stable_pre=round(section["stable_pre"]["fraction"], 4),
                stable_post=round(section["stable_post"]["fraction"], 4),
                pre_gap=round(section["stable_pre"]["mean_gap_delta"], 4),
                pre_acc=round(section["stable_pre"]["mean_accuracy_delta"], 4),
                all_gap=round(section["stable_all"]["mean_gap_delta"], 4),
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The theorem-3 stability condition is empirically non-trivial: most examples do change answers across CoT budgets.",
            "- The clean use of theorem 3(a) is therefore conditional rather than universal.",
            "- The most relevant support signal is whether the stable subset still exhibits confidence-gap growth without corresponding accuracy growth.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    cot_lengths = tuple(int(item.strip()) for item in args.cot_lengths.split(",") if item.strip())
    if len(cot_lengths) != 3:
        raise ValueError("--cot-lengths must specify exactly three checkpoints.")
    rows = _load_rows(Path(args.rows_jsonl))
    payload = _build_summary(
        rows,
        model_name=args.model_name,
        cot_lengths=cot_lengths,  # type: ignore[arg-type]
        benchmarks=[item.strip() for item in args.benchmarks.split(",") if item.strip()],
        splits=[item.strip() for item in args.splits.split(",") if item.strip()],
    )
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_prefix": str(output_prefix), "headline": payload.get("headline", {})}, indent=2))


if __name__ == "__main__":
    main()
