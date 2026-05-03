#!/usr/bin/env python3
"""Build theorem-3 review-response analyses from finished row artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402
from utils.metrics import brier_score, expected_calibration_error  # noqa: E402


DEFAULT_MODEL_ROWS = {
    "llama8_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_dpo/theorem3_eval_retry/theorem3_generation_rows.jsonl",
    "llama8_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_llama8b_grpo/theorem3_eval_retry/theorem3_generation_rows.jsonl",
    "mistral7b": "/work/nvme/bgvi/adas17/tts_results/results/mistral7b_theorem3_real_v1/theorem3_generation_rows.jsonl",
    "gemma9b": "/work/nvme/bgvi/adas17/tts_results/results/gemma9b_theorem3_real_v2/theorem3_generation_rows.jsonl",
    "gemma27b": "/work/nvme/bgvi/adas17/tts_results/results/gemma27b_theorem3_real_v2/theorem3_generation_rows.jsonl",
    "qwen14_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_qwen14b_dpo/theorem3_eval_v2/theorem3_generation_rows.jsonl",
    "qwen14_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_qwen14b_grpo/theorem3_eval_v2/theorem3_generation_rows.jsonl",
    "phi3_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_phi3mini_dpo_v2/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "phi3_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_phi3mini_grpo_r3/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "olmo2_dpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_olmo2_7b_dpo_v2/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "olmo2_grpo": "/work/nvme/bgvi/adas17/tts_results/results/e1_olmo2_7b_grpo_r3/theorem3_eval_recovery_v2/theorem3_generation_rows.jsonl",
    "deepseek_llama8": "/work/nvme/bgvi/adas17/tts_results/results/theorem3_deepseek_r1_llama8_real_v1/theorem3_generation_rows.jsonl",
    "rlcr": "/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/theorem3_eval_full_v3/theorem3_generation_rows.jsonl",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build theorem-3 review-response follow-up analyses.")
    parser.add_argument(
        "--output-prefix",
        default="docs/generated/theorem3_review_followups",
        help="Prefix for .json and .md outputs.",
    )
    parser.add_argument("--short-cot", type=int, default=0)
    parser.add_argument("--long-cot", type=int, default=1024)
    parser.add_argument("--num-bootstrap", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--rlcr-eta-root",
        default="/work/nvme/bgvi/adas17/tts_results/results/rlcr_eta_global_v1",
    )
    parser.add_argument(
        "--trace-json",
        default="/work/nvme/bgvi/adas17/tts_results/theorem3_trace_separation_r1_14b_conflictbank_conflict.json",
    )
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _slice_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    confidences = [float(row.get("confidence", 0.5)) for row in rows]
    outcomes = [int(row.get("outcome", 0)) for row in rows]
    mean_conf = statistics.mean(confidences) if confidences else 0.0
    mean_acc = statistics.mean(outcomes) if outcomes else 0.0
    return {
        "accuracy": mean_acc,
        "ece": expected_calibration_error(confidences, outcomes),
        "brier": brier_score(confidences, outcomes),
        "overconfidence_gap": mean_conf - mean_acc,
    }


def _paired_groups(rows: list[dict[str, Any]], *, short_cot: int, long_cot: int) -> dict[tuple[str, str], dict[str, dict[str, dict[str, Any]]]]:
    by_slice: dict[tuple[str, str], dict[str, dict[str, dict[str, Any]]]] = {}
    for row in rows:
        benchmark = str(row.get("benchmark"))
        split = str(row.get("split"))
        cot = int(row.get("cot_length", 0))
        if cot not in {short_cot, long_cot}:
            continue
        key = (benchmark, split)
        by_slice.setdefault(key, {"short": {}, "long": {}})
        bucket = "short" if cot == short_cot else "long"
        by_slice[key][bucket][str(row.get("id"))] = row
    return by_slice


def _headline_from_resample(
    paired: dict[tuple[str, str], dict[str, dict[str, dict[str, Any]]]],
    *,
    rng: random.Random | None,
) -> dict[str, float] | None:
    trend_rows: list[dict[str, float | str]] = []
    for (benchmark, split), buckets in paired.items():
        ids = sorted(set(buckets["short"]).intersection(buckets["long"]))
        if not ids:
            continue
        sampled_ids = [ids[rng.randrange(len(ids))] for _ in ids] if rng is not None else ids
        short_rows = [buckets["short"][id_] for id_ in sampled_ids]
        long_rows = [buckets["long"][id_] for id_ in sampled_ids]
        short_metrics = _slice_metrics(short_rows)
        long_metrics = _slice_metrics(long_rows)
        trend_rows.append(
            {
                "benchmark": benchmark,
                "split": split,
                "ece_delta": long_metrics["ece"] - short_metrics["ece"],
                "brier_delta": long_metrics["brier"] - short_metrics["brier"],
                "accuracy_delta": long_metrics["accuracy"] - short_metrics["accuracy"],
                "overconfidence_gap_delta": long_metrics["overconfidence_gap"] - short_metrics["overconfidence_gap"],
            }
        )

    conflict = [float(row["ece_delta"]) for row in trend_rows if row["split"] == "conflict"]
    no_conflict = [float(row["ece_delta"]) for row in trend_rows if row["split"] == "no_conflict"]
    if not conflict or not no_conflict:
        return None
    return {
        "mean_conflict_ece_delta": statistics.mean(conflict),
        "mean_no_conflict_ece_delta": statistics.mean(no_conflict),
        "conflict_minus_no_conflict_ece_delta": statistics.mean(conflict) - statistics.mean(no_conflict),
    }


def _bootstrap_ci(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)
    low_idx = max(0, int(0.025 * (len(ordered) - 1)))
    high_idx = min(len(ordered) - 1, int(0.975 * (len(ordered) - 1)))
    return {"ci95_low": round(ordered[low_idx], 4), "ci95_high": round(ordered[high_idx], 4)}


def build_model_cis(
    model_rows: dict[str, str],
    *,
    short_cot: int,
    long_cot: int,
    num_bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, raw_path in model_rows.items():
        path = Path(raw_path)
        if not path.exists():
            continue
        rows = _load_rows(path)
        paired = _paired_groups(rows, short_cot=short_cot, long_cot=long_cot)
        point = _headline_from_resample(paired, rng=None)
        if point is None:
            continue
        rng = random.Random(seed)
        conflict_boot: list[float] = []
        no_conflict_boot: list[float] = []
        sep_boot: list[float] = []
        for _ in range(num_bootstrap):
            sample = _headline_from_resample(paired, rng=rng)
            if sample is None:
                continue
            conflict_boot.append(sample["mean_conflict_ece_delta"])
            no_conflict_boot.append(sample["mean_no_conflict_ece_delta"])
            sep_boot.append(sample["conflict_minus_no_conflict_ece_delta"])
        out[label] = {
            "rows_path": raw_path,
            "point": {key: round(value, 4) for key, value in point.items()},
            "bootstrap": {
                "num_bootstrap": len(conflict_boot),
                "mean_conflict_ece_delta": _bootstrap_ci(conflict_boot),
                "mean_no_conflict_ece_delta": _bootstrap_ci(no_conflict_boot),
                "conflict_minus_no_conflict_ece_delta": _bootstrap_ci(sep_boot),
            },
        }
    return out


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return 0.0
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mean_x) ** 2 for a in x))
    den_y = math.sqrt(sum((b - mean_y) ** 2 for b in y))
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def build_conflict_dose_response(
    rows_path: str,
    *,
    short_cot: int,
    long_cot: int,
    num_bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    rows = _load_rows(Path(rows_path))
    pairs: list[dict[str, Any]] = []
    grouped = _paired_groups(rows, short_cot=short_cot, long_cot=long_cot)
    target = grouped.get(("conflictbank", "conflict"), {"short": {}, "long": {}})
    ids = sorted(set(target["short"]).intersection(target["long"]))
    for id_ in ids:
        short_row = target["short"][id_]
        long_row = target["long"][id_]
        strength = float(short_row.get("features", {}).get("conflict_strength", short_row.get("metadata", {}).get("conflict_strength", 0.0)))
        short_gap = float(short_row.get("confidence", 0.5)) - int(short_row.get("outcome", 0))
        long_gap = float(long_row.get("confidence", 0.5)) - int(long_row.get("outcome", 0))
        pairs.append(
            {
                "id": id_,
                "conflict_strength": strength,
                "ece_proxy_delta": abs(long_gap) - abs(short_gap),
                "gap_delta": long_gap - short_gap,
                "accuracy_delta": int(long_row.get("outcome", 0)) - int(short_row.get("outcome", 0)),
            }
        )
    ordered = sorted(pairs, key=lambda row: row["conflict_strength"])
    if not ordered:
        return {"rows_path": rows_path, "pairs": 0, "bins": [], "spearman_conflict_strength_vs_gap_delta": 0.0}

    chunk = max(1, len(ordered) // 3)
    bins = [
        ("low", ordered[:chunk]),
        ("mid", ordered[chunk : 2 * chunk]),
        ("high", ordered[2 * chunk :]),
    ]
    rng = random.Random(seed)
    bin_rows = []
    for label, bucket in bins:
        if not bucket:
            continue
        gap_boot = []
        ece_boot = []
        for _ in range(num_bootstrap):
            sample = [bucket[rng.randrange(len(bucket))] for _ in bucket]
            gap_boot.append(statistics.mean(row["gap_delta"] for row in sample))
            ece_boot.append(statistics.mean(row["ece_proxy_delta"] for row in sample))
        bin_rows.append(
            {
                "bin": label,
                "count": len(bucket),
                "mean_conflict_strength": round(statistics.mean(row["conflict_strength"] for row in bucket), 4),
                "mean_gap_delta": round(statistics.mean(row["gap_delta"] for row in bucket), 4),
                "mean_ece_proxy_delta": round(statistics.mean(row["ece_proxy_delta"] for row in bucket), 4),
                "gap_delta_ci95": _bootstrap_ci(gap_boot),
                "ece_proxy_delta_ci95": _bootstrap_ci(ece_boot),
            }
        )
    strengths = [row["conflict_strength"] for row in ordered]
    gap_deltas = [row["gap_delta"] for row in ordered]
    spearman = _pearson(_rank(strengths), _rank(gap_deltas))
    return {
        "rows_path": rows_path,
        "pairs": len(ordered),
        "spearman_conflict_strength_vs_gap_delta": round(spearman, 4),
        "bins": bin_rows,
    }


def build_rlcr_eta_breakdown(rlcr_eta_root: str, *, num_bootstrap: int, seed: int) -> dict[str, Any]:
    root = Path(rlcr_eta_root)
    rows = []
    for path in sorted(root.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        meta = data["metadata"]
        evaluation = data["evaluation"]
        baseline = evaluation["baseline"]
        selected = evaluation["selected"]
        rows.append(
            {
                "path": str(path),
                "benchmark": str(meta["benchmark"]),
                "condition": str(meta["condition"]),
                "cot_length": int(meta["cot_length"]),
                "selected_eta": float(data["selection"]["selected_eta"]),
                "accuracy_delta": float(selected["accuracy"]) - float(baseline["accuracy"]),
                "ece_delta": float(selected["ece"]) - float(baseline["ece"]),
                "brier_delta": float(selected["brier"]) - float(baseline["brier"]),
                "overconfidence_gap_delta": float(selected["overconfidence_gap"]) - float(baseline["overconfidence_gap"]),
                "selected_accuracy": float(selected["accuracy"]),
                "baseline_accuracy": float(baseline["accuracy"]),
                "selected_predictions": list(selected.get("predictions", [])),
                "baseline_predictions": list(baseline.get("predictions", [])),
            }
        )
    rng = random.Random(seed)
    per_benchmark: dict[str, Any] = {}
    for benchmark in sorted({row["benchmark"] for row in rows}):
        bucket = [row for row in rows if row["benchmark"] == benchmark]
        ece_boot = []
        brier_boot = []
        acc_boot = []
        for _ in range(num_bootstrap):
            sample = [bucket[rng.randrange(len(bucket))] for _ in bucket]
            ece_boot.append(statistics.mean(row["ece_delta"] for row in sample))
            brier_boot.append(statistics.mean(row["brier_delta"] for row in sample))
            acc_boot.append(statistics.mean(row["accuracy_delta"] for row in sample))
        no_conf = [row for row in bucket if row["condition"] == "aligned_context"]
        per_benchmark[benchmark] = {
            "count_cells": len(bucket),
            "mean_accuracy_delta": round(statistics.mean(row["accuracy_delta"] for row in bucket), 4),
            "mean_ece_delta": round(statistics.mean(row["ece_delta"] for row in bucket), 4),
            "mean_brier_delta": round(statistics.mean(row["brier_delta"] for row in bucket), 4),
            "accuracy_delta_ci95": _bootstrap_ci(acc_boot),
            "ece_delta_ci95": _bootstrap_ci(ece_boot),
            "brier_delta_ci95": _bootstrap_ci(brier_boot),
            "aligned_context_mean_accuracy_delta": round(statistics.mean(row["accuracy_delta"] for row in no_conf), 4) if no_conf else None,
            "selected_eta_values": sorted({row["selected_eta"] for row in bucket}),
        }
    return {"root": rlcr_eta_root, "cells": rows, "per_benchmark": per_benchmark}


def build_trace_shuffled_control(trace_json: str, *, num_bootstrap: int, seed: int) -> dict[str, Any]:
    data = json.loads(Path(trace_json).read_text(encoding="utf-8"))
    records = list(data.get("records", []))
    current_scores = [float(row["current_trace_logprob"]) for row in records]
    competitor_scores = [float(row["best_competing_trace_logprob"]) for row in records]
    observed_win = statistics.mean(1.0 if float(a) > float(b) else 0.0 for a, b in zip(current_scores, competitor_scores)) if records else 0.0
    rng = random.Random(seed)
    shuffled = []
    for _ in range(num_bootstrap):
        perm = current_scores[:]
        rng.shuffle(perm)
        shuffled.append(statistics.mean(1.0 if float(a) > float(b) else 0.0 for a, b in zip(perm, competitor_scores)))
    return {
        "trace_json": trace_json,
        "num_records": len(records),
        "observed_win_fraction": round(observed_win, 4),
        "shuffled_win_fraction_mean": round(statistics.mean(shuffled), 4) if shuffled else 0.0,
        "shuffled_win_fraction_ci95": _bootstrap_ci(shuffled) if shuffled else {"ci95_low": 0.0, "ci95_high": 0.0},
    }


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Theorem 3 Review Follow-Ups",
        "",
        "This note closes the review-facing analysis gaps around theorem-3 uncertainty, conflict severity, and RLCR+eta tradeoffs.",
        "",
        "## Bootstrap CIs On Headline Deltas",
        "",
        "| Model | Conflict delta | 95% CI | No-conflict delta | 95% CI | Conflict-minus-no-conflict | 95% CI |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label, row in payload["model_cis"].items():
        point = row["point"]
        boot = row["bootstrap"]
        lines.append(
            f"| {label} | {point['mean_conflict_ece_delta']:.4f} | "
            f"[{boot['mean_conflict_ece_delta']['ci95_low']:.4f}, {boot['mean_conflict_ece_delta']['ci95_high']:.4f}] | "
            f"{point['mean_no_conflict_ece_delta']:.4f} | "
            f"[{boot['mean_no_conflict_ece_delta']['ci95_low']:.4f}, {boot['mean_no_conflict_ece_delta']['ci95_high']:.4f}] | "
            f"{point['conflict_minus_no_conflict_ece_delta']:.4f} | "
            f"[{boot['conflict_minus_no_conflict_ece_delta']['ci95_low']:.4f}, {boot['conflict_minus_no_conflict_ece_delta']['ci95_high']:.4f}] |"
        )

    dose = payload["dose_response"]
    lines.extend(
        [
            "",
            "## Conflict Severity Dose Response",
            "",
            f"- Source rows: `{dose['rows_path']}`",
            f"- Paired prompts: `{dose['pairs']}`",
            f"- Spearman(conflict strength, gap delta): `{dose['spearman_conflict_strength_vs_gap_delta']}`",
            "",
            "| Bin | Count | Mean conflict strength | Mean gap delta | 95% CI | Mean ECE-proxy delta | 95% CI |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in dose["bins"]:
        lines.append(
            f"| {row['bin']} | {row['count']} | {row['mean_conflict_strength']:.4f} | "
            f"{row['mean_gap_delta']:.4f} | "
            f"[{row['gap_delta_ci95']['ci95_low']:.4f}, {row['gap_delta_ci95']['ci95_high']:.4f}] | "
            f"{row['mean_ece_proxy_delta']:.4f} | "
            f"[{row['ece_proxy_delta_ci95']['ci95_low']:.4f}, {row['ece_proxy_delta_ci95']['ci95_high']:.4f}] |"
        )

    lines.extend(
        [
            "",
            "## RLCR + Eta Per-Benchmark Breakdown",
            "",
            "| Benchmark | Mean accuracy delta | 95% CI | Mean ECE delta | 95% CI | Mean Brier delta | 95% CI | Aligned-context accuracy delta | Selected eta values |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for benchmark, row in sorted(payload["rlcr_eta_breakdown"]["per_benchmark"].items()):
        lines.append(
            f"| {benchmark} | {row['mean_accuracy_delta']:.4f} | "
            f"[{row['accuracy_delta_ci95']['ci95_low']:.4f}, {row['accuracy_delta_ci95']['ci95_high']:.4f}] | "
            f"{row['mean_ece_delta']:.4f} | "
            f"[{row['ece_delta_ci95']['ci95_low']:.4f}, {row['ece_delta_ci95']['ci95_high']:.4f}] | "
            f"{row['mean_brier_delta']:.4f} | "
            f"[{row['brier_delta_ci95']['ci95_low']:.4f}, {row['brier_delta_ci95']['ci95_high']:.4f}] | "
            f"{row['aligned_context_mean_accuracy_delta']:.4f} | "
            f"{', '.join(f'{value:.1f}' for value in row['selected_eta_values'])} |"
        )

    trace = payload["trace_shuffled_control"]
    lines.extend(
        [
            "",
            "## Trace Separation Shuffled Control",
            "",
            f"- Records: `{trace['num_records']}`",
            f"- Observed win fraction: `{trace['observed_win_fraction']}`",
            f"- Shuffled-label mean win fraction: `{trace['shuffled_win_fraction_mean']}`",
            f"- Shuffled-label 95% interval: `[{trace['shuffled_win_fraction_ci95']['ci95_low']}, {trace['shuffled_win_fraction_ci95']['ci95_high']}]`",
            "",
            "## Read",
            "",
            "- The bootstrap table makes the ranking uncertainty explicit instead of implying that all small point differences are meaningful.",
            "- The dose-response cut checks whether conflict blowup scales with conflict strength instead of looking like pure noise.",
            "- The RLCR+eta table shows whether the global gain is broad or mostly carried by `ConflictBank`.",
            "- The shuffled-label trace control checks whether the 0.81 self-confirmation rate is an artifact of the scoring setup.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    payload = {
        "model_cis": build_model_cis(
            DEFAULT_MODEL_ROWS,
            short_cot=args.short_cot,
            long_cot=args.long_cot,
            num_bootstrap=args.num_bootstrap,
            seed=args.seed,
        ),
        "dose_response": build_conflict_dose_response(
            DEFAULT_MODEL_ROWS["llama8_grpo"],
            short_cot=args.short_cot,
            long_cot=args.long_cot,
            num_bootstrap=args.num_bootstrap,
            seed=args.seed,
        ),
        "rlcr_eta_breakdown": build_rlcr_eta_breakdown(
            args.rlcr_eta_root,
            num_bootstrap=args.num_bootstrap,
            seed=args.seed,
        ),
        "trace_shuffled_control": build_trace_shuffled_control(
            args.trace_json,
            num_bootstrap=args.num_bootstrap,
            seed=args.seed,
        ),
    }
    output_prefix = ROOT / args.output_prefix
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_prefix.with_suffix('.json')), "markdown": str(output_prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
