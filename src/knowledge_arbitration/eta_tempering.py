"""Eta-tempered decoding over saved theorem-3 reasoning traces."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
import random
from typing import Any

from utils.metrics import accuracy, brier_score, expected_calibration_error

from .real_generation import PROMPT_STYLES, _answer_set, _answers_match, _question_block


@dataclass(frozen=True)
class CandidateScore:
    answer: str
    normalized_answer: str
    posterior_logprob: float
    prior_logprob: float


@dataclass(frozen=True)
class EtaPrediction:
    eta: float
    answer: str
    confidence: float
    correct: int
    probabilities: dict[str, float]


def candidate_answers_from_row(row: dict[str, Any]) -> list[str]:
    metadata = row.get("metadata", {})
    ordered: list[str] = []
    seen: set[str] = set()

    def _add(values: Any) -> None:
        if values is None:
            return
        if isinstance(values, str):
            local_values = [values]
        elif hasattr(values, "tolist"):
            local_values = list(values.tolist())
        elif isinstance(values, tuple):
            local_values = list(values)
        elif isinstance(values, list):
            local_values = values
        else:
            local_values = [values]
        for value in local_values:
            text = str(value or "").strip()
            if not text:
                continue
            normalized = next(iter(_answer_set(text)), "")
            if not normalized or normalized in seen:
                continue
            ordered.append(text)
            seen.add(normalized)

    _add(metadata.get("parametric_answers"))
    _add(metadata.get("aligned_context_answers"))
    _add(metadata.get("conflict_context_answers"))
    _add(row.get("gold_answers"))
    _add(row.get("answer"))
    return ordered


def _softmax(logits: list[float]) -> list[float]:
    if not logits:
        return []
    max_logit = max(logits)
    weights = [exp(value - max_logit) for value in logits]
    total = sum(weights)
    if total <= 0.0:
        return [1.0 / len(logits)] * len(logits)
    return [value / total for value in weights]


def tempered_distribution(
    scores: list[CandidateScore],
    *,
    eta: float,
) -> list[tuple[CandidateScore, float]]:
    combined = [
        float(eta) * candidate.posterior_logprob + (1.0 - float(eta)) * candidate.prior_logprob
        for candidate in scores
    ]
    probabilities = _softmax(combined)
    return list(zip(scores, probabilities))


def predict_with_eta(
    row: dict[str, Any],
    scores: list[CandidateScore],
    *,
    eta: float,
) -> EtaPrediction:
    distribution = tempered_distribution(scores, eta=eta)
    best_candidate, best_probability = max(distribution, key=lambda item: item[1])
    gold_answers = _answer_set(row.get("gold_answers"))
    confidence_table = {candidate.answer: probability for candidate, probability in distribution}
    return EtaPrediction(
        eta=float(eta),
        answer=best_candidate.answer,
        confidence=float(best_probability),
        correct=int(_answers_match(best_candidate.answer, gold_answers)),
        probabilities=confidence_table,
    )


def build_messages_for_row(row: dict[str, Any], *, condition: str, long_cot: bool) -> list[dict[str, str]]:
    style = PROMPT_STYLES["long_cot"] if long_cot else PROMPT_STYLES["no_cot"]
    return [
        {"role": "system", "content": style.system_prompt},
        {"role": "user", "content": _question_block(row, condition)},
    ]


def choose_eta(
    calibration_rows: list[dict[str, Any]],
    scored_examples: dict[str, list[CandidateScore]],
    *,
    eta_values: list[float],
) -> dict[str, Any]:
    per_eta: list[dict[str, Any]] = []
    baseline_accuracy = None
    baseline_brier = None

    for eta in eta_values:
        predictions = [
            predict_with_eta(row, scored_examples[str(row["id"])], eta=eta)
            for row in calibration_rows
            if str(row["id"]) in scored_examples
        ]
        confidences = [item.confidence for item in predictions]
        outcomes = [item.correct for item in predictions]
        metrics = {
            "eta": eta,
            "count": len(predictions),
            "accuracy": accuracy(bool(value) for value in outcomes),
            "ece": expected_calibration_error(confidences, outcomes),
            "brier": brier_score(confidences, outcomes),
            "mean_confidence": (sum(confidences) / len(confidences)) if confidences else 0.0,
        }
        if abs(eta - 1.0) < 1e-9:
            baseline_accuracy = metrics["accuracy"]
            baseline_brier = metrics["brier"]
        per_eta.append(metrics)

    if baseline_accuracy is None or baseline_brier is None:
        raise ValueError("Eta grid must include eta=1.0 to define the untempered baseline.")

    eligible = [
        row
        for row in per_eta
        if row["accuracy"] >= baseline_accuracy - 1e-9 and row["brier"] <= baseline_brier - 1e-12
    ]
    largest_no_harm = max(eligible, key=lambda row: row["eta"]) if eligible else max(
        [row for row in per_eta if row["accuracy"] >= baseline_accuracy - 1e-9],
        key=lambda row: (-(row["brier"]), row["eta"]),
    )
    brier_optimal = min(per_eta, key=lambda row: (row["brier"], -row["accuracy"], row["eta"]))
    return {
        "selected_eta": brier_optimal["eta"],
        "selected_metrics": brier_optimal,
        "baseline_metrics": next(row for row in per_eta if abs(row["eta"] - 1.0) < 1e-9),
        "largest_no_harm_eta": largest_no_harm["eta"],
        "largest_no_harm_metrics": largest_no_harm,
        "oracle_eta": brier_optimal["eta"],
        "oracle_metrics": brier_optimal,
        "per_eta": per_eta,
    }


def split_rows(
    rows: list[dict[str, Any]],
    *,
    calibration_size: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    unique_rows = list(rows)
    rng = random.Random(seed)
    rng.shuffle(unique_rows)
    if len(unique_rows) <= 1:
        return unique_rows, []
    calibration_count = min(calibration_size, max(1, len(unique_rows) - 1))
    calibration = unique_rows[:calibration_count]
    evaluation = unique_rows[calibration_count:]
    return calibration, evaluation


def evaluate_eta(
    rows: list[dict[str, Any]],
    scored_examples: dict[str, list[CandidateScore]],
    *,
    eta: float,
) -> dict[str, Any]:
    predictions = [
        predict_with_eta(row, scored_examples[str(row["id"])], eta=eta)
        for row in rows
        if str(row["id"]) in scored_examples
    ]
    confidences = [item.confidence for item in predictions]
    outcomes = [item.correct for item in predictions]
    return {
        "eta": eta,
        "count": len(predictions),
        "accuracy": accuracy(bool(value) for value in outcomes),
        "ece": expected_calibration_error(confidences, outcomes),
        "brier": brier_score(confidences, outcomes),
        "mean_confidence": (sum(confidences) / len(confidences)) if confidences else 0.0,
        "overconfidence_gap": ((sum(confidences) / len(confidences)) if confidences else 0.0)
        - accuracy(bool(value) for value in outcomes),
        "predictions": [
            {
                "id": str(row["id"]),
                "answer": prediction.answer,
                "confidence": round(prediction.confidence, 6),
                "correct": prediction.correct,
            }
            for row, prediction in zip(
                [row for row in rows if str(row["id"]) in scored_examples],
                predictions,
                strict=False,
            )
        ],
    }
