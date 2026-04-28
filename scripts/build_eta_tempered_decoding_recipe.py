#!/usr/bin/env python3
"""Build a paper-facing eta-tempered decoding recipe note."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build eta-tempered decoding recipe.")
    parser.add_argument("--eta-summary-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build_summary(eta: dict) -> dict:
    headline = eta["headline"]
    return {
        "headline": headline,
        "recipe": [
            "Hold out a 200-example calibration split for each model-and-benchmark cell.",
            "Generate standard CoT traces once, then sweep eta in [0.1, 1.0] over the post-trace answer distribution.",
            "Choose the largest eta that improves Brier without hurting answer accuracy on the calibration split.",
            "Decode on the evaluation split with p_eta(a | trace, c) proportional to p(a | trace, c)^eta * p_theta(a | q)^(1-eta).",
            "If the best eta still leaves a large confidence gap, treat the failure as answer-level and not calibration-only.",
        ],
        "operating_point": {
            "mean_conflict_eta": headline["mean_conflict_do_no_harm_eta"],
            "mean_no_conflict_eta": headline["mean_no_conflict_do_no_harm_eta"],
            "eta_shrink_factor": headline["conflict_to_no_conflict_eta_shrink_factor"],
            "conflictbank_conflict_best_gap": headline["conflictbank_conflict_best_gap"],
            "wikicontradict_conflict_best_gap": headline["wikicontradict_conflict_best_gap"],
            "wikicontradict_conflict_best_gap_eta": headline["wikicontradict_conflict_best_gap_eta"],
        },
    }


def build_markdown(summary: dict) -> str:
    h = summary["headline"]
    lines = [
        "# Eta-Tempered Decoding Recipe",
        "",
        "This is the concrete method package implied by the theorem-3 rewrite.",
        "It is deliberately conservative: only the confidence layer is tempered, so any remaining error after tempering should be interpreted as answer-level failure rather than miscalibration alone.",
        "",
        "## Recommended Recipe",
        "",
    ]
    for idx, step in enumerate(summary["recipe"], start=1):
        lines.append(f"{idx}. {step}")

    lines.extend(
        [
            "",
            "## Current Operating Point",
            "",
            f"- Mean conflict do-no-harm eta: `{h['mean_conflict_do_no_harm_eta']}`",
            f"- Mean no-conflict do-no-harm eta: `{h['mean_no_conflict_do_no_harm_eta']}`",
            f"- Conflict/no-conflict eta shrink factor: `{h['conflict_to_no_conflict_eta_shrink_factor']}`",
            f"- `ConflictBank` conflict best attainable proxy gap: `{h['conflictbank_conflict_best_gap']}`",
            f"- `WikiContradict` conflict best attainable proxy gap: `{h['wikicontradict_conflict_best_gap']}` at eta `{h['wikicontradict_conflict_best_gap_eta']}`",
            "",
            "## Read",
            "",
            "- The theorem-3 method implication is not `eta < 1` everywhere; it is `eta` should shrink most aggressively on conflict slices and only modestly on no-conflict slices.",
            "- `WikiContradict` behaves like a calibratable regime: confidence-only tempering nearly removes the long-CoT gap.",
            "- `ConflictBank` conflict behaves like an answer-level failure regime: even maximal confidence tempering leaves a large residual gap, so the right next intervention there is retraining or answer-space correction, not just post-hoc calibration.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(_load(args.eta_summary_json))
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
