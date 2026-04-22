"""Final selection rules."""

from __future__ import annotations

from typing import Any


def select_best_candidate(records: list[dict[str, Any]], prefer_survivors: bool = True) -> dict[str, Any] | None:
    if not records:
        return None
    scored = list(records)
    if prefer_survivors:
        scored.sort(
            key=lambda row: (
                1 if row.get("survived") else 0,
                row.get("selection_score", row.get("confidence", 0.0)),
                row.get("public_score", 0.0),
                row.get("trace_strength", 0.0),
                -row.get("candidate_order", 0),
            ),
            reverse=True,
        )
    else:
        scored.sort(
            key=lambda row: (
                row.get("selection_score", row.get("confidence", 0.0)),
                row.get("public_score", 0.0),
                row.get("trace_strength", 0.0),
                -row.get("candidate_order", 0),
            ),
            reverse=True,
        )
    return scored[0]
