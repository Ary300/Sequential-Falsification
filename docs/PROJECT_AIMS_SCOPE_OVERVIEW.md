# Bayes-Optimal Knowledge Arbitration: Aims, Scope, and Overview

## Purpose

This is now the active top-level project map for the repository.

The prior Sequential Falsification / Track B capacity direction is no longer the
main paper target. Those files still exist in the repo as legacy work and
possible reusable infrastructure, but they should be treated as archived
material unless they are explicitly reused for the new arbitration project.

This document answers four things:

- what the new paper is about;
- what headline results are needed for a serious main-track attempt;
- what is in scope for the repo right now;
- what must happen next before we can honestly claim the project is on a
  spotlight path.

## One-sentence thesis

The project now studies knowledge conflict as a posterior-predictive decision
problem, aiming to derive and validate a Bayes-optimal rule for arbitrating
between parametric memory and retrieved context.

## Longer thesis

Modern LLM systems regularly face knowledge conflict:

- parametric memory says one thing;
- retrieved context says another;
- multiple retrieved contexts disagree with each other;
- longer reasoning traces can reinforce whichever source the model initially
  leans toward.

The paper we now want is not another heuristic RAG policy paper. The target is
more ambitious:

1. define the arbitration problem formally;
2. derive the Bayes-optimal arbitration rule;
3. prove that fixed trust policies are minimax-suboptimal;
4. prove a conflict-conditioned calibration-coupling result for chain-of-thought
   length;
5. validate those claims on conflict benchmarks with real LLMs.

The repo therefore needs to behave like a knowledge-conflict theory-and-systems
project, not like a code-generation TTS project with a new abstract.

## Active paper direction

The active submission target is now:

- a Bayes-optimal knowledge arbitration paper;
- aimed at NeurIPS/ICLR-style theory-plus-empirics;
- with spotlight-tier ambition only if the empirical prediction is visibly
  surprising on frontier reasoning models.

The core claim we want reviewers to remember is:

> Fixed trust policies are formally wrong, and long reasoning can make
> conflict-conditioned confidence worse.

## What counts as a headline result now

The paper only becomes headline-level if we land all three of these:

### 1. A real theorem, not just a heuristic rule

We need a main theorem that derives a Bayes-optimal arbitration rule from a
posterior-predictive decision problem, not just a tuned interpolation between
parametric and retrieved scores.

### 2. A real lower bound, not just a better model

We need a minimax or regret-style result showing that fixed trust policies
(`always_context`, `always_parametric`, or fixed-mix) are structurally
suboptimal, not merely empirically weaker on a benchmark.

### 3. A real empirical prediction that lands

The high-risk, high-upside result is a conflict-conditioned calibration claim:

- on conflict subsets, longer CoT should worsen calibration;
- on no-conflict subsets, that degradation should disappear or reverse;
- the phenomenon should persist even under deterministic decoding.

If that three-part arc lands, the paper has a real spotlight argument.

## Main research goals

### Goal 0: Fully pivot the repo

The repo should stop pretending the active paper is Sequential Falsification or
Track B capacity. Legacy code can stay, but top-level planning and new code
must point at knowledge arbitration first.

### Goal 1: Formalize the arbitration problem

We need a clean mathematical object for:

- parametric belief;
- contextual belief;
- context reliability;
- conflict structure;
- decision loss / Bayes risk.

This is the backbone of Theorem 1.

### Goal 2: Prove fixed-policy suboptimality

Theoretical novelty depends on proving that blind trust rules are wrong in a
distributionally meaningful sense, not just suggesting that nuance is better.

This is the backbone of Theorem 2.

### Goal 3: Connect CoT length to calibration under conflict

This is the highest-risk part of the paper and the most likely source of a
headline empirical figure. The project needs:

- a theorem with explicit conflict assumptions;
- a measurable real-model prediction;
- ablations that separate conflict effects from temperature or variance effects.

### Goal 4: Build a benchmarked experimental stack

The paper needs broad, benchmark-aware infrastructure for:

- conflict QA datasets;
- context/no-context/conflict conditions;
- CoT-length sweeps;
- self-consistency sweeps;
- checkpoint-family experiments;
- calibration and Bayes-regret reporting.

### Goal 5: Turn theory into deployable arbitration

The project should also yield a practical recipe:

- estimate context reliability from observable features;
- mix parametric and contextual beliefs using a principled rule;
- compare that rule to existing heuristic adaptive-RAG policies.

## Benchmark scope

The active benchmark set for this project is:

| Benchmark | Role |
| --- | --- |
| `ConflictBank` | large-scale controlled conflict benchmark |
| `PopQA` | prior-strength and popularity-conditioned arbitration |
| `WikiContradict` | small, gold contradiction benchmark |
| `NQ-Swap` | clean entity-substitution conflict |
| `DynamicQA` | dynamicity-aware conflict / staleness |
| `TempLAMA` | temporal staleness |
| `FreshQA` | freshness stress test |
| `MQuAKE-Remastered` | multi-hop conflict propagation |

These benchmarks are not all implemented yet. They are the target matrix.

## Model scope

The intended primary model families are:

| Family | Role |
| --- | --- |
| `Pythia` | checkpoint-resolved controlled temporal analysis |
| `OLMo-2` | open-data/open-checkpoint controlled analysis |
| `Llama-3.1` | strong open-weight baseline |
| `Qwen-2.5` / `Qwen-3` | strong open-weight arbitration and thinking-mode study |
| `Mistral` | cross-family robustness |
| `Phi-3` | medium-scale robustness |
| `DeepSeek-R1-Distill` | long-CoT / reasoning-mode stress test |

At least one checkpoint-resolved family is non-negotiable if we want the paper
to read as more than a benchmark contest.

## Metrics that matter

The repo should prioritize:

- Brier score;
- NLL;
- ECE plus a debiased or smooth variant;
- selective-risk metrics such as AURC;
- Bayes regret relative to an oracle arbitration rule;
- KL divergence between model arbitration and oracle arbitration.

Accuracy alone is not enough for this project.

## What is in scope right now

### In scope

- project planning and theorem framing for Bayes-optimal arbitration;
- benchmark and model matrix design;
- code/config scaffolding for arbitration experiments;
- calibration and regret metric implementations;
- small pilot scripts for arbitration manifests and dry-run planning.

### Legacy-but-reusable scope

- existing metrics utilities;
- reporting utilities;
- cluster launch patterns;
- some benchmark-loading patterns and JSON/result plumbing.

### Explicitly out of scope right now

- claiming the theorems are proved;
- claiming headline results already exist;
- treating old Sequential Falsification numbers as evidence for this paper;
- pretending the current `paper/` LaTeX is the live manuscript for this new
  idea.

## Active near-term deliverables

The immediate deliverables are:

1. clean new PRD and experiment matrix;
2. arbitration-specific module and config scaffold;
3. benchmark registry and evaluation manifest builder;
4. theorem-to-experiment alignment doc;
5. first pilot run plan for PopQA / DynamicQA / ConflictBank-style conditions.

## Current benchmark-backed status

The repo is now past the “planning only” stage.

What is already real:

- a synthetic arbitration pilot and report;
- theorem sketches in
  [`docs/KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/KNOWLEDGE_ARBITRATION_THEOREM_SKETCHES.md);
- built-in benchmark loaders for `PopQA`, `DynamicQA`, `NQ-Swap`, and
  `WikiContradict`, plus a streamed `ConflictBank` subset loader;
- a benchmark-backed headline-wave pilot:
  [`results/arbitration_real_headline_wave_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_real_headline_wave_v2/report/summary.md);
- a focused `WikiContradict` contradiction report:
  [`results/arbitration_wikicontradict_focus/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_wikicontradict_focus/report/summary.md);
- a compact conflict-heavy benchmark wave:
  [`results/arbitration_conflict_focus_compact_v2/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_focus_compact_v2/report/summary.md).

The strongest current empirical signal is theorem-1/theorem-2 shaped:

- in the broad real pilot, `Bayes Proxy` is the best overall policy at
  `0.0000` mean regret;
- the next-best heuristic policy is `heuristic_adaptive` at `0.0593`;
- `simulated_model` is materially worse at `0.3277`;
- `fixed_50` is worse again at `0.3912`;
- naive fixed trust policies are dramatically worse:
  `always_context = 6.3179`, `always_parametric = 6.8936`.

The theorem-3 situation is more mixed:

- broad real pilot mean conflict ECE delta is `-0.0054`, so the wide benchmark
  mix does **not** yet support the headline that longer CoT broadly worsens
  calibration under conflict;
- the strongest positive slice is `WikiContradict`, where conflict ECE delta is
  `+0.1542` while no-conflict delta is `-0.0190`;
- the newer compact conflict-heavy wave keeps the arbitration signal strong but
  still leaves theorem 3 mixed:
  `ConflictBank = -0.1943`, `DynamicQA = -0.0341`,
  `WikiContradict = +0.1826` on conflict ECE delta from short to long CoT.

That means the project now has a real benchmark-backed arbitration signal, but
not yet the broad conflict-conditioned CoT headline needed for the full paper.

## Reality check

This is a stronger idea than the previous direction, but it is also less built.

What is honest today:

- the repo has been pivoted at the planning layer;
- arbitration loaders and benchmark-backed proxy experiments now run end to end;
- there is already a real early theorem-1/theorem-2-style signal;
- the theorem-3 headline is still incomplete.

What must happen before we can talk about a serious main-track paper:

- theorem statements need to be written cleanly;
- `ConflictBank` needs to be integrated into the real benchmark path;
- the broad theorem-3 effect needs to land outside a single contradiction slice;
- the empirical prediction around conflict-conditioned calibration must survive
  first contact with real models.

## Legacy note

The following repo areas are legacy relative to the new paper direction:

- `docs/METHODS_DETAILED.md`
- `docs/RESULTS_DETAILED_UP_TO_NOW.md`
- `paper/`
- `src/capacity.py`
- `src/matching.py`
- `src/verifiers/`
- `src/configs/capacity_experiments.yaml`
- `scripts/estimate_capacity.py`
- `scripts/capacity_pilot.py`
- `scripts/report_capacity.py`

They should be treated as archived infrastructure unless explicitly repurposed.
