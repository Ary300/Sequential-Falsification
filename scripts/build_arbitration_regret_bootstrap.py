#!/usr/bin/env python3
"""Bootstrap headline regret gaps from arbitration report rows."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
NAMED_COMPARATORS = ["self_rag", "astute_rag", "cocoa", "adacad", "cad", "crag", "heuristic_adaptive"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap Bayes-vs-baseline regret gaps from report JSON.")
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--num-bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(q * (len(ordered) - 1))))
    return ordered[idx]


def _pretty(policy: str) -> str:
    mapping = {
        "bayes_proxy": "Bayes proxy",
        "self_rag": "Self-RAG",
        "astute_rag": "Astute RAG",
        "cocoa": "CoCoA",
        "adacad": "AdaCAD",
        "cad": "CAD",
        "crag": "CRAG",
        "heuristic_adaptive": "Heuristic adaptive",
    }
    return mapping.get(policy, policy.replace("_", " ").title())


def _rows_by_series(report: dict) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for row in report["regret"]["rows"]:
        out.setdefault(row["series"], {})[row["policy"]] = float(row["mean_regret"])
    return out


def build_summary(report: dict, *, num_bootstrap: int, seed: int) -> dict:
    series_map = _rows_by_series(report)
    series_names = sorted(series_map)
    rng = random.Random(seed)

    overall = {row["policy"]: float(row["mean_regret"]) for row in report["regret"]["overall"]}
    strongest_named = min((policy for policy in NAMED_COMPARATORS if policy in overall), key=lambda p: overall[p])

    def gap_for(sampled_series: list[str], baseline: str) -> float:
        bayes_vals = [series_map[name]["bayes_proxy"] for name in sampled_series]
        baseline_vals = [series_map[name][baseline] for name in sampled_series]
        return mean(baseline_vals) - mean(bayes_vals)

    heuristic_boot = []
    named_boot = []
    for _ in range(num_bootstrap):
        sampled = [rng.choice(series_names) for _ in series_names]
        heuristic_boot.append(gap_for(sampled, "heuristic_adaptive"))
        named_boot.append(gap_for(sampled, strongest_named))

    summary = {
        "num_series": len(series_names),
        "bayes_proxy_mean_regret": round(overall["bayes_proxy"], 4),
        "heuristic_mean_regret": round(overall["heuristic_adaptive"], 4),
        "strongest_named_comparator": strongest_named,
        "strongest_named_comparator_mean_regret": round(overall[strongest_named], 4),
        "bayes_advantage_vs_heuristic": round(overall["heuristic_adaptive"] - overall["bayes_proxy"], 4),
        "bayes_advantage_vs_strongest_named": round(overall[strongest_named] - overall["bayes_proxy"], 4),
        "bootstrap": {
            "num_bootstrap": num_bootstrap,
            "seed": seed,
            "bayes_vs_heuristic": {
                "mean_gap": round(mean(heuristic_boot), 4),
                "ci95_low": round(_quantile(heuristic_boot, 0.025), 4),
                "ci95_high": round(_quantile(heuristic_boot, 0.975), 4),
            },
            "bayes_vs_strongest_named": {
                "baseline": strongest_named,
                "mean_gap": round(mean(named_boot), 4),
                "ci95_low": round(_quantile(named_boot, 0.025), 4),
                "ci95_high": round(_quantile(named_boot, 0.975), 4),
            },
        },
    }
    return summary


def build_markdown(summary: dict) -> str:
    h = summary["bootstrap"]
    lines = [
        "# Arbitration Regret Bootstrap",
        "",
        f"- Number of series: `{summary['num_series']}`",
        f"- Bayes proxy mean regret: `{summary['bayes_proxy_mean_regret']}`",
        f"- Heuristic mean regret: `{summary['heuristic_mean_regret']}`",
        f"- Bayes advantage vs heuristic: `{summary['bayes_advantage_vs_heuristic']}`",
        f"- Bayes vs heuristic bootstrap CI: "
        f"`[{h['bayes_vs_heuristic']['ci95_low']}, {h['bayes_vs_heuristic']['ci95_high']}]`",
        f"- Strongest named comparator: `{_pretty(summary['strongest_named_comparator'])}` "
        f"at `{summary['strongest_named_comparator_mean_regret']}`",
        f"- Bayes advantage vs strongest named comparator: `{summary['bayes_advantage_vs_strongest_named']}`",
        f"- Bayes vs strongest named comparator bootstrap CI: "
        f"`[{h['bayes_vs_strongest_named']['ci95_low']}, {h['bayes_vs_strongest_named']['ci95_high']}]`",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    report = _load(args.report_json)
    summary = build_summary(report, num_bootstrap=args.num_bootstrap, seed=args.seed)
    prefix = ROOT / args.output_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    prefix.with_suffix(".md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps({"json": str(prefix.with_suffix('.json')), "md": str(prefix.with_suffix('.md'))}, indent=2))


if __name__ == "__main__":
    main()
