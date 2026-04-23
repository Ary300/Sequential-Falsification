"""SCE-trace verifier for Track B capacity experiments."""

from __future__ import annotations

from typing import Any

from falsify import FalsificationConfig, sequential_falsify_candidates
from .base import BaseVerifier, VerifierScore


class SCETraceVerifier(BaseVerifier):
    """Verifier derived from the SCE falsification trace."""

    name = "sce_trace"

    def __init__(
        self,
        timeout: int = 10,
        n_bins: int = 10,
        n_rounds: int = 4,
        max_tiebreak_rounds: int = 4,
        probe_strategy: str = "adaptive_population",
        confidence_mode: str = "wealth",
        max_differential_probes: int = 8,
        consensus_min_fraction: float = 0.70,
        consensus_min_margin: int = 2,
        consensus_min_votes: int = 3,
    ) -> None:
        super().__init__(timeout=timeout, n_bins=n_bins)
        self.config = FalsificationConfig(
            n_rounds=n_rounds,
            max_tiebreak_rounds=max_tiebreak_rounds,
            timeout=timeout,
            probe_strategy=probe_strategy,
            confidence_mode=confidence_mode,
            max_differential_probes=max_differential_probes,
            consensus_min_fraction=consensus_min_fraction,
            consensus_min_margin=consensus_min_margin,
            consensus_min_votes=consensus_min_votes,
        )
        self._records_by_order: dict[int, dict[str, Any]] = {}

    def prepare(
        self,
        problem: dict[str, Any],
        candidates: list[dict[str, Any]],
        evaluator: Any,
    ) -> None:
        payload = sequential_falsify_candidates(candidates, problem, self.config)
        self._records_by_order = {
            int(record.get("candidate_order", idx)): record
            for idx, record in enumerate(payload["records"])
        }

    def score(
        self,
        problem: dict[str, Any],
        candidate: dict[str, Any],
        evaluator: Any,
    ) -> VerifierScore:
        candidate_order = int(candidate.get("candidate_order", 0))
        record = self._records_by_order[candidate_order]
        raw = {
            "confidence": float(record.get("confidence", 0.0)),
            "selection_score": float(record.get("selection_score", 0.0)),
            "survived": bool(record.get("survived", False)),
            "rounds_survived": int(record.get("rounds_survived", 0)),
            "wealth": float(record.get("wealth", 1.0)),
        }
        token = self.tokenize(
            {
                "confidence": raw["confidence"],
                "selection_score": raw["selection_score"],
                "survived": raw["survived"],
                "rounds_survived": raw["rounds_survived"],
            }
        )
        return VerifierScore(verifier=self.name, raw=raw, token=token, metadata=raw)
