#!/usr/bin/env python3
"""Estimate Track B verifier capacity on one or more benchmarks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "src"))

from capacity import (  # noqa: E402
    CapacityConfig,
    capacity_gain_predictions,
    collect_capacity_records,
    rank_verifiers_by_capacity,
    synthetic_capacity_sanity,
)
from generate import GenerationConfig  # noqa: E402
from utils.io import dump_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate verifier capacity for Track B.")
    parser.add_argument("--benchmark", help="Single benchmark.")
    parser.add_argument("--benchmarks", help="Comma-separated benchmarks.")
    parser.add_argument("--verifiers", default="majority,public_test,sce_trace")
    parser.add_argument("--backend", default="mock")
    parser.add_argument("--model", default="mock-model")
    parser.add_argument("--api-base", default="http://localhost:8000/v1")
    parser.add_argument("--api-key", default="none")
    parser.add_argument("--request-timeout", type=float, default=15.0)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-candidates", type=int, default=16)
    parser.add_argument("--max-problems", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--output-dir", default="results/capacity_pilot")
    parser.add_argument("--sanity-check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    benchmarks: list[str] = []
    if args.benchmark:
        benchmarks.append(args.benchmark)
    if args.benchmarks:
        benchmarks.extend([item.strip() for item in args.benchmarks.split(",") if item.strip()])

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.sanity_check:
        sanity = synthetic_capacity_sanity(seed=args.seed)
        dump_json({"sanity": sanity}, output_dir / "sanity.json")
        print(json.dumps({"sanity_capacity": sanity["capacity"]}, indent=2))
        return

    if not benchmarks:
        raise SystemExit("Provide --benchmark or --benchmarks.")

    generation_config = GenerationConfig(
        backend=args.backend,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        request_timeout=args.request_timeout,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        seed=args.seed,
    )
    capacity_config = CapacityConfig(
        verifier_names=[item.strip() for item in args.verifiers.split(",") if item.strip()],
        n_candidates=args.n_candidates,
        timeout=args.timeout,
        max_problems=args.max_problems,
        data_root=args.data_root,
    )

    benchmark_payloads: list[dict[str, Any]] = []
    for benchmark in benchmarks:
        payload = collect_capacity_records(
            benchmark=benchmark,
            generation_config=generation_config,
            capacity_config=capacity_config,
        )
        payload["ranking"] = rank_verifiers_by_capacity(payload)
        for verifier_name, verifier_payload in payload.get("verifiers", {}).items():
            capacity_value = float(verifier_payload.get("summary", {}).get("capacity", 0.0))
            verifier_payload["predicted_curves"] = capacity_gain_predictions(
                oracle_accuracy=1.0,
                capacity_value=capacity_value,
                budgets=[1, 4, 8, 16, 32, 64],
            )
        benchmark_payloads.append(payload)

    result = {
        "benchmarks": benchmark_payloads,
        "metadata": {
            "model": args.model,
            "backend": args.backend,
            "verifiers": capacity_config.verifier_names,
            "n_candidates": args.n_candidates,
            "max_problems": args.max_problems,
            "seed": args.seed,
        },
    }
    dump_json(result, output_dir / "results.json")
    print(
        json.dumps(
            {
                "benchmarks": [payload["benchmark"] for payload in benchmark_payloads],
                "ranking": {payload["benchmark"]: payload["ranking"] for payload in benchmark_payloads},
                "output_dir": str(output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
