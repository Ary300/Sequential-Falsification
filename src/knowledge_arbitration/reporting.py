"""Reporting helpers for knowledge arbitration experiment outputs."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from utils.io import dump_json
from utils.metrics import brier_score, expected_calibration_error
from utils.plotting import maybe_plot_grouped_bars, maybe_plot_scatter, maybe_plot_scaling_curve, save_plot_payload

from .metrics import arbitration_kl_divergence, bayes_regret


ORACLE_CONTEXT_KEYS = (
    "oracle_context_probability",
    "oracle_context_prob",
    "oracle_context_weight",
    "oracle_preference_for_context",
    "oracle_arbitration_probability",
    "oracle_arbitration_prob",
)
MODEL_CONTEXT_KEYS = (
    "model_context_probability",
    "model_context_prob",
    "policy_context_probability",
    "policy_context_prob",
    "policy_arbitration_probability",
    "policy_arbitration_prob",
    "arbitration_probability",
    "context_weight",
)
ORACLE_LOSS_KEYS = ("oracle_loss", "oracle_risk", "oracle_cost")
POLICY_LOSS_KEYS = ("loss", "risk", "cost", "policy_loss")
REGRET_KEYS = ("regret", "bayes_regret", "expected_regret")
CALIBRATION_CONFIDENCE_KEYS = (
    "confidence",
    "predicted_confidence",
    "calibrated_confidence",
    "final_confidence",
    "model_confidence",
    "arbitration_confidence",
    "probability",
    "arbitration_probability",
)
CALIBRATION_OUTCOME_KEYS = ("correct", "is_correct", "passed", "success", "outcome")
COLLECTION_KEYS = ("benchmarks", "experiments", "runs", "groups", "seed_runs")
DEFAULT_POLICY_ORDER = [
    "bayes",
    "bayes_inspired",
    "bayes_proxy",
    "madam_rag",
    "nwcad",
    "juice",
    "cocoa",
    "adacad",
    "cad",
    "astute_rag",
    "crag",
    "self_rag",
    "adaptive",
    "heuristic_adaptive",
    "constant_mix",
    "always_context",
    "always_parametric",
]


def load_results(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _normalize_key(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if _is_number(value):
        numeric = float(value)
        if numeric == numeric and abs(numeric) != float("inf"):
            return numeric
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            numeric = float(stripped)
        except ValueError:
            return None
        if numeric == numeric and abs(numeric) != float("inf"):
            return numeric
    return None


def _as_boolish_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    numeric = _as_float(value)
    if numeric is None:
        return None
    if numeric in {0.0, 1.0}:
        return int(numeric)
    return None


def _search_value(node: Any, candidate_keys: tuple[str, ...], *, max_depth: int = 4) -> Any:
    if max_depth < 0:
        return None
    normalized_targets = {_normalize_key(key) for key in candidate_keys}
    if isinstance(node, dict):
        for key, value in node.items():
            if _normalize_key(str(key)) in normalized_targets and value is not None:
                return value
        for value in node.values():
            if isinstance(value, dict):
                found = _search_value(value, candidate_keys, max_depth=max_depth - 1)
                if found is not None:
                    return found
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                found = _search_value(item, candidate_keys, max_depth=max_depth - 1)
                if found is not None:
                    return found
    return None


def _search_float(node: Any, candidate_keys: tuple[str, ...], *, max_depth: int = 4) -> float | None:
    value = _search_value(node, candidate_keys, max_depth=max_depth)
    return _as_float(value)


def _search_string(node: Any, candidate_keys: tuple[str, ...], *, max_depth: int = 3) -> str | None:
    value = _search_value(node, candidate_keys, max_depth=max_depth)
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def _search_boolish(node: Any, candidate_keys: tuple[str, ...], *, max_depth: int = 4) -> int | None:
    value = _search_value(node, candidate_keys, max_depth=max_depth)
    return _as_boolish_int(value)


def _pretty_label(value: str) -> str:
    mapping = {
        "bayes": "Bayes",
        "bayes_inspired": "Bayes-inspired",
        "bayes_rule": "Bayes",
        "bayes_proxy": "Bayes proxy",
        "madam_rag": "MADAM-RAG",
        "nwcad": "NWCAD",
        "juice": "JuICE",
        "cocoa": "CoCoA",
        "adacad": "AdaCAD",
        "cad": "CAD",
        "astute_rag": "Astute RAG",
        "crag": "CRAG",
        "self_rag": "Self-RAG",
        "adaptive": "Adaptive",
        "heuristic_adaptive": "Heuristic adaptive",
        "constant_mix": "Constant mix",
        "always_context": "Always context",
        "always_parametric": "Always parametric",
        "parametric": "Parametric",
        "context": "Context",
        "conflict": "Conflict",
        "no_conflict": "No conflict",
        "other": "Other",
    }
    return mapping.get(value, value.replace("_", " ").strip().title())


def _canonical_policy_name(name: str) -> str:
    normalized = _normalize_key(name)
    alias_map = {
        "bayes": "bayes",
        "bayesinspired": "bayes_inspired",
        "bayesrule": "bayes",
        "bayesproxy": "bayes_proxy",
        "madamrag": "madam_rag",
        "nwcad": "nwcad",
        "juice": "juice",
        "cocoa": "cocoa",
        "adacad": "adacad",
        "cad": "cad",
        "astuterag": "astute_rag",
        "crag": "crag",
        "selfrag": "self_rag",
        "adaptive": "adaptive",
        "adaptivepolicy": "adaptive",
        "heuristicadaptive": "heuristic_adaptive",
        "constantmix": "constant_mix",
        "constantweight": "constant_mix",
        "constantweightinterpolation": "constant_mix",
        "alwayscontext": "always_context",
        "contextonly": "always_context",
        "alwaysparametric": "always_parametric",
        "parametriconly": "always_parametric",
        "memoryonly": "always_parametric",
    }
    return alias_map.get(normalized, name.strip())


def _build_context(node: dict[str, Any], parent: dict[str, Any] | None = None) -> dict[str, Any]:
    context = dict(parent or {})
    benchmark = _search_string(node, ("benchmark", "dataset", "benchmark_name"))
    model = _search_string(node, ("model", "model_name"))
    condition = _search_string(node, ("condition", "condition_label", "conflict_type", "label"))
    experiment = _search_string(node, ("experiment_name", "name", "run_name"))
    cot_length = _search_float(node, ("cot_length", "cot_budget", "cot_tokens", "reasoning_tokens", "cot"))
    if benchmark:
        context["benchmark"] = benchmark
    if model:
        context["model"] = model
    if condition:
        context["condition"] = condition
    if experiment:
        context["experiment"] = experiment
    if cot_length is not None:
        context["cot_length"] = cot_length
    return context


def _looks_like_group(node: dict[str, Any]) -> bool:
    if any(isinstance(node.get(key), list) and node.get(key) for key in ("results", "examples", "records", "rows")):
        return True
    if any(key in node for key in ("oracle_vs_model", "regret", "regret_by_policy", "calibration_by_cot")):
        return True
    return bool(
        ("summary" in node or "summary_across_seeds" in node)
        and any(key in node for key in ("benchmark", "model", "condition", "experiment_config", "metadata"))
    )


def _iter_groups(node: Any, parent_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    if not isinstance(node, dict):
        return groups
    context = _build_context(node, parent_context)
    has_examples = bool(_extract_examples(node))
    has_slice_keys = any(key in node for key in ("benchmark", "model", "condition", "cot_length"))
    if _looks_like_group(node) and (has_examples or has_slice_keys):
        groups.append({"node": node, "context": context})
    for key in COLLECTION_KEYS:
        children = node.get(key)
        if not isinstance(children, list):
            continue
        for child in children:
            if isinstance(child, dict):
                groups.extend(_iter_groups(child, context))
    return groups


def _extract_examples(node: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("results", "examples", "records", "rows"):
        value = node.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _condition_bucket(condition: str | None) -> str:
    normalized = _normalize_key(condition or "unknown")
    if "conflict" in normalized or "contradict" in normalized:
        return "conflict"
    if any(token in normalized for token in ("aligned", "noconflict", "closedbook", "support", "agree")):
        return "no_conflict"
    return "other"


def _series_key(context: dict[str, Any]) -> str:
    benchmark = context.get("benchmark", "unknown")
    model = context.get("model")
    return f"{benchmark}::{model}" if model else str(benchmark)


def _annotation(context: dict[str, Any]) -> str:
    parts = []
    if context.get("model"):
        parts.append(str(context["model"]))
    if context.get("condition"):
        parts.append(str(context["condition"]))
    cot_length = context.get("cot_length")
    if cot_length is not None:
        parts.append(f"cot={int(cot_length) if float(cot_length).is_integer() else cot_length}")
    return " | ".join(parts) or str(context.get("benchmark", "slice"))


def _extract_oracle_model_pair(row: dict[str, Any]) -> tuple[float | None, float | None]:
    oracle = _search_float(row, ORACLE_CONTEXT_KEYS)
    model = _search_float(row, MODEL_CONTEXT_KEYS)
    return oracle, model


def build_oracle_vs_model_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    series_map: dict[str, dict[str, Any]] = {}
    rows = []
    for group in _iter_groups(payload):
        node = group["node"]
        context = group["context"]
        examples = _extract_examples(node)
        points = []
        for example in examples:
            oracle_prob, model_prob = _extract_oracle_model_pair(example)
            if oracle_prob is None or model_prob is None:
                continue
            points.append((oracle_prob, model_prob))
        if not points:
            oracle_prob, model_prob = _extract_oracle_model_pair(node)
            if oracle_prob is not None and model_prob is not None:
                points.append((oracle_prob, model_prob))
        if not points:
            continue

        avg_oracle = sum(item[0] for item in points) / len(points)
        avg_model = sum(item[1] for item in points) / len(points)
        abs_gap = abs(avg_model - avg_oracle)
        kl_values = [arbitration_kl_divergence(item[0], item[1]) for item in points]
        mean_kl = sum(kl_values) / len(kl_values)
        row = {
            "benchmark": context.get("benchmark", "unknown"),
            "model": context.get("model"),
            "condition": context.get("condition"),
            "cot_length": context.get("cot_length"),
            "annotation": _annotation(context),
            "oracle_context_probability": round(avg_oracle, 4),
            "model_context_probability": round(avg_model, 4),
            "abs_gap": round(abs_gap, 4),
            "mean_kl_to_oracle": round(mean_kl, 4),
            "count": len(points),
        }
        rows.append(row)

        label = _series_key(context)
        series = series_map.setdefault(label, {"label": label, "x": [], "y": [], "annotations": []})
        series["x"].append(avg_oracle)
        series["y"].append(avg_model)
        series["annotations"].append(row["annotation"])

    rows.sort(key=lambda item: (item["benchmark"], item.get("model") or "", item["annotation"]))
    payload_out = {
        "title": "Oracle vs Model Arbitration",
        "x_label": "Oracle P(trust context)",
        "y_label": "Model P(trust context)",
        "diagonal": True,
        "annotate_points": True,
        "series": list(series_map.values()),
    }
    summary = {
        "num_slices": len(rows),
        "num_examples_with_probabilities": sum(row["count"] for row in rows),
        "mean_abs_gap": round(sum(row["abs_gap"] for row in rows) / len(rows), 4) if rows else 0.0,
        "mean_kl_to_oracle": round(sum(row["mean_kl_to_oracle"] for row in rows) / len(rows), 4) if rows else 0.0,
        "worst_slice": max(rows, key=lambda item: item["abs_gap"]) if rows else None,
        "rows": rows,
    }
    return payload_out, summary


def _extract_explicit_regrets(node: dict[str, Any]) -> dict[str, float]:
    explicit = {}
    for key in ("regret", "regret_by_policy", "policy_regret", "policy_regrets"):
        value = node.get(key)
        if isinstance(value, dict):
            for policy_name, policy_value in value.items():
                if isinstance(policy_value, dict):
                    regret_value = _search_float(policy_value, REGRET_KEYS)
                else:
                    regret_value = _as_float(policy_value)
                if regret_value is not None:
                    explicit[_canonical_policy_name(policy_name)] = regret_value
        elif isinstance(value, list):
            for row in value:
                if not isinstance(row, dict):
                    continue
                policy_name = _search_string(row, ("policy", "method", "name"))
                regret_value = _search_float(row, REGRET_KEYS)
                if policy_name and regret_value is not None:
                    explicit[_canonical_policy_name(policy_name)] = regret_value
    return explicit


def _policy_entries(row: dict[str, Any]) -> list[tuple[str, Any]]:
    for key in ("policies", "policy_outputs", "policy_results", "methods"):
        value = row.get(key)
        if isinstance(value, dict):
            return [(str(name), policy_payload) for name, policy_payload in value.items()]
    return []


def _policy_loss(policy_payload: Any) -> float | None:
    if isinstance(policy_payload, dict):
        regret_value = _search_float(policy_payload, REGRET_KEYS)
        if regret_value is not None:
            return regret_value
        loss_value = _search_float(policy_payload, POLICY_LOSS_KEYS)
        if loss_value is not None:
            return loss_value
        correct_value = _search_boolish(policy_payload, CALIBRATION_OUTCOME_KEYS)
        if correct_value is not None:
            return 1.0 - float(correct_value)
    return _as_float(policy_payload)


def _oracle_loss(row: dict[str, Any]) -> float | None:
    direct = _search_float(row, ORACLE_LOSS_KEYS)
    if direct is not None:
        return direct
    oracle_payload = row.get("oracle")
    if isinstance(oracle_payload, dict):
        direct = _search_float(oracle_payload, ORACLE_LOSS_KEYS + POLICY_LOSS_KEYS)
        if direct is not None:
            return direct
        correct_value = _search_boolish(oracle_payload, CALIBRATION_OUTCOME_KEYS)
        if correct_value is not None:
            return 1.0 - float(correct_value)
    correct_value = _search_boolish(row, ("oracle_correct", "oracle_success"))
    if correct_value is not None:
        return 1.0 - float(correct_value)
    return None


def build_regret_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    by_series_policy: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    row_map: dict[tuple[str, str], list[float]] = defaultdict(list)

    for group in _iter_groups(payload):
        node = group["node"]
        context = group["context"]
        explicit_regrets = _extract_explicit_regrets(node)
        label = _series_key(context)
        if explicit_regrets:
            for policy_name, regret_value in explicit_regrets.items():
                by_series_policy[label][policy_name].append(regret_value)
                row_map[(label, policy_name)].append(regret_value)
            continue

        examples = _extract_examples(node)
        for example in examples:
            example_explicit_regrets = _extract_explicit_regrets(example)
            if example_explicit_regrets:
                for policy_name, regret_value in example_explicit_regrets.items():
                    by_series_policy[label][policy_name].append(regret_value)
                    row_map[(label, policy_name)].append(regret_value)
                continue
            oracle_loss = _oracle_loss(example)
            if oracle_loss is None:
                continue
            for policy_name, policy_payload in _policy_entries(example):
                policy_loss = _policy_loss(policy_payload)
                if policy_loss is None:
                    continue
                canonical_name = _canonical_policy_name(policy_name)
                regret_value = bayes_regret(oracle_loss, policy_loss)
                by_series_policy[label][canonical_name].append(regret_value)
                row_map[(label, canonical_name)].append(regret_value)

    policy_names = sorted(
        {
            policy_name
            for policy_map in by_series_policy.values()
            for policy_name in policy_map
        },
        key=lambda item: (DEFAULT_POLICY_ORDER.index(item) if item in DEFAULT_POLICY_ORDER else len(DEFAULT_POLICY_ORDER), item),
    )

    series = []
    rows = []
    for label in sorted(by_series_policy):
        policy_map = by_series_policy[label]
        series.append(
            {
                "label": label,
                "values": [
                    round(sum(policy_map.get(policy_name, [])) / len(policy_map.get(policy_name, [])), 4)
                    if policy_map.get(policy_name)
                    else 0.0
                    for policy_name in policy_names
                ],
            }
        )
    for (label, policy_name), values in sorted(row_map.items()):
        rows.append(
            {
                "series": label,
                "policy": policy_name,
                "mean_regret": round(sum(values) / len(values), 4),
                "count": len(values),
            }
        )

    overall = defaultdict(list)
    for row in rows:
        overall[row["policy"]].append(row["mean_regret"])
    overall_rows = [
        {
            "policy": policy_name,
            "mean_regret": round(sum(values) / len(values), 4),
            "num_series": len(values),
        }
        for policy_name, values in sorted(overall.items(), key=lambda item: sum(item[1]) / len(item[1]))
    ]

    payload_out = {
        "title": "Arbitration Regret by Policy",
        "categories": [_pretty_label(policy_name) for policy_name in policy_names],
        "series": series,
        "x_label": "Policy",
        "y_label": "Average regret",
        "rotation": 20,
    }
    summary = {
        "num_series": len(series),
        "overall_best_policy": overall_rows[0] if overall_rows else None,
        "overall": overall_rows,
        "rows": rows,
    }
    return payload_out, summary


def _extract_group_calibration(node: dict[str, Any]) -> tuple[float | None, float | None]:
    calibration = node.get("calibration")
    if not isinstance(calibration, dict):
        calibration = node.get("summary", {}).get("calibration")
    if not isinstance(calibration, dict):
        calibration = {}
    ece_value = _search_float(calibration, ("ece",))
    brier_value = _search_float(calibration, ("brier", "brier_score"))
    if ece_value is not None or brier_value is not None:
        return ece_value, brier_value

    examples = _extract_examples(node)
    confidences = []
    outcomes = []
    for example in examples:
        confidence = _search_float(example, CALIBRATION_CONFIDENCE_KEYS)
        outcome = _search_boolish(example, CALIBRATION_OUTCOME_KEYS)
        if confidence is None or outcome is None:
            continue
        confidences.append(min(max(confidence, 0.0), 1.0))
        outcomes.append(outcome)
    if not confidences:
        return None, None
    return expected_calibration_error(confidences, outcomes), brier_score(confidences, outcomes)


def build_calibration_by_cot_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    grouped_values: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    rows = []
    for group in _iter_groups(payload):
        node = group["node"]
        context = group["context"]
        cot_length = context.get("cot_length")
        if cot_length is None:
            continue
        benchmark = str(context.get("benchmark", "unknown"))
        condition = context.get("condition")
        bucket = _condition_bucket(condition)
        ece_value, brier_value = _extract_group_calibration(node)
        if ece_value is None and brier_value is None:
            continue
        row = {
            "benchmark": benchmark,
            "condition": condition,
            "condition_bucket": bucket,
            "cot_length": float(cot_length),
            "ece": round(float(ece_value or 0.0), 4),
            "brier": round(float(brier_value or 0.0), 4),
        }
        rows.append(row)
        grouped_values[(benchmark, bucket)].append(
            {
                "cot_length": float(cot_length),
                "ece": float(ece_value or 0.0),
                "brier": float(brier_value or 0.0),
            }
        )

    rows.sort(key=lambda item: (item["benchmark"], item["condition_bucket"], item["cot_length"]))
    series = []
    trend_rows = []
    for (benchmark, bucket), values in sorted(grouped_values.items()):
        deduped: dict[float, list[dict[str, float]]] = defaultdict(list)
        for row in values:
            deduped[row["cot_length"]].append(row)
        ordered = []
        for cot_length, cot_rows in sorted(deduped.items()):
            ordered.append(
                {
                    "cot_length": cot_length,
                    "ece": sum(item["ece"] for item in cot_rows) / len(cot_rows),
                    "brier": sum(item["brier"] for item in cot_rows) / len(cot_rows),
                }
            )
        if not ordered:
            continue
        first = ordered[0]
        last = ordered[-1]
        trend_rows.append(
            {
                "benchmark": benchmark,
                "condition_bucket": bucket,
                "start_cot": first["cot_length"],
                "end_cot": last["cot_length"],
                "ece_delta": round(last["ece"] - first["ece"], 4),
                "brier_delta": round(last["brier"] - first["brier"], 4),
                "points": len(ordered),
            }
        )
        series.append(
            {
                "label": f"{benchmark}::{_pretty_label(bucket)}",
                "x": [item["cot_length"] for item in ordered],
                "y": [round(item["ece"], 4) for item in ordered],
            }
        )

    conflict_deltas = [row["ece_delta"] for row in trend_rows if row["condition_bucket"] == "conflict"]
    no_conflict_deltas = [row["ece_delta"] for row in trend_rows if row["condition_bucket"] == "no_conflict"]
    payload_out = {
        "title": "Calibration by CoT",
        "x_label": "CoT length",
        "y_label": "ECE",
        "x_scale": "linear",
        "series": series,
    }
    summary = {
        "num_series": len(series),
        "rows": rows,
        "trend_rows": trend_rows,
        "mean_conflict_ece_delta": round(sum(conflict_deltas) / len(conflict_deltas), 4) if conflict_deltas else None,
        "mean_no_conflict_ece_delta": round(sum(no_conflict_deltas) / len(no_conflict_deltas), 4) if no_conflict_deltas else None,
    }
    return payload_out, summary


def build_summary(payload: dict[str, Any]) -> dict[str, Any]:
    groups = _iter_groups(payload)
    examples = sum(len(_extract_examples(group["node"])) for group in groups)
    benchmarks = sorted({group["context"].get("benchmark", "unknown") for group in groups})
    models = sorted({group["context"].get("model") for group in groups if group["context"].get("model")})
    oracle_payload, oracle_summary = build_oracle_vs_model_payload(payload)
    regret_payload, regret_summary = build_regret_payload(payload)
    calibration_payload, calibration_summary = build_calibration_by_cot_payload(payload)

    return {
        "metadata": payload.get("metadata", {}),
        "coverage": {
            "num_groups": len(groups),
            "num_examples": examples,
            "benchmarks": benchmarks,
            "models": models,
        },
        "headline": {
            "mean_oracle_model_abs_gap": oracle_summary["mean_abs_gap"],
            "mean_oracle_model_kl": oracle_summary["mean_kl_to_oracle"],
            "best_regret_policy": regret_summary["overall_best_policy"],
            "mean_conflict_ece_delta": calibration_summary["mean_conflict_ece_delta"],
            "mean_no_conflict_ece_delta": calibration_summary["mean_no_conflict_ece_delta"],
        },
        "oracle_vs_model": oracle_summary,
        "regret": regret_summary,
        "calibration_by_cot": calibration_summary,
        "figures": {
            "oracle_vs_model": oracle_payload,
            "regret": regret_payload,
            "calibration_by_cot": calibration_payload,
        },
    }


def _fmt_optional(value: Any, digits: int = 4) -> str:
    numeric = _as_float(value)
    if numeric is None:
        return "n/a"
    return f"{numeric:.{digits}f}"


def _markdown_cell(value: Any) -> str:
    return str(value).replace("|", "/")


def build_markdown_summary(report: dict[str, Any]) -> str:
    coverage = report.get("coverage", {})
    headline = report.get("headline", {})
    oracle = report.get("oracle_vs_model", {})
    regret = report.get("regret", {})
    calibration = report.get("calibration_by_cot", {})
    benchmarks = ", ".join(f"`{item}`" for item in coverage.get("benchmarks", [])) or "`unknown`"
    models = ", ".join(f"`{item}`" for item in coverage.get("models", [])) or "`unknown`"
    best_policy = regret.get("overall_best_policy") or {}

    lines = [
        "# Knowledge Arbitration Report",
        "",
        f"- Benchmarks: {benchmarks}",
        f"- Models: {models}",
        f"- Parsed groups: `{coverage.get('num_groups', 0)}`",
        f"- Parsed examples: `{coverage.get('num_examples', 0)}`",
        "",
        "## Headline Metrics",
        "",
        f"- Oracle-vs-model mean absolute gap: `{_fmt_optional(headline.get('mean_oracle_model_abs_gap'))}`",
        f"- Oracle-vs-model mean KL: `{_fmt_optional(headline.get('mean_oracle_model_kl'))}`",
        f"- Best regret policy: `{_pretty_label(best_policy.get('policy', 'n/a'))}` with mean regret `{_fmt_optional(best_policy.get('mean_regret'))}`",
        f"- Mean conflict ECE delta across CoT: `{_fmt_optional(headline.get('mean_conflict_ece_delta'))}`",
        f"- Mean no-conflict ECE delta across CoT: `{_fmt_optional(headline.get('mean_no_conflict_ece_delta'))}`",
        "",
        "## Oracle vs Model",
        "",
        "| Slice | Oracle P(context) | Model P(context) | Abs gap | Count |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in oracle.get("rows", [])[:8]:
        lines.append(
            f"| {_markdown_cell(row['annotation'])} | {row['oracle_context_probability']:.4f} | "
            f"{row['model_context_probability']:.4f} | {row['abs_gap']:.4f} | {row['count']} |"
        )
    if not oracle.get("rows"):
        lines.append("| no data | -- | -- | -- | -- |")

    lines.extend(
        [
            "",
            "## Regret",
            "",
            "| Policy | Mean regret | Series |",
            "|---|---:|---:|",
        ]
    )
    for row in regret.get("overall", [])[:8]:
        lines.append(f"| {_pretty_label(row['policy'])} | {row['mean_regret']:.4f} | {row['num_series']} |")
    if not regret.get("overall"):
        lines.append("| no data | -- | -- |")

    lines.extend(
        [
            "",
            "## Calibration by CoT",
            "",
            "| Benchmark | Bucket | Start CoT | End CoT | ECE delta | Brier delta |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in calibration.get("trend_rows", [])[:8]:
        lines.append(
            f"| {row['benchmark']} | {_pretty_label(row['condition_bucket'])} | {row['start_cot']:.0f} | "
            f"{row['end_cot']:.0f} | {row['ece_delta']:.4f} | {row['brier_delta']:.4f} |"
        )
    if not calibration.get("trend_rows"):
        lines.append("| no data | -- | -- | -- | -- | -- |")

    lines.append("")
    return "\n".join(lines)


def write_report(payload: dict[str, Any], output_dir: str | Path) -> dict[str, Any]:
    report = build_summary(payload)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary_json_path = output_path / "arbitration_summary.json"
    summary_md_path = output_path / "summary.md"
    oracle_payload_path = output_path / "figure_oracle_vs_model_payload.json"
    regret_payload_path = output_path / "figure_regret_payload.json"
    calibration_payload_path = output_path / "figure_calibration_by_cot_payload.json"

    dump_json(report, summary_json_path)
    summary_md_path.write_text(build_markdown_summary(report), encoding="utf-8")
    save_plot_payload(report["figures"]["oracle_vs_model"], oracle_payload_path)
    save_plot_payload(report["figures"]["regret"], regret_payload_path)
    save_plot_payload(report["figures"]["calibration_by_cot"], calibration_payload_path)

    oracle_format = maybe_plot_scatter(report["figures"]["oracle_vs_model"], output_path / "figure_oracle_vs_model.pdf")
    regret_format = maybe_plot_grouped_bars(report["figures"]["regret"], output_path / "figure_regret.pdf")
    calibration_format = maybe_plot_scaling_curve(
        report["figures"]["calibration_by_cot"],
        output_path / "figure_calibration_by_cot.pdf",
    )

    return {
        "output_dir": str(output_path),
        "summary_json": str(summary_json_path),
        "summary_markdown": str(summary_md_path),
        "figure_payloads": {
            "oracle_vs_model": str(oracle_payload_path),
            "regret": str(regret_payload_path),
            "calibration_by_cot": str(calibration_payload_path),
        },
        "rendered_formats": {
            "oracle_vs_model": oracle_format,
            "regret": regret_format,
            "calibration_by_cot": calibration_format,
        },
    }


__all__ = [
    "build_calibration_by_cot_payload",
    "build_markdown_summary",
    "build_oracle_vs_model_payload",
    "build_regret_payload",
    "build_summary",
    "load_results",
    "write_report",
]
