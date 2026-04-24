"""Feature scaffolding for knowledge arbitration experiments."""

from __future__ import annotations

from dataclasses import dataclass


def _safe_probability(value: float | None, default: float = 0.5) -> float:
    if value is None:
        return default
    return min(max(float(value), 0.0), 1.0)


@dataclass(frozen=True)
class ReliabilityFeatures:
    """Observable features for arbitration.

    This dataclass is intentionally modest. It gives the repo a stable schema
    for benchmark records before the final theorem-derived feature set is
    frozen.
    """

    parametric_confidence: float
    contextual_confidence: float
    retrieval_score: float
    popularity_prior: float
    semantic_entropy: float
    conflict_magnitude: float
    temporal_freshness: float


def build_reliability_features(
    *,
    parametric_confidence: float | None = None,
    contextual_confidence: float | None = None,
    retrieval_score: float | None = None,
    popularity_prior: float | None = None,
    semantic_entropy: float | None = None,
    temporal_freshness: float | None = None,
) -> ReliabilityFeatures:
    """Build a normalized feature object for arbitration experiments."""

    parametric = _safe_probability(parametric_confidence)
    contextual = _safe_probability(contextual_confidence)
    return ReliabilityFeatures(
        parametric_confidence=parametric,
        contextual_confidence=contextual,
        retrieval_score=_safe_probability(retrieval_score),
        popularity_prior=_safe_probability(popularity_prior),
        semantic_entropy=_safe_probability(semantic_entropy),
        conflict_magnitude=abs(contextual - parametric),
        temporal_freshness=_safe_probability(temporal_freshness),
    )

