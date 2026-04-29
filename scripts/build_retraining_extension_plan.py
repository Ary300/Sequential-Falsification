#!/usr/bin/env python3
"""Build a concrete RLCR-style retraining extension plan."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"


def build_payload() -> dict:
    bundle = json.loads((GENERATED / "knowledge_arbitration_headline_bundle.json").read_text(encoding="utf-8"))
    method = json.loads((GENERATED / "theorem3_eta_tempered_method_result.json").read_text(encoding="utf-8"))
    wiki = json.loads((GENERATED / "theorem3_eta_tempered_wikicontradict_result.json").read_text(encoding="utf-8"))

    return {
        "starting_point": {
            "method_only_conflictbank_gap_before": method["evaluation"]["baseline"]["overconfidence_gap"],
            "method_only_conflictbank_gap_after": method["evaluation"]["selected"]["overconfidence_gap"],
            "method_only_conflictbank_accuracy_before": method["evaluation"]["baseline"]["accuracy"],
            "method_only_conflictbank_accuracy_after": method["evaluation"]["selected"]["accuracy"],
            "method_only_wikicontradict_gap_before": wiki["evaluation"]["baseline"]["overconfidence_gap"],
            "method_only_wikicontradict_gap_after": wiki["evaluation"]["selected"]["overconfidence_gap"],
        },
        "priority_models": [
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        ],
        "priority_benchmarks": [
            "ConflictBank",
            "WikiContradict",
            "GPQA",
            "CLIMATEX",
        ],
        "training_recipe": {
            "objective": "accuracy reward plus explicit Brier-style calibration reward",
            "anti_pattern": "pure binary GRPO reward without uncertainty credit",
            "reward_terms": [
                "verifiable answer correctness",
                "negative Brier score on reported answer probability",
                "optional penalty for confidence when the answer is wrong",
            ],
            "comparison_arms": [
                "baseline reasoning model",
                "eta-tempered decoding only",
                "Brier-reward finetune only",
                "Brier-reward finetune plus eta-tempered decoding",
            ],
        },
        "success_targets": {
            "conflictbank_14b_gap_target": 0.35,
            "conflictbank_14b_accuracy_floor": 0.44,
            "wikicontradict_gap_target": 0.30,
            "must_beat_method_only_on_conflictbank": True,
        },
        "compute_note": {
            "requires_external_training_compute": True,
            "estimated_scope": "multi-day fine-tuning plus rerun of the theorem-3 benchmark panel",
        },
    }


def build_markdown(payload: dict) -> str:
    s = payload["starting_point"]
    t = payload["training_recipe"]
    targets = payload["success_targets"]
    lines = [
        "# Retraining Extension Plan",
        "",
        "This is the concrete next-wave plan for the optional retraining-style extension beyond eta-tempered decoding.",
        "",
        "## Why This Is The Right Next Step",
        "",
        f"- The current method-only intervention already improves `ConflictBank` 14B conflict from accuracy `{s['method_only_conflictbank_accuracy_before']:.4f}` to `{s['method_only_conflictbank_accuracy_after']:.4f}` and overconfidence gap `{s['method_only_conflictbank_gap_before']:.4f}` to `{s['method_only_conflictbank_gap_after']:.4f}`.",
        f"- The current method-only intervention already improves `WikiContradict` conflict from gap `{s['method_only_wikicontradict_gap_before']:.4f}` to `{s['method_only_wikicontradict_gap_after']:.4f}`.",
        "- The remaining gap is therefore no longer “missing a method”; it is the classic RLCR-style question of whether training can repair the residual calibration pathology that test-time eta scaling cannot fully remove.",
        "",
        "## Priority Models",
        "",
    ]
    for model in payload["priority_models"]:
        lines.append(f"- `{model}`")

    lines.extend(
        [
            "",
            "## Priority Benchmarks",
            "",
        ]
    )
    for benchmark in payload["priority_benchmarks"]:
        lines.append(f"- `{benchmark}`")

    lines.extend(
        [
            "",
            "## Training Recipe",
            "",
            f"- Objective: {t['objective']}.",
            f"- Avoid: {t['anti_pattern']}.",
            "- Reward terms:",
        ]
    )
    for reward in t["reward_terms"]:
        lines.append(f"- `{reward}`")

    lines.extend(
        [
            "",
            "Comparison arms:",
        ]
    )
    for arm in t["comparison_arms"]:
        lines.append(f"- `{arm}`")

    lines.extend(
        [
            "",
            "## Success Targets",
            "",
            f"- `ConflictBank` 14B conflict overconfidence-gap target: `<= {targets['conflictbank_14b_gap_target']}`.",
            f"- `ConflictBank` 14B conflict accuracy floor: `>= {targets['conflictbank_14b_accuracy_floor']}`.",
            f"- `WikiContradict` conflict overconfidence-gap target: `<= {targets['wikicontradict_gap_target']}`.",
            "- The retrained model should beat the method-only eta-tempered run on the `ConflictBank` 14B conflict slice.",
            "",
            "## Honest Constraint",
            "",
            "- This extension requires fresh external training compute and cannot be truthfully completed from the current local-only session.",
            "- What is finished here is the concrete experimental recipe, targets, and comparison arms, so the remaining blocker is only compute, not ambiguity.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    out_json = GENERATED / "retraining_extension_plan.json"
    out_md = GENERATED / "retraining_extension_plan.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(out_json), "md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
