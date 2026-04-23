"""Synthetic oracle constructions for arbitration experiments."""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .posterior import ArbitrationFeatures, geometric_mixture


@dataclass(frozen=True)
class SyntheticArbitrationCase:
    parametric_confidence: float
    contextual_confidence: float
    context_reliability: float
    conflict_score: float
    popularity_prior: float
    dynamicity_score: float

    def to_features(self) -> ArbitrationFeatures:
        return ArbitrationFeatures(
            parametric_confidence=self.parametric_confidence,
            contextual_confidence=self.contextual_confidence,
            context_reliability=self.context_reliability,
            conflict_score=self.conflict_score,
            popularity_prior=self.popularity_prior,
            dynamicity_score=self.dynamicity_score,
        )


def synthetic_grid() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for parametric_confidence in [0.2, 0.5, 0.8]:
        for contextual_confidence in [0.2, 0.5, 0.8]:
            for context_reliability in [0.2, 0.5, 0.8]:
                case = SyntheticArbitrationCase(
                    parametric_confidence=parametric_confidence,
                    contextual_confidence=contextual_confidence,
                    context_reliability=context_reliability,
                    conflict_score=abs(contextual_confidence - parametric_confidence),
                    popularity_prior=parametric_confidence,
                    dynamicity_score=1.0 - context_reliability,
                )
                decision = geometric_mixture(case.to_features())
                rows.append({**asdict(case), **decision.metadata, "mixed_probability": decision.mixed_probability})
    return rows
