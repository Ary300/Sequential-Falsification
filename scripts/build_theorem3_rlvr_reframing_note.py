#!/usr/bin/env python3
"""Build a theorem-3 reframing note around RLVR and benchmark dependence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 RLVR reframing note.")
    parser.add_argument("--cross-family-json", required=True)
    parser.add_argument("--eta-summary-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build_summary(cross_family: dict, eta: dict) -> dict:
    headline = {
        "conditional_law": (
            "Reasoning-time overconfidence under knowledge conflict is best written as a conditional "
            "RLVR / misspecification law, not as a universal scale law."
        ),
        "deepseek_asymmetry_replicates": cross_family["headline"]["deepseek_7b_14b_conflictbank_asymmetry_replicates"],
        "qwen_asymmetry_replicates": cross_family["headline"]["qwen_7b_14b_conflictbank_asymmetry_replicates"],
        "eta_shrink_factor": eta["headline"]["conflict_to_no_conflict_eta_shrink_factor"],
    }
    return {
        "headline": headline,
        "recommended_statement": (
            "Models trained with verifiable-reward reasoning objectives can enter a misspecified, "
            "endogenous-evidence regime under knowledge conflict, where longer CoT sharpens confidence "
            "faster than it improves accuracy. The effect is benchmark-dependent and strongest on "
            "controlled conflict families."
        ),
        "contrast_points": [
            {
                "paper": "Yoon et al. (NeurIPS 2025)",
                "setting": "QA without explicit knowledge conflict",
                "result": "CoT improves confidence calibration in most settings.",
                "our_read": "Compatible. That is the well-specified or low-conflict side of the split."
            },
            {
                "paper": "Lacombe et al. (ICML 2025 workshop)",
                "setting": "Knowledge-intensive confidence assessment",
                "result": "Longer reasoning budgets impair calibration.",
                "our_read": "Compatible. This is the hard-QA / misspecified side of the split."
            },
            {
                "paper": "Welch et al. (arXiv 2603.16728)",
                "setting": "Vision-language uncertainty under CoT",
                "result": "Implicit answer conditioning drives overconfidence.",
                "our_read": "This is the best mechanistic phrase for the endogenous-evidence side of theorem 3."
            },
            {
                "paper": "Damani et al. (RLCR)",
                "setting": "Reward design for reasoning calibration",
                "result": "Binary reward reasoning hurts calibration; Brier-style rewards repair it.",
                "our_read": "This is the training-time cousin of our test-time conditional law."
            },
        ],
    }


def build_markdown(summary: dict) -> str:
    h = summary["headline"]
    lines = [
        "# Theorem 3 RLVR Reframing Note",
        "",
        "## Headline",
        "",
        f"- Conditional law: {h['conditional_law']}",
        f"- DeepSeek `7B -> 14B` asymmetry replicates: `{h['deepseek_asymmetry_replicates']}`",
        f"- Qwen `7B -> 14B` asymmetry replicates: `{h['qwen_asymmetry_replicates']}`",
        f"- Conflict/no-conflict eta shrink factor: `{h['eta_shrink_factor']}`",
        "",
        "## Recommended Theorem-3 Wording",
        "",
        summary["recommended_statement"],
        "",
        "## Contrast With Nearby Literature",
        "",
        "| Paper | Setting | Their result | How it lines up with the current theorem-3 read |",
        "|---|---|---|---|",
    ]
    for row in summary["contrast_points"]:
        lines.append(
            f"| {row['paper']} | {row['setting']} | {row['result']} | {row['our_read']} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The repo no longer supports a universal `7B recovers / 14B saturates` theorem. That stronger statement is false.",
            "- The repo now does support a better theorem: controlled conflict can keep larger reasoning models in a saturated overconfidence regime, while naturalistic contradiction can still show partial self-correction.",
            "- The RLVR framing is the cleanest way to reconcile the DeepSeek-vs-Qwen split without throwing away the theorem-3 contribution.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(_load(args.cross_family_json), _load(args.eta_summary_json))
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
