#!/usr/bin/env python3
"""Build a compact RLVR-validation note for theorem 3."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 RLVR validation note.")
    parser.add_argument(
        "--source",
        default="results/delta_knowledge_arbitration_extended_wave/arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=1p0/arbitration_spotlight_extended_t3_calibration_wave__seed=44__eta_value=1p0_benchmark_results.json",
    )
    parser.add_argument("--output-prefix", default="docs/generated/theorem3_rlvr_validation_note")
    return parser.parse_args()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_summary(payload: dict) -> dict:
    rows = []
    for experiment in payload.get("experiments", []):
        rows.extend(experiment.get("rows", []))

    target_models = [
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "Qwen/Qwen2.5-32B-Instruct",
        "Qwen/Qwen2.5-14B-Instruct",
    ]
    summaries = {}
    for model in target_models:
        model_rows = [row for row in rows if row.get("model") == model]
        if not model_rows:
            continue
        all_gain = _mean(
            [float(row["regret_by_policy"]["heuristic_adaptive"]) - float(row["regret_by_policy"]["bayes_proxy"]) for row in model_rows]
        )
        conflict_rows = [row for row in model_rows if row.get("split") == "conflict"]
        conflict_gain = _mean(
            [float(row["regret_by_policy"]["heuristic_adaptive"]) - float(row["regret_by_policy"]["bayes_proxy"]) for row in conflict_rows]
        )
        conflictbank_longcot = [
            row
            for row in model_rows
            if row.get("benchmark") == "conflictbank" and row.get("split") == "conflict" and str(row.get("cot_length")) == "1024"
        ]
        conflictbank_longcot_gain = _mean(
            [float(row["regret_by_policy"]["heuristic_adaptive"]) - float(row["regret_by_policy"]["bayes_proxy"]) for row in conflictbank_longcot]
        )
        summaries[model] = {
            "num_rows": len(model_rows),
            "all_gain": round(all_gain, 4),
            "conflict_gain": round(conflict_gain, 4),
            "conflictbank_conflict_longcot_gain": round(conflictbank_longcot_gain, 4),
        }

    llama = summaries.get("deepseek-ai/DeepSeek-R1-Distill-Llama-70B", {})
    qwen_r1 = summaries.get("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", {})
    qwen32 = summaries.get("Qwen/Qwen2.5-32B-Instruct", {})
    qwen14 = summaries.get("Qwen/Qwen2.5-14B-Instruct", {})
    headline = {
        "source_seed": payload.get("metadata", {}).get("seed"),
        "source_eta_value": payload.get("metadata", {}).get("eta_value", "1p0"),
        "deepseek_llama_all_gain": llama.get("all_gain"),
        "deepseek_llama_conflict_gain": llama.get("conflict_gain"),
        "deepseek_llama_conflictbank_conflict_longcot_gain": llama.get("conflictbank_conflict_longcot_gain"),
        "deepseek_qwen_conflictbank_conflict_longcot_gain": qwen_r1.get("conflictbank_conflict_longcot_gain"),
        "qwen32_conflictbank_conflict_longcot_gain": qwen32.get("conflictbank_conflict_longcot_gain"),
        "qwen14_conflictbank_conflict_longcot_gain": qwen14.get("conflictbank_conflict_longcot_gain"),
    }
    return {
        "headline": headline,
        "model_summaries": summaries,
    }


def build_markdown(summary: dict) -> str:
    h = summary["headline"]
    lines = [
        "# Theorem 3 RLVR Validation Note",
        "",
        "This note extracts the `R1-Distill-Llama-70B` read from the completed extended theorem-3 calibration wave.",
        "",
        "## Headline",
        "",
        f"- Source seed: `{h['source_seed']}`",
        f"- DeepSeek `R1-Distill-Llama-70B` all-slice Bayes-vs-heuristic gain: `{h['deepseek_llama_all_gain']}`",
        f"- DeepSeek `R1-Distill-Llama-70B` conflict-only Bayes-vs-heuristic gain: `{h['deepseek_llama_conflict_gain']}`",
        f"- DeepSeek `R1-Distill-Llama-70B` `ConflictBank` conflict `cot=1024` Bayes-vs-heuristic gain: `{h['deepseek_llama_conflictbank_conflict_longcot_gain']}`",
        f"- DeepSeek `R1-Distill-Qwen-7B` matching slice gain: `{h['deepseek_qwen_conflictbank_conflict_longcot_gain']}`",
        f"- `Qwen2.5-32B-Instruct` matching slice gain: `{h['qwen32_conflictbank_conflict_longcot_gain']}`",
        f"- `Qwen2.5-14B-Instruct` matching slice gain: `{h['qwen14_conflictbank_conflict_longcot_gain']}`",
        "",
        "## Read",
        "",
        "- The completed theorem-3 calibration wave now includes a real `DeepSeek-R1-Distill-Llama-70B` cell, so the RLVR-style framing is no longer missing the Llama-backbone validation row.",
        "- The cleanest comparable slice is `ConflictBank` conflict at `cot=1024`, where the DeepSeek-Llama row still favors Bayes over the heuristic.",
        "- The broader conflict-only average remains benchmark-dependent, so the safest wording is still the rewritten RLVR-conditioned two-regime claim rather than a universal monotone law.",
        "",
        "## Model Table",
        "",
        "| Model | Rows | All-slice gain | Conflict-only gain | ConflictBank conflict `cot=1024` gain |",
        "|---|---:|---:|---:|---:|",
    ]
    for model, row in summary["model_summaries"].items():
        lines.append(
            f"| {model} | {row['num_rows']} | {row['all_gain']:.4f} | {row['conflict_gain']:.4f} | {row['conflictbank_conflict_longcot_gain']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(_load(ROOT / args.source))
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
