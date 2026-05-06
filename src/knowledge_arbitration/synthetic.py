"""Synthetic oracle constructions for arbitration experiments."""

from __future__ import annotations

from .posterior import ArbitrationFeatures, bayes_arbitration_result


def synthetic_grid() -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for parametric_score in [0.2, 0.5, 0.8]:
        for contextual_score in [0.2, 0.5, 0.8]:
            for context_reliability in [0.2, 0.5, 0.8]:
                features = ArbitrationFeatures(
                    parametric_score=parametric_score,
                    contextual_score=contextual_score,
                    context_reliability=context_reliability,
                    parametric_reliability=parametric_score,
                    conflict_magnitude=abs(contextual_score - parametric_score),
                )
                decision = bayes_arbitration_result(features)
                rows.append(
                    {
                        "parametric_score": parametric_score,
                        "contextual_score": contextual_score,
                        "context_reliability": context_reliability,
                        "conflict_magnitude": features.conflict_magnitude,
                        "context_weight": decision.context_weight,
                        "parametric_weight": decision.parametric_weight,
                        "arbitration_probability": decision.arbitration_probability,
                    }
                )
    return rows
