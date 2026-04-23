"""PRM verifier placeholder for Track B."""

from __future__ import annotations

from .base import UnavailableVerifier


class PRMVerifier(UnavailableVerifier):
    name = "prm"
    unavailable_reason = "PRM integration is not wired yet. Planned adapters: ThinkPRM / Math-Shepherd / code-PRM."
