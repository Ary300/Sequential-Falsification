"""Track B matching-protocol scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Any

from selection import select_best_candidate


@dataclass
class MatchingConfig:
    score_temperature: float = 1.0
    score_smoothing: float = 1e-6
    max_queries: int | None = None


def extract_scalar_signal(score: Any) -> float:
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)):
        return float(score)
    if isinstance(score, dict):
        for key in ["selection_score", "confidence", "public_score", "cluster_share", "cluster_size", "rounds_survived"]:
            if key in score:
                return float(score[key])
    return 0.0


def normalize_posterior(weights: list[float]) -> list[float]:
    total = sum(weights)
    if total <= 0:
        return [1.0 / len(weights) for _ in weights] if weights else []
    return [weight / total for weight in weights]


def run_matching_protocol(
    candidates: list[dict[str, Any]],
    verifier_scores: list[Any],
    config: MatchingConfig,
) -> dict[str, Any]:
    """Approximate matching-protocol scaffold.

    This is not yet the theorem-grade SPRT proof object. It is a computational
    placeholder that turns verifier scores into a posterior-like distribution so
    Track B experiments can start before the full theorem machinery lands.
    """

    if len(candidates) != len(verifier_scores):
        raise ValueError("candidates and verifier_scores must have the same length")

    scalar_scores = [extract_scalar_signal(score) for score in verifier_scores]
    scaled_weights = [
        exp(score / max(config.score_temperature, config.score_smoothing))
        for score in scalar_scores
    ]
    posterior = normalize_posterior(scaled_weights)

    enriched_candidates = []
    for idx, (candidate, probability, score) in enumerate(zip(candidates, posterior, scalar_scores)):
        enriched_candidates.append(
            {
                **candidate,
                "candidate_order": int(candidate.get("candidate_order", idx)),
                "matching_posterior": probability,
                "matching_score": score,
                "confidence": max(float(candidate.get("confidence", 0.0)), probability),
                "selection_score": max(float(candidate.get("selection_score", 0.0)), probability),
            }
        )

    selected = max(
        enriched_candidates,
        key=lambda row: (
            float(row.get("matching_posterior", 0.0)),
            float(row.get("selection_score", 0.0)),
            -int(row.get("candidate_order", 0)),
        ),
    ) if enriched_candidates else None

    return {
        "selected": selected or select_best_candidate(enriched_candidates),
        "posterior": posterior,
        "scalar_scores": scalar_scores,
        "config": {
            "score_temperature": config.score_temperature,
            "score_smoothing": config.score_smoothing,
            "max_queries": config.max_queries,
        },
    }
