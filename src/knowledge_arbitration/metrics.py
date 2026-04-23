"""Metrics for Bayes-optimal knowledge arbitration experiments."""

from __future__ import annotations

from math import log


def _clip_probability(value: float, eps: float = 1e-8) -> float:
    return min(max(value, eps), 1.0 - eps)


def arbitration_regret(oracle_probability: float, model_probability: float, label: int) -> float:
    oracle_probability = _clip_probability(oracle_probability)
    model_probability = _clip_probability(model_probability)
    oracle_loss = -log(oracle_probability if label else 1.0 - oracle_probability)
    model_loss = -log(model_probability if label else 1.0 - model_probability)
    return model_loss - oracle_loss


def kl_gap(oracle_probability: float, model_probability: float) -> float:
    oracle_probability = _clip_probability(oracle_probability)
    model_probability = _clip_probability(model_probability)
    return (
        oracle_probability * log(oracle_probability / model_probability)
        + (1.0 - oracle_probability) * log((1.0 - oracle_probability) / (1.0 - model_probability))
    )
