#!/usr/bin/env python3
"""Run Paper 2 proxy follow-up experiments and render a reviewer-facing note."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.experiment import run_benchmark_experiment  # noqa: E402


POLICIES = ["bayes_proxy", "cad", "adacad", "self_rag"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Paper 2 proxy follow-up experiments.")
    parser.add_argument("--variant-dir", default=str(ROOT / "data" / "paper2"))
    parser.add_argument("--output-prefix", default=str(ROOT / "docs" / "generated" / "paper2_proxy_followups"))
    parser.add_argument(
        "--models",
        default="meta-llama/Llama-3.1-8B-Instruct,deepseek-ai/DeepSeek-R1-Distill-Llama-8B,mistralai/Mistral-7B-Instruct-v0.3",
    )
    parser.add_argument("--max-examples", type=int, default=0, help="0 keeps all rows from the local variant files.")
    return parser.parse_args()


def _mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _accuracy(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return statistics.mean(1.0 if ((float(row["probability"]) >= 0.5) == bool(int(row["label"]))) else 0.0 for row in rows)


def _spearman(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    def _ranks(values: list[float]) -> list[float]:
        pairs = sorted((value, idx) for idx, value in enumerate(values))
        ranks = [0.0] * len(values)
        i = 0
        while i < len(pairs):
            j = i
            while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
                j += 1
            rank = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                ranks[pairs[k][1]] = rank
            i = j + 1
        return ranks
    xr = _ranks(xs)
    yr = _ranks(ys)
    xm = _mean(xr)
    ym = _mean(yr)
    num = sum((a - xm) * (b - ym) for a, b in zip(xr, yr))
    den_x = sum((a - xm) ** 2 for a in xr) ** 0.5
    den_y = sum((b - ym) ** 2 for b in yr) ** 0.5
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def _policy_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in result.get("experiments", []):
        benchmark = str(group.get("benchmark"))
        model = str(group.get("model"))
        condition = str(group.get("condition"))
        cot_length = str(group.get("cot_length"))
        for row in group.get("rows", []):
            metadata = dict(row.get("metadata", {}) or {})
            for policy_name in POLICIES:
                policy = row.get("policies", {}).get(policy_name)
                if not isinstance(policy, dict):
                    continue
                rows.append(
                    {
                        "benchmark": benchmark,
                        "model": model,
                        "condition": condition,
                        "cot_length": cot_length,
                        "policy": policy_name,
                        "probability": float(policy.get("probability", 0.0)),
                        "regret": float(policy.get("regret", 0.0)),
                        "label": int(row.get("label", 0)),
                        "source_benchmark": str(metadata.get("source_benchmark", benchmark)),
                        "paper2_variant": str(metadata.get("paper2_variant", benchmark)),
                        "noise_rate": float(metadata["noise_rate"]) if "noise_rate" in metadata else None,
                        "num_conflicting_docs": int(metadata["num_conflicting_docs"]) if "num_conflicting_docs" in metadata else None,
                    }
                )
    return rows


def _run_experiment(name: str, dataset_path: Path, models: list[str], *, max_examples: int) -> dict[str, Any]:
    experiment = {
        "name": name,
        "benchmarks": [name],
        "models": models,
        "conditions": ["aligned_context", "conflict_context"],
        "cot_lengths": [0],
        "max_examples": max_examples if max_examples > 0 else 10**9,
        "seed": 42,
    }
    return run_benchmark_experiment(experiment, dataset_overrides={name: str(dataset_path)})


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    variant_dir = Path(args.variant_dir)
    models = [item.strip() for item in args.models.split(",") if item.strip()]
    poisoned = _run_experiment(
        "paper2_poisoned_context",
        variant_dir / "paper2_poisoned_context.jsonl",
        models,
        max_examples=args.max_examples,
    )
    reliability = _run_experiment(
        "paper2_reliability_ablation",
        variant_dir / "paper2_reliability_ablation.jsonl",
        models,
        max_examples=args.max_examples,
    )
    multidoc = _run_experiment(
        "paper2_multidoc_conflict_scaling",
        variant_dir / "paper2_multidoc_conflict_scaling.jsonl",
        models,
        max_examples=args.max_examples,
    )

    poisoned_rows = _policy_rows(poisoned)
    reliability_rows = _policy_rows(reliability)
    multidoc_rows = _policy_rows(multidoc)

    poison_summary: list[dict[str, Any]] = []
    for source_benchmark in sorted({row["source_benchmark"] for row in poisoned_rows}):
        for condition in ["aligned_context", "conflict_context"]:
            scoped = [row for row in poisoned_rows if row["source_benchmark"] == source_benchmark and row["condition"] == condition]
            if not scoped:
                continue
            bayes_scoped = [row for row in scoped if row["policy"] == "bayes_proxy"]
            cad_scoped = [row for row in scoped if row["policy"] == "cad"]
            adacad_scoped = [row for row in scoped if row["policy"] == "adacad"]
            selfrag_scoped = [row for row in scoped if row["policy"] == "self_rag"]
            poison_summary.append(
                {
                    "source_benchmark": source_benchmark,
                    "condition": condition,
                    "bayes_mean_context_weight": round(_mean([row["probability"] for row in bayes_scoped]), 4),
                    "cad_mean_context_weight": round(_mean([row["probability"] for row in cad_scoped]), 4),
                    "adacad_mean_context_weight": round(_mean([row["probability"] for row in adacad_scoped]), 4),
                    "selfrag_mean_context_weight": round(_mean([row["probability"] for row in selfrag_scoped]), 4),
                    "bayes_accuracy": round(_accuracy(bayes_scoped), 4),
                    "cad_accuracy": round(_accuracy(cad_scoped), 4),
                    "bayes_mean_regret": round(_mean([row["regret"] for row in bayes_scoped]), 4),
                    "cad_mean_regret": round(_mean([row["regret"] for row in cad_scoped]), 4),
                    "adacad_mean_regret": round(_mean([row["regret"] for row in adacad_scoped]), 4),
                    "selfrag_mean_regret": round(_mean([row["regret"] for row in selfrag_scoped]), 4),
                }
            )

    reliability_summary: list[dict[str, Any]] = []
    for noise_rate in sorted({float(row["noise_rate"]) for row in reliability_rows if row["noise_rate"] is not None}):
        scoped = [row for row in reliability_rows if row["condition"] == "aligned_context" and row["noise_rate"] == noise_rate]
        if not scoped:
            continue
        for policy in POLICIES:
            policy_scoped = [row for row in scoped if row["policy"] == policy]
            reliability_summary.append(
                {
                    "noise_rate": noise_rate,
                    "policy": policy,
                    "mean_context_weight": round(_mean([row["probability"] for row in policy_scoped]), 4),
                    "accuracy": round(_accuracy(policy_scoped), 4),
                    "mean_regret": round(_mean([row["regret"] for row in policy_scoped]), 4),
                }
            )
    bayes_curve = [row for row in reliability_summary if row["policy"] == "bayes_proxy"]
    bayes_noise_rates = [float(row["noise_rate"]) for row in bayes_curve]
    bayes_weights = [float(row["mean_context_weight"]) for row in bayes_curve]

    multidoc_summary: list[dict[str, Any]] = []
    for k in sorted({int(row["num_conflicting_docs"]) for row in multidoc_rows if row["num_conflicting_docs"] is not None}):
        scoped = [row for row in multidoc_rows if row["condition"] == "conflict_context" and row["num_conflicting_docs"] == k]
        if not scoped:
            continue
        for policy in POLICIES:
            policy_scoped = [row for row in scoped if row["policy"] == policy]
            multidoc_summary.append(
                {
                    "num_conflicting_docs": k,
                    "policy": policy,
                    "mean_context_weight": round(_mean([row["probability"] for row in policy_scoped]), 4),
                    "accuracy": round(_accuracy(policy_scoped), 4),
                    "mean_regret": round(_mean([row["regret"] for row in policy_scoped]), 4),
                }
            )

    return {
        "metadata": {
            "models": models,
            "variant_dir": str(variant_dir),
        },
        "poisoned_context": {
            "summary_rows": poison_summary,
        },
        "reliability_ablation": {
            "summary_rows": reliability_summary,
            "bayes_noise_weight_spearman": round(_spearman(bayes_noise_rates, bayes_weights), 4),
        },
        "multidoc_conflict_scaling": {
            "summary_rows": multidoc_summary,
        },
        "raw_results": {
            "poisoned_context": poisoned,
            "reliability_ablation": reliability,
            "multidoc_conflict_scaling": multidoc,
        },
    }


def build_markdown(payload: dict[str, Any]) -> str:
    poison_rows = payload["poisoned_context"]["summary_rows"]
    reliability_rows = payload["reliability_ablation"]["summary_rows"]
    multidoc_rows = payload["multidoc_conflict_scaling"]["summary_rows"]
    lines = [
        "# Paper 2 Proxy Follow-Ups",
        "",
        "This note runs the fastest Paper 2 follow-ups on top of the benchmark-backed arbitration scaffold using explicit local benchmark variants.",
        "",
        "## Poisoned Context",
        "",
        "These rows test whether the Bayes-style arbitration weight drops on adversarial conflict passages faster than CAD/AdaCAD/Self-RAG.",
        "",
        "| Source benchmark | Condition | Bayes weight | CAD weight | AdaCAD weight | Self-RAG weight | Bayes regret | CAD regret |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in poison_rows:
        lines.append(
            f"| {row['source_benchmark']} | {row['condition']} | {row['bayes_mean_context_weight']:.4f} | "
            f"{row['cad_mean_context_weight']:.4f} | {row['adacad_mean_context_weight']:.4f} | "
            f"{row['selfrag_mean_context_weight']:.4f} | {row['bayes_mean_regret']:.4f} | {row['cad_mean_regret']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Reliability Ablation",
            "",
            f"- Spearman(noise rate, Bayes context weight): `{payload['reliability_ablation']['bayes_noise_weight_spearman']}`",
            "",
            "| Noise rate | Policy | Mean context weight | Accuracy | Mean regret |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in reliability_rows:
        lines.append(
            f"| {row['noise_rate']:.2f} | {row['policy']} | {row['mean_context_weight']:.4f} | "
            f"{row['accuracy']:.4f} | {row['mean_regret']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Multi-Document Conflict Scaling",
            "",
            "| Conflicting docs | Policy | Mean context weight | Accuracy | Mean regret |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in multidoc_rows:
        lines.append(
            f"| {row['num_conflicting_docs']} | {row['policy']} | {row['mean_context_weight']:.4f} | "
            f"{row['accuracy']:.4f} | {row['mean_regret']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The poisoned-context slice is the safety-facing one: if Bayes proxy drops the context weight sharply on `conflict_context` while CAD stays high, that is the direct poisoned-retrieval story.",
            "- The reliability-ablation slice is the T1-facing one: we want the Bayes weight to move monotonically with controlled context corruption rather than staying flat.",
            "- The multi-document scaling slice is the production-shape one: it tests whether arbitration remains helpful as conflicting passages accumulate.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    payload = build_payload(args)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    md_path = output_prefix.with_suffix(".md")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, indent=2))


if __name__ == "__main__":
    main()
