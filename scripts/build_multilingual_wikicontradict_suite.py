#!/usr/bin/env python3
"""Run a small multilingual WikiContradict transfer suite and summarize it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import build_spanish_wikicontradict_probe as multilingual_probe  # noqa: E402


LANGUAGE_MAP = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a multilingual WikiContradict transfer suite.")
    parser.add_argument("--languages", default="es,fr,de,it,pt")
    parser.add_argument("--max-examples", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--search-limit", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=float, default=1.5)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument(
        "--output-prefix",
        default=str(ROOT / "docs/generated/multilingual_wikicontradict_suite"),
    )
    return parser.parse_args()


def _run_language(lang: str, *, args: argparse.Namespace) -> dict[str, Any]:
    label = LANGUAGE_MAP.get(lang, lang)
    cache_file = ROOT / "docs/generated" / f"{label.lower()}_wikicontradict_probe_cache.json"
    per_lang_prefix = ROOT / "docs/generated" / f"{label.lower()}_wikicontradict_probe_{args.max_examples}"
    probe_args = SimpleNamespace(
        max_examples=args.max_examples,
        top_k=args.top_k,
        search_limit=args.search_limit,
        sleep_seconds=args.sleep_seconds,
        max_retries=args.max_retries,
        target_lang=lang,
        target_label=label,
        cache_file=str(cache_file),
        output_prefix=str(per_lang_prefix),
    )
    payload = multilingual_probe.build_payload(probe_args)
    (per_lang_prefix.with_suffix(".json")).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (per_lang_prefix.with_suffix(".md")).write_text(multilingual_probe.build_markdown(payload), encoding="utf-8")
    return payload


def build_suite(args: argparse.Namespace) -> dict[str, Any]:
    rows = []
    payloads = {}
    for lang in [item.strip().lower() for item in args.languages.split(",") if item.strip()]:
        payload = _run_language(lang, args=args)
        payloads[lang] = payload
        rows.append(
            {
                "language": lang,
                "label": payload["headline"]["target_label"],
                "completed_examples": payload["metadata"]["completed_examples"],
                "failed_examples": payload["metadata"]["failed_examples"],
                "top1_gold_hit_rate": payload["headline"]["top1_gold_hit_rate"],
                "top1_conflict_hit_rate": payload["headline"]["top1_conflict_hit_rate"],
                "topk_gold_hit_rate": payload["headline"]["topk_gold_hit_rate"],
                "topk_conflict_hit_rate": payload["headline"]["topk_conflict_hit_rate"],
                "topk_both_hit_rate": payload["headline"]["topk_both_hit_rate"],
            }
        )
    completed = [row for row in rows if row["completed_examples"] > 0]
    summary = {
        "metadata": {
            "languages": [row["language"] for row in rows],
            "max_examples_per_language": args.max_examples,
            "top_k": args.top_k,
        },
        "headline": {
            "languages_run": len(rows),
            "languages_with_any_gold_hit": sum(1 for row in rows if row["topk_gold_hit_rate"] > 0),
            "languages_with_any_conflict_hit": sum(1 for row in rows if row["topk_conflict_hit_rate"] > 0),
            "mean_topk_gold_hit_rate": round(
                sum(row["topk_gold_hit_rate"] for row in completed) / len(completed), 4
            )
            if completed
            else 0.0,
            "mean_topk_conflict_hit_rate": round(
                sum(row["topk_conflict_hit_rate"] for row in completed) / len(completed), 4
            )
            if completed
            else 0.0,
        },
        "rows": rows,
        "payloads": payloads,
    }
    return summary


def build_markdown(summary: dict[str, Any]) -> str:
    h = summary["headline"]
    lines = [
        "# Multilingual WikiContradict Transfer Suite",
        "",
        "This suite expands the earlier single-language transfer spot-check into a small multi-language probe using translated WikiContradict queries and target-language Wikipedia search.",
        "",
        "## Headline",
        "",
        f"- Languages run: `{h['languages_run']}`",
        f"- Languages with any top-k gold hit: `{h['languages_with_any_gold_hit']}`",
        f"- Languages with any top-k conflict hit: `{h['languages_with_any_conflict_hit']}`",
        f"- Mean top-k gold-hit rate across completed languages: `{h['mean_topk_gold_hit_rate']}`",
        f"- Mean top-k conflict-hit rate across completed languages: `{h['mean_topk_conflict_hit_rate']}`",
        "",
        "| Language | Completed | Failed | Top-1 Gold | Top-1 Conflict | Top-k Gold | Top-k Conflict | Top-k Both |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["rows"]:
        lines.append(
            f"| {row['label']} | {row['completed_examples']} | {row['failed_examples']} | "
            f"{row['top1_gold_hit_rate']:.4f} | {row['top1_conflict_hit_rate']:.4f} | "
            f"{row['topk_gold_hit_rate']:.4f} | {row['topk_conflict_hit_rate']:.4f} | "
            f"{row['topk_both_hit_rate']:.4f} |"
        )
    lines.append("")
    lines.append("This remains a transfer probe, not a multilingual theorem-3 replacement benchmark. It does, however, materially weaken the claim that the current evidence is purely English-only.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_suite(args)
    out_prefix = Path(args.output_prefix)
    out_prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    out_prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps(summary["headline"], indent=2))


if __name__ == "__main__":
    main()
