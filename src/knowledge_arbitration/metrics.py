"""Metrics specific to knowledge arbitration experiments."""

from __future__ import annotations

from math import log


def _clip_probability(value: float, eps: float = 1e-9) -> float:
    return min(max(value, eps), 1.0 - eps)


def bayes_regret(oracle_loss: float, policy_loss: float) -> float:
    """Return excess loss relative to an oracle arbitration policy."""

    return float(policy_loss) - float(oracle_loss)


def arbitration_kl_divergence(oracle_context_prob: float, policy_context_prob: float) -> float:
    """KL divergence between oracle and policy arbitration distributions."""

    p = _clip_probability(oracle_context_prob)
    q = _clip_probability(policy_context_prob)
    return p * log(p / q) + (1.0 - p) * log((1.0 - p) / (1.0 - q))
