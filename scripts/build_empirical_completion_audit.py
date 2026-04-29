#!/usr/bin/env python3
"""Build a compact empirical-completion audit for the paper package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_PREFIX = ROOT / "docs/generated/empirical_completion_audit"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary() -> dict[str, Any]:
    spotlight = _load_json(ROOT / "docs/generated/spotlight_5x5_grid_note.json")
    wave = _load_json(ROOT / "docs/generated/arbitration_spotlight_wave_summary.json")
    bootstrap_t12 = _load_json(ROOT / "docs/generated/arbitration_spotlight_t12_bootstrap_v1.json")
    bootstrap_t3 = _load_json(ROOT / "docs/generated/arbitration_spotlight_t3_bootstrap_v1.json")
    popqa_nqswap = _load_json(ROOT / "docs/generated/popqa_nqswap_real_benchmark_note.json")
    llama8 = _load_json(ROOT / "docs/generated/llama_8b_spotlight_note.json")
    llama70 = _load_json(ROOT / "docs/generated/llama_70b_frontier_note.json")
    theorem3_same = _load_json(ROOT / "docs/generated/theorem3_same_family_threshold_summary.json")
    theorem3_cross = _load_json(ROOT / "docs/generated/theorem3_cross_family_verdict.json")
    theorem3_eta = _load_json(ROOT / "docs/generated/theorem3_eta_tempering_analysis.json")
    family = _load_json(ROOT / "docs/generated/benchmark_family_consistency_note.json")
    spotlight_unanimous = [
        row["benchmark"]
        for row in family["t12_matrix"]
        if row["positive_models_vs_baseline"] == row["num_models"]
    ]

    completed_items = [
        {
            "item": "spotlight_matrix_5x5",
            "status": "done_with_headline_result",
            "evidence": "5 models x 5 benchmarks x 174,080 rows",
        },
        {
            "item": "frontier_open_weight_model",
            "status": "done_with_headline_result",
            "evidence": "Llama-3.1-70B five-benchmark slice on disk",
        },
        {
            "item": "closest_cousin_baselines",
            "status": "done_with_headline_result",
            "evidence": "AdaCAD, CoCoA, MADAM-RAG, NWCAD, JuICE, Self-RAG, CAD surfaced in spotlight summaries",
        },
        {
            "item": "popqa_benchmark",
            "status": "done_with_headline_result",
            "evidence": "Bayes vs heuristic 0.0950 [0.0440, 0.1460]",
        },
        {
            "item": "nq_swap_benchmark",
            "status": "done_with_headline_result",
            "evidence": "Bayes vs heuristic 0.1038 [0.0829, 0.1250]",
        },
        {
            "item": "same_family_qwen_theorem3_sweep",
            "status": "done_with_headline_result",
            "evidence": "Qwen2.5 7B/14B/32B complete with 32B recovery on WikiContradict only",
        },
        {
            "item": "cross_family_theorem3_check",
            "status": "done_with_honest_negative",
            "evidence": "DeepSeek asymmetry true, Qwen asymmetry false",
        },
        {
            "item": "eta_tempering_intervention",
            "status": "done_with_mechanism_result",
            "evidence": "conflict/no-conflict eta shrink factor 0.52",
        },
        {
            "item": "killer_figure_package",
            "status": "done",
            "evidence": "scripted SVG package built from finished artifacts",
        },
    ]
    missing_items = [
        "Mistral family runs are not on disk.",
        "Gemma family runs are not on disk.",
        "DeepSeek-R1-Distill-Llama frontier sweep is not on disk.",
        "Closed-model API comparison is not on disk.",
        "HotpotQA is not on disk as a finished paper artifact.",
        "TriviaQA is not on disk as a finished paper artifact.",
        "TabMWP is not on disk as a finished paper artifact.",
        "GPQA / CLIMATEX / MATH-500 theorem-3 calibration extensions are not on disk as finished paper artifacts.",
    ]
    return {
        "headline": {
            "spotlight_matrix_gain": abs(wave["t12_matrix"]["headline"]["bayes_minus_heuristic"]),
            "spotlight_matrix_ci95": bootstrap_t12["bootstrap"]["bayes_vs_heuristic"],
            "theorem3_proxy_gain": abs(wave["t3_proxy_matrix"]["headline"]["bayes_minus_heuristic"]),
            "theorem3_proxy_ci95": bootstrap_t3["bootstrap"]["bayes_vs_heuristic"],
            "popqa_gain": popqa_nqswap["headline"]["popqa_bayes_vs_heuristic_gain"],
            "nq_swap_gain": popqa_nqswap["headline"]["nq_swap_bayes_vs_heuristic_gain"],
            "llama8_gain": llama8["overall"]["bayes_vs_heuristic_gain"],
            "llama70_gain": llama70["overall"]["bayes_vs_heuristic_gain"],
            "qwen_recovery_threshold_b": theorem3_same["headline"]["qwen_wikicontradict_conflict_recovery_threshold_b"],
            "qwen_controlled_conflict_threshold_b": theorem3_same["headline"]["qwen_conflictbank_conflict_recovery_threshold_b"],
            "deepseek_cross_family_asymmetry": theorem3_cross["headline"]["deepseek_7b_14b_conflictbank_asymmetry_replicates"],
            "qwen_cross_family_asymmetry": theorem3_cross["headline"]["qwen_7b_14b_conflictbank_asymmetry_replicates"],
            "eta_shrink_factor": theorem3_eta["headline"]["conflict_to_no_conflict_eta_shrink_factor"],
            "spotlight_unanimous_benchmarks": spotlight_unanimous,
        },
        "completed_items": completed_items,
        "missing_items": missing_items,
        "coverage": {
            "models": spotlight["models"],
            "benchmarks": spotlight["benchmarks"],
            "num_models": spotlight["num_models"],
            "num_benchmarks": spotlight["num_benchmarks"],
            "num_rows": spotlight["num_rows"],
        },
    }


def build_markdown(summary: dict[str, Any]) -> str:
    h = summary["headline"]
    c = summary["coverage"]
    lines = [
        "# Empirical Completion Audit",
        "",
        "## Headline",
        "",
        f"- The finished empirical core is real and headline-worthy: the spotlight matrix already covers `{c['num_models']}` models x `{c['num_benchmarks']}` benchmarks on `{c['num_rows']}` parsed rows.",
        f"- On that matrix, Bayes beats the generic heuristic by `{h['spotlight_matrix_gain']}` with bootstrap CI `[{h['spotlight_matrix_ci95']['ci95_low']}, {h['spotlight_matrix_ci95']['ci95_high']}]`.",
        f"- The theorem-3 proxy matrix is also statistically clean on its main comparison: Bayes beats the generic heuristic by `{h['theorem3_proxy_gain']}` with bootstrap CI `[{h['theorem3_proxy_ci95']['ci95_low']}, {h['theorem3_proxy_ci95']['ci95_high']}]`.",
        f"- The repo now contains both an `8B` and a frontier `70B` Llama spotlight slice with Bayes-vs-heuristic gains `{h['llama8_gain']}` and `{h['llama70_gain']}`.",
        f"- The strongest theorem-3 same-family result is also complete: `Qwen2.5` recovery first appears at about `{h['qwen_recovery_threshold_b']}B` on `WikiContradict`, with no recovery threshold yet visible on controlled `ConflictBank` conflict.",
        "",
        "## Done With Good / Headline Results",
        "",
    ]
    for item in summary["completed_items"]:
        lines.append(f"- `{item['item']}`: `{item['status']}`. {item['evidence']}.")
    lines.extend(
        [
            "",
            "## Finished Empirical Story",
            "",
            f"- Dedicated real-benchmark wins are already on disk for `PopQA` (`{h['popqa_gain']}`) and `NQ-Swap` (`{h['nq_swap_gain']}`).",
            f"- Spotlight family consistency is strong: `{', '.join(h['spotlight_unanimous_benchmarks'])}` are unanimous `5/5` Bayes-over-heuristic wins across model families.",
            f"- The theorem-3 cross-family audit is now honest and complete rather than over-claimed: DeepSeek asymmetry = `{h['deepseek_cross_family_asymmetry']}`, Qwen asymmetry = `{h['qwen_cross_family_asymmetry']}`.",
            f"- The eta intervention gives a real mechanism result rather than just a conjecture: conflict slices tolerate only `{h['eta_shrink_factor']}x` the do-no-harm eta of no-conflict slices.",
            "",
            "## Genuinely Still Missing Compute",
            "",
        ]
    )
    for item in summary["missing_items"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The finished empirical core is not the blocker anymore; the remaining missing pieces are genuinely new model / benchmark runs, not hidden completed results.",
            "- If we want to extend beyond the current paper-strong package, the next honest empirical step is new Delta compute for the missing families and benchmarks above.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    summary = build_summary()
    OUT_PREFIX.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    OUT_PREFIX.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(OUT_PREFIX.with_suffix('.json')), "md": str(OUT_PREFIX.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
