"""Merge multiple experiment result files into publication-ready summary tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

CORE_METHOD_ORDER = [
    "greedy",
    "majority_vote",
    "generated_test_filter",
    "self_debug",
    "falsification",
    "oracle",
    "code_t_proxy",
    "s_star_proxy",
    "prm_best_of_n_placeholder",
]

CORE_METHOD_LABELS = {
    "greedy": "greedy",
    "majority_vote": "majority vote",
    "generated_test_filter": "generated-test filter",
    "self_debug": "self-debug",
    "falsification": "falsification",
    "oracle": "oracle",
    "code_t_proxy": "CodeT proxy",
    "s_star_proxy": "S* proxy",
    "prm_best_of_n_placeholder": "PRM placeholder",
}

METHOD_ALIASES = {
    "code_t": "code_t_proxy",
    "code_t_proxy": "code_t_proxy",
    "s_star": "s_star_proxy",
    "s_star_proxy": "s_star_proxy",
    "prm_best_of_n": "prm_best_of_n_placeholder",
    "prm_best_of_n_placeholder": "prm_best_of_n_placeholder",
}


def _canonical_method_name(method: str) -> str:
    return METHOD_ALIASES.get(method, method)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_summary_rows(
    *,
    source_file: Path,
    model: str,
    benchmark: str,
    num_problems: int,
    partial: bool,
    num_complete_seed_runs: int,
    num_seed_runs: int,
    summary_across_seeds: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    experiment_name: str | None = None,
    experiment_config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    inferred_complete_seed_runs = num_complete_seed_runs
    inferred_seed_runs = num_seed_runs
    if summary and not summary_across_seeds and inferred_seed_runs == 0:
        inferred_seed_runs = 1
        inferred_complete_seed_runs = 0 if partial else 1
    common = {
        "source_file": str(source_file),
        "model": model,
        "benchmark": benchmark,
        "num_problems": num_problems,
        "partial": partial,
        "num_complete_seed_runs": inferred_complete_seed_runs,
        "num_seed_runs": inferred_seed_runs,
    }
    if experiment_name:
        common["experiment_name"] = experiment_name
    if experiment_config:
        for key in ["n_candidates", "n_falsification_rounds", "temperature", "probe_strategy", "confidence_mode"]:
            if key in experiment_config:
                common[key] = experiment_config[key]

    if summary_across_seeds:
        methods = summary_across_seeds.get("methods", {})
        for method, stats in methods.items():
            row = dict(common)
            row.update(
                {
                    "method": _canonical_method_name(method),
                    "accuracy_mean": round(stats["accuracy_mean"] * 100.0, 1),
                    "accuracy_stderr": round(stats["accuracy_stderr"] * 100.0, 2),
                }
            )
            rows.append(row)
    elif summary:
        methods = summary.get("methods", {})
        for method, stats in methods.items():
            row = dict(common)
            row.update(
                {
                    "method": _canonical_method_name(method),
                    "accuracy": round(stats["accuracy"] * 100.0, 1),
                }
            )
            rows.append(row)
    return rows


def iter_benchmark_rows(results_file: Path) -> list[dict[str, Any]]:
    payload = load_json(results_file)
    rows: list[dict[str, Any]] = []

    if "benchmarks" in payload:
        model = payload.get("metadata", {}).get("model", "unknown-model")
        for benchmark_result in payload.get("benchmarks", []):
            rows.extend(
                _iter_summary_rows(
                    source_file=results_file,
                    model=model,
                    benchmark=benchmark_result["benchmark"],
                    num_problems=benchmark_result.get("num_problems", 0),
                    partial=benchmark_result.get("partial", False),
                    num_complete_seed_runs=benchmark_result.get("num_complete_seed_runs", 0),
                    num_seed_runs=benchmark_result.get("num_seed_runs", 0),
                    summary_across_seeds=benchmark_result.get("summary_across_seeds"),
                    summary=benchmark_result.get("summary"),
                )
            )
        return rows

    if "experiments" in payload:
        fallback_model = payload.get("metadata", {}).get("model", "unknown-model")
        for experiment_result in payload.get("experiments", []):
            experiment_config = experiment_result.get("experiment_config", {})
            rows.extend(
                _iter_summary_rows(
                    source_file=results_file,
                    model=experiment_config.get("model", fallback_model),
                    benchmark=experiment_result["benchmark"],
                    num_problems=experiment_result.get("num_problems", 0),
                    partial=experiment_result.get("partial", False),
                    num_complete_seed_runs=experiment_result.get("num_complete_seed_runs", 0),
                    num_seed_runs=experiment_result.get("num_seed_runs", 0),
                    summary_across_seeds=experiment_result.get("summary_across_seeds"),
                    summary=experiment_result.get("summary"),
                    experiment_name=experiment_result.get("experiment_name"),
                    experiment_config=experiment_config,
                )
            )
        return rows

    raise ValueError(f"Unrecognized results payload in {results_file}")


def _fmt_cell(row: dict[str, Any] | None) -> str:
    if row is None:
        return "--"
    if "accuracy_mean" in row:
        return f"{row['accuracy_mean']:.1f} $\\\\pm$ {row['accuracy_stderr']:.2f}"
    return f"{row['accuracy']:.1f}"


def _row_priority(row: dict[str, Any]) -> tuple[int, int, int, int]:
    partial_penalty = 0 if not row.get("partial", False) else 1
    num_problems = int(row.get("num_problems", 0))
    complete_seed_runs = int(row.get("num_complete_seed_runs", 0))
    total_seed_runs = int(row.get("num_seed_runs", 0))
    return (partial_penalty, -num_problems, -complete_seed_runs, -total_seed_runs)


def _source_priority(row: dict[str, Any]) -> tuple[int, str]:
    source_file = Path(row["source_file"]).name
    preferred = {
        "results_from_progress.json": 0,
        "results_from_progress_current.json": 1,
        "results_from_progress_current_labeled.json": 2,
        "results.json": 3,
    }
    return (preferred.get(source_file, 10), source_file)


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (
            row.get("model"),
            row.get("benchmark"),
            row.get("method"),
            row.get("partial", False),
            row.get("num_problems", 0),
            row.get("experiment_name"),
        )
        current = deduped.get(key)
        if current is None:
            deduped[key] = row
            continue
        choose_new = False
        if _source_priority(row) < _source_priority(current):
            choose_new = True
        elif _source_priority(row) == _source_priority(current):
            if _row_priority(row) < _row_priority(current):
                choose_new = True
            elif _row_priority(row) == _row_priority(current):
                current_acc = row.get("accuracy_mean", row.get("accuracy", -1.0))
                existing_acc = current.get("accuracy_mean", current.get("accuracy", -1.0))
                if current_acc > existing_acc:
                    choose_new = True
        if choose_new:
            deduped[key] = row
    return list(deduped.values())


def _table_choice_priority(row: dict[str, Any], *, monitoring_mode: bool) -> tuple[Any, ...]:
    if monitoring_mode:
        return (
            -int(row.get("num_complete_seed_runs", 0)),
            -int(row.get("num_seed_runs", 0)),
            _row_priority(row),
            _source_priority(row),
        )
    return (_row_priority(row), _source_priority(row))


def build_model_method_table(rows: list[dict[str, Any]], *, monitoring_mode: bool) -> str:
    benchmarks = sorted({row["benchmark"] for row in rows})
    model_order: list[str] = []
    seen_models: set[str] = set()
    for row in rows:
        model = row["model"]
        if model not in seen_models:
            seen_models.add(model)
            model_order.append(model)

    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for row in rows:
        key = (row["model"], row["method"])
        benchmark = row["benchmark"]
        current = grouped.setdefault(key, {}).get(benchmark)
        if current is None or _table_choice_priority(row, monitoring_mode=monitoring_mode) < _table_choice_priority(
            current, monitoring_mode=monitoring_mode
        ):
            grouped[key][benchmark] = row

    ordered_keys: list[tuple[str, str]] = []
    for model in model_order:
        present_methods = {
            method
            for candidate_model, method in grouped.keys()
            if candidate_model == model
        }
        for method in CORE_METHOD_ORDER:
            if method in present_methods:
                ordered_keys.append((model, method))
        for method in sorted(present_methods - set(CORE_METHOD_ORDER)):
            ordered_keys.append((model, method))

    lines = [
        "\\begin{tabular}{ll" + "c" * len(benchmarks) + "}",
        "\\toprule",
        "Model & Method & " + " & ".join(benchmarks) + " \\\\",
        "\\midrule",
    ]
    for model, method in ordered_keys:
        cells = [_fmt_cell(grouped.get((model, method), {}).get(benchmark)) for benchmark in benchmarks]
        lines.append(f"{model} & {CORE_METHOD_LABELS.get(method, method)} & " + " & ".join(cells) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def _group_run_rows(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["model"], row["benchmark"]), []).append(row)
    return grouped


def _best_group_row(group_rows: list[dict[str, Any]], *, monitoring_mode: bool) -> dict[str, Any]:
    return sorted(
        group_rows,
        key=lambda row: (
            _table_choice_priority(row, monitoring_mode=monitoring_mode),
            row.get("method", ""),
        ),
    )[0]


def build_completion_table(rows: list[dict[str, Any]], *, monitoring_mode: bool) -> str:
    grouped = _group_run_rows(rows)
    lines = [
        "\\begin{tabular}{llccc}",
        "\\toprule",
        "Model & Benchmark & Problems & Seed runs & Partial \\\\",
        "\\midrule",
    ]
    for (model, benchmark), group_rows in sorted(grouped.items()):
        representative = _best_group_row(group_rows, monitoring_mode=monitoring_mode)
        complete = representative.get("num_complete_seed_runs", 0)
        total = representative.get("num_seed_runs", 0)
        partial = "yes" if representative.get("partial", False) else "no"
        lines.append(
            f"{model} & {benchmark} & {representative.get('num_problems', 0)} & "
            f"{complete}/{total} & {partial} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def build_method_coverage_markdown(rows: list[dict[str, Any]], *, monitoring_mode: bool) -> str:
    if not rows:
        return "# Publication Baseline Coverage\n\nNo publication-eligible rows were available.\n"

    grouped = _group_run_rows(rows)
    must_have = [
        "greedy",
        "majority_vote",
        "generated_test_filter",
        "self_debug",
        "falsification",
        "oracle",
    ]
    proxy_methods = ["code_t_proxy", "s_star_proxy", "prm_best_of_n_placeholder"]

    lines = [
        "# Publication Baseline Coverage",
        "",
        "This file tracks which reviewer-facing baselines are actually present in the current bundle.",
        "",
    ]
    for (model, benchmark), group_rows in sorted(grouped.items()):
        representative = _best_group_row(group_rows, monitoring_mode=monitoring_mode)
        present = {row["method"] for row in group_rows}
        missing = [CORE_METHOD_LABELS[m] for m in must_have if m not in present]
        present_proxies = [CORE_METHOD_LABELS[m] for m in proxy_methods if m in present]

        lines.append(f"## {model} :: {benchmark}")
        lines.append("")
        lines.append(f"- Problems: {representative.get('num_problems', 0)}")
        lines.append(
            f"- Seed runs: {representative.get('num_complete_seed_runs', 0)}/"
            f"{representative.get('num_seed_runs', 0)} complete"
        )
        lines.append(f"- Partial: {'yes' if representative.get('partial', False) else 'no'}")
        lines.append(
            "- Present core baselines: "
            + ", ".join(CORE_METHOD_LABELS[m] for m in must_have if m in present)
        )
        lines.append("- Missing core baselines: " + (", ".join(missing) if missing else "none"))
        lines.append("- Present proxy baselines: " + (", ".join(present_proxies) if present_proxies else "none"))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _best_method_rows(
    rows: list[dict[str, Any]], *, monitoring_mode: bool
) -> dict[tuple[str, str, str], dict[str, Any]]:
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["model"], row["benchmark"], row["method"])
        current = best.get(key)
        if current is None or _table_choice_priority(row, monitoring_mode=monitoring_mode) < _table_choice_priority(
            current, monitoring_mode=monitoring_mode
        ):
            best[key] = row
    return best


def _accuracy_value(row: dict[str, Any] | None) -> float | None:
    if row is None:
        return None
    if "accuracy_mean" in row:
        return float(row["accuracy_mean"])
    if "accuracy" in row:
        return float(row["accuracy"])
    return None


def _fmt_signed(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:+.1f}"


def _oracle_recovery(
    method_value: float | None,
    majority_value: float | None,
    oracle_value: float | None,
) -> float | None:
    if method_value is None or majority_value is None or oracle_value is None:
        return None
    denominator = oracle_value - majority_value
    if denominator <= 0:
        return None
    return 100.0 * (method_value - majority_value) / denominator


def _fmt_recovery(value: float | None) -> str:
    if value is None:
        return "--"
    return f"{value:.1f}\\%"


def build_gap_recovery_table(rows: list[dict[str, Any]], *, monitoring_mode: bool) -> str:
    best = _best_method_rows(rows, monitoring_mode=monitoring_mode)
    run_keys = sorted({(row["model"], row["benchmark"]) for row in rows})
    lines = [
        "\\begin{tabular}{llccccccc}",
        "\\toprule",
        "Model & Benchmark & Problems & MV$\\rightarrow$Oracle & F-SD & F-GTF & F recovery & SD recovery & GTF recovery \\\\",
        "\\midrule",
    ]
    for model, benchmark in run_keys:
        majority = best.get((model, benchmark, "majority_vote"))
        falsification = best.get((model, benchmark, "falsification"))
        self_debug = best.get((model, benchmark, "self_debug"))
        generated_filter = best.get((model, benchmark, "generated_test_filter"))
        oracle = best.get((model, benchmark, "oracle"))
        representative = falsification or oracle or majority or self_debug or generated_filter
        if representative is None:
            continue
        majority_value = _accuracy_value(majority)
        oracle_value = _accuracy_value(oracle)
        falsification_value = _accuracy_value(falsification)
        self_debug_value = _accuracy_value(self_debug)
        generated_filter_value = _accuracy_value(generated_filter)
        mv_oracle_gap = None
        if majority_value is not None and oracle_value is not None:
            mv_oracle_gap = oracle_value - majority_value
        lines.append(
            f"{model} & {benchmark} & {representative.get('num_problems', 0)} & "
            f"{_fmt_signed(mv_oracle_gap)} & "
            f"{_fmt_signed(None if falsification_value is None or self_debug_value is None else falsification_value - self_debug_value)} & "
            f"{_fmt_signed(None if falsification_value is None or generated_filter_value is None else falsification_value - generated_filter_value)} & "
            f"{_fmt_recovery(_oracle_recovery(falsification_value, majority_value, oracle_value))} & "
            f"{_fmt_recovery(_oracle_recovery(self_debug_value, majority_value, oracle_value))} & "
            f"{_fmt_recovery(_oracle_recovery(generated_filter_value, majority_value, oracle_value))} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def build_highlights_markdown(rows: list[dict[str, Any]], *, monitoring_mode: bool) -> str:
    if not rows:
        return "# Publication Highlights\n\nNo publication-eligible rows were available.\n"

    best = _best_method_rows(rows, monitoring_mode=monitoring_mode)
    run_keys = sorted({(row["model"], row["benchmark"]) for row in rows})
    majority_failures: list[tuple[float, str]] = []
    self_debug_gaps: list[tuple[float, str]] = []
    recoveries: list[tuple[float, str]] = []

    for model, benchmark in run_keys:
        greedy = _accuracy_value(best.get((model, benchmark, "greedy")))
        majority = _accuracy_value(best.get((model, benchmark, "majority_vote")))
        falsification = _accuracy_value(best.get((model, benchmark, "falsification")))
        self_debug = _accuracy_value(best.get((model, benchmark, "self_debug")))
        oracle = _accuracy_value(best.get((model, benchmark, "oracle")))

        if greedy is not None and majority is not None and greedy > majority:
            majority_failures.append((greedy - majority, f"{model} :: {benchmark} ({greedy:.1f} vs {majority:.1f})"))
        if falsification is not None and self_debug is not None:
            self_debug_gaps.append((falsification - self_debug, f"{model} :: {benchmark} ({falsification:.1f} vs {self_debug:.1f})"))
        recovery = _oracle_recovery(falsification, majority, oracle)
        if recovery is not None:
            recoveries.append((recovery, f"{model} :: {benchmark} ({recovery:.1f}\\%)"))

    lines = [
        "# Publication Highlights",
        "",
        "This file summarizes the most reviewer-relevant patterns in the current publication bundle.",
        "",
        "## Majority-vote failure cases",
        "",
    ]
    if majority_failures:
        for _, text in sorted(majority_failures, reverse=True):
            lines.append(f"- {text}")
    else:
        lines.append("- None in the current bundle.")

    lines.extend(["", "## Falsification vs self-debug", ""])
    if self_debug_gaps:
        for gap, text in sorted(self_debug_gaps, reverse=True):
            lines.append(f"- {_fmt_signed(gap)}: {text}")
    else:
        lines.append("- No rows contained both falsification and self-debug.")

    lines.extend(["", "## Oracle-gap recovery by falsification", ""])
    if recoveries:
        for _, text in sorted(recoveries, reverse=True):
            lines.append(f"- {text}")
    else:
        lines.append("- No rows contained majority vote, falsification, and oracle together.")

    return "\n".join(lines).rstrip() + "\n"


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        if not fieldnames:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_status_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "# Publication Bundle Status\n\nNo publication-eligible rows were available.\n"
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["model"], row["benchmark"]), []).append(row)

    lines = ["# Publication Bundle Status", ""]
    for (model, benchmark), group_rows in sorted(grouped.items()):
        lines.append(f"## {model} :: {benchmark}")
        lines.append("")
        lines.append("| Method | Accuracy | Problems | Partial | Source |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        for row in sorted(group_rows, key=lambda item: (_row_priority(item), item["method"])):
            lines.append(
                "| "
                + " | ".join(
                    [
                        CORE_METHOD_LABELS.get(row["method"], row["method"]),
                        _fmt_cell(row),
                        str(row.get("num_problems", 0)),
                        "yes" if row.get("partial", False) else "no",
                        Path(row["source_file"]).name,
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a publication-ready bundle from multiple results.json files.")
    parser.add_argument("--results-file", action="append", default=[], help="Path to a results.json file. May be passed multiple times.")
    parser.add_argument("--results-root", help="Optional directory to scan recursively for results.json files.")
    parser.add_argument("--output-dir", default="figures/publication_bundle")
    parser.add_argument("--exclude-benchmark", action="append", default=["synthetic_demo"])
    parser.add_argument("--exclude-model", action="append", default=["mock-model", "unknown-model"])
    parser.add_argument(
        "--include-partial",
        action="store_true",
        help="Include in-progress partial rows from progress-collected results.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Write an empty bundle instead of failing when all rows are filtered out.",
    )
    args = parser.parse_args()

    files = [Path(item) for item in args.results_file]
    if args.results_root:
        files.extend(sorted(Path(args.results_root).glob("**/results.json")))
        files.extend(sorted(Path(args.results_root).glob("**/results_from_progress*.json")))
    files = sorted({path for path in files if path.exists()})
    if not files:
        raise SystemExit("No results files found.")

    rows: list[dict[str, Any]] = []
    for results_file in files:
        rows.extend(iter_benchmark_rows(results_file))
    rows = [
        row
        for row in rows
        if row["benchmark"] not in set(args.exclude_benchmark)
        and row["model"] not in set(args.exclude_model)
        and (args.include_partial or not row.get("partial", False))
    ]
    rows = _dedupe_rows(rows)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not rows and not args.allow_empty:
        raise SystemExit("All rows were filtered out; adjust --exclude-benchmark/--exclude-model.")
    (output_dir / "publication_summary.json").write_text(json.dumps({"rows": rows}, indent=2), encoding="utf-8")
    write_csv(rows, output_dir / "publication_summary.csv")
    if rows:
        table_text = build_model_method_table(rows, monitoring_mode=args.include_partial)
        completion_text = build_completion_table(rows, monitoring_mode=args.include_partial)
        gap_recovery_text = build_gap_recovery_table(rows, monitoring_mode=args.include_partial)
    else:
        table_text = "% No publication-eligible rows were available.\n"
        completion_text = "% No publication-eligible rows were available.\n"
        gap_recovery_text = "% No publication-eligible rows were available.\n"
    (output_dir / "publication_main_table.tex").write_text(table_text, encoding="utf-8")
    (output_dir / "publication_completion_table.tex").write_text(completion_text, encoding="utf-8")
    (output_dir / "publication_gap_recovery_table.tex").write_text(gap_recovery_text, encoding="utf-8")
    (output_dir / "publication_status.md").write_text(build_status_markdown(rows), encoding="utf-8")
    (output_dir / "publication_method_coverage.md").write_text(
        build_method_coverage_markdown(rows, monitoring_mode=args.include_partial),
        encoding="utf-8",
    )
    (output_dir / "publication_highlights.md").write_text(
        build_highlights_markdown(rows, monitoring_mode=args.include_partial),
        encoding="utf-8",
    )
    print(f"Wrote publication bundle with {len(rows)} rows to {output_dir}")


if __name__ == "__main__":
    main()
