#!/usr/bin/env python3
"""Build Holm-corrected per-benchmark sign tables against all named baselines."""

from __future__ import annotations

import argparse
import json
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "results/arbitration_spotlight_t12_benchmark_v2/report/arbitration_summary.json"
DEFAULT_OUT = ROOT / "docs/generated/named_baseline_holm_table"
NAMED_BASELINES = [
    "self_rag",
    "astute_rag",
    "adacad",
    "madam_rag",
    "juice",
    "nwcad",
    "crag",
    "cad",
    "cocoa",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Holm-corrected baseline tables.")
    parser.add_argument("--report-json", default=str(DEFAULT_REPORT))
    parser.add_argument("--output-prefix", default=str(DEFAULT_OUT))
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sign_pvalue(num_positive: int, n: int) -> float:
    if n <= 0:
        return 1.0
    return sum(comb(n, k) for k in range(num_positive, n + 1)) / (2**n)


def _holm_adjust(rows: list[dict], key: str) -> None:
    indexed = sorted(enumerate(rows), key=lambda item: item[1][key])
    m = len(indexed)
    adjusted = [0.0] * m
    running = 0.0
    for rank, (_, row) in enumerate(indexed, start=1):
        candidate = min(1.0, (m - rank + 1) * float(row[key]))
        running = max(running, candidate)
        adjusted[rank - 1] = running
    for ranked, (orig_idx, _) in enumerate(indexed):
        rows[orig_idx][f"{key}_holm"] = round(adjusted[ranked], 4)


def build_summary(report: dict) -> dict:
    series_map: dict[tuple[str, str], dict[str, float]] = {}
    for row in report["regret"]["rows"]:
        benchmark, model = row["series"].split("::", 1)
        values = series_map.setdefault((benchmark, model), {})
        values[row["policy"]] = float(row["mean_regret"])

    summary: dict[str, list[dict]] = {}
    for baseline in NAMED_BASELINES:
        rows = []
        by_benchmark: dict[str, list[float]] = {}
        for (benchmark, _model), values in series_map.items():
            if "bayes_proxy" not in values or baseline not in values:
                continue
            by_benchmark.setdefault(benchmark, []).append(values[baseline] - values["bayes_proxy"])
        for benchmark, gaps in sorted(by_benchmark.items()):
            signs = [1 if gap > 0 else -1 if gap < 0 else 0 for gap in gaps]
            positive = sum(sign > 0 for sign in signs)
            n = len(gaps)
            p = _sign_pvalue(positive, n)
            rows.append(
                {
                    "benchmark": benchmark,
                    "mean_gap": round(sum(gaps) / n, 4),
                    "positive_models": positive,
                    "num_models": n,
                    "one_sided_sign_p": round(p, 4),
                }
            )
        _holm_adjust(rows, "one_sided_sign_p")
        summary[baseline] = rows
    return {
        "source_report": str(Path(args.report_json).resolve().relative_to(ROOT)),
        "named_baselines": summary,
    }


def build_markdown(summary: dict) -> str:
    lines = [
        "# Named Baseline Holm-Corrected Table",
        "",
        "This note reports Bayes-vs-baseline per-benchmark sign tests on the finished spotlight matrix.",
        "For each named baseline, Holm correction is applied across the five benchmark families.",
        "",
    ]
    for baseline, rows in summary["named_baselines"].items():
        title = baseline.replace("_", "-")
        lines.extend(
            [
                f"## {title}",
                "",
                "| Benchmark | Mean gap | Wins | One-sided sign p | Holm p |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['benchmark']} | {row['mean_gap']:.4f} | {row['positive_models']}/{row['num_models']} | "
                f"{row['one_sided_sign_p']:.4f} | {row['one_sided_sign_p_holm']:.4f} |"
            )
        lines.append("")
    return "\n".join(lines)


def build_latex(summary: dict) -> str:
    lines = [
        "\\begin{tabular}{llccc}",
        "\\toprule",
        "Baseline & Benchmark & Mean gap & Wins & Holm $p$ \\\\",
        "\\midrule",
    ]
    first = True
    for baseline, rows in summary["named_baselines"].items():
        pretty = baseline.replace("_", "-")
        for i, row in enumerate(rows):
            baseline_cell = pretty if i == 0 else ""
            lines.append(
                f"{baseline_cell} & {row['benchmark']} & {row['mean_gap']:.4f} & "
                f"{row['positive_models']}/{row['num_models']} & {row['one_sided_sign_p_holm']:.4f} \\\\"
            )
        if not first:
            pass
        first = False
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    global args
    args = parse_args()
    summary = build_summary(_load(args.report_json))
    prefix = Path(args.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    prefix.with_suffix(".tex").write_text(build_latex(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md')), "tex": str(prefix.with_suffix('.tex'))}, indent=2))


if __name__ == "__main__":
    main()
