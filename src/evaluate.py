"""Main experiment runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from baselines import (
    code_t_baseline,
    generated_test_filter_baseline,
    greedy_baseline,
    majority_vote_baseline,
    oracle_baseline,
    prm_best_of_n_placeholder,
    s_star_baseline,
    self_debug_baseline,
)
from falsify import FalsificationConfig, sequential_falsify_candidates
from generate import GenerationConfig, generate_candidates
from selection import select_best_candidate
from utils.data_loading import load_benchmark
from utils.io import dump_json
from utils.metrics import (
    brier_score,
    calibration_bins,
    expected_calibration_error,
    maximum_calibration_error,
    pass_at_k,
    roc_auc_binary,
    selective_prediction_curve,
)
from utils.sandbox import evaluate_candidate


def run_problem(
    problem: dict[str, Any],
    methods: list[str],
    generation_config: GenerationConfig,
    falsification_config: FalsificationConfig,
    n_candidates: int,
) -> dict[str, Any]:
    candidates = generate_candidates(problem, n=n_candidates, config=generation_config)
    outputs: dict[str, Any] = {"problem_id": problem["id"], "type": problem.get("type"), "methods": {}}
    evaluation_cache: dict[tuple[str, bool], dict[str, Any]] = {}

    def cached_evaluate(problem_obj: dict[str, Any], code: str, use_hidden: bool) -> dict[str, Any]:
        key = (code, bool(use_hidden))
        if key not in evaluation_cache:
            evaluation_cache[key] = evaluate_candidate(problem_obj, code, use_hidden=use_hidden)
        return evaluation_cache[key]

    baseline_map = {
        "greedy": greedy_baseline,
        "majority_vote": majority_vote_baseline,
        "oracle": oracle_baseline,
        "self_debug": self_debug_baseline,
        "generated_test_filter": generated_test_filter_baseline,
        "s_star": s_star_baseline,
        "code_t": code_t_baseline,
        "prm_best_of_n": prm_best_of_n_placeholder,
    }

    for method in methods:
        if method == "falsification":
            falsification_payload = sequential_falsify_candidates(candidates, problem, falsification_config)
            records = falsification_payload["records"]
            selected = select_best_candidate(records)
            passed = False
            if selected is not None:
                if problem.get("type") == "math":
                    passed = selected["text"].strip() == str(problem.get("reference_answer", "")).strip()
                else:
                    passed = cached_evaluate(problem, selected["text"], True)["passed"]
            outputs["methods"][method] = {
                "selected": selected,
                "passed": bool(passed),
                "records": records,
            }
        else:
            outputs["methods"][method] = baseline_map[method](problem, candidates, evaluator=cached_evaluate)

    num_correct = 0
    for candidate in candidates:
        if problem.get("type") == "math":
            if candidate["text"].strip() == str(problem.get("reference_answer", "")).strip():
                num_correct += 1
        else:
            if cached_evaluate(problem, candidate["text"], True)["passed"]:
                num_correct += 1

    outputs["pass_at_k"] = {str(k): pass_at_k(len(candidates), num_correct, k) for k in [1, min(10, len(candidates)), len(candidates)]}
    outputs["num_correct_candidates"] = num_correct
    outputs["num_candidates"] = len(candidates)
    outputs["difficulty"] = problem.get("difficulty", "unknown")
    return outputs


def _public_score(
    problem: dict[str, Any],
    candidate: dict[str, Any],
    evaluator: Any,
) -> float:
    if problem.get("type") == "math":
        return 0.0
    result = evaluator(problem, candidate["text"], False)
    num_passed = float(result.get("num_passed", 0))
    num_tests = float(result.get("num_tests", 0))
    return num_passed / num_tests if num_tests > 0 else 0.0


def summarize(results: list[dict[str, Any]], methods: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {"methods": {}, "difficulty": {}}
    method_confidences: dict[str, list[float]] = {}
    method_outcomes: dict[str, list[int]] = {}
    for method in methods:
        passed_flags = [bool(row["methods"][method]["passed"]) for row in results]
        confidences = []
        outcomes_for_method = []
        for row in results:
            selected = row["methods"][method].get("selected")
            if selected is not None:
                confidences.append(float(selected.get("confidence", 0.0)))
                outcomes_for_method.append(1 if row["methods"][method]["passed"] else 0)
        outcomes = [1 if row["methods"][method]["passed"] else 0 for row in results]
        summary["methods"][method] = {
            "accuracy": mean(1.0 if x else 0.0 for x in passed_flags) if passed_flags else 0.0,
            "mean_confidence": mean(confidences) if confidences else 0.0,
            "auroc": roc_auc_binary(confidences, outcomes[: len(confidences)]) if confidences else 0.0,
        }
        method_confidences[method] = confidences
        method_outcomes[method] = outcomes_for_method

    difficulty_groups = sorted({row.get("difficulty", "unknown") for row in results})
    for difficulty in difficulty_groups:
        group = [row for row in results if row.get("difficulty", "unknown") == difficulty]
        summary["difficulty"][difficulty] = {}
        for method in methods:
            values = [1.0 if row["methods"][method]["passed"] else 0.0 for row in group]
            summary["difficulty"][difficulty][method] = mean(values) if values else 0.0

    comparison_methods = [method for method in methods if method_confidences.get(method)]
    per_method_calibration: dict[str, Any] = {}
    for method in comparison_methods:
        confidences = method_confidences.get(method, [])
        outcomes = method_outcomes.get(method, [])
        per_method_calibration[method] = {
            "ece": expected_calibration_error(confidences, outcomes),
            "mce": maximum_calibration_error(confidences, outcomes),
            "brier": brier_score(confidences, outcomes),
            "auroc": roc_auc_binary(confidences, outcomes),
            "bins": calibration_bins(confidences, outcomes),
            "selective_curve": selective_prediction_curve(confidences, outcomes),
        }

    falsification_calibration = per_method_calibration.get("falsification", {})
    majority_calibration = per_method_calibration.get("majority_vote", {})
    self_debug_calibration = per_method_calibration.get("self_debug", {})
    summary["calibration"] = {
        "ece": falsification_calibration.get("ece", 0.0),
        "mce": falsification_calibration.get("mce", 0.0),
        "brier": falsification_calibration.get("brier", 0.0),
        "auroc": falsification_calibration.get("auroc", 0.0),
        "bins": falsification_calibration.get("bins", []),
        "selective_curve": falsification_calibration.get("selective_curve", []),
        "majority_vote_ece": majority_calibration.get("ece", 0.0),
        "majority_vote_bins": majority_calibration.get("bins", []),
        "majority_vote_selective_curve": majority_calibration.get("selective_curve", []),
        "self_debug_ece": self_debug_calibration.get("ece", 0.0),
        "self_debug_bins": self_debug_calibration.get("bins", []),
        "self_debug_selective_curve": self_debug_calibration.get("selective_curve", []),
        "per_method": per_method_calibration,
    }
    return summary


def run_benchmark(
    benchmark: str,
    methods: list[str],
    generation_config: GenerationConfig,
    falsification_config: FalsificationConfig,
    n_candidates: int,
    data_root: str = "data",
    max_problems: int | None = None,
    problem_offset: int = 0,
    progress_output_path: str | Path | None = None,
    resume: bool = False,
) -> dict[str, Any]:
    problems = load_benchmark(benchmark, data_root=data_root)
    if problem_offset:
        problems = problems[problem_offset:]
    if max_problems is not None:
        problems = problems[:max_problems]
    progress_path = Path(progress_output_path) if progress_output_path else None
    problem_results = []
    start_index = 0
    if resume and progress_path is not None and progress_path.exists():
        try:
            progress_payload = json.loads(progress_path.read_text(encoding="utf-8"))
            existing_results = progress_payload.get("results", [])
            if isinstance(existing_results, list):
                problem_results = []
                for row in existing_results[: len(problems)]:
                    if all(method in row.get("methods", {}) for method in methods):
                        problem_results.append(row)
                    else:
                        break
                start_index = len(problem_results)
        except Exception:
            problem_results = []
            start_index = 0

    for idx, problem in enumerate(problems[start_index:], start=start_index):
        problem_results.append(
            run_problem(
                problem=problem,
                methods=methods,
                generation_config=generation_config,
                falsification_config=falsification_config,
                n_candidates=n_candidates,
            )
        )
        if progress_path is not None:
            dump_json(
                {
                    "benchmark": benchmark,
                    "num_problems_total": len(problems),
                    "num_problems_completed": idx + 1,
                    "resumed_from": start_index,
                    "results": problem_results,
                    "summary": summarize(problem_results, methods),
                },
                progress_path,
            )
    return {
        "benchmark": benchmark,
        "num_problems": len(problems),
        "problem_offset": problem_offset,
        "results": problem_results,
        "summary": summarize(problem_results, methods),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate sequential falsification baselines on one or more benchmarks.")
    parser.add_argument("--benchmark", help="Single benchmark name.")
    parser.add_argument("--benchmarks", help="Comma-separated benchmark names.")
    parser.add_argument("--methods", default="greedy,majority_vote,falsification,oracle")
    parser.add_argument("--n-candidates", type=int, default=4)
    parser.add_argument("--n-falsification-rounds", type=int, default=2)
    parser.add_argument("--max-tiebreak-rounds", type=int, default=4)
    parser.add_argument("--delta", type=float, default=0.05)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--probe-strategy", default="adaptive_population")
    parser.add_argument("--adaptive-probe-selection", action="store_true", default=True)
    parser.add_argument("--no-adaptive-probe-selection", dest="adaptive_probe_selection", action="store_false")
    parser.add_argument("--enforce-round-family-diversity", action="store_true", default=True)
    parser.add_argument("--no-enforce-round-family-diversity", dest="enforce_round_family_diversity", action="store_false")
    parser.add_argument("--eliminate-on-detection", action="store_true", default=True)
    parser.add_argument("--no-eliminate-on-detection", dest="eliminate_on_detection", action="store_false")
    parser.add_argument("--confidence-mode", default="wealth", choices=["wealth", "survival_only", "none"])
    parser.add_argument("--max-differential-probes", type=int, default=8)
    parser.add_argument("--consensus-min-fraction", type=float, default=0.70)
    parser.add_argument("--consensus-min-margin", type=int, default=2)
    parser.add_argument("--consensus-min-votes", type=int, default=3)
    parser.add_argument("--backend", default="mock")
    parser.add_argument("--model", default="mock-model")
    parser.add_argument("--api-base", default="http://localhost:8000/v1")
    parser.add_argument("--api-key", default="none")
    parser.add_argument("--request-timeout", type=float, default=15.0)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--seeds", help="Comma-separated seed list; overrides --seed when provided.")
    parser.add_argument("--tp-size", type=int, default=1)
    parser.add_argument("--checkpoint-dir", default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output-dir", default="results/pilot")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--max-problems", type=int, default=None)
    parser.add_argument("--problem-offset", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    benchmarks = []
    if args.benchmark:
        benchmarks.append(args.benchmark)
    if args.benchmarks:
        benchmarks.extend([item.strip() for item in args.benchmarks.split(",") if item.strip()])
    if not benchmarks:
        raise SystemExit("Provide --benchmark or --benchmarks.")

    methods = [item.strip() for item in args.methods.split(",") if item.strip()]
    seed_values = [args.seed]
    if args.seeds:
        seed_values = [int(item.strip()) for item in args.seeds.split(",") if item.strip()]

    falsification_config = FalsificationConfig(
        n_rounds=args.n_falsification_rounds,
        max_tiebreak_rounds=args.max_tiebreak_rounds,
        delta=args.delta,
        alpha=args.alpha,
        timeout=args.timeout,
        probe_strategy=args.probe_strategy,
        adaptive_probe_selection=args.adaptive_probe_selection,
        enforce_round_family_diversity=args.enforce_round_family_diversity,
        eliminate_on_detection=args.eliminate_on_detection,
        confidence_mode=args.confidence_mode,
        max_differential_probes=args.max_differential_probes,
        consensus_min_fraction=args.consensus_min_fraction,
        consensus_min_margin=args.consensus_min_margin,
        consensus_min_votes=args.consensus_min_votes,
    )
    all_results = []
    for benchmark in benchmarks:
        per_seed = []
        for seed in seed_values:
            generation_config = GenerationConfig(
                backend=args.backend,
                model=args.model,
                api_base=args.api_base,
                api_key=args.api_key,
                request_timeout=args.request_timeout,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                seed=seed,
            )
            benchmark_result = run_benchmark(
                benchmark=benchmark,
                methods=methods,
                generation_config=generation_config,
                falsification_config=falsification_config,
                n_candidates=args.n_candidates,
                data_root=args.data_root,
                max_problems=args.max_problems,
                problem_offset=args.problem_offset,
                progress_output_path=Path(args.output_dir) / f"{benchmark}_seed{seed}_progress.json",
                resume=args.resume,
            )
            benchmark_result["seed"] = seed
            per_seed.append(benchmark_result)

        if len(per_seed) == 1:
            combined = per_seed[0]
        else:
            summary_across_seeds: dict[str, Any] = {"methods": {}, "calibration": {}}
            for method in methods:
                accuracies = [row["summary"]["methods"][method]["accuracy"] for row in per_seed]
                mean_acc = sum(accuracies) / len(accuracies)
                if len(accuracies) > 1:
                    variance = sum((x - mean_acc) ** 2 for x in accuracies) / (len(accuracies) - 1)
                    stderr = (variance ** 0.5) / (len(accuracies) ** 0.5)
                else:
                    stderr = 0.0
                summary_across_seeds["methods"][method] = {
                    "accuracy_mean": mean_acc,
                    "accuracy_stderr": stderr,
                    "accuracy_by_seed": accuracies,
                }
            for metric_name in ["ece", "mce", "brier"]:
                values = [row["summary"]["calibration"].get(metric_name, 0.0) for row in per_seed]
                mean_value = sum(values) / len(values)
                if len(values) > 1:
                    variance = sum((x - mean_value) ** 2 for x in values) / (len(values) - 1)
                    stderr = (variance ** 0.5) / (len(values) ** 0.5)
                else:
                    stderr = 0.0
                summary_across_seeds["calibration"][metric_name] = {
                    "mean": mean_value,
                    "stderr": stderr,
                    "by_seed": values,
                }
            combined = {
                "benchmark": benchmark,
                "num_problems": per_seed[0]["num_problems"],
                "seed_runs": per_seed,
                "summary_across_seeds": summary_across_seeds,
            }
        all_results.append(combined)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(
        {
            "benchmarks": all_results,
            "metadata": {
                "model": args.model,
                "backend": args.backend,
                "api_base": args.api_base,
                "request_timeout": args.request_timeout,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "n_candidates": args.n_candidates,
                "n_falsification_rounds": args.n_falsification_rounds,
                "max_tiebreak_rounds": args.max_tiebreak_rounds,
                "probe_strategy": args.probe_strategy,
                "adaptive_probe_selection": args.adaptive_probe_selection,
                "enforce_round_family_diversity": args.enforce_round_family_diversity,
                "eliminate_on_detection": args.eliminate_on_detection,
                "confidence_mode": args.confidence_mode,
                "max_differential_probes": args.max_differential_probes,
                "consensus_min_fraction": args.consensus_min_fraction,
                "consensus_min_margin": args.consensus_min_margin,
                "consensus_min_votes": args.consensus_min_votes,
                "tp_size": args.tp_size,
                "checkpoint_dir": args.checkpoint_dir,
                "resume": args.resume,
                "seeds": seed_values,
                "max_problems": args.max_problems,
                "problem_offset": args.problem_offset,
            },
        },
        output_dir / "results.json",
    )
    print(json.dumps({"benchmarks": [item["benchmark"] for item in all_results], "output_dir": str(output_dir)}, indent=2))


if __name__ == "__main__":
    main()
