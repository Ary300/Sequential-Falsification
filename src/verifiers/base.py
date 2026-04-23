"""Verifier abstractions for Track B capacity experiments."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import Any


def _round_floats(value: Any, digits: int = 4) -> Any:
    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, dict):
        return {key: _round_floats(item, digits=digits) for key, item in value.items()}
    if isinstance(value, list):
        return [_round_floats(item, digits=digits) for item in value]
    if isinstance(value, tuple):
        return tuple(_round_floats(item, digits=digits) for item in value)
    return value


@dataclass
class VerifierScore:
    verifier: str
    raw: Any
    token: str
    metadata: dict[str, Any]


class BaseVerifier(ABC):
    """Abstract verifier interface for capacity experiments."""

    name: str = "base"

    def __init__(self, timeout: int = 10, n_bins: int = 10) -> None:
        self.timeout = timeout
        self.n_bins = n_bins

    def prepare(
        self,
        problem: dict[str, Any],
        candidates: list[dict[str, Any]],
        evaluator: Any,
    ) -> None:
        """Optional pool-level preparation hook."""

    @abstractmethod
    def score(
        self,
        problem: dict[str, Any],
        candidate: dict[str, Any],
        evaluator: Any,
    ) -> VerifierScore:
        """Return a verifier score for one candidate."""

    def supports_streaming(self) -> bool:
        return False

    def cost(self) -> int:
        return 1

    def tokenize(self, value: Any) -> str:
        if isinstance(value, (int, bool, str)) or value is None:
            return str(value)
        if isinstance(value, float):
            bucket = min(self.n_bins - 1, max(0, int(value * self.n_bins)))
            return f"bin:{bucket}"
        return json.dumps(_round_floats(value), sort_keys=True, default=repr)


class UnavailableVerifier(BaseVerifier):
    """Explicit placeholder for verifiers not yet integrated."""

    unavailable_reason: str = "not implemented"

    def score(
        self,
        problem: dict[str, Any],
        candidate: dict[str, Any],
        evaluator: Any,
    ) -> VerifierScore:
        raise NotImplementedError(f"{self.name} verifier is unavailable: {self.unavailable_reason}")
