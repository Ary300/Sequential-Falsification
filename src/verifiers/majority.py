"""Agreement-based verifier surfaces for Track B."""

from __future__ import annotations

from collections import Counter
from typing import Any

from baselines import _execution_vote_signature
from .base import BaseVerifier, VerifierScore


class MajorityVerifier(BaseVerifier):
    """Public-execution agreement verifier.

    For code tasks this reflects the corrected majority-vote baseline: cluster
    candidates by public execution behavior rather than by raw source text.
    """

    name = "majority"

    def prepare(
        self,
        problem: dict[str, Any],
        candidates: list[dict[str, Any]],
        evaluator: Any,
    ) -> None:
        signatures = [_execution_vote_signature(problem, candidate, evaluator) for candidate in candidates]
        self._counts = Counter(signatures)
        self._signature_by_order = {
            int(candidate.get("candidate_order", idx)): signature
            for idx, (candidate, signature) in enumerate(zip(candidates, signatures))
        }
        self._pool_size = max(1, len(candidates))

    def score(
        self,
        problem: dict[str, Any],
        candidate: dict[str, Any],
        evaluator: Any,
    ) -> VerifierScore:
        candidate_order = int(candidate.get("candidate_order", 0))
        signature = self._signature_by_order[candidate_order]
        cluster_size = int(self._counts.get(signature, 0))
        cluster_share = cluster_size / float(self._pool_size)
        raw = {
            "cluster_size": cluster_size,
            "cluster_share": cluster_share,
            "signature": signature,
        }
        token = self.tokenize({"cluster_size": cluster_size, "cluster_share": cluster_share, "signature": signature})
        return VerifierScore(
            verifier=self.name,
            raw=raw,
            token=token,
            metadata={"cluster_size": cluster_size, "cluster_share": cluster_share},
        )
