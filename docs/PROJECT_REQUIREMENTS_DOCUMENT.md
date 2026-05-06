# Project Requirements Document

Project: Bayes-Optimal Knowledge Arbitration Under Context-Memory Conflict

Status: Active research pivot

Target venue: ICML 2026 primary; NeurIPS 2026 fallback; ICLR / NeurIPS 2027 continuation

Ambition: Main-track acceptance with spotlight-tier upside if theorem 3 is successfully rewritten and the empirical matrix is expanded to spotlight-scale

Last updated: 2026-04-23

## 0. Purpose

This document is the new single source of truth for the repository's active
research direction.

The older Sequential Falsification / Track B capacity program is now legacy.
Nothing in this PRD should rely on those older claims being central to the new
paper.

This PRD covers:

- the active research questions;
- the theorem roadmap;
- the benchmark and model matrix;
- the experimental conditions;
- the code structure we need next;
- the milestone and risk plan.

Important note: the literature map that motivated this pivot is strong, but the
exact citation metadata still needs source-by-source re-verification before any
paper text is frozen. This PRD is a research execution plan, not a final
bibliographic artifact.

## 1. Executive summary

### 1.1 What we are building

We are building a theory-plus-empirics paper around one core idea:

> Knowledge conflict should be treated as a posterior-predictive decision
> problem, not a heuristic "trust context or trust memory" choice.

The project has three theorem targets and one empirical spine:

- Theorem 1: derive the Bayes-optimal arbitration rule.
- Theorem 2: prove minimax suboptimality of fixed trust policies.
- Theorem 3: replace the original conflict-only calibration claim with a
  stronger and more defensible two-regime / misspecified-Bayes reasoning
  theorem that survives the corrected `closed_book` control.
- Experimental spine: validate the predictions across conflict benchmarks, open
  model families, and at least one checkpoint-resolved family.

### 1.2 Primary research questions

- Can we derive an optimal arbitration policy between parametric memory and
  retrieved context from a clean Bayesian decision problem?
- Can we prove that fixed trust policies are structurally dominated?
- Under explicit knowledge conflict and hard-QA settings more generally, does
  longer chain-of-thought amplify overconfidence in a predictable, scale- and
  benchmark-dependent way?
- Can we estimate the relevant reliability terms from observable model signals
  tightly enough to make the theory operational?

### 1.3 Success criteria

Minimum:

- a clean theorem for the Bayes-optimal arbitration rule;
- a real-world benchmark matrix spanning at least 3 benchmarks × 5 models;
- one compelling empirical result tying conflict to calibration behavior.

Target:

- all three theorem targets are clean enough for a main-track paper;
- the real-data results confirm a nontrivial prediction from the theory;
- at least one mitigation method derived from the theory improves calibration or
  regret.

Stretch:

- the rewritten theorem-3 result is visibly surprising on frontier reasoning
  models and survives a true `closed_book` control;
- the paper develops a practical arbitration recipe reviewers can immediately
  use in RAG systems.

## 2. Project scope

### 2.1 In scope

- knowledge conflict between parametric memory and retrieved context;
- inter-context conflict when multiple retrieved sources disagree;
- context reliability modeling;
- calibration under conflict;
- Bayesian decision rules for retrieval arbitration;
- open-weight LLM experiments;
- checkpoint-family experiments for temporal or training-cutoff analysis.

### 2.2 Out of scope

- training a new frontier model from scratch;
- claiming human-level or production-grade arbitration;
- pretending the old code-generation TTS results establish this paper;
- relying only on heuristic benchmark wins without theorem support.

### 2.3 Legacy assets

The repo still contains useful legacy infrastructure:

- metric helpers;
- report-generation helpers;
- cluster launcher patterns;
- JSON result plumbing;
- some benchmark loader patterns.

But the old paper framing is archived and should not govern new naming or new
research claims.

## 3. Theoretical program

### 3.1 Core setup

We assume a question `q`, latent correct answer `y*`, model parametric belief
`p_param(y | q)`, retrieved/contextual belief `p_ctx(y | q, c)`, and latent
context reliability `r in [0, 1]`.

We define an arbitration policy `a(q, c)` that chooses a predictive
distribution or answer using:

- parametric evidence,
- contextual evidence,
- reliability signals,
- a loss function over wrong or miscalibrated answers.

### 3.2 Theorem 1: Bayes-optimal arbitration rule

Goal:

- derive the Bayes-optimal arbitration policy from a posterior-predictive
  decision problem;
- show how its operational form reduces to a reliability-weighted combination
  of parametric and contextual beliefs.

Required outputs:

- formal assumptions;
- clean optimality statement;
- excess-risk comparison to fixed trust and fixed-mix baselines.

### 3.3 Theorem 2: Minimax suboptimality of fixed policies

Goal:

- show that `always_context`, `always_parametric`, and constant-weight mixing
  each incur `Omega(1)` excess Bayes risk on some realizable conflict
  distribution;
- show that a reliability-aware rule avoids that worst-case failure.

Required outputs:

- constructive adversarial family;
- minimax or regret-style bound;
- clean discussion of what auxiliary signal is necessary.

### 3.4 Theorem 3: Calibration coupling under conflict

Goal:

- formalize the effect of sequential reasoning under explicit conflict;
- show that calibration error is non-decreasing in CoT depth under conflict
  assumptions;
- prove a measurable rate or at least a monotonicity statement.

Critical boundary condition:

- on no-conflict subsets, the theorem should not predict universal degradation.

### 3.5 Practical theory outputs

The theory should produce:

- a plug-in arbitration rule;
- measurable feature proxies for reliability;
- at least one mitigation idea such as bagging, confidence decoupling, or
  arbitration-aware calibration.

## 4. Experimental program

### 4.1 Benchmark matrix

Primary benchmarks:

| Benchmark | Role |
| --- | --- |
| `ConflictBank` | large-scale controlled conflict benchmark |
| `PopQA` | prior-strength / popularity-conditioned QA |
| `WikiContradict` | gold contradiction benchmark |
| `NQ-Swap` | clean entity-swap context-memory conflict |
| `DynamicQA` | dynamicity-aware conflict benchmark |
| `TempLAMA` | temporal staleness benchmark |
| `FreshQA` | freshness stress test |
| `MQuAKE-Remastered` | multi-hop conflict propagation |

Priority order:

1. `PopQA`
2. `DynamicQA`
3. `ConflictBank`
4. `WikiContradict`
5. `NQ-Swap`
6. the rest

### 4.2 Model matrix

Primary model families:

| Family | Role |
| --- | --- |
| `Pythia` | checkpoint-resolved analysis |
| `OLMo-2` | open-data/open-checkpoint analysis |
| `Llama-3.1` | strong open-weight baseline |
| `Qwen-2.5` / `Qwen-3` | strong arbitration + thinking-mode analysis |
| `Mistral` | cross-family robustness |
| `Phi-3` | medium-scale robustness |
| `DeepSeek-R1-Distill` | reasoning and long-CoT stress test |

Minimum main-track breadth:

- at least 5 models;
- at least one checkpoint-resolved family;
- at least one reasoning-mode family for the CoT theorem.

### 4.3 Conditions per benchmark

For each benchmark-model pair, target these conditions:

- closed-book / no retrieval;
- aligned context;
- conflicting context;
- multi-context contradiction;
- irrelevant retrieval/noise;
- CoT length sweep;
- self-consistency sweep where feasible.

### 4.4 Metrics

Primary:

- accuracy
- Brier score
- NLL
- ECE
- debiased or smooth ECE
- AUROC for confidence vs correctness
- AURC

Theory-facing:

- Bayes regret
- KL divergence to oracle arbitration distribution
- calibration gap split by conflict vs no-conflict
- sensitivity to CoT length on conflict subsets

### 4.5 Headline figures

The paper should aim for these figure types:

1. Bayes-optimal arbitration vs model policy scatter.
2. Worst-case regret comparison for fixed vs adaptive arbitration policies.
3. Conflict-conditioned reliability diagrams across CoT lengths.
4. ECE/Brier vs CoT-length curves split by conflict and no-conflict.
5. Checkpoint-family plots for temporal or staleness effects.

## 5. Code architecture needed next

### 5.1 New active module namespace

Create and grow:

```text
src/knowledge_arbitration/
```

This namespace should absorb all new active work.

### 5.2 Minimum required modules

- `benchmarks.py`: benchmark registry and metadata
- `posterior.py`: arbitration rule utilities
- `metrics.py`: Bayes regret, arbitration KL, calibration helpers
- `features.py`: reliability feature extraction
- `evaluate.py`: benchmark evaluation runner
- `cot.py`: CoT-length sweep helpers

Only the first three are required immediately. The rest can follow.

### 5.3 Configs

Add:

```text
src/configs/knowledge_arbitration_experiments.yaml
```

This should become the main experiment manifest for the project.

### 5.4 Scripts

Immediate scripts:

- `scripts/arbitration_pilot.py`
- `scripts/report_arbitration_status.py`

The first is required now; the second can follow.

## 6. Milestones

### Phase 0: repo pivot

- rewrite top-level docs
- add arbitration module scaffold
- add experiment config
- mark old direction as legacy

### Phase 1: theorem skeleton + synthetic pilot

- formal statement drafts for Theorems 1–3
- synthetic Bernoulli toy or small oracle simulation
- first theorem-to-experiment alignment doc

### Phase 2: first real-data pilots

- PopQA
- DynamicQA
- ConflictBank subset

### Phase 3: calibration-coupling test

- reasoning-mode models
- CoT-length sweeps
- conflict vs no-conflict split
- deterministic-decoding control

### Phase 4: checkpoint-family validation

- Pythia or OLMo family
- temporal/staleness analysis

## 7. Risks

### R1: theorem is elegant but vacuous

Mitigation:

- tie every theorem to a measurable quantity;
- design at least one direct empirical confirmation test per theorem.

### R2: conflict-conditioned CoT claim does not hold

Mitigation:

- make the theorem conditional and explicit;
- ensure the no-conflict case is a positive control, not an embarrassment.

### R3: arbitration rule is dismissed as trivial Bayes

Mitigation:

- emphasize identifiability and excess-risk comparisons;
- include a real lower bound / minimax theorem;
- make the operational rule depend on observable reliability signals.

### R4: benchmark breadth stays too thin

Mitigation:

- prioritize breadth early;
- do not let a single benchmark dominate the paper narrative.

## 8. Writing plan

The intended paper structure is:

1. Introduction
2. Knowledge conflict as a decision problem
3. Bayes-optimal arbitration theorem
4. Fixed-policy suboptimality theorem
5. Calibration-coupling theorem
6. Experiments
7. Mitigations and discussion

The old `paper/` directory is not the live manuscript for this project.

## 9. Immediate tasks

- finalize the repo pivot docs
- build benchmark registry
- build arbitration-rule utilities
- build pilot manifest script
- define the first three benchmark/model pilot cells

That is the current active project baseline.
