#!/usr/bin/env python3
"""Train a lightweight Brier-optimized confidence head on theorem-3 traces.

This is the lightest truthful retraining-style pilot supported by the current
Delta stack. The base LM remains frozen; we extract hidden-state features from
real theorem-3 traces and train a small confidence head with Brier loss to
predict correctness on conflict-heavy examples.
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
    parser = argparse.ArgumentParser(description="Run a theorem-3 confidence-head retraining pilot.")
    parser.add_argument("--rows-jsonl", required=True, help="Comma-separated theorem-3 row files.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--max-train-rows", type=int, default=1200)
    parser.add_argument("--max-val-rows", type=int, default=200)
    parser.add_argument("--max-eval-rows", type=int, default=500)
    parser.add_argument("--train-benchmarks", default="wikicontradict,conflictbank")
    parser.add_argument("--eval-benchmark", default="conflictbank")
    parser.add_argument("--eval-condition", default="conflict_context")
    parser.add_argument("--eval-cot-length", type=int, default=1024)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--feature-batch-size", type=int, default=2)
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
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
    train_benchmarks: set[str],
    eval_benchmark: str,
    eval_condition: str,
    eval_cot_length: int,
    max_train_rows: int,
    max_val_rows: int,
    max_eval_rows: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    filtered = [
        row
        for row in rows
        if str(row.get("benchmark")) in train_benchmarks
        and str(row.get("condition")) in {"closed_book", "aligned_context", "conflict_context"}
        and "outcome" in row
    ]
    eval_rows = [
        row
        for row in filtered
        if str(row.get("benchmark")) == eval_benchmark
        and str(row.get("condition")) == eval_condition
        and int(row.get("cot_length", 0)) == eval_cot_length
    ]
    eval_rows.sort(key=lambda row: (str(row.get("id")), str(row.get("condition")), int(row.get("cot_length", 0))))
    eval_rows = eval_rows[:max_eval_rows]
    eval_keys = {
        (str(row.get("benchmark")), str(row.get("id")), str(row.get("condition")), int(row.get("cot_length", 0)))
        for row in eval_rows
    }

    train_pool = [
        row
        for row in filtered
        if (
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
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    return tokenizer, model


def _batch_features(
    texts: list[str],
    *,
    tokenizer: Any,
    model: Any,
    max_length: int,
    batch_size: int,
):
    import torch

    features = []
    device = model.device if hasattr(model, "device") else next(model.parameters()).device
    for start in range(0, len(texts), batch_size):
        batch_texts = texts[start : start + batch_size]
        token_batches = []
        for text in batch_texts:
            token_ids = tokenizer.encode(text, add_special_tokens=True)
            if len(token_ids) > max_length:
                token_ids = token_ids[-max_length:]
            token_batches.append(token_ids)

        max_len = max(len(item) for item in token_batches)
        pad_id = tokenizer.pad_token_id
        input_ids = []
        attention_mask = []
        for token_ids in token_batches:
            padding = [pad_id] * (max_len - len(token_ids))
            input_ids.append(padding + token_ids)
            attention_mask.append([0] * len(padding) + [1] * len(token_ids))

        input_tensor = torch.tensor(input_ids, dtype=torch.long, device=device)
        mask_tensor = torch.tensor(attention_mask, dtype=torch.long, device=device)
        with torch.no_grad():
            outputs = model(
                input_ids=input_tensor,
                attention_mask=mask_tensor,
                output_hidden_states=True,
                use_cache=False,
            )
            hidden = outputs.hidden_states[-1]
            last_positions = mask_tensor.sum(dim=1) - 1
            pooled = hidden[torch.arange(hidden.shape[0], device=device), last_positions]
            features.extend(pooled.float().cpu())
    return features


def _extract_dataset_features(
    rows: list[dict[str, Any]],
    *,
    tokenizer: Any,
    model: Any,
    max_length: int,
    batch_size: int,
) -> tuple[Any, Any, list[dict[str, Any]]]:
    import torch

    texts = [_row_text(row) for row in rows]
    hidden_features = _batch_features(
        texts,
        tokenizer=tokenizer,
        model=model,
        max_length=max_length,
        batch_size=batch_size,
    )
    confidence_feature = torch.tensor(
        [[float(row.get("confidence", 0.5))] for row in rows],
        dtype=torch.float32,
    )
    stacked = torch.stack(hidden_features, dim=0)
    features = torch.cat([stacked, confidence_feature], dim=1)
    labels = torch.tensor([float(row.get("outcome", 0)) for row in rows], dtype=torch.float32)
    return features, labels, rows


def _train_head(
    train_features,
    train_labels,
    val_features,
    val_labels,
    *,
    lr: float,
    weight_decay: float,
    epochs: int,
    seed: int,
):
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_dim = train_features.shape[1]
    head = torch.nn.Sequential(
        torch.nn.LayerNorm(input_dim),
        torch.nn.Linear(input_dim, 1),
    ).to(device)
    optimizer = torch.optim.AdamW(head.parameters(), lr=lr, weight_decay=weight_decay)

    train_x = train_features.to(device)
    train_y = train_labels.to(device)
    val_x = val_features.to(device)
    val_y = val_labels.to(device)

    best_state = None
    best_val = float("inf")
    history = []
    for epoch in range(1, epochs + 1):
        head.train()
        optimizer.zero_grad(set_to_none=True)
        probs = torch.sigmoid(head(train_x).squeeze(-1))
        loss = torch.mean((probs - train_y) ** 2)
        loss.backward()
        optimizer.step()

        head.eval()
        with torch.no_grad():
            val_probs = torch.sigmoid(head(val_x).squeeze(-1))
            val_loss = torch.mean((val_probs - val_y) ** 2).item()
            train_loss = loss.item()
        history.append({"epoch": epoch, "train_brier": round(train_loss, 6), "val_brier": round(val_loss, 6)})
        if val_loss < best_val:
            best_val = val_loss
            best_state = {key: value.detach().cpu().clone() for key, value in head.state_dict().items()}

    if best_state is not None:
        head.load_state_dict(best_state)
    return head.cpu(), history


def _metrics_for_confidences(confidences: list[float], outcomes: list[int]) -> dict[str, float]:
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


def _evaluate_head(head, features, labels) -> list[float]:
    import torch

    head.eval()
    with torch.no_grad():
        probs = torch.sigmoid(head(features).squeeze(-1)).cpu().tolist()
    return [float(item) for item in probs]


def _build_markdown(payload: dict[str, Any]) -> str:
    base = payload["baseline_eval"]
    pilot = payload["pilot_eval"]
    lines = [
        "# Theorem 3 Confidence-Head Pilot",
        "",
        "This is a lightweight RLCR-inspired retraining pilot: we freeze the base theorem-3 model, extract hidden-state features from real theorem-3 traces, and train a small confidence head with Brier loss to predict correctness on conflict-heavy examples.",
        "",
        "## Setup",
        "",
        f"- Model: `{payload['metadata']['model_name']}`",
        f"- Train rows: `{payload['metadata']['num_train_rows']}`",
        f"- Validation rows: `{payload['metadata']['num_val_rows']}`",
        f"- Eval rows: `{payload['metadata']['num_eval_rows']}`",
        f"- Eval slice: `{payload['metadata']['eval_benchmark']}` / `{payload['metadata']['eval_condition']}` / `cot={payload['metadata']['eval_cot_length']}`",
        "",
        "## Eval Metrics",
        "",
        f"- Baseline accuracy / ECE / Brier / gap: `{base['accuracy']}` / `{base['ece']}` / `{base['brier']}` / `{base['overconfidence_gap']}`",
        f"- Pilot accuracy / ECE / Brier / gap: `{pilot['accuracy']}` / `{pilot['ece']}` / `{pilot['brier']}` / `{pilot['overconfidence_gap']}`",
        "",
        "## Interpretation",
        "",
        "- Accuracy should stay roughly fixed because this pilot only retrains the confidence layer, not the answer tokens.",
        "- The success criterion is lower Brier / ECE and a smaller overconfidence gap on the long-CoT conflict slice.",
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
        train_benchmarks={item.strip() for item in args.train_benchmarks.split(",") if item.strip()},
        eval_benchmark=args.eval_benchmark,
        eval_condition=args.eval_condition,
        eval_cot_length=args.eval_cot_length,
        max_train_rows=args.max_train_rows,
        max_val_rows=args.max_val_rows,
        max_eval_rows=args.max_eval_rows,
        seed=args.seed,
    )
    if not train_rows or not val_rows or not eval_rows:
        raise SystemExit("Need non-empty train/val/eval splits for confidence-head pilot.")

    tokenizer, model = _load_model_and_tokenizer(args.model_name, args.torch_dtype)
    train_features, train_labels, _ = _extract_dataset_features(
        train_rows,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.feature_batch_size,
    )
    val_features, val_labels, _ = _extract_dataset_features(
        val_rows,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.feature_batch_size,
    )
    eval_features, eval_labels, eval_metadata = _extract_dataset_features(
        eval_rows,
        tokenizer=tokenizer,
        model=model,
        max_length=args.max_length,
        batch_size=args.feature_batch_size,
    )
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    head, history = _train_head(
        train_features,
        train_labels,
        val_features,
        val_labels,
        lr=args.lr,
        weight_decay=args.weight_decay,
        epochs=args.epochs,
        seed=args.seed,
    )

    baseline_confidences = [float(row.get("confidence", 0.5)) for row in eval_metadata]
    outcomes = [int(row.get("outcome", 0)) for row in eval_metadata]
    pilot_confidences = _evaluate_head(head, eval_features, eval_labels)

    payload = {
        "metadata": {
            "model_name": args.model_name,
            "source_rows_jsonl": [str(path) for path in row_paths],
            "num_source_rows": len(rows),
            "num_train_rows": len(train_rows),
            "num_val_rows": len(val_rows),
            "num_eval_rows": len(eval_rows),
            "eval_benchmark": args.eval_benchmark,
            "eval_condition": args.eval_condition,
            "eval_cot_length": args.eval_cot_length,
            "max_length": args.max_length,
            "feature_batch_size": args.feature_batch_size,
            "epochs": args.epochs,
            "lr": args.lr,
            "weight_decay": args.weight_decay,
            "seed": args.seed,
        },
        "baseline_eval": _metrics_for_confidences(baseline_confidences, outcomes),
        "pilot_eval": _metrics_for_confidences(pilot_confidences, outcomes),
        "training_history": history,
        "preview": [
            {
                "id": str(row.get("id")),
                "benchmark": str(row.get("benchmark")),
                "condition": str(row.get("condition")),
                "cot_length": int(row.get("cot_length", 0)),
                "outcome": int(row.get("outcome", 0)),
                "baseline_confidence": round(float(row.get("confidence", 0.5)), 6),
                "pilot_confidence": round(float(pred), 6),
            }
            for row, pred in list(zip(eval_metadata, pilot_confidences))[:20]
        ],
    }

    dump_json(payload, output_dir / "theorem3_confidence_head_pilot.json")
    (output_dir / "theorem3_confidence_head_pilot.md").write_text(_build_markdown(payload), encoding="utf-8")
    torch.save({"state_dict": head.state_dict()}, output_dir / "theorem3_confidence_head_pilot.pt")
    print(json.dumps({"output_dir": str(output_dir), "eval_rows": len(eval_rows)}, indent=2))


if __name__ == "__main__":
    main()
