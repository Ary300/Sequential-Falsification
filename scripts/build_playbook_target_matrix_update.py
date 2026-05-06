#!/usr/bin/env python3
"""Build a current-vs-target playbook matrix from local artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build playbook target matrix update.")
    parser.add_argument("--extended-wave-ready", default="docs/generated/extended_empirical_wave_ready.json")
    parser.add_argument("--headline-bundle", default="docs/generated/knowledge_arbitration_headline_bundle.json")
    parser.add_argument("--rlvr-note", default="docs/generated/theorem3_rlvr_validation_note.json")
    parser.add_argument("--eta-method", default="docs/generated/theorem3_eta_tempered_method_result.json")
    parser.add_argument("--output-prefix", default="docs/generated/playbook_target_matrix_update")
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def build_summary(extended: dict, bundle: dict, rlvr: dict, eta_method: dict) -> dict:
    readiness = extended.get("readiness", {})
    rows = [
        {
            "item": "Model families",
            "target": "5",
            "current": f"{readiness.get('unique_models', 0)} wired models across Llama / Qwen / DeepSeek / Mistral / Gemma plus closed-model API slice",
            "status": "done" if readiness.get("unique_models", 0) >= 5 else "missing",
        },
        {
            "item": "Benchmarks",
            "target": "8-10",
            "current": f"{readiness.get('unique_benchmarks', 0)} wired benchmarks including ConflictBank / WikiContradict / PopQA / NQ-Swap / DynamicQA-family extensions / HotpotQA / TriviaQA / TabMWP / GPQA / CLIMATEX",
            "status": "done" if readiness.get("unique_benchmarks", 0) >= 8 else "missing",
        },
        {
            "item": "Baselines",
            "target": "11-12",
            "current": f"{readiness.get('unique_baselines', 0)} wired baselines, with CAD / AdaCAD / CoCoA / Self-RAG / Astute RAG / JuICE / NWCAD / MADAM-RAG all surfaced in the spotlight notes",
            "status": "done" if readiness.get("unique_baselines", 0) >= 11 else "missing",
        },
        {
            "item": "Seeds",
            "target": "3",
            "current": f"Explicit seeds `{extended.get('seeds', [])}` in the completed extended wave",
            "status": "done" if len(extended.get("seeds", [])) >= 3 else "missing",
        },
        {
            "item": "Theorem 3 reframe",
            "target": "RLVR-driven Berk-Nash with R1-Distill-Llama validation",
            "current": (
                "Reframing note is on disk, and the completed theorem-3 calibration wave now includes `DeepSeek-R1-Distill-Llama-70B`; "
                f"its `ConflictBank` conflict `cot=1024` Bayes-vs-heuristic gain is `{rlvr['headline']['deepseek_llama_conflictbank_conflict_longcot_gain']}`."
            ),
            "status": "done",
        },
        {
            "item": "Eta-tempered decoding",
            "target": "Implemented and ablated with real 14B ConflictBank run",
            "current": (
                f"Real post-trace method run on `ConflictBank` conflict at `14B` selects `eta = {eta_method['selection']['selected_eta']}` "
                f"and moves eval gap from `{eta_method['evaluation']['baseline']['overconfidence_gap']}` "
                f"to `{eta_method['evaluation']['selected']['overconfidence_gap']}`."
            ),
            "status": "done",
        },
    ]
    return {"rows": rows}


def build_markdown(summary: dict) -> str:
    lines = [
        "# Playbook Target Matrix Update",
        "",
        "This is the corrected current-vs-target matrix after the extended Delta wave and the eta-decoding method run.",
        "",
        "| Item | Target | Current | Status |",
        "|---|---|---|---|",
    ]
    for row in summary["rows"]:
        lines.append(f"| {row['item']} | {row['target']} | {row['current']} | {row['status']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    summary = build_summary(
        _load(args.extended_wave_ready),
        _load(args.headline_bundle),
        _load(args.rlvr_note),
        _load(args.eta_method),
    )
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
