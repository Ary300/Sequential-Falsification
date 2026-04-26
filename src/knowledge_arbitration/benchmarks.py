"""Benchmark registry for the knowledge arbitration project."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkSpec:
    name: str
    role: str
    family: str
    status: str
    approximate_size: str
    primary_use: str
    notes: str = ""


ARBITRATION_BENCHMARKS: dict[str, BenchmarkSpec] = {
    "conflictbank": BenchmarkSpec(
        name="ConflictBank",
        role="primary conflict benchmark",
        family="knowledge_conflict",
        status="planned",
        approximate_size="large",
        primary_use="controlled context-memory, inter-context, and misinformation conflict",
        notes="Good candidate for the large-scale main experiment once data plumbing is in place.",
    ),
    "popqa": BenchmarkSpec(
        name="PopQA",
        role="prior-strength benchmark",
        family="open_qa",
        status="priority",
        approximate_size="medium",
        primary_use="tests popularity-conditioned arbitration and prior-strength effects",
    ),
    "wikicontradict": BenchmarkSpec(
        name="WikiContradict",
        role="gold contradiction benchmark",
        family="knowledge_conflict",
        status="priority",
        approximate_size="small",
        primary_use="high-precision contradiction evaluation and qualitative examples",
    ),
    "nq_swap": BenchmarkSpec(
        name="NQ-Swap",
        role="entity substitution benchmark",
        family="knowledge_conflict",
        status="priority",
        approximate_size="medium",
        primary_use="clean context-memory conflict from entity substitution",
    ),
    "memotrap": BenchmarkSpec(
        name="MemoTrap",
        role="paired entity substitution comparator",
        family="knowledge_conflict",
        status="planned",
        approximate_size="small",
        primary_use="paired comparator for NQ-Swap and knowledge-conflict retrieval baselines",
        notes="Recommended companion benchmark whenever NQ-Swap is used in a spotlight-scale matrix.",
    ),
    "dynamicqa": BenchmarkSpec(
        name="DynamicQA",
        role="dynamicity benchmark",
        family="temporal_qa",
        status="priority",
        approximate_size="medium",
        primary_use="tests temporal and disputable facts under differing dynamicity levels",
    ),
    "templama": BenchmarkSpec(
        name="TempLAMA",
        role="temporal benchmark",
        family="temporal_qa",
        status="planned",
        approximate_size="large",
        primary_use="staleness and temporal drift analysis",
    ),
    "freshqa": BenchmarkSpec(
        name="FreshQA",
        role="freshness stress test",
        family="temporal_qa",
        status="planned",
        approximate_size="medium",
        primary_use="freshness and recency-aware arbitration",
    ),
    "faitheval": BenchmarkSpec(
        name="FaithEval",
        role="counterfactual faithfulness benchmark",
        family="knowledge_conflict",
        status="planned",
        approximate_size="medium",
        primary_use="counterfactual, inconsistent, and unanswerable context faithfulness evaluation",
    ),
    "ambigdocs": BenchmarkSpec(
        name="AmbigDocs",
        role="ambiguity benchmark",
        family="multi_context_qa",
        status="planned",
        approximate_size="large",
        primary_use="same-name different-entity ambiguity and inter-context arbitration",
    ),
    "ramdocs": BenchmarkSpec(
        name="RAMDocs",
        role="ambiguity-plus-noise benchmark",
        family="multi_context_qa",
        status="planned",
        approximate_size="small",
        primary_use="multi-document ambiguity, misinformation, and noise stress test",
    ),
    "clasheval": BenchmarkSpec(
        name="ClashEval",
        role="conflict diagnostic benchmark",
        family="knowledge_conflict",
        status="planned",
        approximate_size="medium",
        primary_use="counterfactual perturbation and tug-of-war conflict diagnostics across domains",
    ),
    "mquake_remastered": BenchmarkSpec(
        name="MQuAKE-Remastered",
        role="multi-hop conflict benchmark",
        family="multi_hop_qa",
        status="planned",
        approximate_size="small",
        primary_use="tests multi-hop propagation of conflict during reasoning",
    ),
}
