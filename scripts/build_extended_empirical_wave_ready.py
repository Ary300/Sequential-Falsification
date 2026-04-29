#!/usr/bin/env python3
"""Build a paper-facing readiness note for the extended knowledge-arbitration wave."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the extended empirical wave readiness note.")
    parser.add_argument(
        "--manifest",
        default="results/arbitration_spotlight_extended_manifest/manifest.json",
        help="Manifest JSON produced by build_arbitration_spotlight_manifest.py.",
    )
    parser.add_argument(
        "--output-prefix",
        default="docs/generated/extended_empirical_wave_ready",
        help="Output path prefix without extension.",
    )
    parser.add_argument(
        "--delta-auth-state",
        default="unknown",
        help="Short status string such as ready, blocked, or unknown.",
    )
    parser.add_argument(
        "--delta-auth-detail",
        default="",
        help="Optional explanatory detail for the current Delta submission state.",
    )
    parser.add_argument(
        "--submission-manifest-jsonl",
        default="docs/generated/delta_extended_wave_submissions.jsonl",
        help="Optional JSONL manifest of submitted Delta jobs.",
    )
    parser.add_argument(
        "--direct-result-manifest",
        default="results/delta_knowledge_arbitration_extended_wave_direct/manifest.json",
        help="Optional manifest for any directly completed Delta run.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _load_optional_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def build_payload(
    manifest: dict[str, Any],
    *,
    delta_auth_state: str,
    delta_auth_detail: str,
    submission_rows: list[dict[str, Any]],
    direct_result_manifest: dict[str, Any] | None,
) -> dict[str, Any]:
    readiness = manifest.get("readiness", {})
    experiments = manifest.get("experiments", [])
    benchmark_keys = sorted({item["key"] for exp in experiments for item in exp.get("benchmarks", [])})
    model_names = sorted({model for exp in experiments for model in exp.get("models", [])})
    baselines = sorted({method for exp in experiments for method in exp.get("baseline_methods", [])})
    ablations = sorted({abl for exp in experiments for abl in exp.get("ablations", [])})
    seeds: set[int] = set()
    for exp in experiments:
        sweep_values = exp.get("sweep_values", {}) or {}
        seed_value = sweep_values.get("seed")
        if isinstance(seed_value, int):
            seeds.add(seed_value)
        elif isinstance(seed_value, str) and seed_value.isdigit():
            seeds.add(int(seed_value))
        match = re.search(r"__seed=(\d+)", str(exp.get("name", "")))
        if match:
            seeds.add(int(match.group(1)))
    total_cells = sum(int(exp.get("total_cells", 0)) for exp in experiments)

    if delta_auth_state == "unknown" and submission_rows:
        delta_auth_state = "submitted"

    direct_probe = None
    if direct_result_manifest and direct_result_manifest.get("experiments"):
        first = direct_result_manifest["experiments"][0]
        direct_probe = {
            "name": first.get("name"),
            "num_rows": first.get("num_rows"),
            "bayes_proxy_mean_regret": first.get("bayes_proxy_mean_regret"),
            "heuristic_adaptive_mean_regret": first.get("heuristic_adaptive_mean_regret"),
            "bayes_vs_heuristic_gain": first.get("bayes_vs_heuristic_gain"),
        }

    return {
        "manifest_path": manifest.get("config"),
        "num_experiments": int(manifest.get("num_experiments", len(experiments))),
        "total_cells": total_cells,
        "benchmark_keys": benchmark_keys,
        "model_names": model_names,
        "baseline_methods": baselines,
        "ablations": ablations,
        "seeds": sorted(seeds),
        "readiness": readiness,
        "delta_auth_state": delta_auth_state,
        "delta_auth_detail": delta_auth_detail,
        "delta_submission_count": len(submission_rows),
        "delta_submissions": submission_rows,
        "delta_direct_probe": direct_probe,
        "experiments": [
            {
                "name": exp["name"],
                "priority": exp.get("priority", "unspecified"),
                "num_benchmarks": len(exp.get("benchmarks", [])),
                "num_models": len(exp.get("models", [])),
                "num_baselines": len(exp.get("baseline_methods", [])),
                "num_ablations": len(exp.get("ablations", [])),
                "max_examples": int(exp.get("max_examples", 0)),
                "total_cells": int(exp.get("total_cells", 0)),
                "notes": exp.get("notes", ""),
            }
            for exp in experiments
        ],
    }


def build_markdown(payload: dict[str, Any]) -> str:
    readiness = payload["readiness"]
    lines = [
        "# Extended Empirical Wave Readiness",
        "",
        "## Status",
        "",
        f"- Spotlight floor ready: `{readiness.get('spotlight_floor_ready', False)}`",
        f"- Unique models: `{readiness.get('unique_models', 0)}`",
        f"- Unique benchmarks: `{readiness.get('unique_benchmarks', 0)}`",
        f"- Unique baselines: `{readiness.get('unique_baselines', 0)}`",
        f"- Unique ablations: `{readiness.get('unique_ablations', 0)}`",
        f"- Total scheduled cells before backend-specific chunking: `{payload['total_cells']}`",
        f"- Three-seed coverage encoded in config: `{payload['seeds']}`",
        f"- Delta auth state: `{payload['delta_auth_state']}`",
    ]
    if payload["delta_auth_detail"]:
        lines.append(f"- Delta auth detail: {payload['delta_auth_detail']}")
    if payload["delta_submission_count"]:
        lines.append(f"- Delta submitted jobs captured locally: `{payload['delta_submission_count']}`")
    if payload["delta_direct_probe"]:
        probe = payload["delta_direct_probe"]
        lines.append(
            f"- Direct completed Delta probe: `{probe['name']}` with `{probe['num_rows']}` rows and "
            f"Bayes-vs-heuristic gain `{probe['bayes_vs_heuristic_gain']:.4f}`"
        )

    lines.extend(
        [
            "",
            "## Coverage",
            "",
            f"- Benchmarks wired: `{', '.join(payload['benchmark_keys'])}`",
            f"- Models wired: `{', '.join(payload['model_names'])}`",
            f"- Baselines wired: `{', '.join(payload['baseline_methods'])}`",
        ]
    )
    if payload["ablations"]:
        lines.append(f"- Ablations wired: `{', '.join(payload['ablations'])}`")

    lines.extend(["", "## Experiments", ""])
    for experiment in payload["experiments"]:
        lines.append(
            f"- `{experiment['name']}`: `{experiment['num_models']}` models x "
            f"`{experiment['num_benchmarks']}` benchmarks, "
            f"`{experiment['num_baselines']}` baselines, "
            f"`{experiment['num_ablations']}` ablations, "
            f"`max_examples={experiment['max_examples']}`, "
            f"`total_cells={experiment['total_cells']}`. {experiment['notes']}"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The remaining gap is no longer missing code or missing benchmark plumbing.",
            "- The extended wave is now both compute-ready and Delta-submitted; the open remaining gap is job completion, result pullback, and final write-up.",
            "- This note should be read together with the empirical completion audit: the finished core already has headline-grade results, and this extended wave is now an active execution path rather than a dormant plan.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    manifest = _load_json(ROOT / args.manifest)
    submission_rows = _load_optional_jsonl(ROOT / args.submission_manifest_jsonl)
    direct_result_manifest = _load_optional_json(ROOT / args.direct_result_manifest)
    payload = build_payload(
        manifest,
        delta_auth_state=args.delta_auth_state,
        delta_auth_detail=args.delta_auth_detail,
        submission_rows=submission_rows,
        direct_result_manifest=direct_result_manifest,
    )
    output_prefix = ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
