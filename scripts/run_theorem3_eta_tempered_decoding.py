#!/usr/bin/env python3
"""Run eta-tempered decoding over saved theorem-3 reasoning traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.eta_tempering import (  # noqa: E402
    CandidateScore,
    build_messages_for_row,
    candidate_answers_from_row,
    choose_eta,
    evaluate_eta,
    split_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run eta-tempered theorem-3 decoding on saved traces.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--condition", default="conflict_context")
    parser.add_argument("--cot-length", type=int, default=1024)
    parser.add_argument("--calibration-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-examples", type=int)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--eta-grid", default="0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0")
    parser.add_argument("--torch-dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _filter_rows(rows: list[dict[str, Any]], *, benchmark: str, condition: str, cot_length: int) -> list[dict[str, Any]]:
    filtered = [
        row
        for row in rows
        if str(row.get("benchmark")) == benchmark
        and str(row.get("condition")) == condition
        and int(row.get("cot_length", 0)) == cot_length
    ]
    deduped: dict[str, dict[str, Any]] = {}
    for row in filtered:
        deduped[str(row["id"])] = row
    return list(deduped.values())


def _apply_chat_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except ValueError:
            pass
    rendered = []
    for message in messages:
        rendered.append(f"{message['role'].upper()}:\n{message['content'].strip()}\n")
    rendered.append("ASSISTANT:\n")
    return "\n".join(rendered)


def _candidate_suffix(answer: str) -> str:
    return f"{answer}</answer>"


def _score_candidate_batch(
    model: Any,
    tokenizer: Any,
    *,
    prompt: str,
    candidates: list[str],
    batch_size: int,
) -> dict[str, float]:
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)["input_ids"][0]
    prompt_len = int(prompt_ids.shape[0])
    scores: dict[str, float] = {}
    continuations = [_candidate_suffix(candidate) for candidate in candidates]

    for start in range(0, len(candidates), batch_size):
        batch_candidates = candidates[start : start + batch_size]
        batch_texts = [prompt + _candidate_suffix(candidate) for candidate in batch_candidates]
        encoded = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            add_special_tokens=False,
        )
        encoded = {key: value.to(model.device) for key, value in encoded.items()}
        input_ids = encoded["input_ids"]
        attention_mask = encoded["attention_mask"]
        labels = input_ids.clone()
        labels[:, :prompt_len] = -100
        labels = labels.masked_fill(attention_mask == 0, -100)
        with torch.no_grad():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            log_probs = outputs.logits[:, :-1, :].log_softmax(dim=-1)
        target_ids = input_ids[:, 1:]
        target_log_probs = log_probs.gather(dim=-1, index=target_ids.unsqueeze(-1)).squeeze(-1)
        target_mask = (labels[:, 1:] != -100).float()
        sequence_log_probs = (target_log_probs * target_mask).sum(dim=-1).detach().cpu().tolist()
        for candidate, score in zip(batch_candidates, sequence_log_probs, strict=False):
            scores[candidate] = float(score)
    return scores


def _score_rows(
    rows: list[dict[str, Any]],
    *,
    model_name: str,
    batch_size: int,
    torch_dtype: str,
) -> dict[str, list[CandidateScore]]:
    import importlib.util
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype_map = {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    load_kwargs: dict[str, Any] = {"torch_dtype": dtype_map[torch_dtype]}
    if torch.cuda.is_available() and importlib.util.find_spec("accelerate") is not None:
        load_kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    if "device_map" not in load_kwargs:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
    model.eval()

    scored: dict[str, list[CandidateScore]] = {}
    for index, row in enumerate(rows, start=1):
        candidates = candidate_answers_from_row(row)
        if len(candidates) < 2:
            continue
        post_messages = build_messages_for_row(row, condition=str(row["condition"]), long_cot=True)
        post_prompt = (
            _apply_chat_template(tokenizer, post_messages)
            + f"<think>{str(row.get('reasoning_text', '')).strip()}</think>\n<answer>"
        )
        prior_messages = build_messages_for_row(row, condition="closed_book", long_cot=False)
        prior_prompt = _apply_chat_template(tokenizer, prior_messages) + "<answer>"
        posterior_scores = _score_candidate_batch(
            model,
            tokenizer,
            prompt=post_prompt,
            candidates=candidates,
            batch_size=batch_size,
        )
        prior_scores = _score_candidate_batch(
            model,
            tokenizer,
            prompt=prior_prompt,
            candidates=candidates,
            batch_size=batch_size,
        )
        scored[str(row["id"])] = [
            CandidateScore(
                answer=candidate,
                normalized_answer=candidate.strip().lower(),
                posterior_logprob=posterior_scores[candidate],
                prior_logprob=prior_scores[candidate],
            )
            for candidate in candidates
            if candidate in posterior_scores and candidate in prior_scores
        ]
        if index % 25 == 0:
            print(
                json.dumps(
                    {
                        "event": "scored_rows",
                        "completed": index,
                        "total": len(rows),
                        "last_id": str(row["id"]),
                    }
                ),
                flush=True,
            )
    return scored


def _etas(spec: str) -> list[float]:
    normalized = spec.replace(";", ",").replace(":", ",")
    values = [float(item.strip()) for item in normalized.split(",") if item.strip()]
    deduped = sorted({round(value, 6) for value in values})
    if 1.0 not in deduped:
        deduped.append(1.0)
    return deduped


def _round_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    rounded: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, float):
            rounded[key] = round(value, 6)
        else:
            rounded[key] = value
    return rounded


def build_markdown(summary: dict[str, Any]) -> str:
    selection = summary["selection"]
    calibration = summary["calibration"]
    evaluation = summary["evaluation"]
    candidate_stats = summary["candidate_stats"]
    lines = [
        "# Eta-Tempered Decoding Result",
        "",
        f"- Model: `{summary['metadata']['model']}`",
        f"- Benchmark: `{summary['metadata']['benchmark']}`",
        f"- Condition: `{summary['metadata']['condition']}`",
        f"- CoT length: `{summary['metadata']['cot_length']}`",
        f"- Calibration examples: `{summary['metadata']['calibration_size']}`",
        f"- Evaluation examples: `{summary['metadata']['evaluation_size']}`",
        f"- Candidate coverage: `{candidate_stats['covered_examples']}/{candidate_stats['total_examples']}`",
        f"- Mean candidate count: `{candidate_stats['mean_candidate_count']}`",
        "",
        "## Headline",
        "",
        f"- Selected eta: `{selection['selected_eta']}`",
        f"- Calibration baseline Brier at eta=1: `{calibration['baseline_metrics']['brier']}`",
        f"- Calibration selected Brier: `{calibration['selected_metrics']['brier']}`",
        f"- Eval baseline overconfidence gap at eta=1: `{evaluation['baseline']['overconfidence_gap']}`",
        f"- Eval tempered overconfidence gap: `{evaluation['selected']['overconfidence_gap']}`",
        f"- Eval baseline mean confidence at eta=1: `{evaluation['baseline']['mean_confidence']}`",
        f"- Eval tempered mean confidence: `{evaluation['selected']['mean_confidence']}`",
        f"- Eval baseline accuracy at eta=1: `{evaluation['baseline']['accuracy']}`",
        f"- Eval tempered accuracy: `{evaluation['selected']['accuracy']}`",
        "",
        "## Calibration Sweep",
        "",
        "| Eta | Count | Accuracy | ECE | Brier | Mean confidence |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in calibration["per_eta"]:
        lines.append(
            f"| {row['eta']:.2f} | {row['count']} | {row['accuracy']:.4f} | {row['ece']:.4f} | {row['brier']:.4f} | {row['mean_confidence']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Evaluation",
            "",
            "| Setting | Eta | Count | Accuracy | ECE | Brier | Mean confidence | Overconfidence gap |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, row in (
        ("Baseline", evaluation["baseline"]),
        ("Selected", evaluation["selected"]),
        ("Oracle", evaluation["oracle"]),
    ):
        lines.append(
            f"| {label} | {row['eta']:.2f} | {row['count']} | {row['accuracy']:.4f} | {row['ece']:.4f} | {row['brier']:.4f} | {row['mean_confidence']:.4f} | {row['overconfidence_gap']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    rows = _filter_rows(
        _load_rows(Path(args.rows_jsonl)),
        benchmark=args.benchmark,
        condition=args.condition,
        cot_length=args.cot_length,
    )
    if args.max_examples is not None:
        rows = rows[: args.max_examples]
    calibration_rows, evaluation_rows = split_rows(rows, calibration_size=args.calibration_size, seed=args.seed)
    rows_to_score = calibration_rows + evaluation_rows
    scored_examples = _score_rows(
        rows_to_score,
        model_name=args.model,
        batch_size=args.batch_size,
        torch_dtype=args.torch_dtype,
    )
    eta_values = _etas(args.eta_grid)
    calibration = choose_eta(calibration_rows, scored_examples, eta_values=eta_values)
    selected_eta = float(calibration["selected_eta"])
    oracle_eta = float(calibration["oracle_eta"])
    baseline_eval = _round_metrics(evaluate_eta(evaluation_rows, scored_examples, eta=1.0))
    selected_eval = _round_metrics(evaluate_eta(evaluation_rows, scored_examples, eta=selected_eta))
    oracle_eval = _round_metrics(evaluate_eta(evaluation_rows, scored_examples, eta=oracle_eta))
    summary = {
        "metadata": {
            "model": args.model,
            "benchmark": args.benchmark,
            "condition": args.condition,
            "cot_length": args.cot_length,
            "calibration_size": len(calibration_rows),
            "evaluation_size": len(evaluation_rows),
            "eta_grid": eta_values,
            "seed": args.seed,
        },
        "candidate_stats": {
            "total_examples": len(rows_to_score),
            "covered_examples": len(scored_examples),
            "mean_candidate_count": round(
                sum(len(values) for values in scored_examples.values()) / len(scored_examples),
                4,
            )
            if scored_examples
            else 0.0,
        },
        "selection": {
            "selected_eta": selected_eta,
            "oracle_eta": oracle_eta,
        },
        "calibration": {
            "baseline_metrics": _round_metrics(calibration["baseline_metrics"]),
            "selected_metrics": _round_metrics(calibration["selected_metrics"]),
            "oracle_metrics": _round_metrics(calibration["oracle_metrics"]),
            "per_eta": [_round_metrics(row) for row in calibration["per_eta"]],
        },
        "evaluation": {
            "baseline": baseline_eval,
            "selected": selected_eval,
            "oracle": oracle_eval,
        },
    }
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "json": str(output_prefix.with_suffix(".json")),
                "md": str(output_prefix.with_suffix(".md")),
                "selected_eta": selected_eta,
                "baseline_eval_gap": baseline_eval["overconfidence_gap"],
                "selected_eval_gap": selected_eval["overconfidence_gap"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
