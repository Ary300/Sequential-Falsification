#!/usr/bin/env python3
"""Run focused real-generation theorem-3 experiments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from knowledge_arbitration.real_generation import GenerationConfig, run_real_generation_experiment  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run theorem-3 real-generation experiments with actual reasoning traces.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--backend", default="openai", choices=["openai", "mock"])
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--api-key", default="none")
    parser.add_argument("--request-timeout", type=float, default=180.0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--benchmarks", default="wikicontradict,conflictbank")
    parser.add_argument("--wikicontradict-max", type=int, default=200)
    parser.add_argument("--conflictbank-max", type=int, default=500)
    parser.add_argument("--conflictbank-screening-pool", type=int, default=1200)
    parser.add_argument("--ambiguity-low", type=float, default=0.2)
    parser.add_argument("--ambiguity-high", type=float, default=0.8)
    parser.add_argument("--no-resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = GenerationConfig(
        backend=args.backend,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        request_timeout=args.request_timeout,
        temperature=args.temperature,
        seed=args.seed,
    )
    payload = run_real_generation_experiment(
        config=config,
        benchmarks=[item.strip() for item in args.benchmarks.split(",") if item.strip()],
        output_dir=ROOT / args.output_dir,
        wikicontradict_max=args.wikicontradict_max,
        conflictbank_max=args.conflictbank_max,
        conflictbank_screening_pool=args.conflictbank_screening_pool,
        ambiguity_low=args.ambiguity_low,
        ambiguity_high=args.ambiguity_high,
        resume=not args.no_resume,
    )
    print(
        json.dumps(
            {
                "results_file": str(ROOT / args.output_dir / "theorem3_real_generation_results.json"),
                "num_groups": len(payload.get("experiments", [])),
                "metadata": payload.get("metadata", {}),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
