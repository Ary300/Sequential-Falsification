"""Feature placeholders for knowledge-arbitration experiments."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ArbitrationFeatureRow:
    question_id: str
    parametric_confidence: float
    contextual_confidence: float
    context_reliability: float
    conflict_score: float
    popularity_prior: float
    dynamicity_score: float
    cot_length: int
    split: str

    def to_dict(self) -> dict[str, float | str | int]:
        return asdict(self)
