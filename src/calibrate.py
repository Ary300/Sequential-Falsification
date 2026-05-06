"""Confidence-score utilities for the current prototype."""

from __future__ import annotations

from typing import Any

from utils.evals import calibrate_e_to_confidence


def calibrated_confidence_from_wealth(wealth: float, alpha: float = 0.05) -> float:
    return calibrate_e_to_confidence(wealth=wealth, alpha=alpha)


def attach_confidence(record: dict[str, Any], alpha: float = 0.05) -> dict[str, Any]:
    out = dict(record)
    out["confidence"] = calibrated_confidence_from_wealth(record.get("wealth", 1.0), alpha=alpha)
    return out
