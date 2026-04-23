"""Benchmark registry for the Bayes-optimal knowledge arbitration project."""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class BenchmarkSpec:
    name: str
    role: str
    priority: str
    task_type: str
    license: str
    primary_signal: str
    notes: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


ARBITRATION_BENCHMARKS: dict[str, BenchmarkSpec] = {
    "conflictbank": BenchmarkSpec(
        name="conflictbank",
        role="broad conflict coverage",
        priority="P0",
        task_type="qa",
        license="to_verify",
        primary_signal="conflict cause diversity",
        notes="Large-scale umbrella benchmark for misinformation, semantic, and temporal conflict.",
    ),
    "popqa": BenchmarkSpec(
        name="popqa",
        role="prior strength and popularity",
        priority="P0",
        task_type="qa",
        license="MIT",
        primary_signal="entity popularity",
        notes="Useful for connecting prior strength to arbitration behavior.",
    ),
    "dynamicqa": BenchmarkSpec(
        name="dynamicqa",
        role="dynamicity and temporal conflict",
        priority="P0",
        task_type="qa",
        license="MIT",
        primary_signal="fact dynamicity",
        notes="Important for temporal and dispute-conditioned arbitration.",
    ),
    "wikicontradict": BenchmarkSpec(
        name="wikicontradict",
        role="real-world contradiction gold set",
        priority="P1",
        task_type="qa",
        license="CC-BY-4.0",
        primary_signal="human-validated contradiction",
        notes="Small but high-quality contradiction benchmark.",
    ),
    "nq_swap": BenchmarkSpec(
        name="nq_swap",
        role="clean context-memory conflict",
        priority="P1",
        task_type="qa",
        license="to_verify",
        primary_signal="entity substitution",
        notes="Classic clean swap setting.",
    ),
    "mquake_remastered": BenchmarkSpec(
        name="mquake_remastered",
        role="multi-hop conflict propagation",
        priority="P1",
        task_type="qa",
        license="to_verify",
        primary_signal="compositional conflict",
        notes="Useful for testing how conflict compounds across reasoning steps.",
    ),
    "templama": BenchmarkSpec(
        name="templama",
        role="temporal staleness",
        priority="P2",
        task_type="cloze",
        license="to_verify",
        primary_signal="time-sensitive factual drift",
        notes="Useful for staleness-aware arbitration studies.",
    ),
    "freshqa": BenchmarkSpec(
        name="freshqa",
        role="freshness and post-cutoff knowledge",
        priority="P2",
        task_type="qa",
        license="Apache-2.0",
        primary_signal="freshness gap",
        notes="Useful for post-cutoff conflict and freshness analysis.",
    ),
}


def benchmark_table() -> list[dict[str, str]]:
    return [spec.to_dict() for spec in ARBITRATION_BENCHMARKS.values()]
