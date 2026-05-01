#!/usr/bin/env python3
"""Causal attention intervention for theorem-3 endogenous-evidence testing.

This script replays real theorem-3 examples while pre-filling the model with
its own previously generated reasoning trace. It then compares baseline answer
generation against an intervention that zeros attention to the trace tokens
during final-answer decoding.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import random
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402
from utils.metrics import accuracy, brier_score, expected_calibration_error, roc_auc_binary  # noqa: E402
from knowledge_arbitration.real_generation import (  # noqa: E402
    _answer_set,
    _answers_match,
    _condition_split,
    _extract_answer,
    _extract_confidence,
    _prompt_style_for_cot_length,
    _question_block,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run theorem-3 trace-attention intervention.")
    parser.add_argument("--rows-jsonl", required=True, help="Comma-separated theorem-3 row files.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--condition", default="conflict_context")
    parser.add_argument("--cot-lengths", default="0,128,1024")
    parser.add_argument("--max-rows-per-cot", type=int, default=100)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--torch-dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    return parser.parse_args()


def _load_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    rows.append(json.loads(stripped))
    return rows


def _select_rows(
    rows: list[dict[str, Any]],
    *,
    model_name: str,
    benchmark: str,
    condition: str,
    cot_lengths: list[int],
    max_rows_per_cot: int,
    seed: int,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for cot_length in cot_lengths:
        bucket = [
            row
            for row in rows
            if str(row.get("model")) == model_name
            and str(row.get("benchmark")) == benchmark
            and str(row.get("condition")) == condition
            and int(row.get("cot_length", 0)) == cot_length
            and row.get("answer") is not None
        ]
        bucket.sort(key=lambda row: str(row.get("id")))
        if len(bucket) > max_rows_per_cot:
            bucket = rng.sample(bucket, max_rows_per_cot)
            bucket.sort(key=lambda row: str(row.get("id")))
        selected.extend(bucket)
    return selected


def _load_model_and_tokenizer(model_name: str, torch_dtype: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype_map: dict[str, Any] = {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    load_kwargs: dict[str, Any] = {"torch_dtype": dtype_map[torch_dtype], "trust_remote_code": True}
    if torch.cuda.is_available() and importlib.util.find_spec("accelerate") is not None:
        load_kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    if "device_map" not in load_kwargs:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
    model.eval()
    return tokenizer, model


def _build_segments(row: dict[str, Any]) -> tuple[str, str, str]:
    style = _prompt_style_for_cot_length(int(row.get("cot_length", 0)))
    question = _question_block(row, str(row.get("condition")))
    prompt = f"{style.system_prompt}\n\n{question}\n\n"
    reasoning = str(row.get("reasoning_text", "")).strip()
    if int(row.get("cot_length", 0)) > 0 and reasoning:
        reasoning_segment = f"<think>{reasoning}</think>\n"
    else:
        reasoning_segment = ""
    answer_prefix = "<answer>"
    return prompt, reasoning_segment, answer_prefix


def _encode_with_trace_mask(tokenizer: Any, prompt: str, reasoning_segment: str, answer_prefix: str, max_length: int):
    bos = [tokenizer.bos_token_id] if tokenizer.bos_token_id is not None else []
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
    reasoning_ids = tokenizer.encode(reasoning_segment, add_special_tokens=False)
    answer_prefix_ids = tokenizer.encode(answer_prefix, add_special_tokens=False)
    input_ids = bos + prompt_ids + reasoning_ids + answer_prefix_ids
    if len(input_ids) > max_length:
        input_ids = input_ids[-max_length:]
    attention_mask = [1] * len(input_ids)

    # Recompute the reasoning span after truncation.
    reasoning_start = len(bos) + len(prompt_ids)
    reasoning_end = reasoning_start + len(reasoning_ids)
    overflow = len(bos) + len(prompt_ids) + len(reasoning_ids) + len(answer_prefix_ids) - len(input_ids)
    if overflow > 0:
        reasoning_start = max(0, reasoning_start - overflow)
        reasoning_end = max(0, reasoning_end - overflow)
    masked_attention = attention_mask[:]
    for idx in range(reasoning_start, min(reasoning_end, len(masked_attention))):
        masked_attention[idx] = 0
    return input_ids, attention_mask, masked_attention


def _generate(tokenizer: Any, model: Any, input_ids: list[int], attention_mask: list[int], max_new_tokens: int) -> str:
    import torch

    device = model.device if hasattr(model, "device") else next(model.parameters()).device
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)
    mask_tensor = torch.tensor([attention_mask], dtype=torch.long, device=device)
    with torch.no_grad():
        generated = model.generate(
            input_ids=input_tensor,
            attention_mask=mask_tensor,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    new_tokens = generated[0, input_tensor.shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=False)


def _evaluate_setting(
    rows: list[dict[str, Any]],
    *,
    tokenizer: Any,
    model: Any,
    max_length: int,
    max_new_tokens: int,
    masked: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        prompt, reasoning_segment, answer_prefix = _build_segments(row)
        input_ids, full_mask, masked_mask = _encode_with_trace_mask(
            tokenizer,
            prompt,
            reasoning_segment,
            answer_prefix,
            max_length=max_length,
        )
        output_text = _generate(
            tokenizer,
            model,
            input_ids,
            masked_mask if masked else full_mask,
            max_new_tokens=max_new_tokens,
        )
        answer = _extract_answer(output_text)
        confidence = _extract_confidence(output_text)
        if confidence is None:
            confidence = 0.5
        gold_answers = _answer_set(row.get("gold_answers") or row.get("label"))
        outcome = int(_answers_match(answer, gold_answers))
        records.append(
            {
                "id": str(row.get("id")),
                "benchmark": str(row.get("benchmark")),
                "condition": str(row.get("condition")),
                "cot_length": int(row.get("cot_length", 0)),
                "answer": answer,
                "confidence": float(confidence),
                "outcome": outcome,
                "raw_response": output_text,
            }
        )
    return records


def _metrics(records: list[dict[str, Any]]) -> dict[str, float]:
    confidences = [float(row["confidence"]) for row in records]
    outcomes = [int(row["outcome"]) for row in records]
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    mean_accuracy = accuracy(bool(item) for item in outcomes)
    return {
        "count": len(records),
        "accuracy": round(mean_accuracy, 6),
        "ece": round(expected_calibration_error(confidences, outcomes), 6),
        "brier": round(brier_score(confidences, outcomes), 6),
        "auroc": round(roc_auc_binary(confidences, outcomes), 6),
        "mean_confidence": round(mean_confidence, 6),
        "overconfidence_gap": round(mean_confidence - mean_accuracy, 6),
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_cot: dict[int, dict[str, Any]] = {}
    for cot_length in sorted({int(row["cot_length"]) for row in records}):
        bucket = [row for row in records if int(row["cot_length"]) == cot_length]
        by_cot[cot_length] = _metrics(bucket)
    return {str(key): value for key, value in by_cot.items()}


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Theorem 3 Attention Intervention",
        "",
        "This run tests the endogenous-evidence claim causally by replaying the model's own reasoning traces and then zeroing attention to the trace tokens during final-answer decoding.",
        "",
        "## Setup",
        "",
        f"- Model: `{payload['metadata']['model_name']}`",
        f"- Benchmark / condition: `{payload['metadata']['benchmark']}` / `{payload['metadata']['condition']}`",
        f"- CoT lengths: `{payload['metadata']['cot_lengths']}`",
        f"- Max rows per CoT: `{payload['metadata']['max_rows_per_cot']}`",
        "",
        "## Per-CoT Metrics",
        "",
        "| CoT | Setting | Accuracy | ECE | Brier | AUROC | Mean conf | Gap |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cot in payload["baseline"]:
        base = payload["baseline"][cot]
        masked = payload["masked_trace_attention"][cot]
        lines.append(
            f"| {cot} | baseline | {base['accuracy']:.4f} | {base['ece']:.4f} | {base['brier']:.4f} | {base['auroc']:.4f} | {base['mean_confidence']:.4f} | {base['overconfidence_gap']:.4f} |"
        )
        lines.append(
            f"| {cot} | masked | {masked['accuracy']:.4f} | {masked['ece']:.4f} | {masked['brier']:.4f} | {masked['auroc']:.4f} | {masked['mean_confidence']:.4f} | {masked['overconfidence_gap']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            f"- Gap delta at medium CoT: `{payload['headline']['gap_delta_128']}`.",
            f"- Gap delta at long CoT: `{payload['headline']['gap_delta_1024']}`.",
            "- If masking trace attention lowers the gap while holding the prompt and answer format fixed, that is direct causal support for the endogenous-evidence mechanism.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    row_paths = [Path(item.strip()) for item in args.rows_jsonl.split(",") if item.strip()]
    cot_lengths = [int(item.strip()) for item in args.cot_lengths.split(",") if item.strip()]
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_rows(row_paths)
    selected = _select_rows(
        rows,
        model_name=args.model_name,
        benchmark=args.benchmark,
        condition=args.condition,
        cot_lengths=cot_lengths,
        max_rows_per_cot=args.max_rows_per_cot,
        seed=args.seed,
    )
    if not selected:
        raise SystemExit("No matching theorem-3 rows found for attention intervention.")

    tokenizer, model = _load_model_and_tokenizer(args.model_name, args.torch_dtype)
    baseline_records = _evaluate_setting(
        selected,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        max_new_tokens=args.max_new_tokens,
        masked=False,
    )
    masked_records = _evaluate_setting(
        selected,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        max_new_tokens=args.max_new_tokens,
        masked=True,
    )

    baseline = _aggregate(baseline_records)
    masked = _aggregate(masked_records)
    payload = {
        "metadata": {
            "model_name": args.model_name,
            "benchmark": args.benchmark,
            "condition": args.condition,
            "cot_lengths": cot_lengths,
            "max_rows_per_cot": args.max_rows_per_cot,
            "max_new_tokens": args.max_new_tokens,
            "max_length": args.max_length,
            "seed": args.seed,
            "rows_jsonl": [str(path) for path in row_paths],
        },
        "baseline": baseline,
        "masked_trace_attention": masked,
        "headline": {
            "gap_delta_128": round(masked.get("128", {}).get("overconfidence_gap", 0.0) - baseline.get("128", {}).get("overconfidence_gap", 0.0), 6),
            "gap_delta_1024": round(masked.get("1024", {}).get("overconfidence_gap", 0.0) - baseline.get("1024", {}).get("overconfidence_gap", 0.0), 6),
        },
        "baseline_preview": baseline_records[:20],
        "masked_preview": masked_records[:20],
    }
    dump_json(payload, output_dir / "theorem3_attention_intervention.json")
    (output_dir / "theorem3_attention_intervention.md").write_text(_build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "num_rows": len(selected)}, indent=2))


if __name__ == "__main__":
    main()
