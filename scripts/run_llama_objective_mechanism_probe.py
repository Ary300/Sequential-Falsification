#!/usr/bin/env python3
"""Probe a matched-base Llama DPO/GRPO pair for entropy and answer-margin shifts.

This is a reviewer-facing mechanism check for the strongest theorem-3 causal
split in the project. It compares the matched `Llama-8B` DPO and GRPO
checkpoints on the same `ConflictBank` prompts and asks two concrete questions:

1. Does GRPO reduce token-level entropy more strongly on conflict prompts than
   on no-conflict prompts?
2. Does GRPO shift answer log-prob mass toward the context-backed competitor on
   conflict prompts more than DPO does?
"""

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

from knowledge_arbitration.real_generation import _extract_confidence, _prompt_style_for_cot_length  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Llama matched-objective mechanism probe.")
    parser.add_argument("--dpo-model", required=True)
    parser.add_argument("--grpo-model", required=True)
    parser.add_argument("--rows-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--cot-length", type=int, default=1024)
    parser.add_argument("--max-prompts-per-split", type=int, default=64)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--max-prompt-length", type=int, default=2048)
    parser.add_argument("--num-bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
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


def _make_prompt(row: dict[str, Any], *, cot_length: int, split: str) -> str:
    metadata = row.get("metadata", {}) or {}
    question = str(row.get("question", "")).strip()
    style = _prompt_style_for_cot_length(cot_length)
    if split == "conflict":
        context_text = str(metadata.get("conflict_context_text") or "").strip()
    else:
        context_text = str(metadata.get("aligned_context_text") or "").strip()
    question_block = f"Question: {question}\n\nContext:\n{context_text}"
    return (
        f"system:\n{style.system_prompt}\n"
        "user:\n"
        f"{question_block}\n\n"
        "Use the context if it is reliable, but answer the question rather than summarizing the passage.\n"
        "assistant:\n"
    )


def _make_margin_prompt(row: dict[str, Any], *, split: str) -> str:
    metadata = row.get("metadata", {}) or {}
    question = str(row.get("question", "")).strip()
    if split == "conflict":
        context_text = str(metadata.get("conflict_context_text") or "").strip()
    else:
        context_text = str(metadata.get("aligned_context_text") or "").strip()
    return (
        "You are answering a knowledge-conflict question.\n\n"
        f"Question: {question}\n\n"
        f"Retrieved context: {context_text}\n\n"
        "Answer with just the answer.\n\nAnswer:"
    )


def _normalize_answer(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def _select_rows(rows: list[dict[str, Any]], *, benchmark: str, cot_length: int, max_prompts_per_split: int, seed: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    rng = random.Random(seed)
    for split in ("conflict", "no_conflict"):
        split_rows = [
            row
            for row in rows
            if str(row.get("benchmark")) == benchmark
            and str(row.get("split")) == split
            and int(row.get("cot_length", 0)) == cot_length
        ]
        split_rows.sort(key=lambda row: str(row.get("id")))
        rng.shuffle(split_rows)
        selected.extend(split_rows[:max_prompts_per_split])
    return selected


def _bootstrap_ci(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    low_idx = max(0, int(0.025 * (len(ordered) - 1)))
    high_idx = min(len(ordered) - 1, int(0.975 * (len(ordered) - 1)))
    return {"ci95_low": round(ordered[low_idx], 4), "ci95_high": round(ordered[high_idx], 4)}


def _sample_mean(values: list[float], rng: random.Random) -> float:
    resampled = [values[rng.randrange(len(values))] for _ in values]
    return statistics.mean(resampled)


def _mean_or_zero(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def _model_device(model: Any) -> Any:
    if hasattr(model, "device"):
        return model.device
    return next(model.parameters()).device


def _score_completion(model: Any, tokenizer: Any, prompt: str, completion: str, max_prompt_length: int) -> float:
    import torch
    import torch.nn.functional as F

    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, truncation=True, max_length=max_prompt_length)
    full_ids = tokenizer.encode(prompt + completion, add_special_tokens=False, truncation=True, max_length=max_prompt_length + 64)
    if len(full_ids) <= len(prompt_ids):
        return float("nan")
    input_ids = torch.tensor([full_ids], dtype=torch.long, device=_model_device(model))
    attention_mask = torch.ones_like(input_ids)
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, use_cache=False)
    logits = outputs.logits[:, :-1, :]
    targets = input_ids[:, 1:]
    log_probs = F.log_softmax(logits, dim=-1)
    chosen = log_probs.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    mask = torch.zeros_like(targets, dtype=torch.float32)
    boundary = max(len(prompt_ids) - 1, 0)
    if boundary < mask.shape[1]:
        mask[:, boundary:] = 1.0
    denom = mask.sum().clamp_min(1.0)
    return float(((chosen * mask).sum() / denom).item())


def _generate_metrics(model: Any, tokenizer: Any, prompt: str, *, max_new_tokens: int, max_prompt_length: int) -> dict[str, Any]:
    import torch
    import torch.nn.functional as F

    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, truncation=True, max_length=max_prompt_length)
    input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=_model_device(model))
    attention_mask = torch.ones_like(input_ids)
    with torch.no_grad():
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            use_cache=True,
            return_dict_in_generate=True,
            output_scores=True,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    sequences = outputs.sequences[0]
    generated_ids = sequences[len(prompt_ids) :].tolist()
    entropies: list[float] = []
    chosen_logprobs: list[float] = []
    top1_probs: list[float] = []
    for step, scores in enumerate(outputs.scores):
        logits = scores[0]
        log_probs = F.log_softmax(logits, dim=-1)
        probs = log_probs.exp()
        entropies.append(float((-(probs * log_probs).sum()).item()))
        if step < len(generated_ids):
            chosen_id = generated_ids[step]
            chosen_logprobs.append(float(log_probs[chosen_id].item()))
        top1_probs.append(float(probs.max().item()))
    text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    return {
        "generated_text": text,
        "generated_token_count": len(generated_ids),
        "mean_token_entropy": _mean_or_zero(entropies),
        "first_token_entropy": entropies[0] if entropies else 0.0,
        "mean_chosen_logprob": _mean_or_zero(chosen_logprobs),
        "mean_top1_prob": _mean_or_zero(top1_probs),
        "reported_confidence": _extract_confidence(text),
    }


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
    if torch.cuda.is_available():
        load_kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(model_name, **load_kwargs)
    if "device_map" not in load_kwargs:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
    model.eval()
    return tokenizer, model


def _prompt_metrics_for_model(
    model_name: str,
    rows: list[dict[str, Any]],
    *,
    cot_length: int,
    max_new_tokens: int,
    max_prompt_length: int,
    torch_dtype: str,
) -> list[dict[str, Any]]:
    tokenizer, model = _load_model_and_tokenizer(model_name, torch_dtype)
    out: list[dict[str, Any]] = []
    for row in rows:
        split = str(row.get("split"))
        prompt = _make_prompt(row, cot_length=cot_length, split=split)
        margin_prompt = _make_margin_prompt(row, split=split)
        metadata = row.get("metadata", {}) or {}
        gold_answers = row.get("gold_answers") or []
        gold_answer = str(gold_answers[0]) if gold_answers else ""
        competitor_answers = metadata.get("conflict_context_answers") or []
        competitor_answer = str(competitor_answers[0]) if competitor_answers else ""
        generated = _generate_metrics(
            model,
            tokenizer,
            prompt,
            max_new_tokens=max_new_tokens,
            max_prompt_length=max_prompt_length,
        )
        gold_score = _score_completion(model, tokenizer, margin_prompt, gold_answer, max_prompt_length)
        competitor_score = _score_completion(model, tokenizer, margin_prompt, competitor_answer, max_prompt_length)
        out.append(
            {
                "id": str(row.get("id")),
                "benchmark": str(row.get("benchmark")),
                "split": split,
                "conflict_strength": float(metadata.get("conflict_strength", 0.0)),
                "gold_answer": gold_answer,
                "competitor_answer": competitor_answer,
                "gold_vs_competitor_margin": gold_score - competitor_score,
                "generated_outcome": int(row.get("outcome", 0)),
                **generated,
            }
        )
    return out


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_split: dict[str, list[dict[str, Any]]] = {"conflict": [], "no_conflict": []}
    for row in rows:
        split = str(row.get("split"))
        if split in by_split:
            by_split[split].append(row)
    out: dict[str, Any] = {"by_split": {}}
    for split, split_rows in by_split.items():
        out["by_split"][split] = {
            "count": len(split_rows),
            "mean_token_entropy": round(_mean_or_zero([float(r["mean_token_entropy"]) for r in split_rows]), 4),
            "mean_chosen_logprob": round(_mean_or_zero([float(r["mean_chosen_logprob"]) for r in split_rows]), 4),
            "mean_top1_prob": round(_mean_or_zero([float(r["mean_top1_prob"]) for r in split_rows]), 4),
            "mean_margin": round(_mean_or_zero([float(r["gold_vs_competitor_margin"]) for r in split_rows]), 4),
            "mean_reported_confidence": round(
                _mean_or_zero([float(r["reported_confidence"]) for r in split_rows if r["reported_confidence"] is not None]),
                4,
            ),
        }
    if out["by_split"]["conflict"] and out["by_split"]["no_conflict"]:
        out["conflict_minus_no_conflict"] = {
            "mean_token_entropy": round(
                out["by_split"]["conflict"]["mean_token_entropy"] - out["by_split"]["no_conflict"]["mean_token_entropy"],
                4,
            ),
            "mean_chosen_logprob": round(
                out["by_split"]["conflict"]["mean_chosen_logprob"] - out["by_split"]["no_conflict"]["mean_chosen_logprob"],
                4,
            ),
            "mean_top1_prob": round(
                out["by_split"]["conflict"]["mean_top1_prob"] - out["by_split"]["no_conflict"]["mean_top1_prob"],
                4,
            ),
            "mean_margin": round(
                out["by_split"]["conflict"]["mean_margin"] - out["by_split"]["no_conflict"]["mean_margin"],
                4,
            ),
        }
    return out


def _bootstrap(rows: list[dict[str, Any]], *, num_bootstrap: int, seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    by_split: dict[str, list[dict[str, Any]]] = {"conflict": [], "no_conflict": []}
    for row in rows:
        split = str(row.get("split"))
        if split in by_split:
            by_split[split].append(row)
    out: dict[str, Any] = {}
    for metric in ("mean_token_entropy", "mean_chosen_logprob", "mean_top1_prob", "gold_vs_competitor_margin"):
        conflict_samples: list[float] = []
        no_conflict_samples: list[float] = []
        diff_samples: list[float] = []
        conflict_values = [float(row[metric]) for row in by_split["conflict"]]
        no_conflict_values = [float(row[metric]) for row in by_split["no_conflict"]]
        if not conflict_values or not no_conflict_values:
            continue
        for _ in range(num_bootstrap):
            conflict_mean = _sample_mean(conflict_values, rng)
            no_conflict_mean = _sample_mean(no_conflict_values, rng)
            conflict_samples.append(conflict_mean)
            no_conflict_samples.append(no_conflict_mean)
            diff_samples.append(conflict_mean - no_conflict_mean)
        out[metric] = {
            "conflict": _bootstrap_ci(conflict_samples),
            "no_conflict": _bootstrap_ci(no_conflict_samples),
            "conflict_minus_no_conflict": _bootstrap_ci(diff_samples),
        }
    return out


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Llama Objective Mechanism Probe",
        "",
        "This note compares the matched `Llama-8B DPO` and `Llama-8B GRPO` checkpoints on the same `ConflictBank` prompts.",
        "",
        "## Read",
        "",
        "- We measure token-level generation entropy and answer-margin shifts on matched conflict / no-conflict prompts.",
        "- If GRPO collapses entropy or pushes more log-prob mass toward the context-backed competitor on conflict prompts, that supports a concrete mechanism rather than a pure headline anomaly.",
        "",
    ]
    for label in ("dpo", "grpo"):
        model_block = payload["models"][label]
        lines.extend(
            [
                f"## {label.upper()}",
                "",
                f"- Model: `{model_block['model_name']}`",
                f"- Conflict mean token entropy: `{model_block['summary']['by_split']['conflict']['mean_token_entropy']}`",
                f"- No-conflict mean token entropy: `{model_block['summary']['by_split']['no_conflict']['mean_token_entropy']}`",
                f"- Conflict-minus-no-conflict entropy: `{model_block['summary']['conflict_minus_no_conflict']['mean_token_entropy']}`",
                f"- Conflict mean answer margin: `{model_block['summary']['by_split']['conflict']['mean_margin']}`",
                f"- No-conflict mean answer margin: `{model_block['summary']['by_split']['no_conflict']['mean_margin']}`",
                f"- Conflict-minus-no-conflict answer margin: `{model_block['summary']['conflict_minus_no_conflict']['mean_margin']}`",
                "",
            ]
        )

    did = payload["difference_in_differences"]
    lines.extend(
        [
            "## Difference-in-Differences",
            "",
            f"- Entropy diff-in-diff (`GRPO - DPO` on conflict-minus-no-conflict): `{did['mean_token_entropy']}`",
            f"- Answer-margin diff-in-diff (`GRPO - DPO`): `{did['gold_vs_competitor_margin']}`",
            f"- Top-1 probability diff-in-diff (`GRPO - DPO`): `{did['mean_top1_prob']}`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = _load_rows(Path(args.rows_jsonl))
    selected_rows = _select_rows(
        rows,
        benchmark=args.benchmark,
        cot_length=args.cot_length,
        max_prompts_per_split=args.max_prompts_per_split,
        seed=args.seed,
    )
    if not selected_rows:
        raise SystemExit("No matching rows selected for mechanism probe.")

    dpo_rows = _prompt_metrics_for_model(
        args.dpo_model,
        selected_rows,
        cot_length=args.cot_length,
        max_new_tokens=args.max_new_tokens,
        max_prompt_length=args.max_prompt_length,
        torch_dtype=args.torch_dtype,
    )
    grpo_rows = _prompt_metrics_for_model(
        args.grpo_model,
        selected_rows,
        cot_length=args.cot_length,
        max_new_tokens=args.max_new_tokens,
        max_prompt_length=args.max_prompt_length,
        torch_dtype=args.torch_dtype,
    )

    dpo_summary = _aggregate(dpo_rows)
    grpo_summary = _aggregate(grpo_rows)
    dpo_boot = _bootstrap(dpo_rows, num_bootstrap=args.num_bootstrap, seed=args.seed)
    grpo_boot = _bootstrap(grpo_rows, num_bootstrap=args.num_bootstrap, seed=args.seed)

    dpo_diff = dpo_summary["conflict_minus_no_conflict"]
    grpo_diff = grpo_summary["conflict_minus_no_conflict"]
    did = {
        "mean_token_entropy": round(grpo_diff["mean_token_entropy"] - dpo_diff["mean_token_entropy"], 4),
        "mean_chosen_logprob": round(grpo_diff["mean_chosen_logprob"] - dpo_diff["mean_chosen_logprob"], 4),
        "mean_top1_prob": round(grpo_diff["mean_top1_prob"] - dpo_diff["mean_top1_prob"], 4),
        "gold_vs_competitor_margin": round(grpo_diff["mean_margin"] - dpo_diff["mean_margin"], 4),
    }

    payload = {
        "metadata": {
            "benchmark": args.benchmark,
            "cot_length": args.cot_length,
            "max_prompts_per_split": args.max_prompts_per_split,
            "max_new_tokens": args.max_new_tokens,
            "num_bootstrap": args.num_bootstrap,
            "seed": args.seed,
            "rows_jsonl": args.rows_jsonl,
        },
        "models": {
            "dpo": {
                "model_name": args.dpo_model,
                "summary": dpo_summary,
                "bootstrap": dpo_boot,
                "preview_rows": dpo_rows[:5],
            },
            "grpo": {
                "model_name": args.grpo_model,
                "summary": grpo_summary,
                "bootstrap": grpo_boot,
                "preview_rows": grpo_rows[:5],
            },
        },
        "difference_in_differences": did,
    }

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_dir / "llama_objective_mechanism_probe.json")
    (output_dir / "llama_objective_mechanism_probe.md").write_text(_build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
