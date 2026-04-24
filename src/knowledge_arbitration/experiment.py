"""Executable synthetic and benchmark-backed experiments for knowledge arbitration."""

from __future__ import annotations

from math import log, log1p
import random
from statistics import mean
from typing import Any

from utils.metrics import (
    brier_score,
    calibration_bins,
    expected_calibration_error,
    maximum_calibration_error,
    roc_auc_binary,
    selective_prediction_curve,
)

from .loaders import load_arbitration_dataset
from .metrics import arbitration_kl_divergence, bayes_regret
from .posterior import ArbitrationFeatures, bayes_arbitration_probability


def _clip(value: float, lower: float = 1e-6, upper: float = 1.0 - 1e-6) -> float:
    return min(max(value, lower), upper)


def _stable_seed(*parts: Any) -> int:
    text = "||".join(str(part) for part in parts)
    total = 0
    for char in text:
        total = (total * 131 + ord(char)) % (2**32)
    return total


def _log_loss(probability: float, label: int) -> float:
    p = _clip(probability)
    return -log(p if label else 1.0 - p)


def _cot_intensity(cot_budget: int | str) -> float:
    if isinstance(cot_budget, str):
        mapping = {"none": 0.0, "short": 0.2, "medium": 0.45, "long": 0.75, "very_long": 1.0}
        return mapping.get(cot_budget, 0.35)
    if cot_budget <= 0:
        return 0.0
    if cot_budget <= 128:
        return 0.2
    if cot_budget <= 512:
        return 0.45
    if cot_budget <= 2048:
        return 0.75
    return 1.0


def _benchmark_profile(name: str) -> dict[str, float]:
    profiles = {
        "popqa": {"prior": 0.80, "dynamicity": 0.15, "conflict": 0.35, "context": 0.72},
        "dynamicqa": {"prior": 0.48, "dynamicity": 0.82, "conflict": 0.55, "context": 0.78},
        "conflictbank": {"prior": 0.52, "dynamicity": 0.50, "conflict": 0.82, "context": 0.70},
        "wikicontradict": {"prior": 0.56, "dynamicity": 0.38, "conflict": 0.80, "context": 0.73},
        "nq_swap": {"prior": 0.64, "dynamicity": 0.22, "conflict": 0.77, "context": 0.68},
        "templama": {"prior": 0.40, "dynamicity": 0.92, "conflict": 0.48, "context": 0.80},
        "freshqa": {"prior": 0.35, "dynamicity": 0.95, "conflict": 0.58, "context": 0.83},
        "mquake_remastered": {"prior": 0.50, "dynamicity": 0.35, "conflict": 0.88, "context": 0.66},
    }
    return profiles.get(name, {"prior": 0.55, "dynamicity": 0.4, "conflict": 0.5, "context": 0.7})


def _condition_adjustment(condition: str) -> dict[str, float]:
    mapping = {
        "closed_book": {"context": -0.22, "conflict": -0.25},
        "aligned_context": {"context": 0.15, "conflict": -0.18},
        "conflict_context": {"context": 0.05, "conflict": 0.28},
        "two_context_conflict": {"context": -0.08, "conflict": 0.35},
        "dual_conflict": {"context": -0.08, "conflict": 0.35},
        "irrelevant_noise": {"context": -0.35, "conflict": 0.12},
        "noise_context": {"context": -0.35, "conflict": 0.12},
    }
    return mapping.get(condition, {"context": 0.0, "conflict": 0.0})


def _model_profile(model_name: str) -> dict[str, float]:
    name = model_name.lower()
    profile = {"knowledge": 0.60, "overthinking": 0.18, "sharpness": 0.12}
    if "32b" in name or "70b" in name:
        profile["knowledge"] += 0.12
    elif "14b" in name or "13b" in name:
        profile["knowledge"] += 0.05
    if "r1" in name or "thinking" in name:
        profile["overthinking"] += 0.38
        profile["sharpness"] += 0.20
    if "pythia" in name:
        profile["knowledge"] -= 0.16
    if "olmo" in name:
        profile["knowledge"] -= 0.08
    return profile


def _heuristic_adaptive_probability(features: ArbitrationFeatures) -> float:
    context_advantage = features.contextual_score - features.parametric_score
    reliability_advantage = features.context_reliability - features.parametric_reliability
    return _clip(0.5 + 0.65 * context_advantage + 0.35 * reliability_advantage)


def _simulated_model_probability(features: ArbitrationFeatures, model_name: str, cot_length: int | str) -> float:
    oracle = bayes_arbitration_probability(features)
    profile = _model_profile(model_name)
    intensity = _cot_intensity(cot_length)
    initial_source_bias = 1.0 if features.contextual_score >= features.parametric_score else -1.0
    polarization = profile["overthinking"] * intensity * max(0.0, features.conflict_magnitude - 0.15)
    sharpened = oracle + initial_source_bias * polarization
    if intensity > 0.0:
        sharpened = 0.5 + (sharpened - 0.5) * (1.0 + profile["sharpness"] * intensity)
    return _clip(sharpened)


def _split_label(condition: str, conflict_magnitude: float) -> str:
    if condition in {"conflict_context", "two_context_conflict", "dual_conflict"}:
        return "conflict"
    if condition in {"aligned_context", "closed_book"}:
        return "no_conflict"
    if condition in {"irrelevant_noise", "noise_context"}:
        return "other"
    return "conflict" if conflict_magnitude >= 0.5 else "no_conflict"


def _summarize_policy_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    probabilities = [float(row["probability"]) for row in rows]
    labels = [int(row["label"]) for row in rows]
    regrets = [float(row["regret"]) for row in rows]
    kls = [float(row["kl_gap"]) for row in rows]
    accuracies = [1.0 if ((prob >= 0.5) == bool(label)) else 0.0 for prob, label in zip(probabilities, labels)]
    return {
        "num_examples": len(rows),
        "mean_probability": mean(probabilities) if probabilities else 0.0,
        "accuracy": mean(accuracies) if accuracies else 0.0,
        "brier": brier_score(probabilities, labels),
        "ece": expected_calibration_error(probabilities, labels),
        "mce": maximum_calibration_error(probabilities, labels),
        "auroc": roc_auc_binary(probabilities, labels),
        "mean_regret": mean(regrets) if regrets else 0.0,
        "mean_kl_gap": mean(kls) if kls else 0.0,
        "calibration_bins": calibration_bins(probabilities, labels),
        "selective_curve": selective_prediction_curve(probabilities, labels),
    }


def _finalize_experiment_payload(
    experiment: dict[str, Any],
    rows: list[dict[str, Any]],
    grouped_rows: dict[tuple[str, str, str, str], list[dict[str, Any]]],
    policy_rows: dict[str, list[dict[str, Any]]],
    *,
    synthetic: bool,
    metadata_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = {policy_name: _summarize_policy_rows(policy_values) for policy_name, policy_values in policy_rows.items()}

    summary_by_split: dict[str, dict[str, Any]] = {}
    for split in ["conflict", "no_conflict"]:
        summary_by_split[split] = {}
        for policy_name, policy_values in policy_rows.items():
            filtered = [row for row in policy_values if row["split"] == split]
            summary_by_split[split][policy_name] = _summarize_policy_rows(filtered)

    cot_lengths = list(experiment.get("cot_lengths", [])) or list(experiment.get("cot_budgets", [])) or [0]
    summary_by_cot: dict[str, dict[str, Any]] = {}
    for cot_length in cot_lengths:
        key = str(cot_length)
        summary_by_cot[key] = {}
        for policy_name, policy_values in policy_rows.items():
            filtered = [row for row in policy_values if str(row["cot_length"]) == key]
            summary_by_cot[key][policy_name] = _summarize_policy_rows(filtered)

    grouped_payload = []
    for (benchmark, model_name, condition, cot_length), group_values in sorted(grouped_rows.items()):
        grouped_payload.append(
            {
                "benchmark": benchmark,
                "model": model_name,
                "condition": condition,
                "cot_length": cot_length,
                "rows": group_values,
            }
        )

    metadata = {
        "synthetic": synthetic,
        "seed": int(experiment.get("seed", 42)),
        "max_examples": int(experiment.get("max_examples", 128)),
        "benchmarks": list(experiment.get("benchmarks", [])),
        "models": list(experiment.get("models", [])),
        "conditions": list(experiment.get("conditions", [])) or ["closed_book"],
        "cot_lengths": [str(value) for value in cot_lengths],
    }
    if metadata_extra:
        metadata.update(metadata_extra)

    return {
        "experiment_name": experiment["name"],
        "metadata": metadata,
        "experiments": grouped_payload,
        "summary": summary,
        "summary_by_split": summary_by_split,
        "summary_by_cot_length": summary_by_cot,
    }


def _build_features(
    benchmark: str,
    model_name: str,
    condition: str,
    cot_length: int | str,
    example_idx: int,
    seed: int,
) -> ArbitrationFeatures:
    rng = random.Random(_stable_seed(benchmark, model_name, condition, cot_length, example_idx, seed))
    benchmark_profile = _benchmark_profile(benchmark)
    model_profile = _model_profile(model_name)
    condition_adjustment = _condition_adjustment(condition)

    popularity_prior = _clip(benchmark_profile["prior"] + rng.uniform(-0.15, 0.15))
    dynamicity = _clip(benchmark_profile["dynamicity"] + rng.uniform(-0.12, 0.12))
    conflict_magnitude = _clip(
        benchmark_profile["conflict"] + condition_adjustment["conflict"] + rng.uniform(-0.15, 0.15),
        0.0,
        1.0,
    )
    context_reliability = _clip(benchmark_profile["context"] + condition_adjustment["context"] + rng.uniform(-0.15, 0.15))
    parametric_reliability = _clip(
        model_profile["knowledge"] + 0.35 * popularity_prior - 0.45 * dynamicity + rng.uniform(-0.12, 0.12)
    )
    parametric_score = _clip(parametric_reliability + 0.08 * rng.uniform(-1.0, 1.0))
    contextual_score = _clip(context_reliability + 0.08 * rng.uniform(-1.0, 1.0))

    if condition == "closed_book":
        contextual_score = 0.5
        context_reliability = 0.5
        conflict_magnitude = max(0.0, conflict_magnitude - 0.25)

    return ArbitrationFeatures(
        parametric_score=parametric_score,
        contextual_score=contextual_score,
        context_reliability=context_reliability,
        parametric_reliability=parametric_reliability,
        conflict_magnitude=conflict_magnitude,
    )


def run_synthetic_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    """Run a synthetic theorem-validation experiment from an experiment manifest."""

    max_examples = int(experiment.get("max_examples", 128))
    seed = int(experiment.get("seed", 42))
    cot_lengths = list(experiment.get("cot_lengths", [])) or list(experiment.get("cot_budgets", [])) or [0]
    model_names = list(experiment.get("models", []))
    conditions = list(experiment.get("conditions", [])) or ["closed_book"]

    rows: list[dict[str, Any]] = []
    grouped_rows: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    policy_rows: dict[str, list[dict[str, Any]]] = {
        "oracle": [],
        "bayes_proxy": [],
        "heuristic_adaptive": [],
        "fixed_50": [],
        "always_context": [],
        "always_parametric": [],
        "simulated_model": [],
    }

    for benchmark in experiment.get("benchmarks", []):
        for model_name in model_names:
            for condition in conditions:
                for cot_length in cot_lengths:
                    for example_idx in range(max_examples):
                        features = _build_features(benchmark, model_name, condition, cot_length, example_idx, seed)
                        oracle_probability = bayes_arbitration_probability(features)
                        rng = random.Random(_stable_seed("label", benchmark, model_name, condition, cot_length, example_idx, seed))
                        label = 1 if rng.random() < oracle_probability else 0
                        policy_probabilities = {
                            "oracle": oracle_probability,
                            "bayes_proxy": oracle_probability,
                            "heuristic_adaptive": _heuristic_adaptive_probability(features),
                            "fixed_50": 0.5,
                            "always_context": 1.0,
                            "always_parametric": 0.0,
                            "simulated_model": _simulated_model_probability(features, model_name, cot_length),
                        }
                        oracle_loss = _log_loss(oracle_probability, label)

                        split = _split_label(condition, features.conflict_magnitude)
                        row = {
                            "benchmark": benchmark,
                            "model": model_name,
                            "condition": condition,
                            "cot_length": cot_length,
                            "example_idx": example_idx,
                            "split": split,
                            "label": label,
                            "outcome": label,
                            "confidence": policy_probabilities["simulated_model"],
                            "oracle_probability": oracle_probability,
                            "oracle_context_probability": oracle_probability,
                            "model_context_probability": policy_probabilities["simulated_model"],
                            "regret_by_policy": {},
                            "features": {
                                "parametric_score": features.parametric_score,
                                "contextual_score": features.contextual_score,
                                "context_reliability": features.context_reliability,
                                "parametric_reliability": features.parametric_reliability,
                                "conflict_magnitude": features.conflict_magnitude,
                            },
                            "policies": {},
                        }

                        for policy_name, probability in policy_probabilities.items():
                            loss = _log_loss(probability, label)
                            regret = bayes_regret(oracle_loss, loss)
                            gap = arbitration_kl_divergence(oracle_probability, probability)
                            policy_row = {
                                "benchmark": benchmark,
                                "model": model_name,
                                "condition": condition,
                                "cot_length": cot_length,
                                "split": row["split"],
                                "probability": probability,
                                "label": label,
                                "regret": regret,
                                "kl_gap": gap,
                            }
                            policy_rows[policy_name].append(policy_row)
                            row["policies"][policy_name] = {
                                "probability": probability,
                                "regret": regret,
                                "kl_gap": gap,
                            }
                            row["regret_by_policy"][policy_name] = regret
                        rows.append(row)
                        group_key = (benchmark, model_name, condition, str(cot_length))
                        grouped_rows.setdefault(group_key, []).append(row)

    return _finalize_experiment_payload(experiment, rows, grouped_rows, policy_rows, synthetic=True)


def _normalize_scale(value: float | None, *, transform: str = "log") -> float:
    if value is None:
        return 0.5
    numeric = max(float(value), 0.0)
    if transform == "log":
        return _clip(log1p(numeric) / 14.0, 0.0, 1.0)
    return _clip(numeric / 10.0, 0.0, 1.0)


def _answer_set(values: Any) -> set[str]:
    if values is None:
        return set()
    if isinstance(values, str):
        return {values.strip().lower()} if values.strip() else set()
    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, list):
        return {str(item).strip().lower() for item in values if str(item).strip()}
    return {str(values).strip().lower()} if str(values).strip() else set()


def _derive_real_features(example: dict[str, Any], model_name: str, condition: str) -> tuple[ArbitrationFeatures, float, int, dict[str, Any]] | None:
    metadata = example.get("metadata", {})
    supports_conditions = set(metadata.get("supports_conditions", []))
    if supports_conditions and condition not in supports_conditions:
        return None

    gold_answers = _answer_set(example.get("answers"))
    parametric_answers = _answer_set(metadata.get("parametric_answers") or example.get("answers"))
    aligned_answers = _answer_set(metadata.get("aligned_context_answers") or example.get("answers"))
    conflict_answers = _answer_set(metadata.get("conflict_context_answers"))

    if condition == "closed_book":
        context_answers = set()
        context_reliability = 0.10
        oracle_probability = 0.02
    elif condition == "aligned_context":
        context_answers = aligned_answers
        context_reliability = 0.84
        oracle_probability = None
    elif condition == "conflict_context":
        context_answers = conflict_answers
        context_reliability = 0.24
        oracle_probability = None
    elif condition == "irrelevant_noise":
        context_answers = set()
        context_reliability = 0.08
        oracle_probability = 0.05
    else:
        return None

    context_correct = bool(context_answers & gold_answers)
    parametric_correct = bool(parametric_answers & gold_answers)
    label = 1 if context_correct else 0

    if oracle_probability is None:
        if context_correct and not parametric_correct:
            oracle_probability = 0.98
        elif parametric_correct and not context_correct:
            oracle_probability = 0.02
        else:
            oracle_probability = 0.50

    benchmark = str(metadata.get("benchmark", "unknown"))
    benchmark_profile = _benchmark_profile(benchmark)
    model_profile = _model_profile(model_name)
    popularity_score = _normalize_scale(metadata.get("popularity_score"), transform="log")
    dynamicity_score = _normalize_scale(metadata.get("dynamicity_score"), transform="linear")
    conflict_strength = _clip(float(metadata.get("conflict_strength", benchmark_profile["conflict"])))
    condition_adjustment = _condition_adjustment(condition)

    parametric_reliability = _clip(model_profile["knowledge"] + 0.28 * popularity_score - 0.35 * dynamicity_score)
    parametric_score = _clip(parametric_reliability + 0.12 * popularity_score - 0.08 * conflict_strength)
    contextual_score = _clip(context_reliability + 0.10 * benchmark_profile["context"] - 0.06 * popularity_score)
    conflict_magnitude = _clip(conflict_strength + condition_adjustment["conflict"] + 0.25 * dynamicity_score)

    features = ArbitrationFeatures(
        parametric_score=parametric_score,
        contextual_score=contextual_score,
        context_reliability=_clip(context_reliability),
        parametric_reliability=parametric_reliability,
        conflict_magnitude=conflict_magnitude,
    )
    derived = {
        "gold_answers": sorted(gold_answers),
        "parametric_answers": sorted(parametric_answers),
        "context_answers": sorted(context_answers),
        "context_correct": context_correct,
        "parametric_correct": parametric_correct,
        "popularity_score": popularity_score,
        "dynamicity_score": dynamicity_score,
        "conflict_strength": conflict_strength,
    }
    return features, float(oracle_probability), label, derived


def run_benchmark_experiment(
    experiment: dict[str, Any],
    *,
    dataset_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run a benchmark-backed proxy arbitration experiment using built-in loaders."""

    seed = int(experiment.get("seed", 42))
    cot_lengths = list(experiment.get("cot_lengths", [])) or [0]
    model_names = list(experiment.get("models", []))
    conditions = list(experiment.get("conditions", [])) or ["closed_book"]

    rows: list[dict[str, Any]] = []
    grouped_rows: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    policy_rows: dict[str, list[dict[str, Any]]] = {
        "oracle": [],
        "bayes_proxy": [],
        "heuristic_adaptive": [],
        "fixed_50": [],
        "always_context": [],
        "always_parametric": [],
        "simulated_model": [],
    }

    loaded_examples: dict[str, list[dict[str, Any]]] = {}
    skipped_conditions: list[dict[str, str]] = []
    for benchmark in experiment.get("benchmarks", []):
        loaded_examples[benchmark] = load_arbitration_dataset(
            benchmark,
            dataset_path=(dataset_overrides or {}).get(benchmark),
            max_examples=int(experiment.get("max_examples", 128)),
        )

    for benchmark, examples in loaded_examples.items():
        for model_name in model_names:
            for condition in conditions:
                for cot_length in cot_lengths:
                    group_values = []
                    for example_idx, example in enumerate(examples):
                        derived = _derive_real_features(example, model_name, condition)
                        if derived is None:
                            continue
                        features, _, label, derived_info = derived
                        oracle_probability = bayes_arbitration_probability(features)
                        policy_probabilities = {
                            "oracle": oracle_probability,
                            "bayes_proxy": oracle_probability,
                            "heuristic_adaptive": _heuristic_adaptive_probability(features),
                            "fixed_50": 0.5,
                            "always_context": 1.0,
                            "always_parametric": 0.0,
                            "simulated_model": _simulated_model_probability(features, model_name, cot_length),
                        }
                        oracle_loss = _log_loss(oracle_probability, label)
                        split = _split_label(condition, features.conflict_magnitude)
                        row = {
                            "benchmark": benchmark,
                            "model": model_name,
                            "condition": condition,
                            "cot_length": cot_length,
                            "example_idx": example_idx,
                            "id": example.get("id"),
                            "question": example.get("question"),
                            "split": split,
                            "label": label,
                            "outcome": label,
                            "confidence": policy_probabilities["simulated_model"],
                            "oracle_probability": oracle_probability,
                            "oracle_context_probability": oracle_probability,
                            "model_context_probability": policy_probabilities["simulated_model"],
                            "regret_by_policy": {},
                            "features": {
                                "parametric_score": features.parametric_score,
                                "contextual_score": features.contextual_score,
                                "context_reliability": features.context_reliability,
                                "parametric_reliability": features.parametric_reliability,
                                "conflict_magnitude": features.conflict_magnitude,
                                "popularity_score": derived_info["popularity_score"],
                                "dynamicity_score": derived_info["dynamicity_score"],
                                "context_correct": derived_info["context_correct"],
                                "parametric_correct": derived_info["parametric_correct"],
                            },
                            "metadata": example.get("metadata", {}),
                            "policies": {},
                        }
                        for policy_name, probability in policy_probabilities.items():
                            loss = _log_loss(probability, label)
                            regret = bayes_regret(oracle_loss, loss)
                            gap = arbitration_kl_divergence(oracle_probability, probability)
                            policy_row = {
                                "benchmark": benchmark,
                                "model": model_name,
                                "condition": condition,
                                "cot_length": cot_length,
                                "split": split,
                                "probability": probability,
                                "label": label,
                                "regret": regret,
                                "kl_gap": gap,
                            }
                            policy_rows[policy_name].append(policy_row)
                            row["policies"][policy_name] = {
                                "probability": probability,
                                "regret": regret,
                                "kl_gap": gap,
                            }
                            row["regret_by_policy"][policy_name] = regret
                        rows.append(row)
                        group_values.append(row)

                    if group_values:
                        group_key = (benchmark, model_name, condition, str(cot_length))
                        grouped_rows[group_key] = group_values
                    else:
                        skipped_conditions.append(
                            {
                                "benchmark": benchmark,
                                "model": model_name,
                                "condition": condition,
                                "cot_length": str(cot_length),
                                "reason": "unsupported_or_empty",
                            }
                        )

    return _finalize_experiment_payload(
        experiment,
        rows,
        grouped_rows,
        policy_rows,
        synthetic=False,
        metadata_extra={
            "dataset_mode": "built_in_or_local_proxy",
            "num_rows": len(rows),
            "skipped_conditions": skipped_conditions,
        },
    )
