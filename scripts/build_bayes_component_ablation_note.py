#!/usr/bin/env python3
"""Build a Bayes-rule component ablation note from completed benchmark rows."""

from __future__ import annotations

import json
from collections import defaultdict
from math import exp, log
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs/generated"
MODEL_WAVE_ROOT = ROOT / "results/delta_knowledge_arbitration_extended_wave"
SEEDS = [42, 43, 44]
SPOTLIGHT_BENCHMARKS = {"conflictbank", "popqa", "nq_swap", "faitheval", "triviaqa"}


def _clip_probability(value: float, eps: float = 1e-6) -> float:
    return min(max(float(value), eps), 1.0 - eps)


def logit(probability: float) -> float:
    p = _clip_probability(probability)
    return log(p / (1.0 - p))


def sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


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


def policy_probability(features: dict, variant: str) -> float:
    parametric_score = float(features["parametric_score"])
    contextual_score = float(features["contextual_score"])
    context_reliability = float(features["context_reliability"])
    parametric_reliability = float(features["parametric_reliability"])

    if variant == "no_prior_strength":
        parametric_score = 0.5
    elif variant == "no_reliability":
        context_reliability = parametric_reliability

    contextual_logit = logit(contextual_score)
    parametric_logit = logit(parametric_score)
    reliability_gap = logit(context_reliability) - logit(parametric_reliability)
    evidence_gap = contextual_logit - parametric_logit

    if variant == "no_posterior_update":
        combined = 0.3 * reliability_gap
    else:
        combined = 1.4 * evidence_gap + 0.3 * reliability_gap
    return sigmoid(combined)


def log_loss(probability: float, label: int) -> float:
    p = _clip_probability(probability)
    return -log(p) if int(label) == 1 else -log(1.0 - p)


def build_payload() -> dict:
    summaries = defaultdict(lambda: {"regret_sum": 0.0, "count": 0})
    series = defaultdict(lambda: defaultdict(lambda: {"regret_sum": 0.0, "count": 0}))
    variants = ["full_bayes", "no_prior_strength", "no_reliability", "no_posterior_update"]

    for seed in SEEDS:
        for row in load_rows(seed):
            if str(row["benchmark"]) not in SPOTLIGHT_BENCHMARKS:
                continue
            oracle_probability = float(row["oracle_probability"])
            label = int(row["label"])
            oracle_loss = log_loss(oracle_probability, label)
            features = row["features"]
            bench_series = f"{row['benchmark']}::{row['model']}::{seed}"
            for variant in variants:
                if variant == "full_bayes":
                    probability = float(row["policies"]["bayes_proxy"]["probability"])
                else:
                    probability = policy_probability(features, variant)
                regret = log_loss(probability, label) - oracle_loss
                summaries[variant]["regret_sum"] += regret
                summaries[variant]["count"] += 1
                series[variant][bench_series]["regret_sum"] += regret
                series[variant][bench_series]["count"] += 1

    overall_rows = []
    for variant in variants:
        overall_rows.append(
            {
                "variant": variant,
                "mean_regret": round(summaries[variant]["regret_sum"] / summaries[variant]["count"], 4),
                "num_rows": summaries[variant]["count"],
            }
        )

    full_series = {
        key: value["regret_sum"] / value["count"] for key, value in series["full_bayes"].items()
    }
    degraded = {}
    for variant in variants[1:]:
        worse = 0
        total = 0
        for key, value in series[variant].items():
            total += 1
            ablated = value["regret_sum"] / value["count"]
            if ablated > full_series[key]:
                worse += 1
        degraded[variant] = {"worse_series": worse, "num_series": total, "worse_rate": round(worse / total, 4)}

    headline = {
        "full_bayes_mean_regret": overall_rows[0]["mean_regret"],
        "no_prior_strength_mean_regret": overall_rows[1]["mean_regret"],
        "no_reliability_mean_regret": overall_rows[2]["mean_regret"],
        "no_posterior_update_mean_regret": overall_rows[3]["mean_regret"],
    }
    return {"headline": headline, "overall": overall_rows, "degradation": degraded}


def build_markdown(payload: dict) -> str:
    h = payload["headline"]
    lines = [
        "# Bayes Component Ablation Note",
        "",
        "This note removes one component of the practical Bayes rule at a time on the completed three-seed model wave restricted to the spotlight benchmark family.",
        "",
        "## Headline",
        "",
        f"- Full Bayes mean regret: `{h['full_bayes_mean_regret']}`",
        f"- No prior-strength estimate mean regret: `{h['no_prior_strength_mean_regret']}`",
        f"- No reliability estimate mean regret: `{h['no_reliability_mean_regret']}`",
        f"- No posterior update mean regret: `{h['no_posterior_update_mean_regret']}`",
        "",
        "Interpretation:",
        "- Removing the reliability term or the posterior update is clearly harmful both in mean regret and in per-series comparisons.",
        "- Removing the prior-strength term is worse on most series, but not on the aggregate mean; that makes it a mixed, higher-variance component rather than a uniformly necessary one on this broader wave.",
        "",
        "## Overall Table",
        "",
        "| Variant | Mean regret | Rows |",
        "|---|---:|---:|",
    ]
    for row in payload["overall"]:
        lines.append(f"| {row['variant']} | {row['mean_regret']:.4f} | {row['num_rows']} |")
    lines.extend(
        [
            "",
            "## Series Degradation Relative To Full Bayes",
            "",
            "| Ablation | Worse series | Total series | Worse-rate |",
            "|---|---:|---:|---:|",
        ]
    )
    for variant, row in payload["degradation"].items():
        lines.append(
            f"| {variant} | {row['worse_series']} | {row['num_series']} | {row['worse_rate']:.4f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = build_payload()
    out_json = GENERATED / "bayes_component_ablation_note.json"
    out_md = GENERATED / "bayes_component_ablation_note.md"
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    out_md.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(out_json), "md": str(out_md)}, indent=2))


if __name__ == "__main__":
    main()
