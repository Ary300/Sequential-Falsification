#!/usr/bin/env python3
"""Train a LoRA-adapted theorem-3 confidence model with Brier loss.

This is an honest RLCR-style training-time intervention, not a full policy-
gradient RLVR reproduction. We update the base LM through LoRA adapters while
training a confidence head on top of the final hidden state, optimized directly
with Brier loss on conflict-heavy theorem-3 traces.
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RLCR-style LoRA calibration fine-tune.")
    parser.add_argument("--rows-jsonl", required=True, help="Comma-separated theorem-3 row files.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--train-benchmark", default="conflictbank")
    parser.add_argument("--train-condition", default="conflict_context")
    parser.add_argument("--eval-benchmark", default="conflictbank")
    parser.add_argument("--eval-condition", default="conflict_context")
    parser.add_argument("--eval-cot-length", type=int, default=1024)
    parser.add_argument("--max-train-rows", type=int, default=1200)
    parser.add_argument("--max-val-rows", type=int, default=200)
    parser.add_argument("--max-eval-rows", type=int, default=500)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--feature-batch-size", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--head-lr", type=float, default=5e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
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


def _row_text(row: dict[str, Any]) -> str:
    metadata = row.get("metadata", {}) or {}
    question = str(row.get("question", "")).strip()
    condition = str(row.get("condition", "unknown"))
    benchmark = str(row.get("benchmark", "unknown"))
    aligned_context = str(metadata.get("aligned_context_text") or "").strip()
    conflict_context = str(metadata.get("conflict_context_text") or "").strip()
    context_text = ""
    if condition == "aligned_context":
        context_text = aligned_context
    elif condition == "conflict_context":
        context_text = conflict_context

    parts = [
        f"Benchmark: {benchmark}",
        f"Condition: {condition}",
        f"Question: {question}",
    ]
    if context_text:
        parts.append(f"Context: {context_text}")
    reasoning = str(row.get("reasoning_text", "")).strip()
    if reasoning:
        parts.append(f"Reasoning: {reasoning}")
    parts.append(f"Answer: {str(row.get('answer', '')).strip()}")
    parts.append(f"Reported confidence: {float(row.get('confidence', 0.5)):.2f}")
    return "\n\n".join(parts)


def _split_rows(
    rows: list[dict[str, Any]],
    *,
    train_benchmark: str,
    train_condition: str,
    eval_benchmark: str,
    eval_condition: str,
    eval_cot_length: int,
    max_train_rows: int,
    max_val_rows: int,
    max_eval_rows: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    filtered = [row for row in rows if "outcome" in row]
    eval_rows = [
        row
        for row in filtered
        if str(row.get("benchmark")) == eval_benchmark
        and str(row.get("condition")) == eval_condition
        and int(row.get("cot_length", 0)) == eval_cot_length
    ]
    eval_rows.sort(key=lambda row: (str(row.get("id")), int(row.get("cot_length", 0))))
    eval_rows = eval_rows[:max_eval_rows]
    eval_keys = {
        (str(row.get("benchmark")), str(row.get("id")), str(row.get("condition")), int(row.get("cot_length", 0)))
        for row in eval_rows
    }
    train_pool = [
        row
        for row in filtered
        if str(row.get("benchmark")) == train_benchmark
        and str(row.get("condition")) == train_condition
        and (
            str(row.get("benchmark")),
            str(row.get("id")),
            str(row.get("condition")),
            int(row.get("cot_length", 0)),
        )
        not in eval_keys
    ]
    rng.shuffle(train_pool)
    val_rows = train_pool[:max_val_rows]
    train_rows = train_pool[max_val_rows : max_val_rows + max_train_rows]
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
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    load_kwargs: dict[str, Any] = {"torch_dtype": dtype_map[args.torch_dtype], "trust_remote_code": True}
    if torch.cuda.is_available() and importlib.util.find_spec("accelerate") is not None:
        load_kwargs["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(args.model_name, **load_kwargs)
    if "device_map" not in load_kwargs:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.config.use_cache = False
    return tokenizer, model


class ConfidenceHeadWrapper:
    def __init__(self, model: Any, hidden_size: int) -> None:
        import torch

        self.model = model
        self.head = torch.nn.Sequential(
            torch.nn.LayerNorm(hidden_size),
            torch.nn.Linear(hidden_size, 1),
        )

    def parameters(self):
        return list(self.model.parameters()) + list(self.head.parameters())


def _make_batches(rows: list[dict[str, Any]], batch_size: int) -> list[list[dict[str, Any]]]:
    return [rows[i : i + batch_size] for i in range(0, len(rows), batch_size)]


def _forward_batch(wrapper: ConfidenceHeadWrapper, tokenizer: Any, rows: list[dict[str, Any]], max_length: int):
    import torch

    texts = [_row_text(row) for row in rows]
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
    )
    device = wrapper.model.device if hasattr(wrapper.model, "device") else next(wrapper.model.parameters()).device
    encoded = {key: value.to(device) for key, value in encoded.items()}
    outputs = wrapper.model(**encoded, output_hidden_states=True, use_cache=False)
    hidden = outputs.hidden_states[-1]
    last_positions = encoded["attention_mask"].sum(dim=1) - 1
    pooled = hidden[torch.arange(hidden.shape[0], device=device), last_positions]
    logits = wrapper.head.to(device)(pooled).squeeze(-1)
    probs = torch.sigmoid(logits)
    targets = torch.tensor([float(row.get("outcome", 0)) for row in rows], dtype=torch.float32, device=device)
    return probs, targets


def _train(
    wrapper: ConfidenceHeadWrapper,
    tokenizer: Any,
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    *,
    max_length: int,
    batch_size: int,
    epochs: int,
    lr: float,
    head_lr: float,
    weight_decay: float,
    seed: int,
) -> list[dict[str, float]]:
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = wrapper.model.device if hasattr(wrapper.model, "device") else next(wrapper.model.parameters()).device
    wrapper.head = wrapper.head.to(device)
    head_params = list(wrapper.head.parameters())
    model_params = [param for param in wrapper.model.parameters() if param.requires_grad]
    optimizer = torch.optim.AdamW(
        [
            {"params": model_params, "lr": lr},
            {"params": head_params, "lr": head_lr},
        ],
        weight_decay=weight_decay,
    )

    best_state = None
    best_val = float("inf")
    history = []
    for epoch in range(1, epochs + 1):
        wrapper.model.train()
        wrapper.head.train()
        train_losses = []
        for batch_rows in _make_batches(train_rows, batch_size):
            optimizer.zero_grad(set_to_none=True)
            probs, targets = _forward_batch(wrapper, tokenizer, batch_rows, max_length)
            loss = torch.mean((probs - targets) ** 2)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.item()))

        wrapper.model.eval()
        wrapper.head.eval()
        with torch.no_grad():
            val_losses = []
            for batch_rows in _make_batches(val_rows, batch_size):
                probs, targets = _forward_batch(wrapper, tokenizer, batch_rows, max_length)
                val_losses.append(float(torch.mean((probs - targets) ** 2).item()))
        train_loss = sum(train_losses) / max(1, len(train_losses))
        val_loss = sum(val_losses) / max(1, len(val_losses))
        history.append({"epoch": epoch, "train_brier": round(train_loss, 6), "val_brier": round(val_loss, 6)})
        if val_loss < best_val:
            best_val = val_loss
            best_state = {
                "model": {k: v.detach().cpu().clone() for k, v in wrapper.model.state_dict().items()},
                "head": {k: v.detach().cpu().clone() for k, v in wrapper.head.state_dict().items()},
            }
    if best_state is not None:
        wrapper.model.load_state_dict(best_state["model"], strict=False)
        wrapper.head.load_state_dict(best_state["head"], strict=False)
    return history


def _predict(wrapper: ConfidenceHeadWrapper, tokenizer: Any, rows: list[dict[str, Any]], max_length: int, batch_size: int) -> list[float]:
    wrapper.model.eval()
    wrapper.head.eval()
    outputs: list[float] = []
    with __import__("torch").no_grad():
        for batch_rows in _make_batches(rows, batch_size):
            probs, _targets = _forward_batch(wrapper, tokenizer, batch_rows, max_length)
            outputs.extend(float(item) for item in probs.detach().cpu().tolist())
    return outputs


def _metrics(confidences: list[float], outcomes: list[int]) -> dict[str, float]:
    mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    mean_accuracy = accuracy(bool(item) for item in outcomes)
    return {
        "count": len(confidences),
        "accuracy": round(mean_accuracy, 6),
        "ece": round(expected_calibration_error(confidences, outcomes), 6),
        "brier": round(brier_score(confidences, outcomes), 6),
        "mean_confidence": round(mean_confidence, 6),
        "overconfidence_gap": round(mean_confidence - mean_accuracy, 6),
        "auroc": round(roc_auc_binary(confidences, outcomes), 6),
    }


def _build_markdown(payload: dict[str, Any]) -> str:
    base = payload["baseline_eval"]
    tuned = payload["tuned_eval"]
    lines = [
        "# Theorem 3 RLCR-Style LoRA Calibration Run",
        "",
        "This is a training-time Brier-loss intervention: LoRA adapters on the 14B theorem-3 model are trained jointly with a confidence head on conflict-heavy traces.",
        "It is stronger than the frozen-head pilot, but it is not a full GRPO / policy-gradient RL reproduction.",
        "",
        "## Setup",
        "",
        f"- Model: `{payload['metadata']['model_name']}`",
        f"- Train benchmark / condition: `{payload['metadata']['train_benchmark']}` / `{payload['metadata']['train_condition']}`",
        f"- Eval benchmark / condition / CoT: `{payload['metadata']['eval_benchmark']}` / `{payload['metadata']['eval_condition']}` / `{payload['metadata']['eval_cot_length']}`",
        f"- Train / val / eval rows: `{payload['metadata']['num_train_rows']}` / `{payload['metadata']['num_val_rows']}` / `{payload['metadata']['num_eval_rows']}`",
        "",
        "## Eval Metrics",
        "",
        f"- Baseline accuracy / ECE / Brier / gap: `{base['accuracy']}` / `{base['ece']}` / `{base['brier']}` / `{base['overconfidence_gap']}`",
        f"- Tuned accuracy / ECE / Brier / gap: `{tuned['accuracy']}` / `{tuned['ece']}` / `{tuned['brier']}` / `{tuned['overconfidence_gap']}`",
        "",
        "## Read",
        "",
        "- This is the closest truthful training-time cousin of RLCR available in the current stack: the calibration objective updates the model through LoRA adapters rather than only training a frozen post-hoc head.",
        "- The key comparison is whether it improves Brier / ECE beyond the frozen-head pilot and beyond eta-tempering on the same long-CoT conflict slice.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    import torch

    args = parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    row_paths = [Path(item.strip()) for item in args.rows_jsonl.split(",") if item.strip()]
    rows = _load_rows(row_paths)
    train_rows, val_rows, eval_rows = _split_rows(
        rows,
        train_benchmark=args.train_benchmark,
        train_condition=args.train_condition,
        eval_benchmark=args.eval_benchmark,
        eval_condition=args.eval_condition,
        eval_cot_length=args.eval_cot_length,
        max_train_rows=args.max_train_rows,
        max_val_rows=args.max_val_rows,
        max_eval_rows=args.max_eval_rows,
        seed=args.seed,
    )
    if not train_rows or not val_rows or not eval_rows:
        raise SystemExit("Need non-empty train/val/eval splits for RLCR-style LoRA run.")

    tokenizer, model = _load_model_and_tokenizer(args)
    hidden_size = int(getattr(model.config, "hidden_size", 0) or getattr(model.config, "n_embd", 0))
    if hidden_size <= 0:
        raise SystemExit("Could not infer hidden size for confidence head.")
    wrapper = ConfidenceHeadWrapper(model, hidden_size)

    history = _train(
        wrapper,
        tokenizer,
        train_rows,
        val_rows,
        max_length=args.max_length,
        batch_size=args.feature_batch_size,
        epochs=args.epochs,
        lr=args.lr,
        head_lr=args.head_lr,
        weight_decay=args.weight_decay,
        seed=args.seed,
    )
    outcomes = [int(row.get("outcome", 0)) for row in eval_rows]
    baseline_confidences = [float(row.get("confidence", 0.5)) for row in eval_rows]
    tuned_confidences = _predict(wrapper, tokenizer, eval_rows, args.max_length, args.feature_batch_size)

    payload = {
        "metadata": {
            "model_name": args.model_name,
            "rows_jsonl": [str(path) for path in row_paths],
            "num_source_rows": len(rows),
            "num_train_rows": len(train_rows),
            "num_val_rows": len(val_rows),
            "num_eval_rows": len(eval_rows),
            "train_benchmark": args.train_benchmark,
            "train_condition": args.train_condition,
            "eval_benchmark": args.eval_benchmark,
            "eval_condition": args.eval_condition,
            "eval_cot_length": args.eval_cot_length,
            "max_length": args.max_length,
            "feature_batch_size": args.feature_batch_size,
            "epochs": args.epochs,
            "lr": args.lr,
            "head_lr": args.head_lr,
            "weight_decay": args.weight_decay,
            "lora_rank": args.lora_rank,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "seed": args.seed,
        },
        "baseline_eval": _metrics(baseline_confidences, outcomes),
        "tuned_eval": _metrics(tuned_confidences, outcomes),
        "training_history": history,
        "preview": [
            {
                "id": str(row.get("id")),
                "benchmark": str(row.get("benchmark")),
                "condition": str(row.get("condition")),
                "cot_length": int(row.get("cot_length", 0)),
                "outcome": int(row.get("outcome", 0)),
                "baseline_confidence": round(float(row.get("confidence", 0.5)), 6),
                "tuned_confidence": round(float(pred), 6),
            }
            for row, pred in list(zip(eval_rows, tuned_confidences))[:20]
        ],
    }

    dump_json(payload, output_dir / "theorem3_rlcr_style_lora.json")
    (output_dir / "theorem3_rlcr_style_lora.md").write_text(_build_markdown(payload), encoding="utf-8")
    torch.save(
        {
            "model_state_dict": wrapper.model.state_dict(),
            "head_state_dict": wrapper.head.state_dict(),
        },
        output_dir / "theorem3_rlcr_style_lora.pt",
    )
    print(json.dumps({"output_dir": str(output_dir), "eval_rows": len(eval_rows)}, indent=2))


if __name__ == "__main__":
    main()
