# Bayes-Optimal Knowledge Arbitration: Aims, Scope, and Overview

## Purpose

This is now the active top-level project overview for the repository.

The repository is no longer being organized around:

- sequential falsification as the main paper,
- Track B capacity theory for code-generation TTS,
- or a code-only verifier-selection story.

Those directions are now legacy workstreams. Useful infrastructure may still be
reused, but they are not the target paper.

The active paper direction is:

**Bayes-optimal knowledge arbitration under conflict, with a theorem-backed
account of when parametric memory, retrieved evidence, and chain-of-thought
should be trusted.**

## One-sentence thesis

Knowledge-conflict resolution in LLMs should be treated as a posterior-predictive
decision problem, not as a fixed "trust the context" or "trust the model"
heuristic.

## Longer thesis

Large language models often answer under **knowledge conflict**:

- parametric memory says one thing,
- retrieved or provided context says another,
- and longer chain-of-thought can make the model more certain without making it
  more correct.

The active project claims that this should be formalized as a decision problem
with three layers:

1. A **Bayes-optimal arbitration rule** between parametric and contextual
   sources.
2. A **minimax lower bound** showing fixed trust policies are fundamentally
   suboptimal.
3. A **calibration-coupling theorem** showing that under explicit
   context-memory conflict, additional reasoning steps can worsen calibration.

The paper should not read like "another RAG heuristic." It should read like:

- a clean theoretical formalization of knowledge arbitration,
- a practically measurable gap between real LLM behavior and the Bayes rule,
- and a concrete recipe for better conflict handling in deployed systems.

## What is now in scope

### Core theoretical scope

- Posterior-predictive arbitration between parametric and contextual knowledge.
- Reliability-aware mixture rules.
- Lower bounds or regret arguments against fixed policies.
- Calibration under sequential reasoning when sources conflict.
- A constructive mitigation story:
  - confidence-decoupled reasoning,
  - bagged or parallel reasoning,
  - or arbitration-aware decoding.

### Core empirical scope

- Conflict benchmarks:
  - ConflictBank
  - PopQA
  - WikiContradict
  - NQ-Swap
  - DynamicQA
  - TempLAMA
  - FreshQA
  - MQuAKE-Remastered
- Model families:
  - checkpoint-resolved families such as Pythia and OLMo
  - open-weight production families such as Llama, Qwen, Mistral, Phi
  - reasoning-oriented models such as DeepSeek-R1-distill and Qwen thinking
    mode when needed for the CoT theorem
- Metrics:
  - Brier and NLL as primary proper scoring rules
  - ECE / debiased ECE / SmoothECE
  - selective prediction metrics
  - regret vs. Bayes oracle
  - KL gap to oracle arbitration policy

### Implementation scope

- Benchmark registry and experiment manifests for conflict datasets.
- Feature extraction for arbitration:
  - parametric confidence
  - contextual confidence
  - retrieval reliability proxies
  - popularity / dynamicity / entropy features
- Synthetic Bayes-oracle generators.
- Reporting for:
  - oracle-vs-model arbitration
  - fixed-policy regret
  - CoT-length calibration curves
  - checkpoint scaling plots

## Explicitly not the main project anymore

- Sequential falsification as a standalone paper.
- Code-generation TTS capacity as the primary theory paper.
- Reviewer-driven baseline backfilling for the old code paper as the dominant
  priority.

Those assets can still be reused:

- cluster launchers,
- plotting utilities,
- result bundling,
- experiment YAML patterns,
- benchmark-loading patterns.

But they are supporting infrastructure only.

## Headline results this project needs

The paper needs at least three headline results, and each one must be visible in
one figure or theorem statement.

### Headline result 1: Bayes-optimal arbitration is measurable

For a benchmarked conflict setting, real models should deviate from the
Bayes-optimal arbitration rule by a large, measurable amount. The target figure
is:

- x-axis: oracle Bayes posterior preference for context vs. memory
- y-axis: model arbitration behavior
- diagonal reference line
- multiple model families

If frontier models sit far from the diagonal, the result is strong. If larger
models approach the diagonal, that is still publishable as an emergence result.

### Headline result 2: fixed policies are worst-case dominated

On an adversarial but benchmark-realizable distribution, every fixed policy
should incur visibly larger regret than a reliability-aware policy. The target
figure is:

- worst-case regret chart across:
  - always-context
  - always-parametric
  - fixed interpolation
  - adaptive retrieval heuristics
  - Bayes-style arbitration

This must not be a tiny win. It should look structurally different.

### Headline result 3: CoT worsens calibration under conflict

Theorem 3 only matters if it predicts an empirical signature that actually
appears on real models. The desired result is:

- on conflict subsets, ECE/Brier worsen as CoT length grows;
- on no-conflict subsets, CoT is neutral or helpful;
- this persists at temperature 0, ruling out a pure sampling-variance story.

That contrast is the paper's "aha" moment.

## Current execution priorities

### Priority 0: Make the repo internally consistent

The top-level docs, configs, and experiment scaffolding must describe the new
knowledge-arbitration paper rather than the old sequential-falsification /
capacity-theory story.

### Priority 1: Build the theorem-to-experiment bridge

The key danger for this project is a beautiful theorem with mushy validation.
So the repo must support:

- synthetic oracle experiments,
- benchmark feature extraction,
- model-policy comparison,
- calibration-by-CoT-length analysis.

### Priority 2: Get one real benchmark stack working cleanly

The first real empirical stack should be:

- PopQA
- DynamicQA
- ConflictBank

This trio is enough to validate:

- prior strength / popularity effects,
- dynamicity and temporal mismatch,
- broad conflict coverage.

### Priority 3: Add checkpoint-resolved evidence

To get beyond an empirical poster-style claim, the paper needs at least one
model family where training-time evolution or checkpoint variation is visible.
That means:

- Pythia and/or OLMo are not optional if the goal is a strong main-track paper.

### Priority 4: Plan for mentorship and co-authorship

This is a theorem-heavy, spotlight-ambition paper. The realistic successful path
includes outside feedback or co-authorship from a stronger lab or mentor. The
repo should therefore keep a clean, shareable project packet.

## What the repo should produce next

The next concrete repository outputs should be:

1. A project requirements document for Bayes-optimal knowledge arbitration.
2. An experiment matrix doc with benchmarks, models, conditions, and metrics.
3. Config and script scaffolding for the first arbitration pilot.
4. A reporting path for oracle-vs-model arbitration and CoT calibration.
5. A theory outline that cleanly states the three main theorems.

## Reality check

This direction has significantly more novelty upside than the old Track B code
paper, but it also has more ways to fail. The repo should therefore optimize
for:

- sharp theorem statements,
- measurable predictions,
- benchmark breadth,
- and clean boundary conditions.

If the calibration-coupling theorem only holds on conflict subsets, that is
fine. That is still a strong result. The mistake would be overclaiming.

## Active direction marker

As of 2026-04-23:

- **Bayes-optimal knowledge arbitration** is the active paper direction.
- The old sequential falsification / Track B capacity material is legacy.
- New work should prefer the new arbitration docs, configs, and scripts unless
  explicitly revisiting legacy assets for reuse.
