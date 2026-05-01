#!/usr/bin/env python3
"""Train a matched-base LoRA checkpoint with DPO or GRPO-style objectives.

This runner is the closest truthful local implementation of the requested E1
comparison in the current stack:

- matched base model
- matched conflict-heavy training data
- matched LoRA / epoch / optimizer budget

The DPO branch is literal pairwise DPO on chosen vs rejected answers.
The GRPO branch is a verifiable-reward, group-relative policy optimization
surrogate using short sampled answers and a reference-policy regularizer.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import re
import string
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a matched-base DPO or GRPO-style LoRA comparison.")
    parser.add_argument("--objective", required=True, choices=["dpo", "grpo"])
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--benchmark", default="conflictbank")
    parser.add_argument("--max-source-rows", type=int, default=1200)
    parser.add_argument("--max-train-rows", type=int, default=800)
    parser.add_argument("--max-val-rows", type=int, default=120)
    parser.add_argument("--max-eval-rows", type=int, default=120)
    parser.add_argument("--max-prompt-length", type=int, default=768)
    parser.add_argument("--max-answer-length", type=int, default=24)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--beta", type=float, default=0.1, help="DPO temperature / GRPO-style regularization strength.")
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--group-size", type=int, default=4, help="Samples per prompt for GRPO-style objective.")
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--torch-dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    return parser.parse_args()


def _seed_everything(seed: int) -> None:
    import torch

    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _normalize_answer(text: str) -> str:
    text = text.strip().lower()
    text = text.splitlines()[0] if text else text
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _exact_match(prediction: str, gold_answers: list[str]) -> int:
    pred = _normalize_answer(prediction)
    if not pred:
        return 0
    normalized_golds = {_normalize_answer(answer) for answer in gold_answers if str(answer).strip()}
    return int(pred in normalized_golds)


def _conflict_examples(max_examples: int) -> list[dict[str, Any]]:
    rows = load_arbitration_dataset("conflictbank", max_examples=max_examples)
    examples = []
    for row in rows:
        metadata = row.get("metadata", {}) or {}
        conflict_text = str(metadata.get("conflict_context_text") or "").strip()
        gold_answers = [str(item) for item in row.get("answers", []) if str(item).strip()]
        rejected_answers = [str(item) for item in metadata.get("conflict_context_answers", []) if str(item).strip()]
        if not conflict_text or not gold_answers or not rejected_answers:
            continue
        examples.append(
            {
                "id": str(row.get("id")),
                "question": str(row.get("question", "")).strip(),
                "prompt": (
                    "You are answering a knowledge-conflict question.\n\n"
                    f"Question: {str(row.get('question', '')).strip()}\n\n"
                    f"Retrieved context: {conflict_text}\n\n"
                    "Answer with just the answer.\n\nAnswer:"
                ),
                "gold_answers": gold_answers,
                "chosen": gold_answers[0],
                "rejected": rejected_answers[0],
                "metadata": metadata,
            }
        )
    return examples


def _split_examples(examples: list[dict[str, Any]], *, max_train: int, max_val: int, max_eval: int, seed: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    shuffled = list(examples)
    rng.shuffle(shuffled)
    eval_rows = shuffled[:max_eval]
    val_rows = shuffled[max_eval : max_eval + max_val]
    train_rows = shuffled[max_eval + max_val : max_eval + max_val + max_train]
    return train_rows, val_rows, eval_rows


def _load_model_and_tokenizer(args: argparse.Namespace):
    import torch
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype_map: dict[str, Any] = {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=dtype_map[args.torch_dtype],
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.config.use_cache = False
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    return tokenizer, model


def _device_of(model: Any):
    return next(model.parameters()).device


def _tokenize_full(tokenizer: Any, prompt: str, completion: str, max_prompt_length: int) -> tuple[list[int], list[int]]:
    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, truncation=True, max_length=max_prompt_length)
    completion_ids = tokenizer.encode(" " + completion.strip(), add_special_tokens=False)
    if not completion_ids:
        completion_ids = tokenizer.encode(" [EMPTY]", add_special_tokens=False)
    full_ids = prompt_ids + completion_ids
    return prompt_ids, full_ids


def _sequence_logprob(model: Any, tokenizer: Any, prompt: str, completion: str, max_prompt_length: int) -> Any:
    import torch
    import torch.nn.functional as F

    prompt_ids, full_ids = _tokenize_full(tokenizer, prompt, completion, max_prompt_length)
    if len(full_ids) <= len(prompt_ids):
        raise ValueError("Completion tokenization produced no target tokens.")
    input_ids = torch.tensor([full_ids], dtype=torch.long, device=_device_of(model))
    attention_mask = torch.ones_like(input_ids)
    outputs = model(input_ids=input_ids, attention_mask=attention_mask, use_cache=False)
    logits = outputs.logits[:, :-1, :]
    targets = input_ids[:, 1:]
    log_probs = F.log_softmax(logits, dim=-1)
    token_log_probs = log_probs.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    target_mask = torch.zeros_like(targets, dtype=torch.float32)
    prompt_boundary = max(len(prompt_ids) - 1, 0)
    if prompt_boundary < target_mask.shape[1]:
        target_mask[:, prompt_boundary:] = 1.0
    return (token_log_probs * target_mask).sum(dim=1)


def _generate_answer(model: Any, tokenizer: Any, prompt: str, max_prompt_length: int, max_answer_length: int, *, do_sample: bool, temperature: float, top_p: float, num_return_sequences: int = 1) -> list[str]:
    import torch

    prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, truncation=True, max_length=max_prompt_length)
    input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=_device_of(model))
    attention_mask = torch.ones_like(input_ids)
    generation_kwargs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "max_new_tokens": max_answer_length,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "num_return_sequences": num_return_sequences,
        "do_sample": do_sample,
    }
    if do_sample:
        generation_kwargs["temperature"] = temperature
        generation_kwargs["top_p"] = top_p
    with torch.no_grad():
        sequences = model.generate(**generation_kwargs)
    answers = []
    for sequence in sequences:
        completion_ids = sequence[len(prompt_ids) :]
        text = tokenizer.decode(completion_ids, skip_special_tokens=True)
        answers.append(text.strip())
    return answers


def _evaluate_model(model: Any, tokenizer: Any, rows: list[dict[str, Any]], args: argparse.Namespace, *, adapters_enabled: bool) -> dict[str, Any]:
    answers = []
    for row in rows:
        if adapters_enabled:
            generations = _generate_answer(
                model,
                tokenizer,
                row["prompt"],
                args.max_prompt_length,
                args.max_answer_length,
                do_sample=False,
                temperature=args.temperature,
                top_p=args.top_p,
            )
        else:
            with model.disable_adapter():
                generations = _generate_answer(
                    model,
                    tokenizer,
                    row["prompt"],
                    args.max_prompt_length,
                    args.max_answer_length,
                    do_sample=False,
                    temperature=args.temperature,
                    top_p=args.top_p,
                )
        prediction = generations[0] if generations else ""
        answers.append(
            {
                "id": row["id"],
                "prediction": prediction,
                "correct": _exact_match(prediction, row["gold_answers"]),
            }
        )
    accuracy = sum(item["correct"] for item in answers) / max(1, len(answers))
    return {
        "count": len(rows),
        "accuracy": round(float(accuracy), 6),
        "preview": answers[:20],
    }


def _dpo_epoch(model: Any, tokenizer: Any, train_rows: list[dict[str, Any]], args: argparse.Namespace) -> float:
    import torch
    import torch.nn.functional as F

    optimizer = torch.optim.AdamW(
        [param for param in model.parameters() if param.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    rng = random.Random(args.seed)
    running = []
    shuffled = list(train_rows)
    rng.shuffle(shuffled)
    model.train()
    for row in shuffled:
        optimizer.zero_grad(set_to_none=True)
        pi_chosen = _sequence_logprob(model, tokenizer, row["prompt"], row["chosen"], args.max_prompt_length)
        pi_rejected = _sequence_logprob(model, tokenizer, row["prompt"], row["rejected"], args.max_prompt_length)
        with model.disable_adapter():
            ref_chosen = _sequence_logprob(model, tokenizer, row["prompt"], row["chosen"], args.max_prompt_length).detach()
            ref_rejected = _sequence_logprob(model, tokenizer, row["prompt"], row["rejected"], args.max_prompt_length).detach()
        margin = (pi_chosen - pi_rejected) - (ref_chosen - ref_rejected)
        loss = -F.logsigmoid(args.beta * margin).mean()
        loss.backward()
        optimizer.step()
        running.append(float(loss.item()))
    return float(sum(running) / max(1, len(running)))


def _grpo_epoch(model: Any, tokenizer: Any, train_rows: list[dict[str, Any]], args: argparse.Namespace) -> float:
    import torch

    optimizer = torch.optim.AdamW(
        [param for param in model.parameters() if param.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    rng = random.Random(args.seed)
    shuffled = list(train_rows)
    rng.shuffle(shuffled)
    running = []
    model.train()
    for row in shuffled:
        completions = _generate_answer(
            model,
            tokenizer,
            row["prompt"],
            args.max_prompt_length,
            args.max_answer_length,
            do_sample=True,
            temperature=args.temperature,
            top_p=args.top_p,
            num_return_sequences=args.group_size,
        )
        rewards = [_exact_match(completion, row["gold_answers"]) for completion in completions]
        reward_values = torch.tensor(rewards, dtype=torch.float32, device=_device_of(model))
        if float(reward_values.std(unbiased=False).item()) == 0.0:
            continue
        advantages = (reward_values - reward_values.mean()) / (reward_values.std(unbiased=False) + 1e-6)

        optimizer.zero_grad(set_to_none=True)
        policy_terms = []
        ref_terms = []
        for completion in completions:
            policy_terms.append(_sequence_logprob(model, tokenizer, row["prompt"], completion, args.max_prompt_length))
            with model.disable_adapter():
                ref_terms.append(_sequence_logprob(model, tokenizer, row["prompt"], completion, args.max_prompt_length).detach())
        policy_logps = torch.stack(policy_terms).squeeze(-1)
        ref_logps = torch.stack(ref_terms).squeeze(-1)
        policy_loss = -(advantages.detach() * policy_logps).mean()
        kl_penalty = ((policy_logps - ref_logps) ** 2).mean()
        loss = policy_loss + args.beta * kl_penalty
        loss.backward()
        optimizer.step()
        running.append(float(loss.item()))
    return float(sum(running) / max(1, len(running)))


def _train(model: Any, tokenizer: Any, train_rows: list[dict[str, Any]], val_rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, float]]:
    history = []
    for epoch in range(1, args.epochs + 1):
        if args.objective == "dpo":
            train_loss = _dpo_epoch(model, tokenizer, train_rows, args)
        else:
            train_loss = _grpo_epoch(model, tokenizer, train_rows, args)
        val_metrics = _evaluate_model(model, tokenizer, val_rows, args, adapters_enabled=True)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(train_loss, 6),
                "val_accuracy": round(float(val_metrics["accuracy"]), 6),
            }
        )
    return history


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Theorem 3 Matched-Objective LoRA Run",
        "",
        "This run trains a matched-base checkpoint with either DPO or a verifiable-reward GRPO-style objective on the same conflict-heavy source pool.",
        "It is the cleanest controlled objective comparison the current stack can support without depending on the original DeepSeek training code.",
        "",
        "## Setup",
        "",
        f"- Objective: `{payload['metadata']['objective']}`",
        f"- Model: `{payload['metadata']['model_name']}`",
        f"- Benchmark: `{payload['metadata']['benchmark']}`",
        f"- Train / val / eval rows: `{payload['metadata']['num_train_rows']}` / `{payload['metadata']['num_val_rows']}` / `{payload['metadata']['num_eval_rows']}`",
        "",
        "## Eval",
        "",
        f"- Base accuracy: `{payload['base_eval']['accuracy']}`",
        f"- Tuned accuracy: `{payload['tuned_eval']['accuracy']}`",
        "",
        "## Read",
        "",
        "- The DPO branch is literal pairwise preference optimization on gold vs conflict answers.",
        "- The GRPO branch is a group-relative verifiable-reward surrogate, not a byte-for-byte reproduction of the original DeepSeek training recipe.",
        "- The saved merged checkpoint can be fed into the theorem-3 real-generation runner for downstream CoT trajectory evaluation.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    _seed_everything(args.seed)
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    examples = _conflict_examples(args.max_source_rows)
    train_rows, val_rows, eval_rows = _split_examples(
        examples,
        max_train=args.max_train_rows,
        max_val=args.max_val_rows,
        max_eval=args.max_eval_rows,
        seed=args.seed,
    )
    if not train_rows or not val_rows or not eval_rows:
        raise SystemExit("Need non-empty train/val/eval splits.")

    tokenizer, model = _load_model_and_tokenizer(args)
    base_eval = _evaluate_model(model, tokenizer, eval_rows, args, adapters_enabled=False)
    history = _train(model, tokenizer, train_rows, val_rows, args)
    tuned_eval = _evaluate_model(model, tokenizer, eval_rows, args, adapters_enabled=True)

    adapter_dir = output_dir / "adapter"
    merged_dir = output_dir / "merged_model"
    adapter_dir.mkdir(parents=True, exist_ok=True)
    merged_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(adapter_dir)
    tokenizer.save_pretrained(adapter_dir)

    merged_model = model.merge_and_unload() if hasattr(model, "merge_and_unload") else model
    merged_model.save_pretrained(merged_dir)
    tokenizer.save_pretrained(merged_dir)

    payload = {
        "metadata": {
            "objective": args.objective,
            "model_name": args.model_name,
            "benchmark": args.benchmark,
            "num_source_rows": len(examples),
            "num_train_rows": len(train_rows),
            "num_val_rows": len(val_rows),
            "num_eval_rows": len(eval_rows),
            "epochs": args.epochs,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "beta": args.beta,
            "group_size": args.group_size,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "lora_rank": args.lora_rank,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "seed": args.seed,
        },
        "base_eval": base_eval,
        "tuned_eval": tuned_eval,
        "training_history": history,
        "output_paths": {
            "adapter_dir": str(adapter_dir),
            "merged_model_dir": str(merged_dir),
        },
    }
    dump_json(payload, output_dir / "matched_objective_lora.json")
    (output_dir / "matched_objective_lora.md").write_text(_build_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "merged_model_dir": str(merged_dir)}, indent=2))


if __name__ == "__main__":
    main()
