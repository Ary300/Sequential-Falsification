#!/usr/bin/env python3
"""Build the theorem-3 open-item follow-up note."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402
from utils.metrics import expected_calibration_error  # noqa: E402


MODEL_ROWS = {
    "llama8_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_grpo/theorem3_eval_retry/theorem3_generation_rows.jsonl",
    "llama8_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_dpo/theorem3_eval_retry/theorem3_generation_rows.jsonl",
    "llama8_sft": "/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_sft_control/theorem3_eval_full_v2/theorem3_generation_rows.jsonl",
    "phi3_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_phi3mini_grpo_r3/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "phi3_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_phi3mini_dpo_v2/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "deepseek_llama8": "/work/nvme/bgvi/adas17/tts_results/results/theorem3_deepseek_r1_llama8_real_v1/theorem3_generation_rows.jsonl",
    "rlcr": "/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/theorem3_eval_full_v3/theorem3_generation_rows.jsonl",
    "qwen14_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_qwen14b_grpo/theorem3_eval_v2/theorem3_generation_rows.jsonl",
    "qwen14_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_qwen14b_dpo/theorem3_eval_v2/theorem3_generation_rows.jsonl",
    "mistral7b": "/work/nvme/bgvi/adas17/tts_results/results/mistral7b_theorem3_real_v1/theorem3_generation_rows.jsonl",
    "gemma9b": "/work/nvme/bgvi/adas17/tts_results/results/gemma9b_theorem3_real_v2/theorem3_generation_rows.jsonl",
    "gemma27b": "/work/nvme/bgvi/adas17/tts_results/results/gemma27b_theorem3_real_v2/theorem3_generation_rows.jsonl",
    "olmo2_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_olmo2_7b_dpo_v2/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "olmo2_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_olmo2_7b_grpo_r3/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "llama31_8b": "/work/nvme/bgvi/adas17/tts_results/results/theorem3_llama31_8b_real_v2/theorem3_generation_rows.jsonl",
}

ETA_METHOD_JSON = ROOT / "docs/generated/theorem3_eta_tempered_method_result.json"
GENERATED_MD = ROOT / "docs/generated/theorem3_open_item_followups.md"
GENERATED_JSON = ROOT / "docs/generated/theorem3_open_item_followups.json"


def _load_rows(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _ece_equal_mass(confidences: list[float], outcomes: list[int], n_bins: int = 10) -> float:
    if not confidences:
        return 0.0
    pairs = sorted(zip(confidences, outcomes), key=lambda item: item[0])
    total = len(pairs)
    value = 0.0
    for idx in range(n_bins):
        lo = (idx * total) // n_bins
        hi = ((idx + 1) * total) // n_bins
        bucket = pairs[lo:hi]
        if not bucket:
            continue
        avg_conf = sum(conf for conf, _ in bucket) / len(bucket)
        avg_acc = sum(outcome for _, outcome in bucket) / len(bucket)
        value += (len(bucket) / total) * abs(avg_conf - avg_acc)
    return value


def _brier(confidences: list[float], outcomes: list[int]) -> float:
    if not confidences:
        return 0.0
    return sum((conf - outcome) ** 2 for conf, outcome in zip(confidences, outcomes)) / len(confidences)


def _log_loss(confidences: list[float], outcomes: list[int], *, eps: float = 1e-12) -> float:
    if not confidences:
        return 0.0
    values = []
    for conf, outcome in zip(confidences, outcomes):
        bounded = min(1.0 - eps, max(eps, conf))
        values.append(-(outcome * math.log(bounded) + (1 - outcome) * math.log(1.0 - bounded)))
    return sum(values) / len(values)


def _brier_decomposition(confidences: list[float], outcomes: list[int], n_bins: int = 10) -> dict[str, float]:
    bins = [[] for _ in range(n_bins)]
    for conf, outcome in zip(confidences, outcomes):
        bucket = min(n_bins - 1, max(0, int(conf * n_bins)))
        bins[bucket].append((conf, outcome))
    total = len(confidences)
    if total == 0:
        return {"reliability": 0.0, "resolution": 0.0, "uncertainty": 0.0}
    outcome_mean = sum(outcomes) / total
    reliability = 0.0
    resolution = 0.0
    for bucket in bins:
        if not bucket:
            continue
        weight = len(bucket) / total
        conf_mean = sum(conf for conf, _ in bucket) / len(bucket)
        acc_mean = sum(outcome for _, outcome in bucket) / len(bucket)
        reliability += weight * ((conf_mean - acc_mean) ** 2)
        resolution += weight * ((acc_mean - outcome_mean) ** 2)
    return {
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": outcome_mean * (1.0 - outcome_mean),
    }


def _slice_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    confidences = [float(row.get("confidence", 0.5)) for row in rows]
    outcomes = [int(row.get("outcome", 0)) for row in rows]
    decomposition = _brier_decomposition(confidences, outcomes)
    return {
        "ece": expected_calibration_error(confidences, outcomes),
        "adaptive_ece": _ece_equal_mass(confidences, outcomes),
        "brier": _brier(confidences, outcomes),
        "log_loss": _log_loss(confidences, outcomes),
        "brier_reliability": decomposition["reliability"],
        "brier_resolution": decomposition["resolution"],
    }


def _metric_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: {"short": [], "long": []})
    for row in rows:
        cot_length = int(row.get("cot_length", 0))
        if cot_length not in {0, 1024}:
            continue
        bucket = "short" if cot_length == 0 else "long"
        grouped[(str(row.get("benchmark")), str(row.get("split")))][bucket].append(row)

    deltas: dict[str, dict[str, list[float]]] = {
        "conflict": defaultdict(list),
        "no_conflict": defaultdict(list),
    }
    for (_, split), payload in grouped.items():
        if split not in deltas:
            continue
        short_metrics = _slice_metrics(payload["short"])
        long_metrics = _slice_metrics(payload["long"])
        for metric, short_value in short_metrics.items():
            deltas[split][metric].append(long_metrics[metric] - short_value)

    summary: dict[str, Any] = {}
    for metric in ("ece", "adaptive_ece", "brier", "log_loss", "brier_reliability", "brier_resolution"):
        conflict_delta = statistics.mean(deltas["conflict"][metric])
        no_conflict_delta = statistics.mean(deltas["no_conflict"][metric])
        summary[metric] = {
            "conflict_delta": round(conflict_delta, 4),
            "no_conflict_delta": round(no_conflict_delta, 4),
            "separation": round(conflict_delta - no_conflict_delta, 4),
        }
    return summary


def _conflict_construction_audit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = defaultdict(lambda: {"short": [], "long": []})
    for row in rows:
        if str(row.get("benchmark")) != "conflictbank":
            continue
        family = str((row.get("metadata") or {}).get("conflict_family", "unknown"))
        split = str(row.get("split"))
        cot_length = int(row.get("cot_length", 0))
        if cot_length not in {0, 1024}:
            continue
        bucket = "short" if cot_length == 0 else "long"
        grouped[(family, split)][bucket].append(row)

    out: list[dict[str, Any]] = []
    for family in ("misinformation", "temporal", "semantic"):
        conflict_short = _slice_metrics(grouped[(family, "conflict")]["short"])
        conflict_long = _slice_metrics(grouped[(family, "conflict")]["long"])
        no_conf_short = _slice_metrics(grouped[(family, "no_conflict")]["short"])
        no_conf_long = _slice_metrics(grouped[(family, "no_conflict")]["long"])
        conflict_delta = conflict_long["ece"] - conflict_short["ece"]
        no_conf_delta = no_conf_long["ece"] - no_conf_short["ece"]
        out.append(
            {
                "family": family,
                "conflict_ece_delta": round(conflict_delta, 4),
                "no_conflict_ece_delta": round(no_conf_delta, 4),
                "conflict_minus_no_conflict": round(conflict_delta - no_conf_delta, 4),
                "conflict_gap_delta": round(conflict_long["ece"] - conflict_short["ece"], 4),
                "count_conflict": len(grouped[(family, "conflict")]["short"]),
                "count_no_conflict": len(grouped[(family, "no_conflict")]["short"]),
            }
        )
    return out


def _partial_order_check(robustness: dict[str, dict[str, Any]]) -> dict[str, Any]:
    separations = {label: payload["ece"]["separation"] for label, payload in robustness.items()}
    high_group = ["llama8_grpo", "rlcr", "phi3_grpo", "deepseek_llama8"]
    low_group = ["llama8_sft", "llama8_dpo", "qwen14_grpo", "mistral7b", "gemma27b", "olmo2_grpo", "olmo2_dpo", "phi3_dpo", "llama31_8b"]
    wins = 0.0
    comparisons = 0
    for high in high_group:
        for low in low_group:
            if high not in separations or low not in separations:
                continue
            comparisons += 1
            if separations[high] > separations[low]:
                wins += 1.0
            elif separations[high] == separations[low]:
                wins += 0.5
    observed_ranking = sorted(separations.items(), key=lambda item: item[1], reverse=True)
    return {
        "high_group": high_group,
        "low_group": low_group,
        "high_mean_separation": round(statistics.mean(separations[label] for label in high_group if label in separations), 4),
        "low_mean_separation": round(statistics.mean(separations[label] for label in low_group if label in separations), 4),
        "pairwise_auc": round((wins / comparisons) if comparisons else 0.0, 4),
        "pairwise_comparisons": comparisons,
        "observed_ranking": [{"label": label, "separation": round(value, 4)} for label, value in observed_ranking],
    }


def _eta_leakage_audit() -> dict[str, Any]:
    payload = json.loads(ETA_METHOD_JSON.read_text(encoding="utf-8"))
    metadata = payload.get("metadata", {})
    return {
        "selection_rule": metadata.get("selection_rule"),
        "calibration_size": metadata.get("calibration_size"),
        "evaluation_size": metadata.get("evaluation_size"),
        "selected_eta": payload.get("selection", {}).get("selected_eta"),
        "baseline_eval": payload.get("evaluation", {}).get("baseline", {}),
        "selected_eval": payload.get("evaluation", {}).get("selected", {}),
    }


def main() -> None:
    row_payloads = {label: _load_rows(path) for label, path in MODEL_ROWS.items() if Path(path).exists()}
    robustness = {label: _metric_summary(rows) for label, rows in row_payloads.items()}
    conflict_audit = _conflict_construction_audit(row_payloads["llama8_grpo"])
    partial_order = _partial_order_check(robustness)
    eta_audit = _eta_leakage_audit()

    payload = {
        "conflict_construction_audit": conflict_audit,
        "calibration_robustness": robustness,
        "eta_leakage_audit": eta_audit,
        "theorem_partial_order_check": partial_order,
    }
    dump_json(payload, GENERATED_JSON)

    lines = [
        "# Theorem 3 Open-Item Follow-Ups",
        "",
        "Generated follow-up computations for the remaining theorem-3 reviewer-facing open items.",
        "",
        "## Conflict-Construction Audit",
        "",
        "| Conflict family | Conflict ECE delta | No-conflict ECE delta | Conflict minus no-conflict |",
        "|---|---:|---:|---:|",
    ]
    for row in conflict_audit:
        lines.append(
            f"| {row['family']} | {row['conflict_ece_delta']:+.4f} | {row['no_conflict_ece_delta']:+.4f} | {row['conflict_minus_no_conflict']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Calibration-Metric Robustness",
            "",
            "| Model | ECE sep. | Adaptive ECE sep. | Brier sep. | Log-loss sep. | Brier reliability sep. |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label in ("llama8_grpo", "rlcr", "phi3_grpo", "deepseek_llama8", "llama8_sft", "mistral7b", "gemma27b", "qwen14_grpo"):
        if label not in robustness:
            continue
        row = robustness[label]
        lines.append(
            f"| {label} | {row['ece']['separation']:+.4f} | {row['adaptive_ece']['separation']:+.4f} | "
            f"{row['brier']['separation']:+.4f} | {row['log_loss']['separation']:+.4f} | {row['brier_reliability']['separation']:+.4f} |"
        )
    lines.extend(
        [
            "",
            "## Eta-Selection Leakage Audit",
            "",
            f"- Selection rule: `{eta_audit['selection_rule']}`",
            f"- Calibration size: `{eta_audit['calibration_size']}`",
            f"- Evaluation size: `{eta_audit['evaluation_size']}`",
            f"- Selected eta: `{eta_audit['selected_eta']}`",
            "",
            "## Theorem Partial-Order Check",
            "",
            f"- High-regime mean separation: `{partial_order['high_mean_separation']}`",
            f"- Low-regime mean separation: `{partial_order['low_mean_separation']}`",
            f"- Pairwise AUC: `{partial_order['pairwise_auc']}` over `{partial_order['pairwise_comparisons']}` comparisons",
            "",
        ]
    )
    GENERATED_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
