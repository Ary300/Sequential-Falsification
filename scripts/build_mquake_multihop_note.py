#!/usr/bin/env python3
"""Build a compact MQuAKE-Remastered multi-hop compounding note."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.experiment import run_benchmark_experiment  # noqa: E402
from utils.io import dump_json  # noqa: E402


MODELS = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
    "Qwen/Qwen2.5-14B-Instruct",
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    "meta-llama/Llama-3.1-70B-Instruct",
]
POLICIES = ["bayes_proxy", "heuristic_adaptive", "fixed_50", "always_context", "always_parametric"]
DEPTHS = [1, 2, 3]


def _mean(values: list[float]) -> float:
    return sum(values) / max(1, len(values))


def _chain_success(probabilities: list[float], depth: int) -> float:
    return _mean([float(prob) ** depth for prob in probabilities])


def _policy_rows(payload: dict[str, Any], *, model: str, condition: str, policy: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment in payload.get("experiments", []):
        for row in experiment.get("rows", []):
            if str(row.get("model")) != model or str(row.get("condition")) != condition:
                continue
            policy_payload = row.get("policies", {}).get(policy, {})
            if "probability" not in policy_payload:
                continue
            rows.append(policy_payload)
    return rows


def build_payload() -> dict[str, Any]:
    experiment = {
        "name": "mquake_multihop_compounding",
        "benchmarks": ["mquake_remastered"],
        "models": MODELS,
        "conditions": ["aligned_context"],
        "cot_lengths": [0, 128, 1024],
        "max_examples": 256,
        "seed": 42,
    }
    result = run_benchmark_experiment(experiment)

    per_model = []
    for model in MODELS:
        model_row = {"model": model, "policies": {}}
        for policy in POLICIES:
            rows = _policy_rows(result, model=model, condition="aligned_context", policy=policy)
            probs = [float(row["probability"]) for row in rows]
            if not probs:
                continue
            model_row["policies"][policy] = {
                "mean_probability": round(_mean(probs), 6),
                "chain_success": {
                    f"depth_{depth}": round(_chain_success(probs, depth), 6)
                    for depth in DEPTHS
                },
                "chain_error": {
                    f"depth_{depth}": round(1.0 - _chain_success(probs, depth), 6)
                    for depth in DEPTHS
                },
            }
        per_model.append(model_row)

    headline_model = per_model[0]["policies"]
    return {
        "metadata": {
            "benchmark": "mquake_remastered",
            "condition": "aligned_context",
            "models": MODELS,
            "max_examples": 256,
            "seed": 42,
            "depths": DEPTHS,
        },
        "headline": {
            "reference_model": MODELS[0],
            "bayes_depth_2_error": headline_model["bayes_proxy"]["chain_error"]["depth_2"],
            "heuristic_depth_2_error": headline_model["heuristic_adaptive"]["chain_error"]["depth_2"],
            "fixed50_depth_2_error": headline_model["fixed_50"]["chain_error"]["depth_2"],
            "always_parametric_depth_2_error": headline_model["always_parametric"]["chain_error"]["depth_2"],
            "always_context_depth_2_error": headline_model["always_context"]["chain_error"]["depth_2"],
        },
        "per_model": per_model,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# MQuAKE Multi-Hop Compounding Note",
        "",
        "This note treats MQuAKE-Remastered as an edited-world multi-hop arbitration stress test: the updated chain is the gold world, while parametric memory still points to the stale chain.",
        "",
        "## Setup",
        "",
        f"- Benchmark: `{payload['metadata']['benchmark']}`",
        f"- Condition: `{payload['metadata']['condition']}`",
        f"- Max examples: `{payload['metadata']['max_examples']}`",
        f"- Depths evaluated: `{payload['metadata']['depths']}`",
        "",
        "## Headline",
        "",
        f"- Reference model: `{payload['headline']['reference_model']}`",
        f"- Bayes depth-2 chain error: `{payload['headline']['bayes_depth_2_error']}`",
        f"- Heuristic depth-2 chain error: `{payload['headline']['heuristic_depth_2_error']}`",
        f"- Fixed-50 depth-2 chain error: `{payload['headline']['fixed50_depth_2_error']}`",
        f"- Always-parametric depth-2 chain error: `{payload['headline']['always_parametric_depth_2_error']}`",
        f"- Always-context depth-2 chain error: `{payload['headline']['always_context_depth_2_error']}`",
        "",
    ]
    for entry in payload["per_model"]:
        lines.extend(
            [
                f"## {entry['model']}",
                "",
                "| Policy | Mean p(correct source) | Depth-1 error | Depth-2 error | Depth-3 error |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for policy in POLICIES:
            stats = entry["policies"].get(policy)
            if not stats:
                continue
            lines.append(
                f"| {policy} | {stats['mean_probability']} | "
                f"{stats['chain_error']['depth_1']} | {stats['chain_error']['depth_2']} | {stats['chain_error']['depth_3']} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- This is a proxy compounding analysis rather than a full token-level edited-model evaluation.",
            "- It is still useful for the paper because it shows the qualitative prediction cleanly: once the correct source must be chosen repeatedly through a chain, conservative fixed policies degrade multiplicatively.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    out_prefix = ROOT / "docs/generated/mquake_multihop_compounding_note"
    dump_json(payload, out_prefix.with_suffix(".json"))
    out_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["headline"], indent=2))


if __name__ == "__main__":
    main()
