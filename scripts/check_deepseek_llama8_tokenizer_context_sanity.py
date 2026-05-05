#!/usr/bin/env python3
"""Local-first tokenizer/context sanity checks for DeepSeek-Llama-8B diagnosis.

This script is intentionally lightweight and defensive:

- It first inspects local files and local Hugging Face cache snapshots.
- It optionally enriches the report with `transformers` metadata when that
  package is available.
- It never crashes just because `transformers` or cached model files are
  missing; instead it records what could not be checked.

The goal is not to prove the DeepSeek failure mechanism by itself. The goal is
to rule out simple setup issues such as context-window mismatch, tokenizer
special-token mismatch, or an obviously wrong local model/tokenizer snapshot.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local-first tokenizer/context sanity checks for a DeepSeek-Llama-8B model path or repo id."
    )
    parser.add_argument(
        "--model",
        default="deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        help="Local model directory or Hugging Face repo id.",
    )
    parser.add_argument(
        "--run-max-model-len",
        type=int,
        default=12288,
        help="Max model length used by the theorem-3 rerun to compare against the model/tokenizer limits.",
    )
    parser.add_argument(
        "--run-max-prompt-tokens",
        type=int,
        default=4096,
        help="Prompt token budget used by the theorem-3 rerun to compare against the model/tokenizer limits.",
    )
    parser.add_argument(
        "--sample-text",
        default="Question: Which answer should the model trust under conflicting retrieved evidence?\n\n<think>\n",
        help="Short sample string used for a tokenizer smoke check when transformers is available.",
    )
    parser.add_argument(
        "--output-json",
        help="Optional JSON output path. If omitted, the report is printed to stdout.",
    )
    return parser.parse_args()


def _safe_read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _repo_id_to_cache_dirs(repo_id: str) -> list[Path]:
    cache_roots = []
    env_root = os.environ.get("HF_HOME")
    if env_root:
        cache_roots.append(Path(env_root) / "hub")
    cache_roots.append(Path.home() / ".cache" / "huggingface" / "hub")
    safe_repo = repo_id.replace("/", "--")
    out: list[Path] = []
    for root in cache_roots:
        out.append(root / f"models--{safe_repo}")
    return out


def _latest_snapshot(repo_id: str) -> Path | None:
    candidates: list[Path] = []
    for cache_dir in _repo_id_to_cache_dirs(repo_id):
        snapshots = cache_dir / "snapshots"
        if snapshots.exists():
            for child in snapshots.iterdir():
                if child.is_dir():
                    candidates.append(child)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _resolve_local_model_root(model_arg: str) -> tuple[Path | None, str]:
    direct = Path(model_arg).expanduser()
    if direct.exists():
        return direct.resolve(), "direct_path"
    cached = _latest_snapshot(model_arg)
    if cached is not None:
        return cached.resolve(), "hf_cache_snapshot"
    return None, "unresolved"


def _existing_files(root: Path | None) -> dict[str, str]:
    if root is None:
        return {}
    wanted = [
        "config.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "special_tokens_map.json",
        "generation_config.json",
    ]
    found: dict[str, str] = {}
    for name in wanted:
        path = root / name
        if path.exists():
            found[name] = str(path)
    return found


def _context_candidates(config: dict[str, Any] | None, tokenizer_config: dict[str, Any] | None) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if config:
        for key in ("max_position_embeddings", "n_positions", "seq_length", "model_max_length"):
            value = config.get(key)
            if isinstance(value, int):
                out[f"config.{key}"] = value
        rope_scaling = config.get("rope_scaling")
        if isinstance(rope_scaling, dict):
            original = rope_scaling.get("original_max_position_embeddings")
            factor = rope_scaling.get("factor")
            if isinstance(original, int):
                out["config.rope_scaling.original_max_position_embeddings"] = original
            if isinstance(factor, (int, float)):
                out["config.rope_scaling.factor"] = factor
    if tokenizer_config:
        value = tokenizer_config.get("model_max_length")
        if isinstance(value, int):
            out["tokenizer_config.model_max_length"] = value
    return out


def _normalize_context_limit(candidates: dict[str, Any]) -> int | None:
    usable: list[int] = []
    for key, value in candidates.items():
        if not isinstance(value, int):
            continue
        if "factor" in key:
            continue
        if value <= 0:
            continue
        if value > 10**12:
            continue
        usable.append(value)
    return min(usable) if usable else None


def _probe_transformers(model_arg: str, sample_text: str) -> dict[str, Any]:
    try:
        from transformers import AutoConfig, AutoTokenizer  # type: ignore
    except Exception as exc:
        return {
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    report: dict[str, Any] = {"available": True}
    try:
        config = AutoConfig.from_pretrained(model_arg, local_files_only=True, trust_remote_code=True)
        report["config_class"] = type(config).__name__
        report["config_model_type"] = getattr(config, "model_type", None)
        report["config_max_position_embeddings"] = getattr(config, "max_position_embeddings", None)
        report["config_rope_scaling"] = getattr(config, "rope_scaling", None)
    except Exception as exc:
        report["config_error"] = f"{type(exc).__name__}: {exc}"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_arg, local_files_only=True, trust_remote_code=True)
        report["tokenizer_class"] = type(tokenizer).__name__
        report["tokenizer_model_max_length"] = getattr(tokenizer, "model_max_length", None)
        report["pad_token"] = getattr(tokenizer, "pad_token", None)
        report["pad_token_id"] = getattr(tokenizer, "pad_token_id", None)
        report["eos_token"] = getattr(tokenizer, "eos_token", None)
        report["eos_token_id"] = getattr(tokenizer, "eos_token_id", None)
        report["bos_token"] = getattr(tokenizer, "bos_token", None)
        report["bos_token_id"] = getattr(tokenizer, "bos_token_id", None)
        report["think_token_id"] = tokenizer.convert_tokens_to_ids("<think>")
        report["sample_text_token_count"] = len(tokenizer.encode(sample_text, add_special_tokens=True))
        chat_template = getattr(tokenizer, "chat_template", None)
        if isinstance(chat_template, str):
            report["chat_template_present"] = True
            report["chat_template_mentions_system"] = "{{ system" in chat_template or "system" in chat_template.lower()
        else:
            report["chat_template_present"] = False
            report["chat_template_mentions_system"] = False
    except Exception as exc:
        report["tokenizer_error"] = f"{type(exc).__name__}: {exc}"
    return report


def _build_checks(
    *,
    model_arg: str,
    resolved_root: Path | None,
    config: dict[str, Any] | None,
    tokenizer_config: dict[str, Any] | None,
    special_tokens_map: dict[str, Any] | None,
    generation_config: dict[str, Any] | None,
    context_candidates: dict[str, Any],
    effective_limit: int | None,
    run_max_model_len: int,
    run_max_prompt_tokens: int,
    transformers_probe: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append(
        {
            "name": "local_metadata_resolution",
            "status": "pass" if resolved_root is not None else "warn",
            "detail": f"Resolved model metadata locally from `{resolved_root}`."
            if resolved_root is not None
            else f"No local path or HF cache snapshot was found for `{model_arg}`.",
        }
    )

    checks.append(
        {
            "name": "transformers_optional_probe",
            "status": (
                "pass"
                if transformers_probe.get("available")
                and not transformers_probe.get("config_error")
                and not transformers_probe.get("tokenizer_error")
                else "warn"
            ),
            "detail": (
                "Loaded optional transformers config/tokenizer metadata locally."
                if transformers_probe.get("available")
                and not transformers_probe.get("config_error")
                and not transformers_probe.get("tokenizer_error")
                else (
                    "Transformers is installed, but local-only config/tokenizer loading did not succeed: "
                    f"{transformers_probe.get('config_error') or transformers_probe.get('tokenizer_error')}"
                    if transformers_probe.get("available")
                    else f"Transformers unavailable or unusable: {transformers_probe.get('error', 'unknown error')}"
                )
            ),
        }
    )

    checks.append(
        {
            "name": "context_limit_vs_rerun_budget",
            "status": "pass"
            if effective_limit is not None and run_max_model_len <= effective_limit and run_max_prompt_tokens <= effective_limit
            else "warn",
            "detail": (
                f"Effective local context limit `{effective_limit}` comfortably exceeds rerun bounds "
                f"`max_model_len={run_max_model_len}` and `max_prompt_tokens={run_max_prompt_tokens}`."
            )
            if effective_limit is not None and run_max_model_len <= effective_limit and run_max_prompt_tokens <= effective_limit
            else (
                f"Could not verify a local context limit, or rerun bounds exceed it. "
                f"Candidates: {context_candidates or 'none'}."
            ),
        }
    )

    think_present = False
    if isinstance(special_tokens_map, dict):
        think_present = "<think>" in json.dumps(special_tokens_map)
    if isinstance(transformers_probe.get("think_token_id"), int) and transformers_probe["think_token_id"] >= 0:
        think_present = True

    checks.append(
        {
            "name": "think_token_support",
            "status": "pass" if think_present else "warn",
            "detail": "The tokenizer metadata appears to know about `<think>`."
            if think_present
            else "Did not confirm `<think>` in local tokenizer metadata. That does not prove failure, but it weakens the DeepSeek-native prompt path check.",
        }
    )

    chat_mentions_system = bool(transformers_probe.get("chat_template_mentions_system"))
    checks.append(
        {
            "name": "system_prompt_risk",
            "status": "warn" if chat_mentions_system else "pass",
            "detail": "Local tokenizer chat template appears to mention a system role."
            if chat_mentions_system
            else "Did not find a local chat-template signal that forces a system role.",
        }
    )

    do_sample = generation_config.get("do_sample") if isinstance(generation_config, dict) else None
    temperature = generation_config.get("temperature") if isinstance(generation_config, dict) else None
    checks.append(
        {
            "name": "generation_defaults_snapshot",
            "status": "pass",
            "detail": f"Local generation config snapshot: do_sample={do_sample!r}, temperature={temperature!r}.",
        }
    )

    return checks


def main() -> int:
    args = parse_args()

    resolved_root, resolution_mode = _resolve_local_model_root(args.model)
    files = _existing_files(resolved_root)

    config = _safe_read_json(Path(files["config.json"])) if "config.json" in files else None
    tokenizer_config = _safe_read_json(Path(files["tokenizer_config.json"])) if "tokenizer_config.json" in files else None
    special_tokens_map = _safe_read_json(Path(files["special_tokens_map.json"])) if "special_tokens_map.json" in files else None
    generation_config = _safe_read_json(Path(files["generation_config.json"])) if "generation_config.json" in files else None

    context_candidates = _context_candidates(config, tokenizer_config)
    effective_limit = _normalize_context_limit(context_candidates)
    transformers_probe = _probe_transformers(args.model, args.sample_text)

    report: dict[str, Any] = {
        "model": args.model,
        "resolved_local_root": str(resolved_root) if resolved_root is not None else None,
        "resolution_mode": resolution_mode,
        "local_files_found": files,
        "config_summary": {
            "model_type": config.get("model_type") if isinstance(config, dict) else None,
            "architectures": config.get("architectures") if isinstance(config, dict) else None,
            "max_position_embeddings": config.get("max_position_embeddings") if isinstance(config, dict) else None,
            "rope_scaling": config.get("rope_scaling") if isinstance(config, dict) else None,
        },
        "tokenizer_config_summary": {
            "model_max_length": tokenizer_config.get("model_max_length") if isinstance(tokenizer_config, dict) else None,
            "padding_side": tokenizer_config.get("padding_side") if isinstance(tokenizer_config, dict) else None,
            "chat_template_present": bool(tokenizer_config.get("chat_template")) if isinstance(tokenizer_config, dict) else None,
        },
        "special_tokens_summary": {
            "has_special_tokens_map": bool(special_tokens_map),
            "keys": sorted(special_tokens_map.keys()) if isinstance(special_tokens_map, dict) else [],
        },
        "generation_config_summary": generation_config if isinstance(generation_config, dict) else None,
        "context_limit_candidates": context_candidates,
        "effective_context_limit": effective_limit,
        "rerun_budget": {
            "max_model_len": args.run_max_model_len,
            "max_prompt_tokens": args.run_max_prompt_tokens,
        },
        "transformers_probe": transformers_probe,
    }
    report["checks"] = _build_checks(
        model_arg=args.model,
        resolved_root=resolved_root,
        config=config,
        tokenizer_config=tokenizer_config,
        special_tokens_map=special_tokens_map,
        generation_config=generation_config,
        context_candidates=context_candidates,
        effective_limit=effective_limit,
        run_max_model_len=args.run_max_model_len,
        run_max_prompt_tokens=args.run_max_prompt_tokens,
        transformers_probe=transformers_probe,
    )

    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
