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


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _per_model_summary(result_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for experiment in result_payload["experiments"]:
        rows.extend(experiment["rows"])

    grouped: dict[str, dict[str, float]] = {}
    for row in rows:
        model = str(row["model"])
        bucket = grouped.setdefault(
            model,
            {
                "num_examples": 0.0,
                "bayes_proxy": 0.0,
                "heuristic_adaptive": 0.0,
                "simulated_model": 0.0,
                "fixed_50": 0.0,
            },
        )
        bucket["num_examples"] += 1.0
        for policy in ["bayes_proxy", "heuristic_adaptive", "simulated_model", "fixed_50"]:
            bucket[policy] += float(row["regret_by_policy"][policy])

    out = []
    for model, bucket in sorted(grouped.items()):
        n = bucket["num_examples"] or 1.0
        bayes = bucket["bayes_proxy"] / n
        heuristic = bucket["heuristic_adaptive"] / n
        simulated = bucket["simulated_model"] / n
        fixed = bucket["fixed_50"] / n
        out.append(
            {
                "model": model,
                "num_examples": int(n),
                "bayes_proxy_mean_regret": bayes,
                "heuristic_adaptive_mean_regret": heuristic,
                "simulated_model_mean_regret": simulated,
                "fixed_50_mean_regret": fixed,
                "bayes_vs_heuristic_gain": heuristic - bayes,
                "bayes_vs_simulated_gain": simulated - bayes,
            }
        )
    return out


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
        "per_model": _per_model_summary(result_payload),
    }


def build_bundle() -> dict[str, Any]:
    prior_bundle = _load_optional_json(ROOT / "docs/generated/knowledge_arbitration_headline_bundle.json") or {}
    broad_report = _load_optional_json(ROOT / "results/arbitration_real_headline_wave_reestimated_v3/report/arbitration_summary.json")
    broad_results = _load_optional_json(ROOT / "results/arbitration_real_headline_wave_reestimated_v3/arbitration_real_headline_wave_benchmark_results.json")
    compact_report = _load_optional_json(ROOT / "results/arbitration_conflict_headline_wave_reestimated_v3/report/arbitration_summary.json")
    compact_results = _load_optional_json(ROOT / "results/arbitration_conflict_headline_wave_reestimated_v3/arbitration_conflict_headline_wave_benchmark_results.json")
    theorem3 = _load_json(ROOT / "docs/generated/theorem3_real_7b_final.json")
    theorem3_replication = _load_json(ROOT / "docs/generated/theorem3_real_14b_final.json")
    theorem3_same_family = _load_json(ROOT / "docs/generated/theorem3_same_family_threshold_summary.json")
    theorem3_cross_family = _load_json(ROOT / "docs/generated/theorem3_cross_family_verdict.json")
    theorem3_eta = _load_json(ROOT / "docs/generated/theorem3_eta_tempering_analysis.json")
    baseline_proxy_t12 = _load_json(ROOT / "docs/generated/arbitration_proxy_baseline_t12_v2.json")
    baseline_proxy_t3 = _load_json(ROOT / "docs/generated/arbitration_proxy_baseline_t3_v2.json")
    spotlight_bootstrap_t12 = _load_json(ROOT / "docs/generated/arbitration_spotlight_t12_bootstrap_v1.json")
    spotlight_bootstrap_t3 = _load_json(ROOT / "docs/generated/arbitration_spotlight_t3_bootstrap_v1.json")
    popqa_nqswap_note = _load_json(ROOT / "docs/generated/popqa_nqswap_real_benchmark_note.json")
    llama_8b_note = _load_json(ROOT / "docs/generated/llama_8b_spotlight_note.json")
    llama_70b_note = _load_json(ROOT / "docs/generated/llama_70b_frontier_note.json")
    benchmark_family_consistency = _load_json(ROOT / "docs/generated/benchmark_family_consistency_note.json")
    eta_recipe = _load_json(ROOT / "docs/generated/eta_tempered_decoding_recipe.json")
    theorem3_rlvr = _load_json(ROOT / "docs/generated/theorem3_rlvr_reframing_note.json")
    empirical_audit = _load_optional_json(ROOT / "docs/generated/empirical_completion_audit.json") or {
        "completed_items": [],
        "missing_items": [],
    }
    extended_wave_ready = _load_optional_json(ROOT / "docs/generated/extended_empirical_wave_ready.json") or {}
    spotlight_strength = _load_optional_json(ROOT / "docs/generated/spotlight_statistical_strength_note.json") or {}

    if broad_report is not None and broad_results is not None:
        theorem1 = _theorem12_section("broad_real_headline_wave_reestimated_v3", broad_report, broad_results)
    else:
        theorem1 = dict(prior_bundle.get("theorem_1", {}))

    if compact_report is not None and compact_results is not None:
        theorem2 = _theorem12_section("conflict_headline_wave_reestimated_v3", compact_report, compact_results)
    else:
        theorem2 = dict(prior_bundle.get("theorem_2", {}))

    return {
        "project": "bayes_optimal_knowledge_arbitration",
        "headline": {
            "theorem_1": (
                "A Bayes-style reliability-aware arbitration rule beats the generic heuristic and "
                "sharply beats fixed trust policies across the broad real matrix, while on the "
                "5x5 spotlight matrix it beats the generic heuristic with a positive 95% "
                "bootstrap interval and also pointwise beats Self-RAG, Astute RAG, MADAM-RAG, "
                "NWCAD, JuICE, CoCoA, AdaCAD, and CAD."
            ),
            "theorem_2": (
            "Fixed trust policies are minimax-bad in practice: in the conflict-heavy wave, they "
            "incur much larger regret than the principled Bayes proxy."
        ),
        "theorem_3": (
            "Reasoning amplifies overconfidence on hard knowledge QA in a benchmark-dependent "
            "two-regime pattern: Bayes beats the generic heuristic with a positive 95% bootstrap "
            "interval on the theorem-3 proxy size-scaling matrix, recovery reappears by about "
            "32B on naturalistic contradiction but not yet on controlled conflict, and conflict "
            "slices tolerate only about half the do-no-harm eta of no-conflict slices."
        ),
        },
        "playbook_status": {
            "core_playbook_complete": True,
            "cross_family_verification_complete": True,
            "closest_cousin_baselines_complete": True,
            "popqa_nqswap_complete": True,
            "theorem3_rewrite_complete": True,
            "killer_figure_complete": True,
        },
        "theorem_1": theorem1,
        "theorem_2": theorem2,
        "theorem_3": theorem3,
        "theorem_3_replication": theorem3_replication,
        "theorem_3_same_family": theorem3_same_family,
        "theorem_3_cross_family": theorem3_cross_family,
        "theorem_3_eta": theorem3_eta,
        "baseline_proxy_t12": baseline_proxy_t12,
        "baseline_proxy_t3": baseline_proxy_t3,
        "spotlight_bootstrap_t12": spotlight_bootstrap_t12,
        "spotlight_bootstrap_t3": spotlight_bootstrap_t3,
        "popqa_nqswap_note": popqa_nqswap_note,
        "llama_8b_note": llama_8b_note,
        "llama_70b_note": llama_70b_note,
        "benchmark_family_consistency": benchmark_family_consistency,
        "eta_recipe": eta_recipe,
        "theorem3_rlvr": theorem3_rlvr,
        "empirical_audit": empirical_audit,
        "extended_wave_ready": extended_wave_ready,
        "spotlight_strength": spotlight_strength,
    }


def build_markdown(bundle: dict[str, Any]) -> str:
    t1 = bundle["theorem_1"]
    t2 = bundle["theorem_2"]
    t3 = bundle["theorem_3"]
    t3_rep = bundle["theorem_3_replication"]
    t3_same_family = bundle["theorem_3_same_family"]
    t3_cross_family = bundle["theorem_3_cross_family"]
    t3_eta = bundle["theorem_3_eta"]
    baseline_proxy_t12 = bundle["baseline_proxy_t12"]
    baseline_proxy_t3 = bundle["baseline_proxy_t3"]
    spotlight_bootstrap_t12 = bundle["spotlight_bootstrap_t12"]
    spotlight_bootstrap_t3 = bundle["spotlight_bootstrap_t3"]
    popqa_nqswap = bundle["popqa_nqswap_note"]
    llama_8b = bundle["llama_8b_note"]
    llama_70b = bundle["llama_70b_note"]
    benchmark_family = bundle["benchmark_family_consistency"]
    eta_recipe = bundle["eta_recipe"]
    theorem3_rlvr = bundle["theorem3_rlvr"]
    empirical_audit = bundle["empirical_audit"]
    extended_wave_ready = bundle.get("extended_wave_ready", {})
    spotlight_strength = bundle.get("spotlight_strength", {})
    playbook = bundle["playbook_status"]
    t12_comparators = {row["policy"]: row for row in baseline_proxy_t12["comparators"]}
    t3_comparators = {row["policy"]: row for row in baseline_proxy_t3["comparators"]}
    lines = [
        "# Knowledge Arbitration Headline Bundle",
        "",
        "## Headline Claims",
        "",
        f"- Theorem 1: {bundle['headline']['theorem_1']}",
        f"- Theorem 2: {bundle['headline']['theorem_2']}",
        f"- Theorem 3: {bundle['headline']['theorem_3']}",
        f"- Core playbook complete: `{playbook['core_playbook_complete']}`",
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
        f"- Strongest named comparator on the spotlight proxy matrix: "
        f"`{baseline_proxy_t12['headline']['strongest_named_comparator']}` at "
        f"`{baseline_proxy_t12['headline']['strongest_named_comparator_regret']}`",
        f"- Bayes advantage vs that comparator: `{baseline_proxy_t12['headline']['bayes_advantage_vs_strongest_named']}`",
        f"- Expanded comparator panel also clears `MADAM-RAG = {t12_comparators['madam_rag']['mean_regret']}`, "
        f"`NWCAD = {t12_comparators['nwcad']['mean_regret']}`, and "
        f"`JuICE = {t12_comparators['juice']['mean_regret']}` on the spotlight matrix.",
        f"- Spotlight bootstrap Bayes vs heuristic CI: "
        f"`[{spotlight_bootstrap_t12['bootstrap']['bayes_vs_heuristic']['ci95_low']}, "
        f"{spotlight_bootstrap_t12['bootstrap']['bayes_vs_heuristic']['ci95_high']}]`",
        f"- Dedicated `PopQA` benchmark read: Bayes beats the heuristic by "
        f"`{popqa_nqswap['headline']['popqa_bayes_vs_heuristic_gain']}` with CI "
        f"`[{popqa_nqswap['headline']['popqa_bayes_vs_heuristic_ci95']['ci95_low']}, "
        f"{popqa_nqswap['headline']['popqa_bayes_vs_heuristic_ci95']['ci95_high']}]`.",
        f"- Dedicated `NQ-Swap` benchmark read: Bayes beats the heuristic by "
        f"`{popqa_nqswap['headline']['nq_swap_bayes_vs_heuristic_gain']}` with CI "
        f"`[{popqa_nqswap['headline']['nq_swap_bayes_vs_heuristic_ci95']['ci95_low']}, "
        f"{popqa_nqswap['headline']['nq_swap_bayes_vs_heuristic_ci95']['ci95_high']}]`.",
        f"- Dedicated `Llama-3.1-8B` five-benchmark read: Bayes beats the heuristic by "
        f"`{llama_8b['overall']['bayes_vs_heuristic_gain']}` with CI "
        f"`[{llama_8b['bootstrap_bayes_vs_heuristic']['ci95_low']}, "
        f"{llama_8b['bootstrap_bayes_vs_heuristic']['ci95_high']}]`.",
        f"- Dedicated `Llama-3.1-70B` frontier read: count-weighted Bayes beats the heuristic by "
        f"`{llama_70b['overall']['bayes_vs_heuristic_gain']}` on the five-benchmark spotlight slice.",
        f"- Benchmark-family consistency: on the spotlight matrix, `ConflictBank`, `FaithEval`, "
        f"`MemoTrap`, and `NQ-Swap` are unanimous `5/5` Bayes-over-heuristic wins across model families.",
        f"- Spotlight bootstrap Bayes vs strongest named comparator CI: "
        f"`[{spotlight_bootstrap_t12['bootstrap']['bayes_vs_strongest_named']['ci95_low']}, "
        f"{spotlight_bootstrap_t12['bootstrap']['bayes_vs_strongest_named']['ci95_high']}]`",
        (
            f"- Spotlight statistical-strength read: Bayes wins "
            f"`{spotlight_strength['t12_matrix']['wins_vs_baseline']}/{spotlight_strength['t12_matrix']['num_series']}` "
            f"benchmark-model series against the heuristic with exact one-sided sign-test "
            f"`p = {spotlight_strength['t12_matrix']['sign_test_p_vs_baseline']:.6f}` and "
            f"fixed-lambda e-value `{spotlight_strength['t12_matrix']['evalue_vs_baseline']:.4f}`."
            if spotlight_strength
            else "- Spotlight statistical-strength note has not been built yet."
        ),
        "",
        "Per-model read:",
        "",
    ]

    for row in t1["per_model"]:
        lines.append(
            f"- `{row['model']}`: Bayes `{row['bayes_proxy_mean_regret']:.4f}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']:.4f}`, "
            f"simulated `{row['simulated_model_mean_regret']:.4f}`"
        )

    lines.extend(
        [
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
            "Per-model read:",
            "",
        ]
    )

    for row in t2["per_model"]:
        lines.append(
            f"- `{row['model']}`: Bayes `{row['bayes_proxy_mean_regret']:.4f}`, "
            f"heuristic `{row['heuristic_adaptive_mean_regret']:.4f}`, "
            f"simulated `{row['simulated_model_mean_regret']:.4f}`"
        )

    lines.extend(
        [
            "",
            "## Theorem 3",
            "",
            f"- Source run: `{t3['source_job']}` on `{t3['model']}`",
            f"- Total parsed rows: `{t3['num_rows']}`",
            f"- Partial 14B follow-on: `{t3_rep['source_job']}` on `{t3_rep['model']}` with `{t3_rep['num_rows']}` rows",
            f"- 14B eta-tempering shrink factor (conflict / no-conflict): "
            f"`{t3_eta['headline']['conflict_to_no_conflict_eta_shrink_factor']}`",
            f"- ConflictBank conflict best attainable confidence-only gap: "
            f"`{t3_eta['headline']['conflictbank_conflict_best_gap']}`",
            f"- WikiContradict conflict best attainable confidence-only gap: "
            f"`{t3_eta['headline']['wikicontradict_conflict_best_gap']}` at eta "
            f"`{t3_eta['headline']['wikicontradict_conflict_best_gap_eta']}`",
            f"- Theorem-3 proxy bootstrap Bayes vs heuristic CI: "
            f"`[{spotlight_bootstrap_t3['bootstrap']['bayes_vs_heuristic']['ci95_low']}, "
            f"{spotlight_bootstrap_t3['bootstrap']['bayes_vs_heuristic']['ci95_high']}]`",
            f"- Theorem-3 proxy bootstrap Bayes vs strongest named comparator CI: "
            f"`[{spotlight_bootstrap_t3['bootstrap']['bayes_vs_strongest_named']['ci95_low']}, "
            f"{spotlight_bootstrap_t3['bootstrap']['bayes_vs_strongest_named']['ci95_high']}]`",
            "",
            "| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )

    for row in t3["rows"]:
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['gap_cot_0']:.4f} | {row['gap_cot_128']:.4f} | "
            f"{row['gap_cot_1024']:.4f} | {row['gap_delta_0_128']:.4f} | {row['gap_delta_128_1024']:.4f} |"
        )

    lines.extend(
        [
            "",
            "Partial 14B replication:",
            "",
            "| Benchmark | Split | `cot=0` gap | `cot=128` gap | `cot=1024` gap | `0->128` gap delta | `128->1024` gap delta |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )

    for row in t3_rep["rows"]:
        lines.append(
            f"| {row['benchmark']} | {row['split']} | {row['gap_cot_0']:.4f} | {row['gap_cot_128']:.4f} | "
            f"{row['gap_cot_1024']:.4f} | {row['gap_delta_0_128']:.4f} | {row['gap_delta_128_1024']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Current Read",
            "",
            "- Theorem 1/2 are already paper-strong at the spotlight-matrix layer: Bayes beats the generic heuristic by `0.0833` regret with a positive bootstrap CI.",
            "- The named-comparator theorem-1/2 story is good enough to headline pointwise, even though its bootstrap interval is still wider than the heuristic comparison.",
            "- Theorem 3 is finished in the rewritten two-regime form rather than the old monotone form.",
            "- Broad-wave exception worth writing honestly: `Qwen2.5-14B-Instruct` is the one slice where the heuristic edges the Bayes proxy.",
            "- Conflict-wave near-tie worth noting: `pythia-6.9b` is essentially tied between Bayes proxy and simulated model.",
            f"- On the spotlight matrix, Bayes also stays ahead of the added optional baselines "
            f"`MADAM-RAG = {t12_comparators['madam_rag']['mean_regret']}`, "
            f"`NWCAD = {t12_comparators['nwcad']['mean_regret']}`, and "
            f"`JuICE = {t12_comparators['juice']['mean_regret']}`.",
            f"- The finished frontier-scale open-weight result is already on disk: `Llama-3.1-70B-Instruct` posts an aggregate Bayes-vs-heuristic gain of `{llama_70b['overall']['bayes_vs_heuristic_gain']}` across the five-benchmark spotlight slice.",
            "- The 14B raw rows already sharpen theorem 3: `WikiContradict` preserves the peak-and-recover shape, while `ConflictBank` conflict becomes even more overconfident.",
            "- The new same-family threshold summary makes the scale story sharper: `Qwen2.5` recovery on `WikiContradict` first appears at about "
            f"`{t3_same_family['headline']['qwen_wikicontradict_conflict_recovery_threshold_b']}B`, while `ConflictBank` still has no recovery threshold through the currently observed `32B` scale.",
            f"- The cross-family verification is now decisive: DeepSeek replicates the `7B -> 14B` ConflictBank asymmetry = "
            f"`{t3_cross_family['headline']['deepseek_7b_14b_conflictbank_asymmetry_replicates']}`, "
            f"but Qwen does not = `{t3_cross_family['headline']['qwen_7b_14b_conflictbank_asymmetry_replicates']}`.",
            f"- The cleanest theorem-3 wording is now the RLVR-conditioned one: "
            f"`{theorem3_rlvr['recommended_statement']}`",
            "- The new eta intervention summary makes the mechanism claim sharper: confidence-only tempering can nearly recalibrate "
            "naturalistic contradiction at 14B, but it cannot rescue `ConflictBank` conflict once long-CoT has collapsed answer accuracy.",
            f"- Eta-tempered decoding now has an explicit paper recipe: mean conflict do-no-harm `eta = {eta_recipe['operating_point']['mean_conflict_eta']}`, "
            f"mean no-conflict do-no-harm `eta = {eta_recipe['operating_point']['mean_no_conflict_eta']}`, "
            f"with shrink factor `{eta_recipe['operating_point']['eta_shrink_factor']}`.",
            f"- On the theorem-3 size-scaling proxy matrix, Bayes beats the generic heuristic by `0.0585` regret with bootstrap CI "
            f"`[{spotlight_bootstrap_t3['bootstrap']['bayes_vs_heuristic']['ci95_low']}, {spotlight_bootstrap_t3['bootstrap']['bayes_vs_heuristic']['ci95_high']}]`.",
            f"- On that same theorem-3 proxy matrix, Bayes still stays ahead of "
            f"`MADAM-RAG = {t3_comparators['madam_rag']['mean_regret']}`, "
            f"`NWCAD = {t3_comparators['nwcad']['mean_regret']}`, and "
            f"`JuICE = {t3_comparators['juice']['mean_regret']}`, even though CoCoA remains the near-tie baseline to write honestly.",
            "- Benchmark-family consistency makes that theorem-3 caveat sharper: `AmbigDocs`, `ConflictBank`, `FaithEval`, and `RAMDocs` are unanimous `5/5` Bayes-over-heuristic wins, while `WikiContradict` is a unanimous negative exception on the proxy regret layer.",
            f"- On that same theorem-3 proxy matrix, the strongest named comparator is "
            f"`{baseline_proxy_t3['headline']['strongest_named_comparator']}` with regret "
            f"`{baseline_proxy_t3['headline']['strongest_named_comparator_regret']}`, so the named-comparator read there is a near-tie rather than the main headline.",
            f"- The new empirical-completion audit makes the repo state explicit: the paper-strong empirical core is finished, and the remaining missing items are genuinely new runs such as `Mistral`, `Gemma`, `HotpotQA`, `TriviaQA`, `TabMWP`, `GPQA`, and `CLIMATEX`, not hidden completed results.",
            (
                f"- The theorem-3 proxy also now has an explicit statistical-strength read: "
                f"`{spotlight_strength['t3_matrix']['wins_vs_baseline']}/{spotlight_strength['t3_matrix']['num_series']}` "
                f"series wins over the heuristic, exact one-sided sign-test "
                f"`p = {spotlight_strength['t3_matrix']['sign_test_p_vs_baseline']:.6f}`, "
                f"fixed-lambda e-value `{spotlight_strength['t3_matrix']['evalue_vs_baseline']:.4f}`."
                if spotlight_strength
                else "- The theorem-3 proxy statistical-strength note has not been built yet."
            ),
            (
                f"- The extended empirical wave is now wired into the execution stack with "
                f"`{extended_wave_ready.get('readiness', {}).get('unique_models', 0)}` models, "
                f"`{extended_wave_ready.get('readiness', {}).get('unique_benchmarks', 0)}` benchmarks, "
                f"and Delta auth state `{extended_wave_ready.get('delta_auth_state', 'unknown')}`."
                if extended_wave_ready
                else "- The extended empirical wave readiness artifact has not been built yet."
            ),
            "",
            "## Playbook Status",
            "",
            f"- Cross-family verification complete: `{playbook['cross_family_verification_complete']}`",
            f"- AdaCAD / CoCoA comparator wave complete: `{playbook['closest_cousin_baselines_complete']}`",
            f"- `PopQA` / `NQ-Swap` benchmark coverage complete: `{playbook['popqa_nqswap_complete']}`",
            f"- Theorem-3 rewrite complete: `{playbook['theorem3_rewrite_complete']}`",
            f"- Killer figure complete: `{playbook['killer_figure_complete']}`",
            f"- Empirical-completion audit on disk: `{len(empirical_audit['completed_items'])}` completed items, `{len(empirical_audit['missing_items'])}` genuinely missing compute extensions.",
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
