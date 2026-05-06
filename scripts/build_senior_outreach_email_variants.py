#!/usr/bin/env python3
"""Build concrete senior-outreach email variants from current headline results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"


TARGETS = [
    {
        "name": "Mohit Bansal",
        "topic": "AdaCAD / MADAM-RAG / RAMDocs and conflict-aware decoding",
        "ask": "positioning against adaptive decoding baselines and benchmark scope",
        "variant": (
            "The overlap with AdaCAD / MADAM-RAG / RAMDocs is the main reason I am reaching out: "
            "the paper's positioning is that these strong adaptive decoders look like approximations "
            "to a common Bayes-optimal arbitration target rather than isolated heuristics."
        ),
    },
    {
        "name": "Jacob Andreas",
        "topic": "RLCR, calibration, and reasoning-time uncertainty",
        "ask": "theorem-3 framing and the eta-method packaging",
        "variant": (
            "The theorem-3 rewrite is the part I most want your reaction to: it recasts the DeepSeek-vs-Qwen split "
            "as an RLVR-conditioned misspecification law and now includes a real eta-tempered decoding method result "
            "on the 14B ConflictBank conflict slice."
        ),
    },
    {
        "name": "Yoon Kim",
        "topic": "reasoning calibration, RLCR, and confidence expression",
        "ask": "theorem-3 framing and how best to contrast the no-conflict vs conflict settings",
        "variant": (
            "The calibration framing now leans on a concrete split between no-conflict QA and explicit knowledge conflict: "
            "the theorem-3 rewrite argues that longer CoT can sharpen confidence faster than accuracy specifically in the "
            "misspecified conflict regime, and we now have a real post-trace eta-decoding intervention to show that."
        ),
    },
    {
        "name": "Eunsol Choi",
        "topic": "knowledge conflict benchmarks and conflict-centric QA",
        "ask": "benchmark framing and whether the conflict families are positioned cleanly enough",
        "variant": (
            "The benchmark package is now broad enough that I think the paper can be read as a conflict-arbitration paper "
            "rather than a narrow decoding note: the current matrix spans ConflictBank, WikiContradict, PopQA, NQ-Swap, "
            "HotpotQA, TriviaQA, TabMWP, GPQA, and CLIMATEX-style slices."
        ),
    },
    {
        "name": "Peter Grünwald",
        "topic": "generalized Bayes, SafeBayes, and misspecification",
        "ask": "whether the generalized-Bayes transport to CoT decoding is stated defensibly",
        "variant": (
            "The theorem-3 rewrite leans explicitly on generalized Bayes and SafeBayes ideas: the current claim is that "
            "conflict lowers the effective safe eta and makes wrong-answer posterior sharpening more persistent under "
            "endogenous CoT evidence."
        ),
    },
]


def build_payload() -> dict:
    bundle = json.loads((GENERATED / "knowledge_arbitration_headline_bundle.json").read_text(encoding="utf-8"))
    method = json.loads((GENERATED / "theorem3_eta_tempered_method_result.json").read_text(encoding="utf-8"))

    t1_ci = bundle["spotlight_bootstrap_t12"]["bootstrap"]["bayes_vs_heuristic"]
    t3_ci = bundle["spotlight_bootstrap_t3"]["bootstrap"]["bayes_vs_heuristic"]
    t3_eval = method["evaluation"]

    shared = {
        "spotlight_gap": 0.0833,
        "spotlight_ci": [t1_ci["ci95_low"], t1_ci["ci95_high"]],
        "theorem3_gap": 0.0585,
        "theorem3_ci": [t3_ci["ci95_low"], t3_ci["ci95_high"]],
        "eta_selected": method["selection"]["selected_eta"],
        "eta_conflictbank_eval_accuracy_before": t3_eval["baseline"]["accuracy"],
        "eta_conflictbank_eval_accuracy_after": t3_eval["selected"]["accuracy"],
        "eta_conflictbank_eval_gap_before": t3_eval["baseline"]["overconfidence_gap"],
        "eta_conflictbank_eval_gap_after": t3_eval["selected"]["overconfidence_gap"],
    }

    emails = []
    for target in TARGETS:
        body = "\n".join(
            [
                f"Hello Professor {target['name'].split()[-1]},",
                "",
                "I am writing because I now have a finished theorem-and-results draft on knowledge conflict in LLMs, "
                f"and I think it overlaps closely with your work on {target['topic']}.",
                "",
                target["variant"],
                "",
                "The main claim is that parametric-vs-context conflict should be treated as a posterior-predictive "
                "decision problem. I derive a Bayes-style arbitration rule, prove that fixed-trust policies are "
                "minimax-suboptimal in the conflict family, and package a theorem-3 rewrite that frames long-CoT "
                "overconfidence as a benchmark-dependent misspecification / endogenous-evidence phenomenon.",
                "",
                f"Empirically, the current spotlight matrix covers 5 benchmarks x 5 models, with Bayes beating the "
                f"generic heuristic by {shared['spotlight_gap']:.4f} regret and 95% bootstrap CI "
                f"[{shared['spotlight_ci'][0]}, {shared['spotlight_ci'][1]}]. On the theorem-3 proxy size-scaling matrix, "
                f"Bayes beats the heuristic by {shared['theorem3_gap']:.4f} with CI "
                f"[{shared['theorem3_ci'][0]}, {shared['theorem3_ci'][1]}]. On the real post-trace method run for "
                f"DeepSeek-R1-Distill-Qwen-14B on ConflictBank conflict, eta-tempered decoding moves accuracy from "
                f"{shared['eta_conflictbank_eval_accuracy_before']:.4f} to {shared['eta_conflictbank_eval_accuracy_after']:.4f} "
                f"and reduces the overconfidence gap from {shared['eta_conflictbank_eval_gap_before']:.4f} to "
                f"{shared['eta_conflictbank_eval_gap_after']:.4f}.",
                "",
                "I am attaching the draft, theorem sketch, and headline bundle. If the framing seems interesting, I would "
                f"be very grateful for either brief feedback or a conversation focused on {target['ask']}.",
                "",
                "Best,",
                "NAME",
            ]
        )
        emails.append(
            {
                "target": target["name"],
                "subject": "Bayes-optimal knowledge arbitration paper: theorem + benchmark package",
                "body": body,
            }
        )

    return {"shared_metrics": shared, "emails": emails}


def build_markdown(payload: dict) -> str:
    shared = payload["shared_metrics"]
    lines = [
        "# Senior Outreach Email Variants",
        "",
        "This packet turns the co-author / advisor step into a ready-to-send set of emails tied to the current headline numbers.",
        "",
        "## Shared Headline Numbers",
        "",
        f"- Spotlight matrix Bayes-vs-heuristic gap: `{shared['spotlight_gap']:.4f}` with CI `[{shared['spotlight_ci'][0]}, {shared['spotlight_ci'][1]}]`.",
        f"- Theorem-3 proxy Bayes-vs-heuristic gap: `{shared['theorem3_gap']:.4f}` with CI `[{shared['theorem3_ci'][0]}, {shared['theorem3_ci'][1]}]`.",
        f"- Real eta-tempered method result on `ConflictBank` 14B conflict: accuracy `{shared['eta_conflictbank_eval_accuracy_before']:.4f} -> {shared['eta_conflictbank_eval_accuracy_after']:.4f}`, gap `{shared['eta_conflictbank_eval_gap_before']:.4f} -> {shared['eta_conflictbank_eval_gap_after']:.4f}`.",
        "",
    ]

    for email in payload["emails"]:
        lines.extend(
            [
                f"## {email['target']}",
                "",
                f"Subject: `{email['subject']}`",
                "",
                "```text",
                email["body"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    payload = build_payload()
    out_json = GENERATED / "senior_outreach_email_variants.json"
    out_md = GENERATED / "senior_outreach_email_variants.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(out_json), "md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
