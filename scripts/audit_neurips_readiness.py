"""Audit publication bundles for NeurIPS-style result readiness.

The goal is not to decide whether the paper is "accepted"; it is to prevent
accidental over-claiming.  The audit separates missing coverage, partial rows,
baseline gaps, and weak headline claims so the manuscript can stay honest while
cluster runs are still landing.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CORE_METHODS = [
    "greedy",
    "majority_vote",
    "generated_test_filter",
    "self_debug",
    "falsification",
    "oracle",
]

PROXY_METHODS = ["code_t_proxy", "s_star_proxy"]

TARGET_BENCHMARKS = ["humaneval_plus", "mbpp_plus", "livecodebench_v6", "math500"]


def _accuracy(row: dict[str, Any] | None) -> float | None:
    if row is None:
        return None
    if "accuracy_mean" in row:
        return float(row["accuracy_mean"])
    if "accuracy" in row:
        return float(row["accuracy"])
    return None


def _best_rows(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row["model"], row["benchmark"], row["method"])
        current = best.get(key)
        if current is None:
            best[key] = row
            continue
        current_rank = (
            bool(current.get("partial", False)),
            -int(current.get("num_problems", 0)),
            -int(current.get("num_complete_seed_runs", 0)),
        )
        row_rank = (
            bool(row.get("partial", False)),
            -int(row.get("num_problems", 0)),
            -int(row.get("num_complete_seed_runs", 0)),
        )
        if row_rank < current_rank:
            best[key] = row
    return best


def _recovery(method: float | None, majority: float | None, oracle: float | None) -> float | None:
    if method is None or majority is None or oracle is None:
        return None
    gap = oracle - majority
    if gap <= 0:
        return None
    return 100.0 * (method - majority) / gap


def _fmt(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "--"
    return f"{value:.1f}{suffix}"


def audit_rows(rows: list[dict[str, Any]], *, min_complete_seeds: int, min_problem_counts: dict[str, int]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["benchmark"])].append(row)
    best = _best_rows(rows)

    models = sorted({row["model"] for row in rows})
    issues: list[dict[str, Any]] = []
    headline_rows: list[dict[str, Any]] = []

    for model in models:
        for benchmark in TARGET_BENCHMARKS:
            run_rows = grouped.get((model, benchmark), [])
            if not run_rows:
                issues.append(
                    {
                        "severity": "missing",
                        "model": model,
                        "benchmark": benchmark,
                        "message": "No row for target benchmark/model pair.",
                    }
                )
                continue

            representative = max(run_rows, key=lambda row: int(row.get("num_problems", 0)))
            expected_problem_count = min_problem_counts.get(benchmark, 0)
            if int(representative.get("num_problems", 0)) < expected_problem_count:
                issues.append(
                    {
                        "severity": "coverage",
                        "model": model,
                        "benchmark": benchmark,
                        "message": (
                            f"Only {representative.get('num_problems', 0)} problems; "
                            f"target is {expected_problem_count}."
                        ),
                    }
                )

            if any(row.get("partial", False) for row in run_rows):
                issues.append(
                    {
                        "severity": "partial",
                        "model": model,
                        "benchmark": benchmark,
                        "message": "At least one best-available row is progress-derived/partial.",
                    }
                )

            complete_seed_runs = max(int(row.get("num_complete_seed_runs", 0)) for row in run_rows)
            if complete_seed_runs < min_complete_seeds:
                issues.append(
                    {
                        "severity": "seeds",
                        "model": model,
                        "benchmark": benchmark,
                        "message": f"Only {complete_seed_runs} complete seed runs; target is {min_complete_seeds}.",
                    }
                )

            present = {row["method"] for row in run_rows}
            missing_core = [method for method in CORE_METHODS if method not in present]
            if missing_core:
                issues.append(
                    {
                        "severity": "baseline",
                        "model": model,
                        "benchmark": benchmark,
                        "message": "Missing core methods: " + ", ".join(missing_core),
                    }
                )
            missing_proxy = [method for method in PROXY_METHODS if method not in present]
            if benchmark in {"humaneval_plus", "mbpp_plus"} and missing_proxy:
                issues.append(
                    {
                        "severity": "proxy",
                        "model": model,
                        "benchmark": benchmark,
                        "message": "Missing local proxy baselines: " + ", ".join(missing_proxy),
                    }
                )

            majority = _accuracy(best.get((model, benchmark, "majority_vote")))
            oracle = _accuracy(best.get((model, benchmark, "oracle")))
            falsification = _accuracy(best.get((model, benchmark, "falsification")))
            self_debug = _accuracy(best.get((model, benchmark, "self_debug")))
            generated_filter = _accuracy(best.get((model, benchmark, "generated_test_filter")))
            recovery = _recovery(falsification, majority, oracle)
            fsd_gap = None if falsification is None or self_debug is None else falsification - self_debug
            fgtf_gap = None if falsification is None or generated_filter is None else falsification - generated_filter

            headline_rows.append(
                {
                    "model": model,
                    "benchmark": benchmark,
                    "majority_vote": majority,
                    "falsification": falsification,
                    "self_debug": self_debug,
                    "generated_test_filter": generated_filter,
                    "oracle": oracle,
                    "oracle_gap_recovery": recovery,
                    "falsification_minus_self_debug": fsd_gap,
                    "falsification_minus_generated_test_filter": fgtf_gap,
                }
            )

            if recovery is not None and recovery < 85.0:
                issues.append(
                    {
                        "severity": "headline",
                        "model": model,
                        "benchmark": benchmark,
                        "message": f"Falsification recovers only {recovery:.1f}% of majority-to-oracle gap.",
                    }
                )
            if fsd_gap is not None and fsd_gap < -1.0:
                issues.append(
                    {
                        "severity": "self_debug",
                        "model": model,
                        "benchmark": benchmark,
                        "message": f"Falsification trails self-debug by {-fsd_gap:.1f} points.",
                    }
                )
            if fgtf_gap is not None and fgtf_gap < -1.0:
                issues.append(
                    {
                        "severity": "gtf",
                        "model": model,
                        "benchmark": benchmark,
                        "message": f"Falsification trails generated-test filtering by {-fgtf_gap:.1f} points.",
                    }
                )

    return {"headline_rows": headline_rows, "issues": issues}


def build_markdown(audit: dict[str, Any]) -> str:
    rows = audit["headline_rows"]
    issues = audit["issues"]
    lines = [
        "# NeurIPS Readiness Audit",
        "",
        "This audit is intentionally conservative. It flags missing rows, partial results, thin seed coverage, and weak headline comparisons so the paper does not over-claim.",
        "",
        "## Headline Metrics",
        "",
        "| Model | Benchmark | MV | Falsification | Self-debug | Gen-test filter | Oracle | F recovery | F-SD | F-GTF |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["model"],
                    row["benchmark"],
                    _fmt(row["majority_vote"]),
                    _fmt(row["falsification"]),
                    _fmt(row["self_debug"]),
                    _fmt(row["generated_test_filter"]),
                    _fmt(row["oracle"]),
                    _fmt(row["oracle_gap_recovery"], "%"),
                    _fmt(row["falsification_minus_self_debug"]),
                    _fmt(row["falsification_minus_generated_test_filter"]),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Issues", ""])
    if not issues:
        lines.append("- No issues under the current audit thresholds.")
    else:
        for issue in issues:
            lines.append(
                f"- `{issue['severity']}` {issue['model']} :: {issue['benchmark']}: {issue['message']}"
            )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit publication bundle readiness for a NeurIPS-style submission.")
    parser.add_argument("--publication-summary", required=True, help="Path to publication_summary.json.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--min-complete-seeds", type=int, default=3)
    parser.add_argument("--humaneval-min-problems", type=int, default=164)
    parser.add_argument("--mbpp-min-problems", type=int, default=378)
    parser.add_argument("--livecodebench-min-problems", type=int, default=400)
    parser.add_argument("--math500-min-problems", type=int, default=500)
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    payload = json.loads(Path(args.publication_summary).read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    min_problem_counts = {
        "humaneval_plus": args.humaneval_min_problems,
        "mbpp_plus": args.mbpp_min_problems,
        "livecodebench_v6": args.livecodebench_min_problems,
        "math500": args.math500_min_problems,
    }
    audit = audit_rows(rows, min_complete_seeds=args.min_complete_seeds, min_problem_counts=min_problem_counts)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "neurips_readiness.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (output_dir / "neurips_readiness.md").write_text(build_markdown(audit), encoding="utf-8")
    print(f"Wrote NeurIPS readiness audit to {output_dir}")

    if args.fail_on_critical:
        critical = [issue for issue in audit["issues"] if issue["severity"] in {"missing", "baseline", "partial"}]
        if critical:
            raise SystemExit(f"Readiness audit found {len(critical)} critical issue(s).")


if __name__ == "__main__":
    main()
