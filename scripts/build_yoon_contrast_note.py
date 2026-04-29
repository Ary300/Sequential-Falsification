#!/usr/bin/env python3
"""Build a Yoon-style calibration sign-flip note from completed model-wave runs."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"


MODEL_WAVE_ROOT = ROOT / "results/delta_knowledge_arbitration_extended_wave"
SEEDS = [42, 43, 44]


def confidence_gap(rows: list[dict]) -> float:
    if not rows:
        return 0.0
    mean_conf = sum(float(row["confidence"]) for row in rows) / len(rows)
    acc = sum(int(row["outcome"]) for row in rows) / len(rows)
    return round(mean_conf - acc, 4)


def load_rows(seed: int) -> list[dict]:
    path = (
        MODEL_WAVE_ROOT
        / f"arbitration_spotlight_extended_model_wave__seed={seed}"
        / f"arbitration_spotlight_extended_model_wave__seed={seed}_benchmark_results.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for exp in payload["experiments"]:
        rows.extend(exp["rows"])
    return rows


def build_payload() -> dict:
    grouped: dict[tuple[int, str, str, str, int], list[dict]] = defaultdict(list)
    for seed in SEEDS:
        for row in load_rows(seed):
            benchmark = str(row["benchmark"])
            condition = str(row["condition"])
            if (benchmark, condition) not in {("triviaqa", "aligned_context"), ("conflictbank", "conflict_context")}:
                continue
            key = (seed, str(row["model"]), benchmark, condition, int(row["cot_length"]))
            grouped[key].append(row)

    per_series = []
    flip_count = 0
    total = 0
    by_model = defaultdict(lambda: {"trivia_delta_sum": 0.0, "conflict_delta_sum": 0.0, "count": 0})
    for seed in SEEDS:
        models = sorted({k[1] for k in grouped if k[0] == seed})
        for model in models:
            trivia_0 = confidence_gap(grouped[(seed, model, "triviaqa", "aligned_context", 0)])
            trivia_long = confidence_gap(grouped[(seed, model, "triviaqa", "aligned_context", 2048)])
            conflict_0 = confidence_gap(grouped[(seed, model, "conflictbank", "conflict_context", 0)])
            conflict_long = confidence_gap(grouped[(seed, model, "conflictbank", "conflict_context", 2048)])
            trivia_delta = round(abs(trivia_long) - abs(trivia_0), 4)
            conflict_delta = round(abs(conflict_long) - abs(conflict_0), 4)
            flipped = trivia_delta < 0.0 and conflict_delta > 0.0
            per_series.append(
                {
                    "seed": seed,
                    "model": model,
                    "triviaqa_gap_cot0": trivia_0,
                    "triviaqa_gap_long": trivia_long,
                    "triviaqa_gap_delta": trivia_delta,
                    "conflictbank_gap_cot0": conflict_0,
                    "conflictbank_gap_long": conflict_long,
                    "conflictbank_gap_delta": conflict_delta,
                    "sign_flip": flipped,
                }
            )
            total += 1
            flip_count += int(flipped)
            by_model[model]["trivia_delta_sum"] += trivia_delta
            by_model[model]["conflict_delta_sum"] += conflict_delta
            by_model[model]["count"] += 1

    model_rows = []
    for model, bucket in sorted(by_model.items()):
        model_rows.append(
            {
                "model": model,
                "mean_triviaqa_gap_delta": round(bucket["trivia_delta_sum"] / bucket["count"], 4),
                "mean_conflictbank_gap_delta": round(bucket["conflict_delta_sum"] / bucket["count"], 4),
                "count": bucket["count"],
            }
        )

    headline = {
        "flip_count": flip_count,
        "num_series": total,
        "flip_rate": round(flip_count / total, 4) if total else 0.0,
        "mean_triviaqa_gap_delta": round(sum(r["triviaqa_gap_delta"] for r in per_series) / total, 4),
        "mean_conflictbank_gap_delta": round(sum(r["conflictbank_gap_delta"] for r in per_series) / total, 4),
    }
    return {"headline": headline, "per_series": per_series, "per_model": model_rows}


def build_markdown(payload: dict) -> str:
    h = payload["headline"]
    lines = [
        "# Yoon Contrast Note",
        "",
        "This note tests the reviewer-facing contrast directly: a no-conflict QA control (`TriviaQA` aligned-context) versus explicit conflict (`ConflictBank` conflict-context), measured by how the magnitude of the confidence-accuracy gap changes from `cot=0` to the longest completed budget.",
        "",
        "## Headline",
        "",
        f"- Sign-flip count: `{h['flip_count']}/{h['num_series']}`",
        f"- Sign-flip rate: `{h['flip_rate']}`",
        f"- Mean `TriviaQA` no-conflict gap-magnitude delta (`cot 2048 - cot 0`): `{h['mean_triviaqa_gap_delta']}`",
        f"- Mean `ConflictBank` conflict gap-magnitude delta (`cot 2048 - cot 0`): `{h['mean_conflictbank_gap_delta']}`",
        "",
        "Interpretation:",
        "- Negative delta means calibration improves with longer CoT.",
        "- Positive delta means calibration worsens with longer CoT.",
        "- On the completed proxy wave, this direct `TriviaQA` vs `ConflictBank` control does not produce the clean sign flip by itself, so the stronger theorem-3 contrast should still be written around the real-trace conflict results rather than this proxy alone.",
        "",
        "## Per-Model Means",
        "",
        "| Model | Mean TriviaQA delta | Mean ConflictBank delta | Count |",
        "|---|---:|---:|---:|",
    ]
    for row in payload["per_model"]:
        lines.append(
            f"| {row['model']} | {row['mean_triviaqa_gap_delta']:.4f} | "
            f"{row['mean_conflictbank_gap_delta']:.4f} | {row['count']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    out_json = GENERATED / "yoon_contrast_note.json"
    out_md = GENERATED / "yoon_contrast_note.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(out_json), "md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
