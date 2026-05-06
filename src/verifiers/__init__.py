"""Verifier registry for Track B capacity experiments."""

from __future__ import annotations

from typing import Any

from .base import BaseVerifier
from .llm_judge import LLMJudgeVerifier
from .majority import MajorityVerifier
from .prm import PRMVerifier
from .public_test import PublicTestVerifier
from .sce_trace import SCETraceVerifier


VERIFIER_REGISTRY = {
    "majority": MajorityVerifier,
    "public_test": PublicTestVerifier,
    "sce_trace": SCETraceVerifier,
    "prm": PRMVerifier,
    "llm_judge": LLMJudgeVerifier,
}


def create_verifier(name: str, **kwargs: Any) -> BaseVerifier:
    key = name.strip().lower()
    if key not in VERIFIER_REGISTRY:
        raise KeyError(f"Unknown verifier: {name}. Available: {sorted(VERIFIER_REGISTRY)}")
    return VERIFIER_REGISTRY[key](**kwargs)


__all__ = [
    "BaseVerifier",
    "MajorityVerifier",
    "PublicTestVerifier",
    "SCETraceVerifier",
    "PRMVerifier",
    "LLMJudgeVerifier",
    "create_verifier",
    "VERIFIER_REGISTRY",
]
