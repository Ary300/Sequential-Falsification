"""Posterior-style utilities for knowledge arbitration experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log


def _clip_probability(value: float, eps: float = 1e-6) -> float:
    return min(max(value, eps), 1.0 - eps)


@dataclass(frozen=True)
class ArbitrationFeatures:
    """Observable features for one arbitration decision.

    This is intentionally lightweight. It is not the full theorem object; it is
    the first practical scaffold for experiments that need a principled
    reliability-aware mixing rule.
    """

    parametric_score: float
    contextual_score: float
    context_reliability: float
    parametric_reliability: float = 0.5
    conflict_magnitude: float = 0.0


@dataclass(frozen=True)
class ArbitrationResult:
    """Result of a Bayes-inspired arbitration step."""

    context_weight: float
    parametric_weight: float
    arbitration_probability: float
    mixed_log_score: float


def logit(probability: float) -> float:
    p = _clip_probability(probability)
    return log(p / (1.0 - p))


def sigmoid(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def bayes_arbitration_probability(features: ArbitrationFeatures) -> float:
    """Return a simple Bayes-inspired probability of trusting context.

    This is a research scaffold rather than the finished theorem-derived rule.
    It combines:

    - relative contextual vs parametric evidence,
    - source reliability difference,
    - a conflict-magnitude correction term.
    """

    contextual_logit = logit(_clip_probability(features.contextual_score))
    parametric_logit = logit(_clip_probability(features.parametric_score))
    reliability_gap = logit(_clip_probability(features.context_reliability)) - logit(
        _clip_probability(features.parametric_reliability)
    )
    combined = (
        contextual_logit
        - parametric_logit
        + reliability_gap
        + float(features.conflict_magnitude)
    )
    return sigmoid(combined)


def bayes_arbitration_result(features: ArbitrationFeatures) -> ArbitrationResult:
    """Return a reliability-aware arbitration result."""

    context_weight = bayes_arbitration_probability(features)
    parametric_weight = 1.0 - context_weight
    mixed_log_score = (
        context_weight * log(_clip_probability(features.contextual_score))
        + parametric_weight * log(_clip_probability(features.parametric_score))
    )
    return ArbitrationResult(
        context_weight=context_weight,
        parametric_weight=parametric_weight,
        arbitration_probability=context_weight,
        mixed_log_score=mixed_log_score,
    )
