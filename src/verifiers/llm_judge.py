"""LLM-judge verifier placeholder for Track B."""

from __future__ import annotations

from .base import UnavailableVerifier


class LLMJudgeVerifier(UnavailableVerifier):
    name = "llm_judge"
    unavailable_reason = "LLM judge integration is not wired yet. Planned implementation: OpenAI-compatible judge backend with rubric prompts."
