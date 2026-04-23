# Project Requirements Document

**Project:** Bayes-Optimal Knowledge Arbitration Under Conflict  
**Status:** Active research direction  
**Target venue:** NeurIPS 2027 main conference  
**Ambition:** Main-track acceptance with spotlight-tier upside  
**Last updated:** 2026-04-23

## 0. Purpose

This document is the main execution plan for the active project.

It defines:

- the paper's core claims,
- the theorem roadmap,
- the experiment matrix,
- the initial code architecture,
- the metrics and statistical standards,
- the compute plan,
- and the milestones that would turn this from an interesting idea into a real
  paper.

This document supersedes the old Track B capacity PRD as the active planning
document.

## 1. Executive summary

The project asks a simple but high-value question:

**When parametric memory and contextual evidence conflict, what is the optimal
decision rule for an LLM, and what goes wrong when the model reasons longer
under that conflict?**

The paper is built around three main contributions.

### Contribution 1: Bayes-optimal arbitration

We cast knowledge-conflict resolution as a posterior-predictive decision
problem. We derive an optimal arbitration rule between:

- parametric memory,
- contextual or retrieved evidence,
- and a reliability variable controlling how much the context should be trusted.

This produces a mathematically grounded alternative to fixed trust rules and
heuristic adaptive retrieval policies.

### Contribution 2: fixed-policy lower bound

We prove that fixed policies such as:

- always trust context,
- always trust parametric memory,
- or use a constant interpolation weight,

are minimax suboptimal whenever conflict regimes vary and reliability is not
constant.

### Contribution 3: calibration-coupling under conflict

We prove and test a conflict-conditioned theorem: under explicit disagreement
between parametric and contextual sources, longer chain-of-thought can worsen
calibration even if accuracy does not improve or does not collapse.

This is the paper's most important empirical-theoretical bet.

## 2. Research questions

### Primary questions

- What is the Bayes-optimal arbitration rule when parametric and contextual
  knowledge disagree?
- How much regret do fixed trust policies incur relative to the Bayes rule?
- Can a measurable reliability signal materially close that regret?
- Under conflict, how does chain-of-thought length affect calibration?
- Can this deterioration be predicted from a misspecified-Bayes view of
  reasoning?

### Secondary questions

- Which observable features best approximate contextual reliability?
- Do larger models become more Bayes-optimal, or just more confident?
- Does self-consistency or bagging reduce the calibration damage predicted by
  the theorem?
- Which benchmark families most cleanly separate arbitration quality from raw
  factual knowledge?

## 3. Paper-level claim hierarchy

### Minimum viable main-track claim

- Bayes-optimal arbitration is formally derived.
- Fixed policies have a non-trivial worst-case regret lower bound.
- Real LLMs are measurably misaligned with the Bayes rule on conflict
  benchmarks.

### Strong claim

- A practical arbitration proxy using observable signals materially reduces
  regret versus fixed policies on real benchmarks.
- Conflict-conditioned CoT calibration degradation is visible and reproducible
  across multiple model families.

### Headline claim

- Frontier reasoning models become **more overconfident** under conflict as they
  reason longer, and a Bayes-grounded arbitration rule plus decoupled confidence
  mitigates this reliably.

## 4. Theorem roadmap

### Theorem 1: Bayes-optimal arbitration rule

Define:

- query `q`
- answer `y`
- context `c`
- latent context reliability `r`
- parametric model posterior `p_theta(y | q)`
- context-conditioned answer model `p_ctx(y | q, c)`

Then derive the Bayes-optimal posterior-predictive decision rule as a
reliability-dependent mixture. The theorem must state:

- optimality criterion,
- assumptions on `p(c | y, r)` or equivalent identifiable formulation,
- and the excess risk of fixed alternatives.

### Theorem 2: minimax suboptimality of fixed trust policies

Show that for any fixed policy class without a usable reliability signal, there
exists a conflict distribution on which its regret remains bounded away from
zero relative to the Bayes-optimal rule.

The intended proof style is Yao/minimax plus two or more hard regimes:

- high-quality context
- low-quality context
- and optionally dynamic or popularity-skewed priors

### Theorem 3: calibration-coupling under conflict

Under a conflict condition such as:

- answer-relevant disagreement between parametric and contextual predictive
  distributions exceeding a threshold,

show that sequential reasoning updates can worsen calibration monotonically or
near-monotonically with reasoning depth under generic conditions.

This theorem must be explicitly scoped:

- conflict-conditioned,
- not universal across all QA settings,
- and compatible with no-conflict regimes where CoT helps or is neutral.

## 5. Empirical program

## 5.1 Benchmarks

The primary benchmark registry for the paper should include:

| Benchmark | Role | Priority |
| --- | --- | --- |
| ConflictBank | broad large-scale conflict benchmark | critical |
| PopQA | prior-strength and popularity signal | critical |
| DynamicQA | dynamicity and temporal mismatch | critical |
| WikiContradict | high-quality real contradiction benchmark | high |
| NQ-Swap | clean entity-substitution conflict | high |
| TempLAMA | temporal staleness | medium |
| FreshQA | freshness / post-cutoff knowledge | medium |
| MQuAKE-Remastered | multi-hop conflict propagation | high |

The first complete pilot should cover:

- PopQA
- DynamicQA
- ConflictBank

## 5.2 Models

Minimum serious model set:

| Model family | Role |
| --- | --- |
| Pythia checkpoints | controlled temporal / scale analysis |
| OLMo checkpoints | open-data, traceable training provenance |
| Llama 3.1 8B | modern strong base model |
| Qwen 2.5 7B / 32B | strong open family |
| Mistral 7B | cross-family robustness |
| Phi-3 medium | medium-size robustness |

Reasoning-focused extensions for Theorem 3:

- DeepSeek-R1-distill variants
- Qwen thinking-mode variants

## 5.3 Experimental conditions

Every benchmark-model cell should ideally include:

- closed-book
- aligned context
- conflicting context
- dual contradictory contexts
- irrelevant/noisy context

For CoT-sensitive experiments:

- no CoT
- short CoT
- medium CoT
- long CoT
- deterministic decoding and stochastic decoding

## 5.4 Metrics

Primary metrics:

- Brier score
- negative log-likelihood
- ECE
- debiased ECE
- SmoothECE

Arbitration-specific metrics:

- regret vs. Bayes oracle
- KL gap to Bayes oracle policy
- source-selection accuracy
- context-vs-memory arbitration accuracy

Selective prediction metrics:

- AUROC for correctness
- coverage-risk curve
- AURC

## 5.5 Headline figures

The paper needs at least these figures:

1. **Bayes oracle vs. model arbitration scatter**
2. **Worst-case regret radar or grouped bar chart**
3. **Conflict-conditioned reliability diagrams by CoT length**
4. **Checkpoint or scale trend for arbitration optimality**
5. **Mitigation plot showing bagging / decoupled confidence reduces calibration
   damage**

## 6. Experiment matrix

The primary matrix should be tracked in repo configs and reports.

### Tier 1 matrix

- Benchmarks: PopQA, DynamicQA, ConflictBank
- Models: Pythia family subset, OLMo subset, Llama-3.1-8B, Qwen-2.5-7B,
  Qwen-2.5-32B
- Conditions: closed-book, aligned, conflict

### Tier 2 matrix

- Benchmarks: WikiContradict, NQ-Swap, MQuAKE-Remastered
- Models: same plus one reasoning-family extension
- Conditions: add long-CoT calibration sweeps

### Tier 3 matrix

- TempLAMA, FreshQA
- extended checkpoints
- mitigation experiments

## 7. Initial code architecture

The new project should live under a dedicated namespace rather than being
intertwined with legacy sequential-falsification modules.

Required modules:

```text
src/knowledge_arbitration/
  __init__.py
  benchmarks.py
  posterior.py
  metrics.py
  synthetic.py
  features.py
scripts/
  arbitration_pilot.py
  report_arbitration_results.py
src/configs/
  knowledge_arbitration_experiments.yaml
```

### Module responsibilities

- `benchmarks.py`
  - registry of supported conflict benchmarks
  - benchmark roles, licenses, split metadata, and task type
- `posterior.py`
  - Bayes-optimal mixture functions
  - reliability-aware interpolation
  - regret helpers against oracle
- `metrics.py`
  - arbitration KL gap
  - regret metrics
  - calibration summaries specialized to conflict/no-conflict slices
- `synthetic.py`
  - exact toy problems with computable oracle
- `features.py`
  - extraction of observable arbitration signals:
    - parametric confidence
    - contextual confidence
    - popularity
    - dynamicity
    - semantic entropy
- `arbitration_pilot.py`
  - manifest-driven pilot runner

## 8. Statistical methodology

### Primary reporting

- mean and bootstrap CI over problems
- paired bootstrap when comparing policies
- calibration curves stratified by conflict class
- no hidden cherry-picking of only conflict-positive subsets without reporting
  the base rates

### Seed policy

- at least 3 seeds for stochastic decoding experiments
- deterministic temperature-0 sweeps do not need seed multiplicity but do need
  exact reproducibility metadata

### Multiple testing

- use FDR control for families of significance claims in the main benchmark
  matrix
- explicitly label exploratory ablations as exploratory

## 9. Compute plan

This project is expensive enough to need structure, but not so expensive that it
is infeasible.

The first milestone should not burn frontier-model budget.

### Phase 1: low-risk pilot

- synthetic oracle experiments
- PopQA / DynamicQA pilot
- smaller open models and checkpoint subsets

### Phase 2: theorem-critical experiments

- conflict-conditioned CoT length sweeps
- deterministic temperature-0 sweeps
- bagging / self-consistency mitigation

### Phase 3: breadth and scaling

- larger models
- broader benchmark set
- checkpoint family plots

## 10. Risks

### Risk 1: trivial-Bayes reviewer objection

Mitigation:

- emphasize identifiability and regret gap
- prove lower bounds, not just a derivation
- tie theorem to measurable observables

### Risk 2: CoT theorem fails on real frontier models

Mitigation:

- frame either outcome as informative:
  - mismatch to theorem boundary
  - or emergence toward Bayes-optimality

### Risk 3: calibration degradation is explained away by variance

Mitigation:

- temperature-0 experiments are mandatory
- deterministic decoding must be part of the main ablation

### Risk 4: theory-empirics disconnect

Mitigation:

- insist every theorem yields at least one visible empirical prediction
- do not write the paper around abstract theory only

### Risk 5: benchmark / citation slippage

Mitigation:

- before submission, every citation and date in the literature map must be
  independently verified against primary sources
- this document is a working execution plan, not the final citation authority

## 11. Milestones

### Month 1

- repo pivot complete
- benchmark registry implemented
- synthetic oracle code in place
- theory note for Theorem 1 drafted

### Month 2

- PopQA / DynamicQA pilot running
- first oracle-vs-model arbitration plots
- first fixed-policy regret experiments

### Month 3

- ConflictBank integrated
- checkpoint family subset running
- first draft of theorem statements stabilized

### Months 4–6

- full theorem-to-experiment bridge for Theorems 1 and 2
- first real Theorem 3 calibration sweeps
- start outside feedback / mentorship cycle

### Months 7–12

- breadth, mitigation experiments, robustness
- workshop-quality writeup if main-track story is not yet mature

## 12. Immediate next tasks

- Replace legacy Track B framing in top-level docs.
- Add benchmark and config scaffolding for the arbitration project.
- Build the synthetic Bayes-oracle pilot.
- Implement feature extraction placeholders for context reliability.
- Define the exact theorem notation in a separate methods/theory doc.
- Prepare a concise project packet suitable for external mentor feedback.
