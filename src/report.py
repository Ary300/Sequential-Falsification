"""Generate figure payloads and summary tables from experiment outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from utils.io import dump_json
from utils.plotting import (
    maybe_plot_calibration,
    maybe_plot_difficulty,
    maybe_plot_scaling_curve,
    maybe_plot_selective_prediction,
    maybe_plot_wealth,
    save_plot_payload,
)


def load_results(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _format_stat_cell(row: dict[str, Any]) -> str:
    if "accuracy_mean" in row:
        return f"{row['accuracy_mean']:.1f} $\\\\pm$ {row['accuracy_stderr']:.2f}"
    return f"{row['accuracy']:.1f}"


def _pretty_method_name(method: str) -> str:
    mapping = {
        "falsification": "Ours",
        "s_star": "S* proxy",
        "s_star_proxy": "S* proxy",
        "code_t": "CodeT proxy",
        "code_t_proxy": "CodeT proxy",
        "generated_test_filter": "Generated-test filter",
        "majority_vote": "Majority vote",
        "self_debug": "Self-debug",
        "greedy": "Greedy",
        "oracle": "Oracle",
        "prm_best_of_n": "PRM best-of-N",
    }
    return mapping.get(method, method)


def _method_aliases(method: str) -> tuple[str, ...]:
    alias_map = {
        "s_star": ("s_star_proxy", "s_star"),
        "s_star_proxy": ("s_star_proxy", "s_star"),
        "code_t": ("code_t_proxy", "code_t"),
        "code_t_proxy": ("code_t_proxy", "code_t"),
    }
    return alias_map.get(method, (method,))


def _get_method_stats(methods: dict[str, Any], method: str) -> dict[str, Any] | None:
    for alias in _method_aliases(method):
        stats = methods.get(alias)
        if stats:
            return stats
    return None


def build_main_table(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    rows = []
    for benchmark_result in payload.get(key, []):
        benchmark = benchmark_result["benchmark"]
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        if "summary_across_seeds" in benchmark_result:
            for method, stats in benchmark_result["summary_across_seeds"]["methods"].items():
                rows.append(
                    {
                        "benchmark": benchmark,
                        "method": method,
                        "accuracy_mean": round(stats["accuracy_mean"] * 100.0, 1),
                        "accuracy_stderr": round(stats["accuracy_stderr"] * 100.0, 2),
                    }
                )
        else:
            for method, stats in benchmark_result["summary"]["methods"].items():
                rows.append(
                    {
                        "benchmark": benchmark,
                        "method": method,
                        "accuracy": round(stats["accuracy"] * 100.0, 1),
                    }
                )
    return {"rows": rows}


def build_calibration_table(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    rows = []
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        if "summary_across_seeds" in benchmark_result:
            cal = benchmark_result["summary_across_seeds"].get("calibration", {})
            rows.append(
                {
                    "benchmark": benchmark_result["benchmark"],
                    "ece_mean": round(cal.get("ece", {}).get("mean", 0.0), 3),
                    "ece_stderr": round(cal.get("ece", {}).get("stderr", 0.0), 3),
                    "mce_mean": round(cal.get("mce", {}).get("mean", 0.0), 3),
                    "mce_stderr": round(cal.get("mce", {}).get("stderr", 0.0), 3),
                    "brier_mean": round(cal.get("brier", {}).get("mean", 0.0), 3),
                    "brier_stderr": round(cal.get("brier", {}).get("stderr", 0.0), 3),
                }
            )
        else:
            cal = benchmark_result["summary"].get("calibration", {})
            rows.append(
                {
                    "benchmark": benchmark_result["benchmark"],
                    "ece": round(cal.get("ece", 0.0), 3),
                    "mce": round(cal.get("mce", 0.0), 3),
                    "brier": round(cal.get("brier", 0.0), 3),
                    "auroc": round(cal.get("auroc", 0.0), 3),
                }
            )
    return {"rows": rows}


def _extract_method_stats(benchmark_result: dict[str, Any]) -> dict[str, Any]:
    if "summary_across_seeds" in benchmark_result:
        return benchmark_result["summary_across_seeds"]["methods"]
    if "summary" in benchmark_result:
        return benchmark_result["summary"]["methods"]
    return {}


def _extract_accuracy_percent(stats: dict[str, Any]) -> float:
    if "accuracy_mean" in stats:
        return round(stats["accuracy_mean"] * 100.0, 2)
    return round(stats.get("accuracy", 0.0) * 100.0, 2)


def _extract_experiment_name(benchmark_result: dict[str, Any]) -> str:
    config = benchmark_result.get("experiment_config", {})
    return config.get("expanded_from") or config.get("name") or benchmark_result.get("experiment_name", "unnamed")


def _compute_budget_proxy(config: dict[str, Any]) -> int:
    n_candidates = int(config.get("n_candidates", 1))
    n_rounds = int(config.get("n_falsification_rounds", 0))
    return n_candidates * max(1, n_rounds + 1)


def build_scaling_curve_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "experiments" in payload:
        grouped: dict[tuple[str, str], list[tuple[int, float]]] = {}
        for experiment_result in payload.get("experiments", []):
            benchmark = experiment_result["benchmark"]
            config = experiment_result.get("experiment_config", {})
            x_value = int(config.get("n_candidates", 1))
            methods = _extract_method_stats(experiment_result)
            if not methods:
                continue
            for method, stats in methods.items():
                grouped.setdefault((benchmark, method), []).append((x_value, _extract_accuracy_percent(stats)))
        series = []
        for (benchmark, method), points in sorted(grouped.items()):
            points = sorted(points, key=lambda item: item[0])
            series.append(
                {
                    "label": f"{benchmark}::{method}",
                    "x": [x for x, _ in points],
                    "y": [y for _, y in points],
                }
            )
    else:
        series = []
        for benchmark_result in payload.get("benchmarks", []):
            methods = _extract_method_stats(benchmark_result)
            x = [int(payload.get("metadata", {}).get("n_candidates", 1))]
            for method, stats in methods.items():
                series.append(
                    {
                        "label": f"{benchmark_result['benchmark']}::{method}",
                        "x": x,
                        "y": [_extract_accuracy_percent(stats)],
                    }
                )
    return {
        "title": "Scaling Summary",
        "x_label": "N",
        "y_label": "Accuracy (%)",
        "series": series,
    }


def build_round_ablation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    series = []
    if "experiments" not in payload:
        return {"title": "Falsification Round Ablation", "x_label": "Rounds", "y_label": "Accuracy (%)", "series": series}

    grouped: dict[tuple[str, str], list[tuple[int, float]]] = {}
    for experiment_result in payload.get("experiments", []):
        benchmark = experiment_result["benchmark"]
        config = experiment_result.get("experiment_config", {})
        x_value = int(config.get("n_falsification_rounds", 0))
        methods = _extract_method_stats(experiment_result)
        if not methods:
            continue
        for method in ["falsification", "s_star_proxy", "generated_test_filter", "majority_vote", "self_debug", "oracle"]:
            stats = _get_method_stats(methods, method)
            if not stats:
                continue
            grouped.setdefault((benchmark, method), []).append((x_value, _extract_accuracy_percent(stats)))
    for (benchmark, method), points in sorted(grouped.items()):
        points = sorted(points, key=lambda item: item[0])
        series.append(
            {
                "label": f"{benchmark}::{method}",
                "x": [x for x, _ in points],
                "y": [y for _, y in points],
            }
        )
    return {"title": "Falsification Round Ablation", "x_label": "Rounds", "y_label": "Accuracy (%)", "series": series}


def build_temperature_payload(payload: dict[str, Any]) -> dict[str, Any]:
    series = []
    if "experiments" not in payload:
        return {"title": "Temperature Sensitivity", "x_label": "Temperature", "y_label": "Accuracy (%)", "series": series}

    grouped: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for experiment_result in payload.get("experiments", []):
        if _extract_experiment_name(experiment_result) != "temperature_ablation_mbpp_7b":
            continue
        benchmark = experiment_result["benchmark"]
        config = experiment_result.get("experiment_config", {})
        x_value = float(config.get("temperature", 0.0))
        methods = _extract_method_stats(experiment_result)
        if not methods:
            continue
        for method in ["falsification", "generated_test_filter", "majority_vote", "self_debug", "oracle"]:
            stats = methods.get(method)
            if not stats:
                continue
            grouped.setdefault((benchmark, method), []).append((x_value, _extract_accuracy_percent(stats)))
    for (benchmark, method), points in sorted(grouped.items()):
        points = sorted(points, key=lambda item: item[0])
        series.append(
            {
                "label": f"{benchmark}::{method}",
                "x": [x for x, _ in points],
                "y": [y for _, y in points],
            }
        )
    return {"title": "Temperature Sensitivity", "x_label": "Temperature", "y_label": "Accuracy (%)", "x_scale": "linear", "series": series}


def build_compute_matched_payload(payload: dict[str, Any]) -> dict[str, Any]:
    series = []
    if "experiments" not in payload:
        return {"title": "Compute-Matched Comparison", "x_label": "Budget Proxy", "y_label": "Accuracy (%)", "series": series}

    grouped: dict[tuple[str, str], list[tuple[int, float]]] = {}
    for experiment_result in payload.get("experiments", []):
        if _extract_experiment_name(experiment_result) != "compute_matched_mbpp_7b":
            continue
        benchmark = experiment_result["benchmark"]
        config = experiment_result.get("experiment_config", {})
        budget = _compute_budget_proxy(config)
        methods = _extract_method_stats(experiment_result)
        if not methods:
            continue
        for method in ["falsification", "generated_test_filter", "majority_vote", "self_debug", "oracle"]:
            stats = methods.get(method)
            if not stats:
                continue
            grouped.setdefault((benchmark, method), []).append((budget, _extract_accuracy_percent(stats)))
    for (benchmark, method), points in sorted(grouped.items()):
        points = sorted(points, key=lambda item: item[0])
        series.append(
            {
                "label": f"{benchmark}::{method}",
                "x": [x for x, _ in points],
                "y": [y for _, y in points],
            }
        )
    return {"title": "Compute-Matched Comparison", "x_label": "Budget Proxy", "y_label": "Accuracy (%)", "x_scale": "linear", "series": series}


def build_compute_matched_table(payload: dict[str, Any]) -> dict[str, Any]:
    rows = []
    if "experiments" not in payload:
        return {"rows": rows}
    for experiment_result in payload.get("experiments", []):
        if _extract_experiment_name(experiment_result) != "compute_matched_mbpp_7b":
            continue
        config = experiment_result.get("experiment_config", {})
        methods = _extract_method_stats(experiment_result)
        if not methods:
            continue
        rows.append(
            {
                "benchmark": experiment_result["benchmark"],
                "experiment": config.get("name", experiment_result.get("experiment_name", "unnamed")),
                "n_candidates": int(config.get("n_candidates", 0)),
                "n_rounds": int(config.get("n_falsification_rounds", 0)),
                "budget_proxy": _compute_budget_proxy(config),
                "majority_vote": round(methods.get("majority_vote", {}).get("accuracy", methods.get("majority_vote", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "generated_test_filter": round(methods.get("generated_test_filter", {}).get("accuracy", methods.get("generated_test_filter", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "falsification": round(methods.get("falsification", {}).get("accuracy", methods.get("falsification", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "self_debug": round(methods.get("self_debug", {}).get("accuracy", methods.get("self_debug", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "oracle": round(methods.get("oracle", {}).get("accuracy", methods.get("oracle", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
            }
        )
    return {"rows": rows}


def build_probe_family_table(payload: dict[str, Any]) -> dict[str, Any]:
    rows = []
    if "experiments" not in payload:
        return {"rows": rows}
    for experiment_result in payload.get("experiments", []):
        config = experiment_result.get("experiment_config", {})
        methods = _extract_method_stats(experiment_result)
        if not methods:
            continue
        falsification = methods.get("falsification")
        if not falsification:
            continue
        rows.append(
            {
                "benchmark": experiment_result["benchmark"],
                "experiment": config.get("name", experiment_result.get("experiment_name", "unnamed")),
                "probe_strategy": config.get("probe_strategy", "unknown"),
                "n_candidates": config.get("n_candidates", 0),
                "n_rounds": config.get("n_falsification_rounds", 0),
                "falsification_accuracy": _extract_accuracy_percent(falsification),
            }
        )
    return {"rows": rows}


def build_calibration_figure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    panels = []
    method_order = ["falsification", "s_star_proxy", "code_t_proxy", "generated_test_filter", "majority_vote", "self_debug", "greedy"]
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        calibration = benchmark_result.get("summary", {}).get("calibration", {})
        if not calibration and "seed_runs" in benchmark_result:
            calibration = benchmark_result["seed_runs"][0].get("summary", {}).get("calibration", {})
        per_method = calibration.get("per_method", {})
        series = []
        for method in method_order:
            stats = _get_method_stats(per_method, method)
            if not stats:
                continue
            series.append({"method": method, "bins": stats.get("bins", [])})
        panels.append(
            {
                "benchmark": benchmark_result["benchmark"],
                "series": series,
                "perfect_calibration": [{"x": i / 10, "y": i / 10} for i in range(11)],
            }
        )
    return {"title": "Calibration Reliability", "panels": panels}


def build_selective_prediction_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    panels = []
    method_order = ["falsification", "s_star_proxy", "code_t_proxy", "generated_test_filter", "majority_vote", "self_debug", "greedy"]
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        calibration = benchmark_result.get("summary", {}).get("calibration", {})
        if not calibration and "seed_runs" in benchmark_result:
            calibration = benchmark_result["seed_runs"][0].get("summary", {}).get("calibration", {})
        per_method = calibration.get("per_method", {})
        series = []
        for method in method_order:
            stats = _get_method_stats(per_method, method)
            if not stats:
                continue
            series.append({"method": method, "curve": stats.get("selective_curve", [])})
        panels.append(
            {
                "benchmark": benchmark_result["benchmark"],
                "series": series,
            }
        )
    return {"title": "Selective Prediction", "panels": panels}


def build_difficulty_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    panels = []
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        difficulty = benchmark_result.get("summary", {}).get("difficulty", {})
        if not difficulty and "seed_runs" in benchmark_result:
            difficulty = benchmark_result["seed_runs"][0].get("summary", {}).get("difficulty", {})
        panels.append({"benchmark": benchmark_result["benchmark"], "difficulty": difficulty})
    return {"title": "Difficulty Stratification", "panels": panels}


def build_wealth_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    traces = []
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        result_source = benchmark_result.get("results")
        if result_source is None and "seed_runs" in benchmark_result:
            result_source = benchmark_result["seed_runs"][0].get("results", [])
        if not result_source:
            continue
        for problem in result_source[:5]:
            falsification = problem["methods"].get("falsification", {})
            records = falsification.get("records", [])
            for record in records[:2]:
                traces.append(
                    {
                        "benchmark": benchmark_result["benchmark"],
                        "problem_id": problem["problem_id"],
                        "candidate_id": record.get("candidate_id"),
                        "survived": record.get("survived", False),
                        "wealth": [step.get("wealth", 1.0) for step in record.get("trace", [])],
                    }
                )
    return {"title": "E-value Wealth Process", "threshold": 20.0, "traces": traces}


def build_component_table(payload: dict[str, Any]) -> dict[str, Any]:
    rows = []
    if "experiments" not in payload:
        return {"rows": rows}
    for benchmark_result in payload.get("experiments", []):
        methods = _extract_method_stats(benchmark_result)
        if not methods:
            continue
        config = benchmark_result.get("experiment_config", {})
        experiment_name = config.get("name", benchmark_result.get("experiment_name", "unnamed"))
        if "component_ablation" not in experiment_name:
            continue
        rows.append(
            {
                "benchmark": benchmark_result["benchmark"],
                "experiment": experiment_name,
                "probe_strategy": config.get("probe_strategy", "unknown"),
                "adaptive_probe_selection": bool(config.get("adaptive_probe_selection", True)),
                "eliminate_on_detection": bool(config.get("eliminate_on_detection", True)),
                "confidence_mode": config.get("confidence_mode", "wealth"),
                "majority_vote": round(methods.get("majority_vote", {}).get("accuracy", methods.get("majority_vote", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "generated_test_filter": round(methods.get("generated_test_filter", {}).get("accuracy", methods.get("generated_test_filter", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "falsification": round(methods.get("falsification", {}).get("accuracy", methods.get("falsification", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "self_debug": round(methods.get("self_debug", {}).get("accuracy", methods.get("self_debug", {}).get("accuracy_mean", 0.0)) * 100.0, 1),
                "s_star": round(_get_method_stats(methods, "s_star_proxy").get("accuracy", _get_method_stats(methods, "s_star_proxy").get("accuracy_mean", 0.0)) * 100.0, 1) if _get_method_stats(methods, "s_star_proxy") else 0.0,
            }
        )
    return {"rows": rows}


def build_compute_matched_table_latex(payload: dict[str, Any]) -> str:
    table = build_compute_matched_table(payload)
    if not table["rows"]:
        return ""
    lines = [
        "\\begin{tabular}{lrrccccc}",
        "\\toprule",
        "Benchmark & $N$ & $T$ & Budget & Majority & Gen-test & Ours & Self-debug & Oracle \\\\",
        "\\midrule",
    ]
    for row in table["rows"]:
        lines.append(
            f"{row['benchmark']} & {row['n_candidates']} & {row['n_rounds']} & {row['budget_proxy']} & "
            f"{row['majority_vote']:.1f} & {row['generated_test_filter']:.1f} & {row['falsification']:.1f} & "
            f"{row['self_debug']:.1f} & {row['oracle']:.1f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def build_main_table_latex(payload: dict[str, Any]) -> str:
    main_table = build_main_table(payload)
    benchmarks = sorted({row["benchmark"] for row in main_table["rows"]})
    methods = []
    seen = set()
    for row in main_table["rows"]:
        method = row["method"]
        if method not in seen:
            seen.add(method)
            methods.append(method)

    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in main_table["rows"]:
        grouped.setdefault(row["method"], {})[row["benchmark"]] = row

    lines = [
        "\\begin{tabular}{l" + "c" * len(benchmarks) + "}",
        "\\toprule",
        "Method & " + " & ".join(benchmarks) + " \\\\",
        "\\midrule",
    ]
    for method in methods:
        cells = []
        for benchmark in benchmarks:
            row = grouped.get(method, {}).get(benchmark)
            cells.append(_format_stat_cell(row) if row else "--")
        lines.append(f"{_pretty_method_name(method)} & " + " & ".join(cells) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def build_calibration_table_latex(payload: dict[str, Any]) -> str:
    calibration = build_calibration_table(payload)
    if not calibration["rows"]:
        return ""

    sample = calibration["rows"][0]
    seeded = "ece_mean" in sample
    if seeded:
        lines = [
            "\\begin{tabular}{lccc}",
            "\\toprule",
            "Benchmark & ECE & MCE & Brier \\\\",
            "\\midrule",
        ]
        for row in calibration["rows"]:
            lines.append(
                f"{row['benchmark']} & "
                f"{row['ece_mean']:.3f} $\\\\pm$ {row['ece_stderr']:.3f} & "
                f"{row['mce_mean']:.3f} $\\\\pm$ {row['mce_stderr']:.3f} & "
                f"{row['brier_mean']:.3f} $\\\\pm$ {row['brier_stderr']:.3f} \\\\"
            )
    else:
        lines = [
            "\\begin{tabular}{lcccc}",
            "\\toprule",
            "Benchmark & ECE & MCE & Brier & AUROC \\\\",
            "\\midrule",
        ]
        for row in calibration["rows"]:
            lines.append(
                f"{row['benchmark']} & {row['ece']:.3f} & {row['mce']:.3f} & {row['brier']:.3f} & {row['auroc']:.3f} \\\\"
            )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def build_calibration_comparison_table_latex(payload: dict[str, Any]) -> str:
    key = "benchmarks" if "benchmarks" in payload else "experiments"
    lines = [
        "\\begin{tabular}{llcccc}",
        "\\toprule",
        "Benchmark & Method & ECE & MCE & Brier & AUROC \\\\",
        "\\midrule",
    ]
    wrote_row = False
    for benchmark_result in payload.get(key, []):
        if "summary_across_seeds" not in benchmark_result and "summary" not in benchmark_result:
            continue
        calibration = benchmark_result.get("summary", {}).get("calibration", {})
        if not calibration and "seed_runs" in benchmark_result:
            calibration = benchmark_result["seed_runs"][0].get("summary", {}).get("calibration", {})
        per_method = calibration.get("per_method", {})
        for method in ["falsification", "s_star_proxy", "code_t_proxy", "generated_test_filter", "majority_vote", "self_debug", "greedy"]:
            stats = _get_method_stats(per_method, method)
            if not stats:
                continue
            wrote_row = True
            lines.append(
                f"{benchmark_result['benchmark']} & {_pretty_method_name(method)} & "
                f"{stats.get('ece', 0.0):.3f} & {stats.get('mce', 0.0):.3f} & "
                f"{stats.get('brier', 0.0):.3f} & {stats.get('auroc', 0.0):.3f} \\\\"
            )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n" if wrote_row else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build prototype tables and figures from results JSON.")
    parser.add_argument("--results-file", required=True)
    parser.add_argument("--output-dir", default="figures")
    args = parser.parse_args()

    payload = load_results(args.results_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    main_table = build_main_table(payload)
    calibration_table = build_calibration_table(payload)
    component_table = build_component_table(payload)
    compute_matched_table = build_compute_matched_table(payload)
    scaling_payload = build_scaling_curve_payload(payload)
    round_payload = build_round_ablation_payload(payload)
    temperature_payload = build_temperature_payload(payload)
    compute_matched_payload = build_compute_matched_payload(payload)
    calibration_payload = build_calibration_figure_payload(payload)
    difficulty_payload = build_difficulty_payload(payload)
    wealth_payload = build_wealth_payload(payload)
    selective_payload = build_selective_prediction_payload(payload)
    probe_family_table = build_probe_family_table(payload)

    dump_json(main_table, output_dir / "table_main.json")
    dump_json(calibration_table, output_dir / "table_calibration.json")
    dump_json(component_table, output_dir / "table_ablation.json")
    dump_json(compute_matched_table, output_dir / "table_compute_matched.json")
    dump_json(probe_family_table, output_dir / "table_probe_family.json")
    (output_dir / "table_main.tex").write_text(build_main_table_latex(payload), encoding="utf-8")
    calibration_tex = build_calibration_table_latex(payload)
    if calibration_tex:
        (output_dir / "table_calibration.tex").write_text(calibration_tex, encoding="utf-8")
    calibration_comparison_tex = build_calibration_comparison_table_latex(payload)
    if calibration_comparison_tex:
        (output_dir / "table_calibration_comparison.tex").write_text(calibration_comparison_tex, encoding="utf-8")
    compute_matched_tex = build_compute_matched_table_latex(payload)
    if compute_matched_tex:
        (output_dir / "table_compute_matched.tex").write_text(compute_matched_tex, encoding="utf-8")
    save_plot_payload(scaling_payload, output_dir / "figure_scaling_payload.json")
    save_plot_payload(round_payload, output_dir / "figure_rounds_payload.json")
    save_plot_payload(temperature_payload, output_dir / "figure_temperature_payload.json")
    save_plot_payload(compute_matched_payload, output_dir / "figure_compute_matched_payload.json")
    save_plot_payload(calibration_payload, output_dir / "figure_calibration_payload.json")
    save_plot_payload(selective_payload, output_dir / "figure_selective_payload.json")
    save_plot_payload(difficulty_payload, output_dir / "figure_difficulty_payload.json")
    save_plot_payload(wealth_payload, output_dir / "figure_wealth_payload.json")
    maybe_plot_scaling_curve(scaling_payload, output_dir / "figure_scaling.pdf")
    maybe_plot_scaling_curve(round_payload, output_dir / "figure_rounds.pdf")
    maybe_plot_scaling_curve(temperature_payload, output_dir / "figure_temperature.pdf")
    maybe_plot_scaling_curve(compute_matched_payload, output_dir / "figure_compute_matched.pdf")
    maybe_plot_calibration(calibration_payload, output_dir / "figure_calibration.pdf")
    maybe_plot_selective_prediction(selective_payload, output_dir / "figure_selective.pdf")
    maybe_plot_difficulty(difficulty_payload, output_dir / "figure_difficulty.pdf")
    maybe_plot_wealth(wealth_payload, output_dir / "figure_wealth.pdf")
    print(f"Wrote report artifacts to {output_dir}")


if __name__ == "__main__":
    main()
