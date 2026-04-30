#!/usr/bin/env python3
"""Empirically test self-confirming trace separation for theorem 3."""

from __future__ import annotations

import argparse
import importlib.util
import json
from math import exp
from pathlib import Path
import random
import statistics
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.eta_tempering import candidate_answers_from_row  # noqa: E402
from knowledge_arbitration.real_generation import _answer_set, _answers_match, _question_block, build_prompt_styles  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run theorem-3 self-confirming trace separation check.")
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--condition", default="conflict_context")
    parser.add_argument("--cot-length", type=int, default=1024)
    parser.add_argument("--max-examples", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--torch-dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    parser.add_argument("--long-cot-style", type=int, default=1024)
    return parser.parse_args()


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _normalize(text: str) -> str:
    normalized_set = _answer_set(text)
    return next(iter(normalized_set), "")


def _choose_current_answer(row: dict[str, Any], candidates: list[str]) -> str:
    row_answer = str(row.get("answer", ""))
    matching = [candidate for candidate in candidates if _answers_match(row_answer, _answer_set(candidate))]
    if matching:
        return min(matching, key=len)
    if row_answer.strip():
        return row_answer.strip()
    return candidates[0]


def _choose_competitors(current_answer: str, candidates: list[str]) -> list[str]:
    current_norm = _normalize(current_answer)
    competitors = [
        candidate
        for candidate in candidates
        if _normalize(candidate) and _normalize(candidate) != current_norm
    ]
    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in competitors:
        normalized = _normalize(candidate)
        if normalized in seen:
            continue
        deduped.append(candidate)
        seen.add(normalized)
    return deduped


def _load_model_and_tokenizer(model_name: str, torch_dtype: str) -> tuple[Any, Any]:
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
    return model, tokenizer


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


def _answer_state_messages(row: dict[str, Any], *, condition: str, candidate_answer: str, long_cot_style: int) -> list[dict[str, str]]:
    style = build_prompt_styles([long_cot_style])[0]
    user_block = _question_block(row, condition)
    user_block += (
        "\n\nAssume your current tentative answer state is:\n"
        f"{candidate_answer}\n\n"
        "Continue the reasoning trace that would be most consistent with that tentative answer before any final answer is emitted."
    )
    return [
        {"role": "system", "content": style.system_prompt},
        {"role": "user", "content": user_block},
    ]


def _score_continuation_batch(model: Any, tokenizer: Any, *, prompt: str, continuations: list[str], batch_size: int) -> list[float]:
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)["input_ids"][0]
    prompt_len = int(prompt_ids.shape[0])
    scores: list[float] = []
    for start in range(0, len(continuations), batch_size):
        batch_conts = continuations[start : start + batch_size]
        batch_texts = [prompt + continuation for continuation in batch_conts]
        encoded = tokenizer(batch_texts, return_tensors="pt", padding=True, add_special_tokens=False)
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
        scores.extend(float(score) for score in sequence_log_probs)
    return scores


def _subset_rows(rows: list[dict[str, Any]], *, benchmark: str, condition: str, cot_length: int, max_examples: int, seed: int) -> list[dict[str, Any]]:
    filtered = [
        row
        for row in rows
        if str(row.get("benchmark")) == benchmark
        and str(row.get("condition")) == condition
        and int(row.get("cot_length", 0)) == cot_length
        and str(row.get("reasoning_text", "")).strip()
    ]
    deduped: dict[str, dict[str, Any]] = {}
    for row in filtered:
        deduped[str(row["id"])] = row
    subset = list(deduped.values())
    rng = random.Random(seed)
    rng.shuffle(subset)
    return subset[: min(max_examples, len(subset))]


def run_check(args: argparse.Namespace) -> dict[str, Any]:
    rows = _load_rows(Path(args.rows_jsonl))
    subset = _subset_rows(
        rows,
        benchmark=args.benchmark,
        condition=args.condition,
        cot_length=args.cot_length,
        max_examples=args.max_examples,
        seed=args.seed,
    )
    model, tokenizer = _load_model_and_tokenizer(args.model, args.torch_dtype)

    records: list[dict[str, Any]] = []
    for index, row in enumerate(subset, start=1):
        candidates = candidate_answers_from_row(row)
        if len(candidates) < 2:
            continue
        current_answer = _choose_current_answer(row, candidates)
        competitors = _choose_competitors(current_answer, candidates)
        if not competitors:
            continue
        target_trace = f"<think>{str(row.get('reasoning_text', '')).strip()}</think>"

        current_prompt = _apply_chat_template(
            tokenizer,
            _answer_state_messages(
                row,
                condition=str(row["condition"]),
                candidate_answer=current_answer,
                long_cot_style=args.long_cot_style,
            ),
        )
        current_score = _score_continuation_batch(
            model,
            tokenizer,
            prompt=current_prompt,
            continuations=[target_trace],
            batch_size=1,
        )[0]

        competitor_scores: dict[str, float] = {}
        for competitor in competitors:
            prompt = _apply_chat_template(
                tokenizer,
                _answer_state_messages(
                    row,
                    condition=str(row["condition"]),
                    candidate_answer=competitor,
                    long_cot_style=args.long_cot_style,
                ),
            )
            competitor_scores[competitor] = _score_continuation_batch(
                model,
                tokenizer,
                prompt=prompt,
                continuations=[target_trace],
                batch_size=1,
            )[0]

        best_competitor, best_competitor_score = max(competitor_scores.items(), key=lambda item: item[1])
        margin = float(current_score - best_competitor_score)
        records.append(
            {
                "id": str(row["id"]),
                "benchmark": str(row["benchmark"]),
                "condition": str(row["condition"]),
                "cot_length": int(row["cot_length"]),
                "outcome": int(row.get("outcome", 0)),
                "current_answer_state": current_answer,
                "best_competing_answer_state": best_competitor,
                "current_trace_logprob": float(current_score),
                "best_competing_trace_logprob": float(best_competitor_score),
                "margin": margin,
                "current_beats_best_competitor": margin > 0.0,
            }
        )
        if index % 10 == 0:
            print(json.dumps({"event": "scored_examples", "completed": index, "kept": len(records)}), flush=True)

    positive = [record for record in records if record["current_beats_best_competitor"]]
    margins = [float(record["margin"]) for record in records]
    positive_margins = [margin for margin in margins if margin > 0.0]
    negative_margins = [margin for margin in margins if margin <= 0.0]
    correct_rows = [record for record in records if int(record["outcome"]) == 1]
    incorrect_rows = [record for record in records if int(record["outcome"]) == 0]

    def _mean_or_none(values: list[float]) -> float | None:
        return (sum(values) / len(values)) if values else None

    payload = {
        "metadata": {
            "model": args.model,
            "rows_jsonl": args.rows_jsonl,
            "benchmark": args.benchmark,
            "condition": args.condition,
            "cot_length": args.cot_length,
            "requested_examples": args.max_examples,
            "scored_examples": len(records),
            "seed": args.seed,
            "long_cot_style": args.long_cot_style,
        },
        "headline": {
            "fraction_current_beats_best_competitor": _mean_or_none([1.0 if record["current_beats_best_competitor"] else 0.0 for record in records]),
            "mean_margin": _mean_or_none(margins),
            "median_margin": statistics.median(margins) if margins else None,
            "mean_positive_margin": _mean_or_none(positive_margins),
            "mean_nonpositive_margin": _mean_or_none(negative_margins),
            "correct_fraction_current_beats_best_competitor": _mean_or_none([1.0 if record["current_beats_best_competitor"] else 0.0 for record in correct_rows]),
            "incorrect_fraction_current_beats_best_competitor": _mean_or_none([1.0 if record["current_beats_best_competitor"] else 0.0 for record in incorrect_rows]),
        },
        "records": records[:25],
        "extremes": {
            "largest_positive_margins": sorted(records, key=lambda item: item["margin"], reverse=True)[:5],
            "largest_negative_margins": sorted(records, key=lambda item: item["margin"])[:5],
        },
    }
    return payload


def build_markdown(payload: dict[str, Any]) -> str:
    h = payload["headline"]
    m = payload["metadata"]
    lines = [
        "# Theorem 3 Trace-Separation Check",
        "",
        "This note operationalizes Assumption 3.2 by comparing the log-likelihood of an observed reasoning trace under the model's generated answer state versus the strongest competing answer state.",
        "",
        f"- Model: `{m['model']}`",
        f"- Benchmark: `{m['benchmark']}`",
        f"- Condition: `{m['condition']}`",
        f"- CoT length: `{m['cot_length']}`",
        f"- Scored examples: `{m['scored_examples']}`",
        "",
        "## Headline",
        "",
        f"- Fraction where current answer state beats the strongest competing state: `{h['fraction_current_beats_best_competitor']}`",
        f"- Mean margin: `{h['mean_margin']}`",
        f"- Median margin: `{h['median_margin']}`",
        f"- Mean positive margin: `{h['mean_positive_margin']}`",
        f"- Mean non-positive margin: `{h['mean_nonpositive_margin']}`",
        f"- Correct-example win fraction: `{h['correct_fraction_current_beats_best_competitor']}`",
        f"- Incorrect-example win fraction: `{h['incorrect_fraction_current_beats_best_competitor']}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    payload = run_check(args)
    output_prefix = Path(args.output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_prefix": str(output_prefix), "headline": payload["headline"]}, indent=2))


if __name__ == "__main__":
    main()
