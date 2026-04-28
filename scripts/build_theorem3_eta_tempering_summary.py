#!/usr/bin/env python3
"""Build an eta-tempering intervention summary for theorem 3.

This is an offline calibration intervention over the observed long-CoT
confidence, not a fresh decoding run. We use it to answer a narrower but still
important question: how much can confidence-only eta tempering help once the
answer trajectory has already been fixed by long reasoning?
"""

from __future__ import annotations

import argparse
import json
from math import exp, log
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 eta-tempering summary artifacts.")
    parser.add_argument("--source", default="docs/generated/theorem3_real_14b_final.json")
    parser.add_argument("--output-prefix", default="docs/generated/theorem3_eta_tempering_analysis")
    parser.add_argument("--eta-step", type=float, default=0.05)
    return parser.parse_args()


def _clip(value: float, eps: float = 1e-6) -> float:
    return min(max(float(value), eps), 1.0 - eps)


def _logit(value: float) -> float:
    probability = _clip(value)
    return log(probability / (1.0 - probability))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def _tempered_confidence(confidence: float, eta: float) -> float:
    return _sigmoid(float(eta) * _logit(confidence))


def _proxy_brier(confidence: float, accuracy: float) -> float:
    acc = min(max(float(accuracy), 0.0), 1.0)
    conf = min(max(float(confidence), 0.0), 1.0)
    return acc * (1.0 - conf) ** 2 + (1.0 - acc) * conf**2


def _load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload.get("rows", []))


def _paired_targets(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(row["benchmark"], row["split"]): row for row in rows}


def _etas(step: float) -> list[float]:
    values = []
    current = 0.0
    while current <= 1.000001:
        values.append(round(current, 4))
        current += step
    if values[-1] != 1.0:
        values.append(1.0)
    return values


def build_summary(rows: list[dict[str, Any]], *, eta_step: float) -> dict[str, Any]:
    eta_values = _etas(eta_step)
    paired = _paired_targets(rows)
    slice_rows = []
    conflict_do_no_harm = []
    no_conflict_do_no_harm = []

    for row in rows:
        if "accuracy_cot_1024" not in row or "mean_confidence_cot_1024" not in row:
            continue

        benchmark = str(row["benchmark"])
        split = str(row["split"])
        short_gap = abs(float(row["gap_cot_0"]))
        long_gap = abs(float(row["gap_cot_1024"]))
        long_accuracy = float(row["accuracy_cot_1024"])
        long_confidence = float(row["mean_confidence_cot_1024"])

        paired_no_conf = paired.get((benchmark, "no_conflict"))
        paired_target_gap = abs(float(paired_no_conf["gap_cot_1024"])) if paired_no_conf is not None else None

        eta_rows = []
        do_no_harm_candidates: list[float] = []
        paired_target_candidates: list[float] = []

        for eta in eta_values:
            tempered_confidence = _tempered_confidence(long_confidence, eta)
            tempered_gap = tempered_confidence - long_accuracy
            abs_gap = abs(tempered_gap)
            brier = _proxy_brier(tempered_confidence, long_accuracy)
            eta_rows.append(
                {
                    "eta": eta,
                    "tempered_confidence": round(tempered_confidence, 4),
                    "proxy_abs_gap": round(abs_gap, 4),
                    "proxy_brier": round(brier, 4),
                }
            )
            if abs_gap <= short_gap + 1e-9:
                do_no_harm_candidates.append(eta)
            if paired_target_gap is not None and abs_gap <= paired_target_gap + 1e-9:
                paired_target_candidates.append(eta)

        best_gap_row = min(eta_rows, key=lambda item: item["proxy_abs_gap"])
        best_brier_row = min(eta_rows, key=lambda item: item["proxy_brier"])
        gap_floor = abs(0.5 - long_accuracy)
        do_no_harm_eta = max(do_no_harm_candidates) if do_no_harm_candidates else None
        paired_target_eta = max(paired_target_candidates) if paired_target_candidates else None

        if split == "conflict" and do_no_harm_eta is not None:
            conflict_do_no_harm.append(do_no_harm_eta)
        if split == "no_conflict" and do_no_harm_eta is not None:
            no_conflict_do_no_harm.append(do_no_harm_eta)

        slice_rows.append(
            {
                "benchmark": benchmark,
                "split": split,
                "long_accuracy": round(long_accuracy, 4),
                "long_confidence": round(long_confidence, 4),
                "observed_long_gap": round(long_gap, 4),
                "no_cot_gap": round(short_gap, 4),
                "gap_floor_at_eta_zero": round(gap_floor, 4),
                "best_gap_eta": best_gap_row["eta"],
                "best_gap_value": best_gap_row["proxy_abs_gap"],
                "best_brier_eta": best_brier_row["eta"],
                "best_brier_value": best_brier_row["proxy_brier"],
                "do_no_harm_eta": do_no_harm_eta,
                "paired_no_conf_target_gap": round(paired_target_gap, 4) if paired_target_gap is not None else None,
                "paired_no_conf_eta": paired_target_eta,
                "eta_rows": eta_rows,
            }
        )

    mean_conflict_eta = sum(conflict_do_no_harm) / len(conflict_do_no_harm) if conflict_do_no_harm else None
    mean_no_conflict_eta = sum(no_conflict_do_no_harm) / len(no_conflict_do_no_harm) if no_conflict_do_no_harm else None
    shrink_factor = (
        mean_conflict_eta / mean_no_conflict_eta
        if mean_conflict_eta is not None and mean_no_conflict_eta not in {None, 0.0}
        else None
    )

    lookup = {(row["benchmark"], row["split"]): row for row in slice_rows}
    conflictbank_conflict = lookup.get(("conflictbank", "conflict"))
    wikicontradict_conflict = lookup.get(("wikicontradict", "conflict"))

    return {
        "source": "theorem3_real_14b_final",
        "headline": {
            "mean_conflict_do_no_harm_eta": round(mean_conflict_eta, 4) if mean_conflict_eta is not None else None,
            "mean_no_conflict_do_no_harm_eta": round(mean_no_conflict_eta, 4) if mean_no_conflict_eta is not None else None,
            "conflict_to_no_conflict_eta_shrink_factor": round(shrink_factor, 4) if shrink_factor is not None else None,
            "conflictbank_conflict_gap_floor_at_eta_zero": None
            if conflictbank_conflict is None
            else conflictbank_conflict["gap_floor_at_eta_zero"],
            "conflictbank_conflict_best_gap": None if conflictbank_conflict is None else conflictbank_conflict["best_gap_value"],
            "wikicontradict_conflict_best_gap": None
            if wikicontradict_conflict is None
            else wikicontradict_conflict["best_gap_value"],
            "wikicontradict_conflict_best_gap_eta": None
            if wikicontradict_conflict is None
            else wikicontradict_conflict["best_gap_eta"],
        },
        "slice_rows": slice_rows,
    }


def build_markdown(summary: dict[str, Any]) -> str:
    headline = summary["headline"]
    lines = [
        "# Theorem 3 Eta Tempering Analysis",
        "",
        "This is an offline confidence-only eta tempering intervention over the observed long-CoT posterior.",
        "It does not change answers, so it is a conservative read on how much calibration can be rescued without answer-level correction.",
        "",
        "## Headline",
        "",
        f"- Mean conflict do-no-harm eta: `{headline.get('mean_conflict_do_no_harm_eta')}`",
        f"- Mean no-conflict do-no-harm eta: `{headline.get('mean_no_conflict_do_no_harm_eta')}`",
        f"- Conflict/no-conflict eta shrink factor: `{headline.get('conflict_to_no_conflict_eta_shrink_factor')}`",
        f"- ConflictBank conflict gap floor at eta -> 0: `{headline.get('conflictbank_conflict_gap_floor_at_eta_zero')}`",
        f"- ConflictBank conflict best attainable proxy gap: `{headline.get('conflictbank_conflict_best_gap')}`",
        f"- WikiContradict conflict best attainable proxy gap: `{headline.get('wikicontradict_conflict_best_gap')}` at eta `{headline.get('wikicontradict_conflict_best_gap_eta')}`",
        "",
        "## Slice Summary",
        "",
        "| Benchmark | Split | Long acc | Long conf | Observed gap | Gap floor @ eta=0 | Best gap | Do-no-harm eta | Paired no-conf eta |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["slice_rows"]:
        do_no_harm_eta = "--" if row["do_no_harm_eta"] is None else f"{row['do_no_harm_eta']:.2f}"
        paired_no_conf_eta = "--" if row["paired_no_conf_eta"] is None else f"{row['paired_no_conf_eta']:.2f}"
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['long_accuracy']:.4f} | {row['long_confidence']:.4f} | "
            f"{row['observed_long_gap']:.4f} | {row['gap_floor_at_eta_zero']:.4f} | {row['best_gap_value']:.4f} | "
            f"{do_no_harm_eta} | {paired_no_conf_eta} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    rows = _load_rows(ROOT / args.source)
    summary = build_summary(rows, eta_step=args.eta_step)
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
