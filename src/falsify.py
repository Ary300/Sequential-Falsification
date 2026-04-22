"""Sequential falsification logic.

The key distinction from self-debugging is that falsification operates on the
full candidate population. It chooses probes that maximally separate surviving
candidates, then eliminates inconsistent candidates rather than repairing them.

The confidence score remains an empirical ranking proxy motivated by
sequential-testing ideas; the repository does not currently claim a fully
validated anytime-valid guarantee for it.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from calibrate import calibrated_confidence_from_wealth
from utils.evals import compute_e_value, estimate_detection_probability
from utils.io import dump_json
from utils.sandbox import evaluate_candidate, execute_code_function, execute_stdin_program


@dataclass
class FalsificationConfig:
    n_rounds: int = 4
    max_tiebreak_rounds: int = 4
    delta: float = 0.05
    timeout: int = 10
    alpha: float = 0.05
    probe_strategy: str = "adaptive_population"
    adaptive_probe_selection: bool = True
    eliminate_on_detection: bool = True
    confidence_mode: str = "wealth"
    max_public_tests_for_probes: int = 3
    max_generated_probes: int = 12
    max_edge_case_probes: int = 8
    max_random_stress_probes: int = 8
    max_differential_probes: int = 8
    allow_hidden_test_probes: bool = False
    enforce_round_family_diversity: bool = True
    selection_confidence_weight: float = 0.55
    selection_public_weight: float = 0.35
    selection_trace_weight: float = 0.10


def _is_labeled_probe(probe: dict[str, Any]) -> bool:
    test = probe.get("test")
    return isinstance(test, dict) and "output" in test


def _normalize_answer_text(text: Any) -> str:
    return str(text).strip().lower()


def _math_agreement_scores(records: list[dict[str, Any]]) -> dict[int, float]:
    if not records:
        return {}
    counts: dict[str, int] = {}
    for record in records:
        token = _normalize_answer_text(record.get("text", ""))
        counts[token] = counts.get(token, 0) + 1
    denominator = max(1, len(records))
    return {
        int(record.get("candidate_order", idx)): counts.get(_normalize_answer_text(record.get("text", "")), 0) / denominator
        for idx, record in enumerate(records)
    }


def _probe_signature(probe: dict[str, Any]) -> str:
    return json.dumps(probe, sort_keys=True, default=repr)


def _dedupe_preserving_order(items: list[Any]) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for item in items:
        signature = json.dumps(item, sort_keys=True, default=repr)
        if signature in seen:
            continue
        seen.add(signature)
        output.append(item)
    return output


def _normalize_output_token(result: dict[str, Any]) -> str:
    if result.get("status") != "passed":
        return f"status:{result.get('status')}"
    if "observed_output" in result:
        return repr(result.get("observed_output"))
    if "stdout" in result:
        return f"stdout:{result.get('stdout', '').strip()}"
    return repr(result)


def _mutate_scalar(value: Any) -> list[Any]:
    if isinstance(value, bool):
        return [not value]
    if isinstance(value, int) and not isinstance(value, bool):
        options = [0, value + 1, value - 1, value * 2]
        if value != 0:
            options.append(-value)
        return _dedupe_preserving_order(options)
    if isinstance(value, float):
        options = [0.0, value + 1.0, value - 1.0, value * 2.0]
        if value != 0.0:
            options.append(-value)
        return _dedupe_preserving_order(options)
    if isinstance(value, str):
        options = [value + value, value[::-1]]
        if value:
            options.extend([value[:-1], value + "a"])
        else:
            options.append("a")
        return _dedupe_preserving_order(options)
    return []


def _mutate_value(value: Any) -> list[Any]:
    direct = _mutate_scalar(value)
    if direct:
        return direct
    if isinstance(value, list):
        mutations: list[Any] = []
        if value:
            mutations.append(list(reversed(value)))
            mutations.append(value[:-1])
            first_mutations = _mutate_scalar(value[0])
            for first in first_mutations[:2]:
                mutated = list(value)
                mutated[0] = first
                mutations.append(mutated)
        else:
            mutations.append([0])
        return _dedupe_preserving_order(mutations)
    if isinstance(value, tuple):
        return [tuple(item) if isinstance(item, list) else item for item in _mutate_value(list(value))]
    return []


def _mutate_function_test_inputs(test_input: Any) -> list[list[Any]]:
    args = list(test_input) if isinstance(test_input, (list, tuple)) else [test_input]
    mutations: list[list[Any]] = []
    for idx, value in enumerate(args):
        for candidate in _mutate_value(value)[:3]:
            if candidate == value:
                continue
            mutated = list(args)
            mutated[idx] = candidate
            mutations.append(mutated)
    if len(args) >= 2:
        mutations.append(list(reversed(args)))
    return _dedupe_preserving_order([mutation for mutation in mutations if mutation != args])


def _edge_case_values(value: Any) -> list[Any]:
    if isinstance(value, bool):
        return [False, True]
    if isinstance(value, int) and not isinstance(value, bool):
        return _dedupe_preserving_order([0, 1, -1, abs(value), -abs(value), 10, -10])
    if isinstance(value, float):
        return _dedupe_preserving_order([0.0, 1.0, -1.0, abs(value), -abs(value), 10.0, -10.0])
    if isinstance(value, str):
        return _dedupe_preserving_order(["", "a", value[:1], value + value])
    if isinstance(value, list):
        if not value:
            return [[0], [1], [-1]]
        head = value[0]
        return _dedupe_preserving_order([[], [head], [head, head], list(reversed(value))])
    return []


def _edge_case_function_test_inputs(test_input: Any) -> list[list[Any]]:
    args = list(test_input) if isinstance(test_input, (list, tuple)) else [test_input]
    probes: list[list[Any]] = []
    for idx, value in enumerate(args):
        for candidate in _edge_case_values(value)[:4]:
            mutated = list(args)
            mutated[idx] = candidate
            probes.append(mutated)
    if len(args) == 1 and isinstance(args[0], list):
        probes.extend([[[]], [[0]], [[1]], [[-1]]])
    return _dedupe_preserving_order([probe for probe in probes if probe != args])


def _randomize_scalar(value: Any, rng: random.Random) -> Any:
    if isinstance(value, bool):
        return rng.choice([False, True])
    if isinstance(value, int) and not isinstance(value, bool):
        scale = max(3, abs(value) + 3)
        return rng.randint(-scale, scale)
    if isinstance(value, float):
        scale = max(3.0, abs(value) + 3.0)
        return rng.uniform(-scale, scale)
    if isinstance(value, str):
        alphabet = "abcxyz"
        return "".join(rng.choice(alphabet) for _ in range(max(1, min(4, len(value) or 2))))
    if isinstance(value, list):
        length = rng.randint(0, max(3, min(6, len(value) + 2)))
        if not value:
            return [rng.randint(-3, 3) for _ in range(length)]
        return [_randomize_scalar(value[min(i, len(value) - 1)], rng) for i in range(length)]
    return value


def _random_stress_function_test_inputs(test_input: Any, n_samples: int = 3) -> list[list[Any]]:
    args = list(test_input) if isinstance(test_input, (list, tuple)) else [test_input]
    rng = random.Random(json.dumps(args, sort_keys=True, default=repr))
    probes: list[list[Any]] = []
    for _ in range(n_samples):
        probes.append([_randomize_scalar(value, rng) for value in args])
    return _dedupe_preserving_order([probe for probe in probes if probe != args])


def _build_reference_labeled_test(
    problem: dict[str, Any],
    base_test: dict[str, Any],
    candidate_input: Any,
    timeout: int,
) -> dict[str, Any] | None:
    reference_solution = problem.get("reference_solution")
    if not reference_solution:
        return None

    if base_test.get("testtype") == "stdin":
        # We currently skip stdin mutation synthesis because the benchmark tasks
        # do not expose safe structured transforms for arbitrary programs.
        return None

    entry_point = problem.get("entry_point")
    if not entry_point:
        return None

    execution = execute_code_function(
        code=reference_solution,
        entry_point=entry_point,
        test_input=list(candidate_input) if isinstance(candidate_input, (list, tuple)) else [candidate_input],
        timeout=timeout,
    )
    if execution.get("status") != "passed":
        return None
    return {"input": candidate_input, "output": execution.get("observed_output")}


def _strategy_flags(config: FalsificationConfig) -> dict[str, bool]:
    strategy = config.probe_strategy
    flags = {
        "public": True,
        "mutation": True,
        "edge_case": True,
        "random_stress": True,
        "differential": True,
        "hidden": bool(config.allow_hidden_test_probes),
    }
    if strategy == "public_only":
        flags.update({"mutation": False, "edge_case": False, "random_stress": False, "differential": False, "hidden": False})
    elif strategy == "generated_only":
        flags.update({"public": False, "mutation": True, "edge_case": True, "random_stress": True, "differential": False, "hidden": False})
    elif strategy == "mutation_only":
        flags.update({"public": False, "edge_case": False, "random_stress": False, "differential": False, "hidden": False})
    elif strategy == "edge_case":
        flags.update({"mutation": False, "random_stress": False, "differential": False, "hidden": False})
    elif strategy == "random_stress":
        flags.update({"mutation": False, "edge_case": False, "differential": False, "hidden": False})
    elif strategy == "differential_only":
        flags.update({"public": False, "mutation": False, "edge_case": False, "random_stress": False, "differential": True, "hidden": False})
    elif strategy == "public_then_hidden":
        flags.update({"mutation": False, "edge_case": False, "random_stress": False, "differential": False, "hidden": bool(config.allow_hidden_test_probes)})
    return flags


def _default_round_family_schedule(config: FalsificationConfig) -> list[str]:
    strategy = config.probe_strategy
    if strategy == "public_only":
        return ["public"] * max(1, config.n_rounds)
    if strategy == "mutation_only":
        return ["mutation"] * max(1, config.n_rounds)
    if strategy == "edge_case":
        return ["edge_case"] * max(1, config.n_rounds)
    if strategy == "random_stress":
        return ["random_stress"] * max(1, config.n_rounds)
    if strategy == "differential_only":
        return ["differential"] * max(1, config.n_rounds)
    if strategy == "public_then_hidden":
        return ["public"] + ["hidden"] * max(0, config.n_rounds - 1)

    # For the main adaptive falsification path, force each round to target a
    # distinct failure mode before the schedule cycles. This makes sequential
    # falsification empirically different from one-shot generated filtering.
    if strategy in {"adaptive_population", "generated_only"}:
        base = ["edge_case", "mutation", "random_stress", "differential"]
        if strategy == "generated_only":
            base = ["edge_case", "mutation", "random_stress"]
        schedule: list[str] = []
        while len(schedule) < max(1, config.n_rounds):
            schedule.extend(base)
        return schedule[: max(1, config.n_rounds)]

    return ["public"] * max(1, config.n_rounds)


def _family_balanced_probe_subset(
    probes: list[dict[str, Any]],
    family_schedule: list[str],
    max_probes: int,
) -> list[dict[str, Any]]:
    if max_probes <= 0:
        return []

    remaining = list(probes)
    selected: list[dict[str, Any]] = []
    for family in family_schedule:
        if len(selected) >= max_probes:
            break
        for idx, probe in enumerate(remaining):
            if probe.get("family") == family:
                selected.append(probe)
                remaining.pop(idx)
                break

    for probe in remaining:
        if len(selected) >= max_probes:
            break
        selected.append(probe)
    return selected


def _build_probe_bank(problem: dict[str, Any], config: FalsificationConfig) -> list[dict[str, Any]]:
    if problem.get("type") == "math":
        # We do not use reference answers as falsification probes. Math tasks
        # need a real verifier/PRM before they can support adversarial probing;
        # until then selection falls back to non-oracle answer agreement.
        return []

    strategy_flags = _strategy_flags(config)
    public_tests = list(problem.get("public_tests", []))[: config.max_public_tests_for_probes]
    hidden_tests = list(problem.get("hidden_tests", [])) if strategy_flags["hidden"] else []
    probes: list[dict[str, Any]] = []

    if strategy_flags["public"]:
        for idx, test in enumerate(public_tests):
            probes.append({"kind": "public_test", "family": "public", "test": test, "round": idx})

    for idx, test in enumerate(hidden_tests):
        probes.append({"kind": "hidden_test", "family": "hidden", "test": test, "round": idx + len(probes)})

    generated = 0
    if strategy_flags["mutation"]:
        for idx, test in enumerate(public_tests):
            if test.get("testtype") == "stdin":
                continue
            for mutated_input in _mutate_function_test_inputs(test.get("input", [])):
                labeled = _build_reference_labeled_test(problem, test, mutated_input, timeout=config.timeout)
                if not labeled:
                    continue
                probes.append(
                    {
                        "kind": "mutation_test",
                        "family": "mutation",
                        "round": idx,
                        "base_test": test,
                        "test": labeled,
                    }
                )
                generated += 1
                if generated >= config.max_generated_probes:
                    break
            if generated >= config.max_generated_probes:
                break

    if strategy_flags["edge_case"]:
        generated_edge = 0
        for idx, test in enumerate(public_tests):
            if test.get("testtype") == "stdin":
                continue
            for candidate_input in _edge_case_function_test_inputs(test.get("input", [])):
                labeled = _build_reference_labeled_test(problem, test, candidate_input, timeout=config.timeout)
                if not labeled:
                    continue
                probes.append(
                    {
                        "kind": "edge_case_test",
                        "family": "edge_case",
                        "round": idx,
                        "base_test": test,
                        "test": labeled,
                    }
                )
                generated_edge += 1
                if generated_edge >= config.max_edge_case_probes:
                    break
            if generated_edge >= config.max_edge_case_probes:
                break

    if strategy_flags["random_stress"]:
        generated_stress = 0
        for idx, test in enumerate(public_tests):
            if test.get("testtype") == "stdin":
                continue
            for candidate_input in _random_stress_function_test_inputs(test.get("input", [])):
                labeled = _build_reference_labeled_test(problem, test, candidate_input, timeout=config.timeout)
                if not labeled:
                    continue
                probes.append(
                    {
                        "kind": "random_stress_test",
                        "family": "random_stress",
                        "round": idx,
                        "base_test": test,
                        "test": labeled,
                    }
                )
                generated_stress += 1
                if generated_stress >= config.max_random_stress_probes:
                    break
            if generated_stress >= config.max_random_stress_probes:
                break

    return _dedupe_preserving_order(probes)


def _build_differential_probe_bank(
    problem: dict[str, Any],
    surviving_records: list[dict[str, Any]],
    config: FalsificationConfig,
    execution_cache: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    if problem.get("type") == "math":
        return []
    if len(surviving_records) <= 1:
        return []

    strategy_flags = _strategy_flags(config)
    if not strategy_flags.get("differential", False):
        return []

    public_tests = list(problem.get("public_tests", []))[: config.max_public_tests_for_probes]
    probes: list[dict[str, Any]] = []
    seen_inputs: set[str] = set()

    for idx, test in enumerate(public_tests):
        if test.get("testtype") == "stdin":
            continue
        candidate_inputs = []
        candidate_inputs.extend(_mutate_function_test_inputs(test.get("input", [])))
        candidate_inputs.extend(_edge_case_function_test_inputs(test.get("input", [])))
        candidate_inputs.extend(_random_stress_function_test_inputs(test.get("input", []), n_samples=4))
        for candidate_input in _dedupe_preserving_order(candidate_inputs):
            input_signature = json.dumps(candidate_input, sort_keys=True, default=repr)
            if input_signature in seen_inputs:
                continue
            seen_inputs.add(input_signature)

            unlabeled_probe = {
                "kind": "differential_candidate",
                "family": "differential_candidate",
                "round": idx,
                "base_test": test,
                "test": {"input": candidate_input},
            }
            execution_tokens: set[str] = set()
            for record in surviving_records:
                cache_key = (record["text"], _probe_signature(unlabeled_probe))
                if cache_key not in execution_cache:
                    execution_cache[cache_key] = _execute_probe(problem, record["text"], unlabeled_probe, timeout=config.timeout)
                execution_tokens.add(_normalize_output_token(execution_cache[cache_key]["execution"]))
            if len(execution_tokens) <= 1:
                continue

            labeled = _build_reference_labeled_test(problem, test, candidate_input, timeout=config.timeout)
            if not labeled:
                continue
            probes.append(
                {
                    "kind": "differential_test",
                    "family": "differential",
                    "round": idx,
                    "base_test": test,
                    "test": labeled,
                    "candidate_input": candidate_input,
                    "disagreement_count": len(execution_tokens),
                }
            )
            if len(probes) >= config.max_differential_probes:
                return _dedupe_preserving_order(probes)

    return _dedupe_preserving_order(probes)


def generate_probe(problem: dict[str, Any], round_index: int) -> dict[str, Any]:
    return generate_probe_with_strategy(problem, round_index, strategy="adaptive_population")


def generate_probe_with_strategy(problem: dict[str, Any], round_index: int, strategy: str) -> dict[str, Any]:
    config = FalsificationConfig(probe_strategy=strategy)
    bank = _build_probe_bank(problem, config)
    if not bank:
        return {"kind": "no_probe", "round": round_index}
    return dict(bank[min(round_index, len(bank) - 1)])


def _execute_probe(problem: dict[str, Any], candidate_text: str, probe: dict[str, Any], timeout: int) -> dict[str, Any]:
    if probe.get("kind") == "answer_check":
        return {
            "detected": False,
            "execution": {
                "status": "skipped_oracle_probe",
                "passed": False,
                "note": "answer_check probes are disabled because they use hidden math answers.",
            },
        }

    test = probe.get("test")
    if not isinstance(test, dict):
        return {"detected": False, "execution": {"status": "skipped"}}

    scoped_problem = {
        **problem,
        "public_tests": [test],
        "hidden_tests": [],
    }
    if test.get("testtype") == "stdin" and "output" not in test:
        execution = execute_stdin_program(candidate_text, stdin=test.get("input", ""), timeout=timeout)
        return {"detected": False, "execution": execution}
    if test.get("testtype") != "stdin" and "output" not in test:
        execution = execute_code_function(
            code=candidate_text,
            entry_point=problem["entry_point"],
            test_input=test.get("input", []),
            timeout=timeout,
        )
        return {"detected": False, "execution": execution}

    result = evaluate_candidate(scoped_problem, candidate_text, use_hidden=False, timeout=timeout)
    return {"detected": not result["passed"], "execution": result}


def check_probe_result(problem: dict[str, Any], candidate_text: str, probe: dict[str, Any], timeout: int = 10) -> dict[str, Any]:
    return _execute_probe(problem, candidate_text, probe, timeout=timeout)


def _consensus_detected_flags(executions: list[dict[str, Any]]) -> list[bool] | None:
    tokens = [_normalize_output_token(item["execution"]) for item in executions]
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    consensus_token, consensus_count = max(counts.items(), key=lambda item: item[1])
    if consensus_count <= len(tokens) // 2:
        return None
    if len(counts) == 1:
        return None
    return [token != consensus_token for token in tokens]


def _score_probe(
    problem: dict[str, Any],
    surviving_records: list[dict[str, Any]],
    probe: dict[str, Any],
    timeout: int,
    execution_cache: dict[tuple[str, str], dict[str, Any]],
) -> tuple[tuple[int, int, int], list[dict[str, Any]], list[bool] | None]:
    probe_key = _probe_signature(probe)
    executions: list[dict[str, Any]] = []
    detected_flags: list[bool] = []

    for record in surviving_records:
        cache_key = (record["text"], probe_key)
        if cache_key not in execution_cache:
            execution_cache[cache_key] = _execute_probe(problem, record["text"], probe, timeout=timeout)
        result = execution_cache[cache_key]
        executions.append(result)
        detected_flags.append(bool(result.get("detected", False)))

    if _is_labeled_probe(probe):
        num_detected = sum(detected_flags)
        if num_detected == 0 or num_detected == len(surviving_records):
            return (-1, -1, -1), executions, detected_flags
        diversity = len({_normalize_output_token(item["execution"]) for item in executions})
        novelty_bonus = 1 if probe.get("family") not in {"public", "hidden"} else 0
        return (num_detected, diversity + novelty_bonus, len(surviving_records) - num_detected), executions, detected_flags

    consensus_flags = _consensus_detected_flags(executions)
    if consensus_flags is None:
        return (-1, -1, -1), executions, None
    num_detected = sum(consensus_flags)
    diversity = len({_normalize_output_token(item["execution"]) for item in executions})
    novelty_bonus = 1 if probe.get("family") not in {"public", "hidden"} else 0
    return (num_detected, diversity + novelty_bonus, len(surviving_records) - num_detected), executions, consensus_flags


def _choose_best_probe(
    problem: dict[str, Any],
    records: list[dict[str, Any]],
    config: FalsificationConfig,
    used_probes: set[str],
    execution_cache: dict[tuple[str, str], dict[str, Any]],
    preferred_families: list[str] | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[bool] | None]:
    survivors = [record for record in records if record.get("survived")]
    if len(survivors) <= 1:
        return None, [], None

    probe_bank = _build_probe_bank(problem, config)
    probe_bank.extend(_build_differential_probe_bank(problem, survivors, config, execution_cache))
    candidate_banks: list[list[dict[str, Any]]] = []
    if preferred_families:
        preferred = [probe for probe in probe_bank if probe.get("family") in set(preferred_families)]
        fallback = [probe for probe in probe_bank if probe.get("family") not in set(preferred_families)]
        candidate_banks = [preferred, fallback]
    else:
        candidate_banks = [probe_bank]

    if not config.adaptive_probe_selection:
        for probe_bank_candidate in candidate_banks:
            for probe in probe_bank_candidate:
                signature = _probe_signature(probe)
                if signature in used_probes:
                    continue
                score, executions, flags = _score_probe(problem, survivors, probe, config.timeout, execution_cache)
                if score[0] < 0:
                    continue
                return probe, executions, flags
        return None, [], None

    best_probe: dict[str, Any] | None = None
    best_executions: list[dict[str, Any]] = []
    best_flags: list[bool] | None = None
    best_score = (-1, -1, -1)

    for probe_bank_candidate in candidate_banks:
        for probe in probe_bank_candidate:
            signature = _probe_signature(probe)
            if signature in used_probes:
                continue
            score, executions, flags = _score_probe(problem, survivors, probe, config.timeout, execution_cache)
            if score > best_score:
                best_score = score
                best_probe = probe
                best_executions = executions
                best_flags = flags
        if best_score[0] >= 0 and best_probe is not None:
            break

    if best_score[0] < 0:
        return None, [], None
    return best_probe, best_executions, best_flags


def sequential_falsify_candidates(
    candidates: list[dict[str, Any]],
    problem: dict[str, Any],
    config: FalsificationConfig,
) -> dict[str, Any]:
    records = [
        {
            **candidate,
            "candidate_order": index,
            "survived": True,
            "rejected": False,
            "wealth": 1.0,
            "confidence": 0.0,
            "selection_score": 0.0,
            "rounds_survived": 0,
            "trace": [],
        }
        for index, candidate in enumerate(candidates)
    ]

    used_probes: set[str] = set()
    execution_cache: dict[tuple[str, str], dict[str, Any]] = {}
    round_family_schedule = _default_round_family_schedule(config)

    def _apply_probe_round(round_index: int, probe: dict[str, Any], probe_executions: list[dict[str, Any]], detected_flags: list[bool]) -> None:
        alive_records = [record for record in records if record.get("survived")]
        p_k = estimate_detection_probability(round_index)

        for record, probe_result, detected in zip(alive_records, probe_executions, detected_flags):
            detected = bool(detected)
            e_k = compute_e_value(detected, delta_k=config.delta, p_k=p_k)
            record["wealth"] *= e_k
            record["trace"].append(
                {
                    "round": round_index,
                    "probe": probe,
                    "probe_detected_error": detected,
                    "p_k": p_k,
                    "e_value": e_k,
                    "wealth": record["wealth"],
                    "execution": probe_result["execution"],
                    "round_type": probe.get("round_type", "main"),
                }
            )
            if detected and config.eliminate_on_detection:
                record["survived"] = False
                record["rejected"] = True
                record["confidence"] = 0.0
                record["selection_score"] = 0.0
                record["rounds_survived"] = round_index
            else:
                record["rounds_survived"] = round_index + 1

    for round_index in range(config.n_rounds):
        preferred_families = None
        if config.enforce_round_family_diversity and round_family_schedule:
            preferred_families = [round_family_schedule[min(round_index, len(round_family_schedule) - 1)]]
        probe, probe_executions, detected_flags = _choose_best_probe(
            problem=problem,
            records=records,
            config=config,
            used_probes=used_probes,
            execution_cache=execution_cache,
            preferred_families=preferred_families,
        )
        if probe is None or detected_flags is None:
            break

        probe_signature = _probe_signature(probe)
        if preferred_families:
            probe = {**probe, "scheduled_family": preferred_families[0]}
        used_probes.add(probe_signature)
        _apply_probe_round(round_index, probe, probe_executions, detected_flags)

    # Spend additional compute only when the survivor pool is still ambiguous.
    # These extra rounds stay true to the falsification framing: they synthesize
    # differential probes against the remaining population rather than repairing
    # a single candidate.
    for extra_index in range(config.max_tiebreak_rounds):
        if sum(1 for record in records if record.get("survived")) <= 1:
            break
        tiebreak_config = FalsificationConfig(
            n_rounds=1,
            max_tiebreak_rounds=0,
            delta=config.delta,
            timeout=config.timeout,
            alpha=config.alpha,
            probe_strategy="differential_only",
            adaptive_probe_selection=True,
            eliminate_on_detection=config.eliminate_on_detection,
            confidence_mode=config.confidence_mode,
            max_public_tests_for_probes=config.max_public_tests_for_probes,
            max_generated_probes=config.max_generated_probes,
            max_edge_case_probes=config.max_edge_case_probes,
            max_random_stress_probes=config.max_random_stress_probes,
            max_differential_probes=max(config.max_differential_probes, 12),
            allow_hidden_test_probes=False,
            selection_confidence_weight=config.selection_confidence_weight,
            selection_public_weight=config.selection_public_weight,
            selection_trace_weight=config.selection_trace_weight,
        )
        probe, probe_executions, detected_flags = _choose_best_probe(
            problem=problem,
            records=records,
            config=tiebreak_config,
            used_probes=used_probes,
            execution_cache=execution_cache,
        )
        if probe is None or detected_flags is None:
            break
        probe_signature = _probe_signature(probe)
        probe = {**probe, "round_type": "tiebreak"}
        used_probes.add(probe_signature)
        _apply_probe_round(config.n_rounds + extra_index, probe, probe_executions, detected_flags)

    survivor_count = sum(1 for record in records if record.get("survived"))
    total_round_budget = max(1, config.n_rounds + config.max_tiebreak_rounds)
    math_agreement = _math_agreement_scores(records) if problem.get("type") == "math" else {}
    for record in records:
        if problem.get("type") == "math":
            public_score = math_agreement.get(int(record.get("candidate_order", 0)), 0.0)
        else:
            public_eval = evaluate_candidate(problem, record["text"], use_hidden=False, timeout=config.timeout)
            num_passed = float(public_eval.get("num_passed", 0))
            num_tests = float(public_eval.get("num_tests", 0))
            public_score = num_passed / num_tests if num_tests > 0 else 0.0
        trace_strength = min(1.0, float(record.get("rounds_survived", 0)) / float(total_round_budget))
        record["public_score"] = public_score
        record["trace_strength"] = trace_strength
        if not record.get("survived"):
            record["confidence"] = 0.0
            record["selection_score"] = 0.0
            continue
        base_confidence = (
            calibrated_confidence_from_wealth(record["wealth"], alpha=config.alpha)
            if record.get("trace")
            else 0.0
        )
        exclusivity_bonus = 0.0
        if survivor_count > 0:
            exclusivity_bonus = 0.1 * (1.0 - (survivor_count - 1) / max(len(records) - 1, 1))
        if config.confidence_mode == "none":
            confidence = 0.0
            selection_score = 1.0
        elif config.confidence_mode == "survival_only":
            confidence = min(1.0, exclusivity_bonus)
            selection_score = (
                config.selection_public_weight * public_score
                + config.selection_trace_weight * trace_strength
                + (1.0 - config.selection_public_weight - config.selection_trace_weight)
            )
        else:
            confidence = min(1.0, base_confidence + exclusivity_bonus)
            selection_score = (
                config.selection_confidence_weight * confidence
                + config.selection_public_weight * public_score
                + config.selection_trace_weight * trace_strength
            )
        record["confidence"] = confidence
        record["selection_score"] = selection_score

    return {"records": records}


def sequential_falsify(
    candidate_text: str,
    problem: dict[str, Any],
    config: FalsificationConfig,
) -> dict[str, Any]:
    payload = sequential_falsify_candidates(
        candidates=[{"text": candidate_text, "candidate_id": "candidate_0"}],
        problem=problem,
        config=config,
    )
    return payload["records"][0]


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run sequential falsification for one candidate/problem pair.")
    parser.add_argument("--problem-file", required=True)
    parser.add_argument("--candidate-file", required=True)
    parser.add_argument("--n-rounds", type=int, default=4)
    parser.add_argument("--probe-strategy", default="adaptive_population")
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    problem = json.loads(Path(args.problem_file).read_text(encoding="utf-8"))
    candidate_text = Path(args.candidate_file).read_text(encoding="utf-8")
    result = sequential_falsify(
        candidate_text,
        problem,
        FalsificationConfig(n_rounds=args.n_rounds, probe_strategy=args.probe_strategy),
    )
    dump_json(result, args.output_file)


if __name__ == "__main__":
    _cli()
