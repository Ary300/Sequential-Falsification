"""Baseline implementations for local experiments."""

from __future__ import annotations

from typing import Any
from collections.abc import Callable

from falsify import (
    FalsificationConfig,
    _build_probe_bank,
    _build_differential_probe_bank,
    _consensus_detected_flags,
    _default_round_family_schedule,
    _execute_probe,
    _family_balanced_probe_subset,
    _is_labeled_probe,
    sequential_falsify_candidates,
)
from selection import select_best_candidate
from utils.sandbox import evaluate_candidate


def _estimate_candidate_confidence(candidate: dict[str, Any], numerator: float, denominator: float) -> dict[str, Any]:
    out = dict(candidate)
    out["confidence"] = 0.0 if denominator <= 0 else max(0.0, min(1.0, numerator / denominator))
    return out


def _candidate_passes_hidden(
    problem: dict[str, Any],
    candidate: dict[str, Any],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]],
) -> bool:
    if problem.get("type") == "math":
        return candidate["text"].strip() == str(problem.get("reference_answer", "")).strip()
    return bool(evaluator(problem, candidate["text"], True)["passed"])


def _public_score(
    problem: dict[str, Any],
    candidate: dict[str, Any],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]],
) -> float:
    if problem.get("type") == "math":
        return 1.0 if candidate["text"].strip() == str(problem.get("reference_answer", "")).strip() else 0.0
    result = evaluator(problem, candidate["text"], False)
    num_passed = float(result.get("num_passed", 0))
    num_tests = float(result.get("num_tests", 0))
    return num_passed / num_tests if num_tests > 0 else 0.0


def _break_ties_by_public_score(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]],
) -> dict[str, Any]:
    return max(
        candidates,
        key=lambda candidate: (
            _public_score(problem, candidate, evaluator),
            float(candidate.get("selection_score", candidate.get("confidence", 0.0))),
            -int(candidate.get("candidate_order", 0)),
        ),
    )


def greedy_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
) -> dict[str, Any]:
    chosen = _estimate_candidate_confidence(candidates[0], numerator=1.0, denominator=1.0)
    evaluation = evaluator(problem, chosen["text"], True)
    return {"selected": chosen, "passed": evaluation["passed"], "meta": {"method": "greedy"}}


def majority_vote_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
) -> dict[str, Any]:
    counts: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        counts.setdefault(candidate["text"].strip(), []).append(candidate)
    selected_group = max(counts.values(), key=len)
    chosen = _estimate_candidate_confidence(selected_group[0], numerator=len(selected_group), denominator=len(candidates))
    evaluation = evaluator(problem, chosen["text"], True)
    return {
        "selected": chosen,
        "passed": evaluation["passed"],
        "meta": {"method": "majority_vote", "vote_count": len(selected_group)},
    }


def oracle_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
) -> dict[str, Any]:
    evaluations = [evaluator(problem, candidate["text"], True) for candidate in candidates]
    for candidate, evaluation in zip(candidates, evaluations):
        if evaluation["passed"]:
            return {
                "selected": _estimate_candidate_confidence(candidate, numerator=1.0, denominator=1.0),
                "passed": True,
                "meta": {"method": "oracle"},
            }
    return {
        "selected": _estimate_candidate_confidence(candidates[0], numerator=0.0, denominator=1.0),
        "passed": False,
        "meta": {"method": "oracle"},
    }


def self_debug_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
) -> dict[str, Any]:
    first = candidates[0]
    evaluation = evaluator(problem, first["text"], False)
    if evaluation["passed"]:
        final_eval = evaluator(problem, first["text"], True)
        return {
            "selected": _estimate_candidate_confidence(first, numerator=0.75, denominator=1.0),
            "passed": final_eval["passed"],
            "meta": {"method": "self_debug", "rounds": 0},
        }

    fallback = None
    for candidate in candidates[1:]:
        candidate_eval = evaluator(problem, candidate["text"], False)
        if candidate_eval["passed"]:
            fallback = candidate
            break
    chosen = _estimate_candidate_confidence(fallback or first, numerator=0.5 if fallback else 0.25, denominator=1.0)
    final_eval = evaluator(problem, chosen["text"], True)
    return {
        "selected": chosen,
        "passed": final_eval["passed"],
        "meta": {"method": "self_debug", "rounds": 1 if fallback else 0},
    }


def generated_test_filter_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
    timeout: int = 10,
    max_probes: int = 4,
) -> dict[str, Any]:
    """Filter candidates using non-adaptive generated probes.

    This baseline is intentionally non-adaptive: it builds a one-shot generated
    probe bank, then filters candidates without using survivor-conditioned probe
    synthesis. The default budget is compute-matched to the main falsification
    recipe (four probe rounds) rather than quietly spending more total tests.
    """

    config = FalsificationConfig(
        n_rounds=max_probes,
        timeout=timeout,
        probe_strategy="generated_only",
        adaptive_probe_selection=False,
        allow_hidden_test_probes=False,
    )
    probe_bank = _build_probe_bank(problem, config)
    probe_bank = [probe for probe in probe_bank if probe.get("family") != "public"]
    family_schedule = _default_round_family_schedule(config)
    probe_bank = _family_balanced_probe_subset(probe_bank, family_schedule, max_probes=max_probes)
    if not probe_bank:
        result = majority_vote_baseline(problem, candidates, evaluator=evaluator)
        result["meta"]["method"] = "generated_test_filter"
        result["meta"]["note"] = "No generated probes were available; fell back to majority voting."
        return result

    survivors = list(candidates)
    probes_used = 0
    eliminated = 0
    for probe in probe_bank:
        if len(survivors) <= 1:
            break
        executions = [_execute_probe(problem, candidate["text"], probe, timeout=timeout) for candidate in survivors]
        if _is_labeled_probe(probe):
            detected_flags: list[bool] | None = [bool(item.get("detected", False)) for item in executions]
        else:
            detected_flags = _consensus_detected_flags(executions)
        if detected_flags is None:
            continue
        num_detected = sum(detected_flags)
        if num_detected == 0 or num_detected == len(survivors):
            continue
        probes_used += 1
        eliminated += num_detected
        survivors = [candidate for candidate, detected in zip(survivors, detected_flags) if not detected]

    chosen = _break_ties_by_public_score(problem, survivors, evaluator) if survivors else candidates[0]
    confidence = 1.0 - max(0, len(survivors) - 1) / max(1, len(candidates))
    selected = dict(chosen)
    selected["confidence"] = min(1.0, max(selected.get("confidence", 0.0), confidence))
    final_eval = evaluator(problem, selected["text"], True)
    return {
        "selected": selected,
        "passed": final_eval["passed"],
        "meta": {
            "method": "generated_test_filter",
            "compute_matched": True,
            "family_schedule": family_schedule[:max_probes],
            "probes_used": probes_used,
            "eliminated": eliminated,
            "survivors": len(survivors),
        },
    }


def s_star_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
    timeout: int = 10,
    max_rounds: int = 6,
) -> dict[str, Any]:
    """Adaptive elimination proxy inspired by S*.

    This is not the external SkyThought implementation. It is a local,
    executable adaptive-test-synthesis proxy that removes our calibrated
    confidence layer so we can compare against the adaptive elimination idea
    directly.
    """

    if problem.get("type") == "math":
        result = majority_vote_baseline(problem, candidates, evaluator=evaluator)
        result["meta"]["method"] = "s_star_proxy"
        result["meta"]["note"] = "Math fallback: majority vote. External SkyThought S* integration is not enabled."
        return result

    payload = sequential_falsify_candidates(
        candidates,
        problem,
        FalsificationConfig(
            n_rounds=max_rounds,
            timeout=timeout,
            probe_strategy="adaptive_population",
            adaptive_probe_selection=True,
            eliminate_on_detection=True,
            confidence_mode="survival_only",
            allow_hidden_test_probes=False,
        ),
    )
    records = payload["records"]
    survivors = [record for record in records if record.get("survived")]
    if survivors:
        chosen = _break_ties_by_public_score(problem, survivors, evaluator)
    else:
        chosen = select_best_candidate(records) or records[0]
    selected = dict(chosen)
    survivor_confidence = 1.0 - max(0, len(survivors) - 1) / max(1, len(candidates))
    selected["confidence"] = max(float(selected.get("confidence", 0.0)), survivor_confidence)
    return {
        "selected": selected,
        "passed": _candidate_passes_hidden(problem, selected, evaluator),
        "meta": {
            "method": "s_star_proxy",
            "survivors": len(survivors),
            "rounds": max_rounds,
            "note": "Local adaptive elimination proxy inspired by S*; external SkyThought integration is not enabled.",
        },
    }


def code_t_baseline(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
    timeout: int = 10,
    max_probes: int = 10,
) -> dict[str, Any]:
    """Executable local proxy for CodeT-style agreement scoring."""

    if problem.get("type") == "math":
        result = majority_vote_baseline(problem, candidates, evaluator=evaluator)
        result["meta"]["method"] = "code_t_proxy"
        result["meta"]["note"] = "Math fallback: majority vote. External CodeT integration is not enabled."
        return result

    config = FalsificationConfig(
        n_rounds=max_probes,
        timeout=timeout,
        probe_strategy="generated_only",
        adaptive_probe_selection=False,
        allow_hidden_test_probes=False,
    )
    execution_cache: dict[tuple[str, str], dict[str, Any]] = {}
    candidate_records = [
        {
            **candidate,
            "text": candidate["text"],
            "candidate_order": idx,
            "survived": True,
        }
        for idx, candidate in enumerate(candidates)
    ]
    probe_bank = _build_probe_bank(problem, config)
    probe_bank.extend(_build_differential_probe_bank(problem, candidate_records, config, execution_cache))
    probe_bank = [probe for probe in probe_bank if probe.get("family") != "public"][:max_probes]
    if not probe_bank:
        result = majority_vote_baseline(problem, candidates, evaluator=evaluator)
        result["meta"]["method"] = "code_t_proxy"
        result["meta"]["note"] = "No generated probes were available; fell back to majority vote."
        return result

    scores = [0.0 for _ in candidates]
    labeled_probes = 0
    consensus_probes = 0
    probes_used = 0
    for probe in probe_bank:
        executions = [_execute_probe(problem, candidate["text"], probe, timeout=timeout) for candidate in candidates]
        if _is_labeled_probe(probe):
            labels = [not bool(item.get("detected", False)) for item in executions]
            if len(set(labels)) <= 1:
                continue
            probes_used += 1
            labeled_probes += 1
            for idx, passed in enumerate(labels):
                if passed:
                    scores[idx] += 1.25 if probe.get("family") == "differential" else 1.0
            continue

        consensus_flags = _consensus_detected_flags(executions)
        if consensus_flags is None:
            continue
        probes_used += 1
        consensus_probes += 1
        for idx, detected in enumerate(consensus_flags):
            if not detected:
                scores[idx] += 1.1 if probe.get("family") == "differential" else 1.0

    if probes_used == 0:
        result = majority_vote_baseline(problem, candidates, evaluator=evaluator)
        result["meta"]["method"] = "code_t_proxy"
        result["meta"]["note"] = "Generated probes produced no usable agreement signal; fell back to majority vote."
        return result

    ranked = []
    for idx, candidate in enumerate(candidates):
        public = _public_score(problem, candidate, evaluator)
        ranked.append((scores[idx], public, -idx, candidate))
    best_score, best_public, _, chosen = max(ranked, key=lambda item: (item[0], item[1], item[2]))
    selected = dict(chosen)
    selected["confidence"] = max(float(selected.get("confidence", 0.0)), best_score / probes_used)
    return {
        "selected": selected,
        "passed": _candidate_passes_hidden(problem, selected, evaluator),
        "meta": {
            "method": "code_t_proxy",
            "probes_used": probes_used,
            "labeled_probes": labeled_probes,
            "consensus_probes": consensus_probes,
            "score": best_score,
            "public_score": best_public,
            "note": "Local agreement-scoring proxy inspired by CodeT; external CodeT integration is not enabled.",
        },
    }


def prm_best_of_n_placeholder(
    problem: dict[str, Any],
    candidates: list[dict[str, Any]],
    evaluator: Callable[[dict[str, Any], str, bool], dict[str, Any]] = lambda problem, code, use_hidden: evaluate_candidate(
        problem, code, use_hidden=use_hidden
    ),
) -> dict[str, Any]:
    scored = []
    for candidate in candidates:
        public_eval = evaluator(problem, candidate["text"], False)
        score = public_eval.get("num_passed", 0) / max(1, public_eval.get("num_tests", 1))
        scored.append((score, candidate))
    best_score, best_candidate = max(scored, key=lambda item: item[0])
    selected = _estimate_candidate_confidence(best_candidate, numerator=best_score, denominator=1.0)
    final_eval = evaluator(problem, selected["text"], True)
    return {
        "selected": selected,
        "passed": final_eval["passed"],
        "meta": {"method": "prm_best_of_n_placeholder", "score": best_score},
    }
