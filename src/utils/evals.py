"""Testing-inspired score helpers and lightweight confidence utilities.

The current prototype uses these functions as empirical ranking heuristics.
They should not be interpreted as a formally validated e-process unless the
benchmark-specific null assumptions are calibrated externally.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import prod
from typing import Iterable


@dataclass
class WealthTrace:
    values: list[float]

    @property
    def final(self) -> float:
        return self.values[-1] if self.values else 1.0


def compute_e_value(probe_detected: bool, delta_k: float, p_k: float) -> float:
    delta_k = min(max(delta_k, 1e-9), 1.0 - 1e-9)
    p_k = min(max(p_k, 1e-9), 1.0 - 1e-9)
    if probe_detected:
        return 1.0 / delta_k
    return (1.0 - p_k) / (1.0 - delta_k)


def wealth_process(probe_results: Iterable[bool], delta_k: float, p_k: float) -> WealthTrace:
    wealth = 1.0
    values = []
    for detected in probe_results:
        wealth *= compute_e_value(detected, delta_k=delta_k, p_k=p_k)
        values.append(wealth)
    return WealthTrace(values=values)


def calibrate_e_to_confidence(wealth: float, alpha: float = 0.05) -> float:
    if wealth <= 0:
        return 0.0
    threshold = 1.0 / max(alpha, 1e-9)
    if wealth >= threshold:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (wealth / threshold)))


def survival_probability_lower_bound(p_values: Iterable[float]) -> float:
    clipped = [min(max(v, 0.0), 1.0) for v in p_values]
    return prod(1.0 - v for v in clipped)


def estimate_detection_probability(round_index: int, base: float = 0.35, decay: float = 0.06) -> float:
    return min(0.95, max(0.05, base - round_index * decay))
