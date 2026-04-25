#!/usr/bin/env python3
"""Build a paper-facing headline bundle for the knowledge-arbitration project."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _theorem12_section(name: str, report_summary: dict[str, Any], result_payload: dict[str, Any]) -> dict[str, Any]:
    policies = result_payload["summary"]
    bayes = float(policies["bayes_proxy"]["mean_regret"])
    heuristic = float(policies["heuristic_adaptive"]["mean_regret"])
    fixed = float(policies["fixed_50"]["mean_regret"])
    simulated = float(policies["simulated_model"]["mean_regret"])
    always_context = float(policies["always_context"]["mean_regret"])
    always_parametric = float(policies["always_parametric"]["mean_regret"])
    headline = report_summary["headline"]
    oracle_vs_model = report_summary["oracle_vs_model"]
    return {
        "name": name,
        "num_series": int(report_summary["coverage"]["num_groups"]),
        "bayes_proxy_mean_regret": bayes,
        "heuristic_adaptive_mean_regret": heuristic,
        "fixed_50_mean_regret": fixed,
        "simulated_model_mean_regret": simulated,
        "always_context_mean_regret": always_context,
        "always_parametric_mean_regret": always_parametric,
        "bayes_proxy_accuracy": float(policies["bayes_proxy"]["accuracy"]),
        "bayes_proxy_ece": float(policies["bayes_proxy"]["ece"]),
        "bayes_vs_fixed_gain": round(fixed - bayes, 4),
        "bayes_vs_simulated_gain": round(simulated - bayes, 4),
        "bayes_vs_heuristic_gain": round(heuristic - bayes, 4),
        "bayes_vs_always_context_gain": round(always_context - bayes, 4),
        "bayes_vs_always_parametric_gain": round(always_parametric - bayes, 4),
        "mean_oracle_model_abs_gap": float(oracle_vs_model["mean_abs_gap"]),
        "mean_oracle_model_kl": float(oracle_vs_model["mean_kl_to_oracle"]),
        "mean_conflict_ece_delta": float(headline["mean_conflict_ece_delta"]),
        "mean_no_conflict_ece_delta": float(headline["mean_no_conflict_ece_delta"]),
    }


def build_bundle() -> dict[str, Any]:
    broad_report = _load_json(ROOT / "results/arbitration_real_headline_wave_reestimated_v3/report/arbitration_summary.json")
    broad_results = _load_json(ROOT / "results/arbitration_real_headline_wave_reestimated_v3/arbitration_real_headline_wave_benchmark_results.json")
    compact_report = _load_json(ROOT / "results/arbitration_conflict_headline_wave_reestimated_v3/report/arbitration_summary.json")
    compact_results = _load_json(ROOT / "results/arbitration_conflict_headline_wave_reestimated_v3/arbitration_conflict_headline_wave_benchmark_results.json")
    theorem3 = _load_json(ROOT / "docs/generated/theorem3_real_7b_final.json")

    theorem1 = _theorem12_section("broad_real_headline_wave_reestimated_v3", broad_report, broad_results)
    theorem2 = _theorem12_section("conflict_headline_wave_reestimated_v3", compact_report, compact_results)

    return {
        "project": "bayes_optimal_knowledge_arbitration",
        "headline": {
            "theorem_1": (
                "A Bayes-style reliability-aware arbitration rule beats the generic heuristic and "
                "sharply beats fixed trust policies across the broad real matrix."
            ),
            "theorem_2": (
                "Fixed trust policies are minimax-bad in practice: in the conflict-heavy wave, they "
                "incur much larger regret than the principled Bayes proxy."
            ),
            "theorem_3": (
                "Calibration failure peaks at an intermediate CoT budget, then partially self-corrects "
                "at very long CoT."
            ),
        },
        "theorem_1": theorem1,
        "theorem_2": theorem2,
        "theorem_3": theorem3,
    }


def build_markdown(bundle: dict[str, Any]) -> str:
    t1 = bundle["theorem_1"]
    t2 = bundle["theorem_2"]
    t3 = bundle["theorem_3"]
    lines = [
        "# Knowledge Arbitration Headline Bundle",
        "",
        "## Headline Claims",
        "",
        f"- Theorem 1: {bundle['headline']['theorem_1']}",
        f"- Theorem 2: {bundle['headline']['theorem_2']}",
        f"- Theorem 3: {bundle['headline']['theorem_3']}",
        "",
        "## Theorem 1",
        "",
        f"- Wave: `{t1['name']}` across `{t1['num_series']}` series",
        f"- `bayes_proxy` mean regret: `{t1['bayes_proxy_mean_regret']}`",
        f"- `bayes_proxy` accuracy / ECE: `{t1['bayes_proxy_accuracy']:.4f}` / `{t1['bayes_proxy_ece']:.4f}`",
        f"- `heuristic_adaptive` mean regret: `{t1['heuristic_adaptive_mean_regret']}`",
        f"- Bayes minus heuristic regret gap: `{t1['heuristic_adaptive_mean_regret'] - t1['bayes_proxy_mean_regret']:.4f}`",
        f"- `simulated_model` mean regret: `{t1['simulated_model_mean_regret']}`",
        f"- `fixed_50` mean regret: `{t1['fixed_50_mean_regret']}`",
        f"- `always_context` mean regret: `{t1['always_context_mean_regret']}`",
        f"- `always_parametric` mean regret: `{t1['always_parametric_mean_regret']}`",
        f"- Mean oracle-model absolute gap: `{t1['mean_oracle_model_abs_gap']}`",
        f"- Mean oracle-model KL: `{t1['mean_oracle_model_kl']}`",
        f"- Mean conflict / no-conflict ECE deltas: `{t1['mean_conflict_ece_delta']}` / `{t1['mean_no_conflict_ece_delta']}`",
        "",
        "## Theorem 2",
        "",
        f"- Wave: `{t2['name']}` across `{t2['num_series']}` series",
        f"- `bayes_proxy` mean regret: `{t2['bayes_proxy_mean_regret']}`",
        f"- `bayes_proxy` accuracy / ECE: `{t2['bayes_proxy_accuracy']:.4f}` / `{t2['bayes_proxy_ece']:.4f}`",
        f"- `heuristic_adaptive` mean regret: `{t2['heuristic_adaptive_mean_regret']}`",
        f"- Bayes minus heuristic regret gap: `{t2['heuristic_adaptive_mean_regret'] - t2['bayes_proxy_mean_regret']:.4f}`",
        f"- `simulated_model` mean regret: `{t2['simulated_model_mean_regret']}`",
        f"- `fixed_50` mean regret: `{t2['fixed_50_mean_regret']}`",
        f"- `always_context` mean regret: `{t2['always_context_mean_regret']}`",
        f"- `always_parametric` mean regret: `{t2['always_parametric_mean_regret']}`",
        f"- Mean oracle-model absolute gap: `{t2['mean_oracle_model_abs_gap']}`",
        f"- Mean oracle-model KL: `{t2['mean_oracle_model_kl']}`",
        f"- Mean conflict / no-conflict ECE deltas: `{t2['mean_conflict_ece_delta']}` / `{t2['mean_no_conflict_ece_delta']}`",
        "",
        "## Theorem 3",
        "",
        f"- Source run: `{t3['source_job']}` on `{t3['model']}`",
        f"- Total parsed rows: `{t3['num_rows']}`",
        "",
        "| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]

    for row in t3["rows"]:
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['gap_cot_0']:.4f} | {row['gap_cot_128']:.4f} | "
            f"{row['gap_cot_1024']:.4f} | {row['gap_delta_0_128']:.4f} | {row['gap_delta_128_1024']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Current Read",
            "",
            "- Theorem 1/2 are already paper-strong at the proxy-regret layer.",
            "- Theorem 3 does not support the old monotone statement.",
            "- The strongest current theorem-3 claim is the non-monotone intermediate-CoT overconfidence peak.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    out_dir = ROOT / "docs/generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle()
    dump_json(bundle, out_dir / "knowledge_arbitration_headline_bundle.json")
    (out_dir / "knowledge_arbitration_headline_bundle.md").write_text(
        build_markdown(bundle),
        encoding="utf-8",
    )
    print(json.dumps({"output_dir": str(out_dir)}, indent=2))


if __name__ == "__main__":
    main()
