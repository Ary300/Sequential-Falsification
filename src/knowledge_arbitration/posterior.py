"""Bayes-style arbitration helpers for knowledge-conflict experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log


def _clip_probability(value: float, eps: float = 1e-8) -> float:
    return min(max(value, eps), 1.0 - eps)


def _logit(value: float) -> float:
    value = _clip_probability(value)
    return log(value / (1.0 - value))


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


@dataclass(frozen=True)
class ArbitrationFeatures:
    parametric_confidence: float
    contextual_confidence: float
    context_reliability: float
    conflict_score: float = 0.0
    popularity_prior: float = 0.5
    dynamicity_score: float = 0.0


@dataclass(frozen=True)
class ArbitrationDecision:
    weight_context: float
    weight_parametric: float
    mixed_probability: float
    metadata: dict[str, float]


def bayes_optimal_weight(features: ArbitrationFeatures) -> float:
    """Approximate Bayes-style context weight from observable features.

    This is deliberately lightweight scaffolding rather than a final theorem
    implementation. It exposes the core shape the paper wants:

    - context weight rises with reliability,
    - falls as popularity-supported parametric prior gets stronger,
    - and is amplified when direct conflict is high.
    """

    reliability_term = 1.75 * (features.context_reliability - 0.5)
    prior_term = -1.25 * (features.popularity_prior - 0.5)
    conflict_term = 0.75 * features.conflict_score
    dynamicity_term = 0.50 * features.dynamicity_score
    return _sigmoid(reliability_term + prior_term + conflict_term + dynamicity_term)


def geometric_mixture(features: ArbitrationFeatures) -> ArbitrationDecision:
    weight_context = bayes_optimal_weight(features)
    weight_parametric = 1.0 - weight_context
    mixed_logit = (
        weight_parametric * _logit(features.parametric_confidence)
        + weight_context * _logit(features.contextual_confidence)
    )
    mixed_probability = _sigmoid(mixed_logit)
    return ArbitrationDecision(
        weight_context=weight_context,
        weight_parametric=weight_parametric,
        mixed_probability=mixed_probability,
        metadata={
            "conflict_score": features.conflict_score,
            "context_reliability": features.context_reliability,
            "popularity_prior": features.popularity_prior,
            "dynamicity_score": features.dynamicity_score,
        },
    )
