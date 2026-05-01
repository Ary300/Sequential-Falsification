#!/usr/bin/env python3
"""Build a pre-registered held-out conflict-family evaluation note."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.experiment import run_benchmark_experiment  # noqa: E402
from utils.metrics import expected_calibration_error  # noqa: E402


GENERATED = ROOT / "docs/generated"
SEEDS = [42, 43, 44]
BENCHMARKS = ["clasheval", "ramdocs"]
MODELS = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "Qwen/Qwen2.5-14B-Instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
]
BASELINES = ["heuristic_adaptive", "cocoa", "astute_rag", "self_rag", "fixed_50", "always_context", "always_parametric"]


def _run_seed(seed: int) -> dict:
    experiment = {
        "name": f"preregistered_heldout_seed_{seed}",
        "benchmarks": BENCHMARKS,
        "models": MODELS,
        "conditions": ["aligned_context", "conflict_context"],
        "cot_lengths": [0, 128, 1024],
        "max_examples": 96,
        "seed": seed,
    }
    return run_benchmark_experiment(experiment)


def _policy_mean_regret(payload: dict, policy: str) -> float:
    return float(payload["summary"][policy]["mean_regret"])


def _group_ece(rows: list[dict]) -> float:
    probabilities = [float(row["policies"]["simulated_model"]["probability"]) for row in rows]
    labels = [int(row["label"]) for row in rows]
    return float(expected_calibration_error(probabilities, labels))


def _theorem3_direction(payload: dict) -> list[dict]:
    grouped = {}
    for group in payload["experiments"]:
        grouped[(group["benchmark"], group["model"], group["condition"], int(group["cot_length"]))] = group["rows"]

    rows = []
    for benchmark in BENCHMARKS:
        for model in MODELS:
            conflict_0 = _group_ece(grouped[(benchmark, model, "conflict_context", 0)])
            conflict_1024 = _group_ece(grouped[(benchmark, model, "conflict_context", 1024)])
            no_conflict_0 = _group_ece(grouped[(benchmark, model, "aligned_context", 0)])
            no_conflict_1024 = _group_ece(grouped[(benchmark, model, "aligned_context", 1024)])
            conflict_delta = conflict_1024 - conflict_0
            no_conflict_delta = no_conflict_1024 - no_conflict_0
            rows.append(
                {
                    "benchmark": benchmark,
                    "model": model,
                    "conflict_ece_delta": conflict_delta,
                    "no_conflict_ece_delta": no_conflict_delta,
                    "conflict_minus_no_conflict": conflict_delta - no_conflict_delta,
                }
            )
    return rows


def run_analysis() -> dict:
    preregistered_predictions = [
        {
            "id": "P1",
            "text": "On held-out conflict families, Bayes proxy will beat heuristic adaptive, CoCoA, Astute RAG, and Self-RAG on mean regret.",
        },
        {
            "id": "P2",
            "text": "Always-context and always-parametric will remain catastrophically suboptimal on held-out conflict families.",
        },
        {
            "id": "P3",
            "text": "The simulated theorem-3 model will show a larger long-CoT ECE change on conflict slices than on aligned-context slices.",
        },
    ]

    seed_payloads = {seed: _run_seed(seed) for seed in SEEDS}
    baseline_summary = {}
    for baseline in BASELINES:
        gaps = []
        for seed in SEEDS:
            gaps.append(_policy_mean_regret(seed_payloads[seed], baseline) - _policy_mean_regret(seed_payloads[seed], "bayes_proxy"))
        baseline_summary[baseline] = {
            "mean_gap": round(float(np.mean(gaps)), 4),
            "seed_gaps": [round(float(value), 4) for value in gaps],
            "all_positive": bool(all(value > 0 for value in gaps)),
        }

    theorem3_rows = []
    for seed in SEEDS:
        for row in _theorem3_direction(seed_payloads[seed]):
            theorem3_rows.append({"seed": seed, **row})

    by_model = {}
    for model in MODELS:
        model_rows = [row for row in theorem3_rows if row["model"] == model]
        by_model[model] = {
            "mean_conflict_ece_delta": round(float(np.mean([row["conflict_ece_delta"] for row in model_rows])), 4),
            "mean_no_conflict_ece_delta": round(float(np.mean([row["no_conflict_ece_delta"] for row in model_rows])), 4),
            "mean_conflict_minus_no_conflict": round(float(np.mean([row["conflict_minus_no_conflict"] for row in model_rows])), 4),
            "all_positive_conflict_minus_no_conflict": bool(all(row["conflict_minus_no_conflict"] > 0 for row in model_rows)),
        }

    results = {
        "P1": {
            "supported": bool(
                baseline_summary["heuristic_adaptive"]["all_positive"]
                and baseline_summary["cocoa"]["all_positive"]
                and baseline_summary["astute_rag"]["all_positive"]
                and baseline_summary["self_rag"]["all_positive"]
            ),
            "details": baseline_summary,
        },
        "P2": {
            "supported": bool(
                baseline_summary["always_context"]["all_positive"]
                and baseline_summary["always_parametric"]["all_positive"]
            ),
            "details": {
                "always_context": baseline_summary["always_context"],
                "always_parametric": baseline_summary["always_parametric"],
            },
        },
        "P3": {
            "supported": bool(all(summary["all_positive_conflict_minus_no_conflict"] for summary in by_model.values())),
            "details": by_model,
        },
    }

    headline = {
        "heldout_benchmarks": BENCHMARKS,
        "seeds": SEEDS,
        "all_predictions_supported": bool(all(item["supported"] for item in results.values())),
    }
    return {
        "headline": headline,
        "predictions": preregistered_predictions,
        "results": results,
        "theorem3_rows": theorem3_rows,
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Pre-Registered Held-Out Conflict-Family Test",
        "",
        "This note freezes three predictions before inspecting the held-out results on two conflict families that were not part of the main spotlight matrix: `ClashEval` and `RAMDocs`.",
        "The goal is to turn a piece of the empirical story from post-hoc validation into an explicit out-of-sample test.",
        "",
        "## Pre-Registered Predictions",
        "",
    ]
    for row in payload["predictions"]:
        lines.append(f"- `{row['id']}`: {row['text']}")
    lines.extend(
        [
            "",
            "## Headline",
            "",
            f"- Held-out benchmarks: `{payload['headline']['heldout_benchmarks']}`",
            f"- Seeds: `{payload['headline']['seeds']}`",
            f"- All pre-registered predictions supported: `{payload['headline']['all_predictions_supported']}`",
            "",
            "## Results",
            "",
        ]
    )

    p1 = payload["results"]["P1"]
    lines.append(f"- `P1` supported: `{p1['supported']}`")
    lines.append("| Baseline | Mean regret gap vs Bayes | Seed gaps | All seeds positive |")
    lines.append("|---|---:|---|---:|")
    for baseline, details in p1["details"].items():
        if baseline not in {"heuristic_adaptive", "cocoa", "astute_rag", "self_rag"}:
            continue
        lines.append(
            f"| {baseline} | {details['mean_gap']:.4f} | `{details['seed_gaps']}` | {details['all_positive']} |"
        )
    lines.append("")

    p2 = payload["results"]["P2"]
    lines.append(f"- `P2` supported: `{p2['supported']}`")
    lines.append("| Policy | Mean regret gap vs Bayes | Seed gaps | All seeds positive |")
    lines.append("|---|---:|---|---:|")
    for policy, details in p2["details"].items():
        lines.append(
            f"| {policy} | {details['mean_gap']:.4f} | `{details['seed_gaps']}` | {details['all_positive']} |"
        )
    lines.append("")

    p3 = payload["results"]["P3"]
    lines.append(f"- `P3` supported: `{p3['supported']}`")
    lines.append("| Model | Mean conflict ECE delta | Mean no-conflict ECE delta | Mean conflict-minus-no-conflict | Positive on all seeded held-out cells |")
    lines.append("|---|---:|---:|---:|---:|")
    for model, details in p3["details"].items():
        lines.append(
            f"| {model} | {details['mean_conflict_ece_delta']:.4f} | {details['mean_no_conflict_ece_delta']:.4f} | "
            f"{details['mean_conflict_minus_no_conflict']:.4f} | {details['all_positive_conflict_minus_no_conflict']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is still a proxy-family test, not a gold-standard preregistration filed in advance with an external timestamped registry.",
            "- It is much better than pure post-hoc narration: the predictions are explicit, the held-out families are different from the main spotlight families, and the outcomes are reported against those predictions directly.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = run_analysis()
    GENERATED.mkdir(parents=True, exist_ok=True)
    json_path = GENERATED / "preregistered_heldout_test.json"
    md_path = GENERATED / "preregistered_heldout_test.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
