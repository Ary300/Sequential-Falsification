#!/usr/bin/env python3
"""Build empirical follow-up notes for the Paper 2 review weaknesses."""

from __future__ import annotations

import json
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.loaders import load_arbitration_dataset  # noqa: E402
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def _normalize(text: str) -> str:
    return " ".join(match.group(0).lower() for match in TOKEN_RE.finditer(text or ""))


def _contains_any(snippet: str, answers: list[str]) -> bool:
    hay = _normalize(snippet)
    return any((needle := _normalize(answer)) and needle in hay for answer in answers)


def _bootstrap_interval(values: list[float]) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    ordered = sorted(values)
    low_idx = max(0, int(0.025 * (len(ordered) - 1)))
    high_idx = min(len(ordered) - 1, int(0.975 * (len(ordered) - 1)))
    return ordered[low_idx], ordered[high_idx]


def _bootstrap_mean_interval(values: list[float], *, seed: int = 0, num_boot: int = 10000) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = []
    for _ in range(num_boot):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(statistics.mean(sample))
    return _bootstrap_interval(means)


def build_conditional_independence_note() -> dict[str, object]:
    payload: dict[str, object] = {"diagnostic": "bounded_conflict_context_verbatim_sample", "datasets": {}}
    dataset_specs = {"wikicontradict": 253, "conflictbank": 256}
    for benchmark, max_examples in dataset_specs.items():
        rows = load_arbitration_dataset(benchmark, max_examples=max_examples)
        total = gold = conflict = both = 0
        family_counts: dict[str, list[int]] = {}
        for row in rows:
            meta = row.get("metadata", {}) or {}
            context_text = str(meta.get("conflict_context_text") or "")
            answers = [str(item) for item in row.get("answers", []) if str(item).strip()]
            conflict_answers = [str(item) for item in meta.get("conflict_context_answers", []) if str(item).strip()]
            gold_hit = _contains_any(context_text, answers)
            conflict_hit = _contains_any(context_text, conflict_answers)
            fam = str(meta.get("conflict_family") or "all")
            family_counts.setdefault(fam, [0, 0, 0, 0])
            family_counts[fam][0] += 1
            family_counts[fam][1] += int(gold_hit)
            family_counts[fam][2] += int(conflict_hit)
            family_counts[fam][3] += int(gold_hit and conflict_hit)
            total += 1
            gold += int(gold_hit)
            conflict += int(conflict_hit)
            both += int(gold_hit and conflict_hit)
        payload["datasets"][benchmark] = {
            "rows": total,
            "gold_verbatim_rate": round(gold / total, 4) if total else 0.0,
            "conflict_verbatim_rate": round(conflict / total, 4) if total else 0.0,
            "both_verbatim_rate": round(both / total, 4) if total else 0.0,
            "family_breakdown": {
                fam: {
                    "rows": count,
                    "gold_verbatim_rate": round(g / count, 4) if count else 0.0,
                    "conflict_verbatim_rate": round(c / count, 4) if count else 0.0,
                    "both_verbatim_rate": round(b / count, 4) if count else 0.0,
                }
                for fam, (count, g, c, b) in family_counts.items()
            },
        }
    return payload


def _load_regret_rows() -> list[dict[str, object]]:
    summary_path = ROOT / "results/arbitration_spotlight_t12_benchmark_v2/report/arbitration_summary.json"
    return json.loads(summary_path.read_text(encoding="utf-8"))["regret"]["rows"]


def build_comparator_note() -> dict[str, object]:
    rows = _load_regret_rows()
    series_map: dict[str, dict[str, float]] = {}
    for row in rows:
        series_map.setdefault(str(row["series"]), {})[str(row["policy"])] = float(row["mean_regret"])

    payload = {"comparators": {}}
    for baseline in ["adacad", "cocoa", "self_rag", "heuristic_adaptive"]:
        gaps = []
        wins = 0
        total = 0
        benchmark_map: dict[str, list[float]] = {}
        for series, policies in series_map.items():
            if "bayes_proxy" not in policies or baseline not in policies:
                continue
            benchmark = series.split("::", 1)[0]
            gap = policies[baseline] - policies["bayes_proxy"]
            gaps.append(gap)
            wins += int(gap > 0)
            total += 1
            benchmark_map.setdefault(benchmark, []).append(gap)
        low, high = _bootstrap_mean_interval(gaps, seed=17 + total)
        payload["comparators"][baseline] = {
            "mean_gap": round(statistics.mean(gaps), 4) if gaps else 0.0,
            "ci95": [round(low, 4), round(high, 4)],
            "wins": wins,
            "total": total,
            "benchmark_breakdown": {
                benchmark: {
                    "mean_gap": round(statistics.mean(vals), 4),
                    "wins": sum(val > 0 for val in vals),
                    "total": len(vals),
                }
                for benchmark, vals in sorted(benchmark_map.items())
            },
        }
    return payload


def build_closed_model_note() -> dict[str, object]:
    summary_path = ROOT / "results/delta_knowledge_arbitration_extended_wave/arbitration_spotlight_extended_api_slice__seed=42/report/arbitration_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    regret_rows = summary["regret"]["rows"]
    oracle_rows = summary["oracle_vs_model"]["rows"]
    cal_rows = summary["calibration_by_cot"]["trend_rows"]

    models = sorted({row["series"].split("::", 1)[1] for row in regret_rows})
    benchmarks = sorted({row["series"].split("::", 1)[0] for row in regret_rows})
    payload: dict[str, object] = {
        "models": models,
        "benchmarks": benchmarks,
        "methodology": "benchmark_backed_proxy_scaffold_not_api_native_logprobs",
        "per_model_regret": {},
        "conflict_oracle_gap_rows": [],
        "calibration_rows": [],
    }
    for model in models:
        model_rows = [row for row in regret_rows if row["series"].endswith(f"::{model}")]
        policy_map = {str(row["policy"]): float(row["mean_regret"]) for row in model_rows}
        payload["per_model_regret"][model] = {
            "bayes_proxy": round(policy_map.get("bayes_proxy", 0.0), 4),
            "heuristic_adaptive": round(policy_map.get("heuristic_adaptive", 0.0), 4),
            "cocoa": round(policy_map.get("cocoa", 0.0), 4),
            "self_rag": round(policy_map.get("self_rag", 0.0), 4),
            "best_policy": min(policy_map, key=policy_map.get) if policy_map else "unknown",
        }
    for row in oracle_rows:
        annotation = str(row.get("annotation") or "")
        if str(row.get("condition")) != "conflict_context":
            continue
        payload["conflict_oracle_gap_rows"].append(
            {
                "slice": annotation,
                "oracle_p_context": round(float(row["oracle_context_probability"]), 4),
                "model_p_context": round(float(row["model_context_probability"]), 4),
                "abs_gap": round(float(row["abs_gap"]), 4),
                "count": int(row["count"]),
            }
        )
    for row in cal_rows:
        payload["calibration_rows"].append(
            {
                "benchmark": str(row["benchmark"]),
                "bucket": str(row["condition_bucket"]),
                "ece_delta": round(float(row["ece_delta"]), 4),
                "brier_delta": round(float(row["brier_delta"]), 4),
            }
        )
    return payload


def build_eta_binding_note() -> dict[str, object]:
    note_path = ROOT / "docs/generated/theorem3_eta_tempered_method_result.md"
    text = note_path.read_text(encoding="utf-8")
    numbers = {}
    for label, pattern in {
        "selected_eta": r"Selected eta: `([^`]+)`",
        "baseline_brier": r"Calibration baseline Brier at eta=1: `([^`]+)`",
        "selected_brier": r"Calibration selected Brier: `([^`]+)`",
        "baseline_accuracy": r"Eval baseline accuracy / confidence / gap at eta=1: `([^`]+)` / `([^`]+)` / `([^`]+)`",
        "tempered_accuracy": r"Eval tempered accuracy / confidence / gap: `([^`]+)` / `([^`]+)` / `([^`]+)`",
    }.items():
        match = re.search(pattern, text)
        if match:
            numbers[label] = match.groups()
    return {
        "selected_eta": float(numbers["selected_eta"][0]),
        "baseline_brier": float(numbers["baseline_brier"][0]),
        "selected_brier": float(numbers["selected_brier"][0]),
        "baseline_accuracy": float(numbers["baseline_accuracy"][0]),
        "baseline_confidence": float(numbers["baseline_accuracy"][1]),
        "baseline_gap": float(numbers["baseline_accuracy"][2]),
        "tempered_accuracy": float(numbers["tempered_accuracy"][0]),
        "tempered_confidence": float(numbers["tempered_accuracy"][1]),
        "tempered_gap": float(numbers["tempered_accuracy"][2]),
    }


def _write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    conditional = build_conditional_independence_note()
    comparators = build_comparator_note()
    closed_model = build_closed_model_note()
    eta_binding = build_eta_binding_note()

    out_dir = ROOT / "docs/generated"
    _write_json(out_dir / "conditional_independence_diagnostic.json", conditional)
    _write_json(out_dir / "spotlight_comparator_strength_note.json", comparators)
    _write_json(out_dir / "closed_model_api_breakdown.json", closed_model)
    _write_json(out_dir / "eta_do_no_harm_binding_note.json", eta_binding)

    _write_markdown(
        out_dir / "conditional_independence_diagnostic.md",
        "\n".join(
            [
                "# Conditional-Independence Diagnostic",
                "",
                "This note puts numbers on the reviewer concern that some conflict passages may contain the answer verbatim, making a scalar reliability variable do more work than advertised.",
                "",
                "These are bounded diagnostic samples rather than the full corpora, but they are large enough to show the benchmark geometry cleanly.",
                "",
                "## Headline",
                "",
                f"- `WikiContradict` sampled rows: `{conditional['datasets']['wikicontradict']['rows']}`",
                f"- `WikiContradict` gold-answer verbatim rate in conflict context: `{conditional['datasets']['wikicontradict']['gold_verbatim_rate']}`",
                f"- `WikiContradict` conflict-answer verbatim rate in conflict context: `{conditional['datasets']['wikicontradict']['conflict_verbatim_rate']}`",
                f"- `ConflictBank` sampled rows: `{conditional['datasets']['conflictbank']['rows']}`",
                f"- `ConflictBank` gold-answer verbatim rate in conflict context: `{conditional['datasets']['conflictbank']['gold_verbatim_rate']}`",
                f"- `ConflictBank` conflict-answer verbatim rate in conflict context: `{conditional['datasets']['conflictbank']['conflict_verbatim_rate']}`",
                "",
                "## Read",
                "",
                "- `WikiContradict` is mixed: the gold answer appears verbatim in the conflict passage often enough that scalar-reliability-only assumptions should be read cautiously there.",
                "- `ConflictBank` shows the opposite geometry: the conflicting answer is almost always written explicitly in the conflict evidence, while the gold answer is rarely verbatim. That makes the benchmark a particularly strong stress test of whether the arbitration rule can discount high-salience but wrong contextual evidence.",
            ]
        ),
    )

    _write_markdown(
        out_dir / "spotlight_comparator_strength_note.md",
        "\n".join(
            [
                "# Spotlight Comparator Strength Note",
                "",
                "This note answers the review concern that the strongest headline may be inflated by comparing primarily against the generic heuristic.",
                "",
                "## Headline",
                "",
                f"- Bayes vs `AdaCAD`: mean regret gap `{comparators['comparators']['adacad']['mean_gap']}`, CI `{comparators['comparators']['adacad']['ci95']}`, wins `{comparators['comparators']['adacad']['wins']}/{comparators['comparators']['adacad']['total']}`",
                f"- Bayes vs `CoCoA`: mean regret gap `{comparators['comparators']['cocoa']['mean_gap']}`, CI `{comparators['comparators']['cocoa']['ci95']}`, wins `{comparators['comparators']['cocoa']['wins']}/{comparators['comparators']['cocoa']['total']}`",
                f"- Bayes vs `Self-RAG`: mean regret gap `{comparators['comparators']['self_rag']['mean_gap']}`, CI `{comparators['comparators']['self_rag']['ci95']}`, wins `{comparators['comparators']['self_rag']['wins']}/{comparators['comparators']['self_rag']['total']}`",
                "",
                "## Read",
                "",
                "- The AdaCAD comparison is real and materially stronger than the Self-RAG comparison; if the paper wants one body-facing decoder-level comparator, AdaCAD is the cleanest choice.",
                "- The Self-RAG comparison is positive overall but clearly the weakest of the powered head-to-heads, largely because of the known PopQA reversal.",
            ]
        ),
    )

    oracle_rows = closed_model["conflict_oracle_gap_rows"][:9]
    _write_markdown(
        out_dir / "closed_model_api_breakdown.md",
        "\n".join(
            [
                "# Closed-Model API Breakdown",
                "",
                "This note makes the closed-model slice explicit instead of leaving it as a thin appendix claim.",
                "",
                "## Methodology",
                "",
                "- Current slice type: `benchmark-backed proxy scaffold`, not direct API-native token logprobs.",
                "- Closed models covered: `GPT-4o-mini`, `Claude-3.5-Haiku`, `Gemini-1.5-Flash`.",
                "- Benchmarks covered in the slice: `conflictbank`, `faitheval`, `popqa`, `triviaqa`.",
                "",
                "## Per-Model Regret",
                "",
            ]
            + [
                f"- `{model}`: Bayes `{vals['bayes_proxy']}`, heuristic `{vals['heuristic_adaptive']}`, CoCoA `{vals['cocoa']}`, best policy `{vals['best_policy']}`"
                for model, vals in closed_model["per_model_regret"].items()
            ]
            + [
                "",
                "## Conflict Oracle-vs-Model Rows",
                "",
            ]
            + [
                f"- `{row['slice']}`: oracle `P(context)={row['oracle_p_context']}`, model `P(context)={row['model_p_context']}`, abs gap `{row['abs_gap']}`, count `{row['count']}`"
                for row in oracle_rows
            ]
            + [
                "",
                "## Read",
                "",
                "- This slice is useful as a deployment-adjacent proxy sanity check, but it should not be described as if we had direct access to closed-model posterior factors.",
                "- The strongest empirical fact here is actually negative: on this proxy scaffold, `always_parametric` is the best policy overall, which means the slice is not a clean headline win for the geometric mixture.",
            ]
        ),
    )

    _write_markdown(
        out_dir / "eta_do_no_harm_binding_note.md",
        "\n".join(
            [
                "# Eta Do-No-Harm Binding Note",
                "",
                "This note answers the reviewer question about why the worst theorem-3 cell selects `eta=0` while accuracy improves sharply.",
                "",
                "## Headline",
                "",
                f"- Selected eta: `{eta_binding['selected_eta']}`",
                f"- Baseline accuracy / Brier / gap at `eta=1`: `{eta_binding['baseline_accuracy']}` / `{eta_binding['baseline_brier']}` / `{eta_binding['baseline_gap']}`",
                f"- Tempered accuracy / Brier / gap at selected eta: `{eta_binding['tempered_accuracy']}` / `{eta_binding['selected_brier']}` / `{eta_binding['tempered_gap']}`",
                "",
                "## Read",
                "",
                "- On this cell the do-no-harm constraint does not bind against a better-Brier-but-worse-accuracy eta. Instead, the best point is already `eta=0`, which improves both accuracy and Brier.",
                "- The correct interpretation is therefore not that the fallback protected accuracy from an aggressive calibration fix; it is that the conflict-conditioned long-CoT posterior is so bad that collapsing toward the closed-book prior is simultaneously a better answer policy and a better calibration policy.",
            ]
        ),
    )

    _write_markdown(
        out_dir / "paper2_empirical_weakness_fixes.md",
        "\n".join(
            [
                "# Paper 2 Empirical Weakness Fixes",
                "",
                "This note consolidates the empirical follow-ups that can be landed immediately while the matched-base GRPO/DPO and RLCR jobs remain queued.",
                "",
                "## New empirical answers",
                "",
                f"- `AdaCAD` head-to-head is now explicit: mean Bayes advantage `{comparators['comparators']['adacad']['mean_gap']}`, CI `{comparators['comparators']['adacad']['ci95']}`.",
                f"- `Self-RAG` is now explicitly marked as the weakest powered comparator: mean gap `{comparators['comparators']['self_rag']['mean_gap']}`, CI `{comparators['comparators']['self_rag']['ci95']}`, wins `{comparators['comparators']['self_rag']['wins']}/{comparators['comparators']['self_rag']['total']}`.",
                f"- Conditional-independence diagnostic now has numbers: sampled `WikiContradict` conflict passages contain the gold answer verbatim at rate `{conditional['datasets']['wikicontradict']['gold_verbatim_rate']}`, while sampled `ConflictBank` conflict passages contain the conflicting answer verbatim at rate `{conditional['datasets']['conflictbank']['conflict_verbatim_rate']}` and the gold answer only `{conditional['datasets']['conflictbank']['gold_verbatim_rate']}`.",
                f"- Closed-model slice is now broken down per benchmark/model and explicitly labeled as a proxy scaffold rather than a direct API-logprob experiment.",
                f"- The do-no-harm `eta=0` case is now diagnosed directly: baseline accuracy `{eta_binding['baseline_accuracy']}` improves to `{eta_binding['tempered_accuracy']}` while Brier drops from `{eta_binding['baseline_brier']}` to `{eta_binding['selected_brier']}`.",
                "",
                "## Still waiting on Delta",
                "",
                "- Matched-base `GRPO` vs `DPO` (`E1`): still pending.",
                "- RLCR head-to-head (`E6`): still pending.",
                "",
                "## Honest read",
                "",
                "- The immediate empirical package is now much better on the reviewer-facing weak points that do not require new GPU training.",
                "- The only truly unresolved causal claims are still the two training-heavy ones: matched-base objective control and RLCR head-to-head.",
            ]
        ),
    )

    print(
        json.dumps(
            {
                "conditional": str(out_dir / "conditional_independence_diagnostic.md"),
                "comparators": str(out_dir / "spotlight_comparator_strength_note.md"),
                "closed_model": str(out_dir / "closed_model_api_breakdown.md"),
                "eta_binding": str(out_dir / "eta_do_no_harm_binding_note.md"),
                "summary": str(out_dir / "paper2_empirical_weakness_fixes.md"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
