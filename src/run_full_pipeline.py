"""Config-driven experiment entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from experiment_registry import filter_experiments, load_expanded_experiments
from evaluate import run_benchmark
from falsify import FalsificationConfig
from generate import GenerationConfig
from utils.io import dump_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full experiment pipeline from a config file.")
    parser.add_argument("--config", default="src/configs/experiments.yaml")
    parser.add_argument("--output-root", default="results/full")
    parser.add_argument("--experiment-name", action="append", default=[], help="Run only experiments with this exact base or expanded name. May be repeated.")
    parser.add_argument("--experiment-prefix", action="append", default=[], help="Run only experiments whose base or expanded name starts with this prefix. May be repeated.")
    parser.add_argument("--backend-override", default=None)
    parser.add_argument("--api-base-override", default=None)
    parser.add_argument("--model-override", default=None)
    parser.add_argument("--seed-override", type=int, default=None)
    parser.add_argument("--max-problems-override", type=int, default=None)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    experiment_results: list[dict[str, Any]] = []
    expanded_experiments = filter_experiments(
        load_expanded_experiments(args.config),
        names=args.experiment_name,
        prefixes=args.experiment_prefix,
    )
    if not expanded_experiments:
        raise SystemExit("No experiments matched the provided filters.")

    for experiment in expanded_experiments:
        generation_config = GenerationConfig(
            backend=args.backend_override or experiment.get("backend", "mock"),
            model=args.model_override or experiment.get("model", "mock-model"),
            api_base=args.api_base_override or experiment.get("api_base", "http://localhost:8000/v1"),
            api_key=experiment.get("api_key", "none"),
            request_timeout=experiment.get("request_timeout", 15.0),
            max_tokens=experiment.get("max_tokens", 512),
            temperature=experiment.get("temperature", 0.7),
            seed=args.seed_override if args.seed_override is not None else experiment.get("seed", 42),
        )
        falsification_config = FalsificationConfig(
            n_rounds=experiment.get("n_falsification_rounds", 2),
            delta=experiment.get("delta", 0.05),
            timeout=experiment.get("timeout", 10),
            alpha=experiment.get("alpha", 0.05),
            probe_strategy=experiment.get("probe_strategy", "adaptive_population"),
            adaptive_probe_selection=experiment.get("adaptive_probe_selection", True),
            eliminate_on_detection=experiment.get("eliminate_on_detection", True),
            confidence_mode=experiment.get("confidence_mode", "wealth"),
        )
        for benchmark in experiment.get("benchmarks", []):
            try:
                result = run_benchmark(
                    benchmark=benchmark,
                    methods=experiment.get("methods", ["greedy", "majority_vote", "falsification", "oracle"]),
                    generation_config=generation_config,
                    falsification_config=falsification_config,
                    n_candidates=experiment.get("n_candidates", 4),
                    data_root=experiment.get("data_root", "data"),
                    max_problems=args.max_problems_override if args.max_problems_override is not None else experiment.get("max_problems"),
                )
            except Exception as exc:
                result = {
                    "benchmark": benchmark,
                    "error": f"{type(exc).__name__}: {exc}",
                    "num_problems": 0,
                    "results": [],
                }
            result["experiment_name"] = experiment.get("name", "unnamed")
            result["experiment_config"] = {
                "name": experiment.get("name", "unnamed"),
                "expanded_from": experiment.get("expanded_from"),
                "sweep_values": experiment.get("sweep_values", {}),
                "model": experiment.get("model", "mock-model"),
                "backend": args.backend_override or experiment.get("backend", "mock"),
                "methods": experiment.get("methods", ["greedy", "majority_vote", "falsification", "oracle"]),
                "n_candidates": experiment.get("n_candidates", 4),
                "n_falsification_rounds": experiment.get("n_falsification_rounds", 2),
                "probe_strategy": experiment.get("probe_strategy", "adaptive_population"),
                "adaptive_probe_selection": experiment.get("adaptive_probe_selection", True),
                "eliminate_on_detection": experiment.get("eliminate_on_detection", True),
                "confidence_mode": experiment.get("confidence_mode", "wealth"),
                "temperature": experiment.get("temperature", 0.7),
                "seed": args.seed_override if args.seed_override is not None else experiment.get("seed", 42),
                "max_problems": args.max_problems_override if args.max_problems_override is not None else experiment.get("max_problems"),
            }
            experiment_results.append(result)

    dump_json({"experiments": experiment_results}, output_root / "results.json")
    print(f"Wrote {len(experiment_results)} experiment results to {output_root / 'results.json'}")


if __name__ == "__main__":
    main()
