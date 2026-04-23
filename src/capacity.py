"""Track B capacity estimation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
import random
from statistics import mean
from typing import Any

from generate import GenerationConfig, generate_candidates
from utils.data_loading import load_benchmark
from utils.metrics import bootstrap_confidence_interval
from utils.sandbox import evaluate_candidate
from verifiers import create_verifier


@dataclass
class CapacityConfig:
    verifier_names: list[str]
    n_candidates: int = 16
    timeout: int = 10
    n_score_bins: int = 10
    max_problems: int | None = None
    data_root: str = "data"


def mutual_information_from_records(records: list[dict[str, Any]]) -> float:
    if not records:
        return 0.0

    total = len(records)
    joint_counts: dict[tuple[str, int], int] = {}
    token_counts: dict[str, int] = {}
    label_counts: dict[int, int] = {}

    for row in records:
        token = str(row["score_token"])
        label = int(bool(row["correct"]))
        joint_counts[(token, label)] = joint_counts.get((token, label), 0) + 1
        token_counts[token] = token_counts.get(token, 0) + 1
        label_counts[label] = label_counts.get(label, 0) + 1

    mutual_information = 0.0
    for (token, label), count in joint_counts.items():
        p_xy = count / total
        p_x = token_counts[token] / total
        p_y = label_counts[label] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mutual_information += p_xy * log(p_xy / (p_x * p_y))
    return mutual_information


def estimate_capacity_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_problem: dict[str, list[dict[str, Any]]] = {}
    for row in records:
        by_problem.setdefault(str(row["problem_id"]), []).append(row)

    per_problem = [
        {
            "problem_id": problem_id,
            "mutual_information": mutual_information_from_records(problem_rows),
            "num_records": len(problem_rows),
        }
        for problem_id, problem_rows in by_problem.items()
    ]
    per_problem_values = [float(row["mutual_information"]) for row in per_problem]
    capacity = mean(per_problem_values) if per_problem_values else 0.0
    ci_low, ci_high = bootstrap_confidence_interval(per_problem_values, seed=42) if per_problem_values else (0.0, 0.0)
    return {
        "capacity": capacity,
        "capacity_ci": [ci_low, ci_high],
        "num_problems": len(per_problem),
        "per_problem": per_problem,
    }


def _hidden_correct(problem: dict[str, Any], candidate_text: str, timeout: int) -> bool:
    if problem.get("type") == "math":
        return candidate_text.strip() == str(problem.get("reference_answer", "")).strip()
    return bool(evaluate_candidate(problem, candidate_text, use_hidden=True, timeout=timeout)["passed"])


def collect_capacity_records(
    benchmark: str,
    generation_config: GenerationConfig,
    capacity_config: CapacityConfig,
) -> dict[str, Any]:
    problems = load_benchmark(benchmark, data_root=capacity_config.data_root)
    if capacity_config.max_problems is not None:
        problems = problems[: capacity_config.max_problems]

    verifier_payloads = {
        name: {"verifier": create_verifier(name, timeout=capacity_config.timeout, n_bins=capacity_config.n_score_bins), "records": []}
        for name in capacity_config.verifier_names
    }

    for problem_index, problem in enumerate(problems):
        candidates = generate_candidates(problem, n=capacity_config.n_candidates, config=generation_config)
        evaluation_cache: dict[tuple[str, bool], dict[str, Any]] = {}

        def cached_evaluate(problem_obj: dict[str, Any], code: str, use_hidden: bool) -> dict[str, Any]:
            key = (code, bool(use_hidden))
            if key not in evaluation_cache:
                evaluation_cache[key] = evaluate_candidate(problem_obj, code, use_hidden=use_hidden, timeout=capacity_config.timeout)
            return evaluation_cache[key]

        enriched_candidates = [
            {**candidate, "candidate_order": index}
            for index, candidate in enumerate(candidates)
        ]

        for payload in verifier_payloads.values():
            verifier = payload["verifier"]
            try:
                verifier.prepare(problem, enriched_candidates, cached_evaluate)
            except NotImplementedError as exc:
                payload.setdefault("errors", []).append(str(exc))
                continue

            for candidate in enriched_candidates:
                try:
                    score = verifier.score(problem, candidate, cached_evaluate)
                except NotImplementedError as exc:
                    payload.setdefault("errors", []).append(str(exc))
                    break
                payload["records"].append(
                    {
                        "benchmark": benchmark,
                        "problem_id": problem["id"],
                        "problem_index": problem_index,
                        "difficulty": problem.get("difficulty", "unknown"),
                        "candidate_order": int(candidate["candidate_order"]),
                        "score_token": score.token,
                        "score_raw": score.raw,
                        "score_metadata": score.metadata,
                        "correct": _hidden_correct(problem, candidate["text"], timeout=capacity_config.timeout),
                    }
                )

    results: dict[str, Any] = {
        "benchmark": benchmark,
        "num_problems": len(problems),
        "n_candidates": capacity_config.n_candidates,
        "verifiers": {},
    }
    for verifier_name, payload in verifier_payloads.items():
        records = payload["records"]
        results["verifiers"][verifier_name] = {
            "summary": estimate_capacity_from_records(records),
            "records": records,
            "errors": payload.get("errors", []),
        }
    return results


def capacity_gain_predictions(
    oracle_accuracy: float,
    capacity_value: float,
    budgets: list[int],
) -> list[dict[str, float]]:
    predictions: list[dict[str, float]] = []
    for budget in budgets:
        selective_accuracy = oracle_accuracy * (1.0 - exp(-budget * capacity_value))
        predictions.append({"budget": float(budget), "predicted_accuracy": selective_accuracy})
    return predictions


def rank_verifiers_by_capacity(capacity_payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranking = []
    for verifier_name, verifier_payload in capacity_payload.get("verifiers", {}).items():
        ranking.append(
            {
                "verifier": verifier_name,
                "capacity": float(verifier_payload.get("summary", {}).get("capacity", 0.0)),
                "num_problems": int(verifier_payload.get("summary", {}).get("num_problems", 0)),
            }
        )
    return sorted(ranking, key=lambda row: row["capacity"], reverse=True)


def synthetic_capacity_sanity(seed: int = 42) -> dict[str, Any]:
    rng = random.Random(seed)
    records = []
    for problem_idx in range(50):
        threshold = rng.random()
        for candidate_order in range(16):
            label = 1 if rng.random() > 0.7 else 0
            noisy_score = label if rng.random() > threshold else 1 - label
            records.append(
                {
                    "problem_id": f"synthetic_{problem_idx}",
                    "score_token": str(noisy_score),
                    "correct": label,
                }
            )
    return estimate_capacity_from_records(records)
