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
        status="priority",
        approximate_size="large",
        primary_use="controlled context-memory, inter-context, and misinformation conflict",
        notes="Core spotlight benchmark with completed headline runs and synthetic-oracle compatibility.",
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
        status="priority",
        approximate_size="medium",
        primary_use="counterfactual, inconsistent, and unanswerable context faithfulness evaluation",
        notes="Best benchmark for Theorem 2's always-trust-context failure mode.",
    ),
    "ambigdocs": BenchmarkSpec(
        name="AmbigDocs",
        role="ambiguity benchmark",
        family="multi_context_qa",
        status="priority",
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
    "triviaqa": BenchmarkSpec(
        name="TriviaQA",
        role="open-domain coverage benchmark",
        family="open_qa",
        status="priority",
        approximate_size="large",
        primary_use="broad open-domain QA coverage with retriever-provided evidence snippets",
        notes="Standard conflict-decoding comparison benchmark used to expand beyond the initial 5-benchmark core.",
    ),
    "hotpotqa": BenchmarkSpec(
        name="HotpotQA-Distractor",
        role="multi-hop distractor benchmark",
        family="multi_hop_qa",
        status="priority",
        approximate_size="large",
        primary_use="tests arbitration under multi-hop evidence with distractor passages",
        notes="Important for showing the method is not only single-hop factual arbitration.",
    ),
    "tabmwp": BenchmarkSpec(
        name="TabMWP",
        role="table reasoning benchmark",
        family="table_reasoning",
        status="priority",
        approximate_size="large",
        primary_use="extends arbitration to table-grounded reasoning and option-level conflict",
        notes="Included because AdaCAD and CoCoA both evaluate table-context settings.",
    ),
    "gpqa": BenchmarkSpec(
        name="GPQA-Style Verified Reasoning",
        role="domain expertise calibration benchmark",
        family="expert_reasoning",
        status="priority",
        approximate_size="small",
        primary_use="Theorem 3 domain-expertise calibration stress test under reasoning-heavy prompts",
        notes="Compute-light public proxy for the GPQA-style calibration regime discussed by Mei et al.",
    ),
    "climatex": BenchmarkSpec(
        name="ClimateX",
        role="over-reasoning calibration benchmark",
        family="scientific_claims",
        status="priority",
        approximate_size="large",
        primary_use="tests confidence calibration for contested scientific statements and evidence annotations",
        notes="Useful for the Lacombe-style over-reasoning calibration objection to Theorem 3.",
    ),
}
