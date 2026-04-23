"""Public-test verifier surfaces for Track B."""

from __future__ import annotations

from typing import Any

from .base import BaseVerifier, VerifierScore


class PublicTestVerifier(BaseVerifier):
    """Verifier using the public-test pass rate."""

    name = "public_test"

    def score(
        self,
        problem: dict[str, Any],
        candidate: dict[str, Any],
        evaluator: Any,
    ) -> VerifierScore:
        if problem.get("type") == "math":
            raw = {"public_score": 0.0, "num_passed": 0, "num_tests": 0}
            return VerifierScore(verifier=self.name, raw=raw, token=self.tokenize(0.0), metadata=raw)

        result = evaluator(problem, candidate["text"], False)
        num_passed = int(result.get("num_passed", 0))
        num_tests = int(result.get("num_tests", 0))
        public_score = num_passed / float(num_tests) if num_tests > 0 else 0.0
        raw = {"public_score": public_score, "num_passed": num_passed, "num_tests": num_tests}
        return VerifierScore(
            verifier=self.name,
            raw=raw,
            token=self.tokenize(public_score),
            metadata=raw,
        )
