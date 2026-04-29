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
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(manifest: dict[str, Any], *, delta_auth_state: str, delta_auth_detail: str) -> dict[str, Any]:
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
            "- The remaining gap is authenticated external compute for the newly wired model and benchmark wave.",
            "- This note should be read together with the empirical completion audit: the finished core already has headline-grade results, and this extended wave is the next compute-ready upgrade path.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    manifest = _load_json(ROOT / args.manifest)
    payload = build_payload(
        manifest,
        delta_auth_state=args.delta_auth_state,
        delta_auth_detail=args.delta_auth_detail,
    )
    output_prefix = ROOT / args.output_prefix
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    dump_json(payload, output_prefix.with_suffix(".json"))
    output_prefix.with_suffix(".md").write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
