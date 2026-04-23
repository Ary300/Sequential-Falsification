# Bayes-Optimal Knowledge Arbitration: Results Tracker

## Purpose

This file tracks the specific results required for the knowledge-arbitration
paper to be competitive at a strong main-track level.

This is not a generic todo list. Every row below corresponds to a figure, table,
 or theorem-validation claim that should exist before the paper is considered
 "headline-ready."

## Headline result checklist

| Result | Why it matters | Status |
| --- | --- | --- |
| Bayes-oracle vs model arbitration scatter on real benchmarks | proves the theorem is empirically non-vacuous | open |
| Fixed-policy regret lower-bound plot | gives the impossibility / dominance result | open |
| Conflict-conditioned CoT calibration degradation plot | validates Theorem 3 | open |
| No-conflict positive control where CoT does not hurt calibration | defines theorem boundary condition | open |
| Temperature-0 replication of calibration degradation | rules out pure variance explanation | open |
| Checkpoint-family scaling plot | gives a stronger science story than one-off frontier snapshots | open |
| Mitigation plot showing bagging or confidence decoupling reduces harm | turns the paper from diagnosis into actionable guidance | open |

## Main theorem validation table

| Theorem | Required empirical validation | Status |
| --- | --- | --- |
| Bayes-optimal arbitration rule | synthetic oracle + 3 real benchmark families | open |
| Minimax suboptimality of fixed policies | worst-case regret on adversarial benchmark-realizable distributions | open |
| Calibration-coupling under conflict | CoT-length sweep on conflict vs no-conflict subsets | open |

## Benchmark coverage tracker

| Benchmark | Bayes arbitration | Fixed-policy regret | CoT calibration | Notes |
| --- | --- | --- | --- | --- |
| PopQA | open | open | optional | prior/popularity anchor |
| DynamicQA | open | open | open | temporal and dynamicity anchor |
| ConflictBank | open | open | open | broad conflict anchor |
| WikiContradict | open | optional | open | small but high-quality |
| NQ-Swap | optional | open | optional | clean swap regime |
| MQuAKE-Remastered | optional | optional | open | multi-hop conflict |
| TempLAMA | optional | optional | optional | checkpoint-friendly |
| FreshQA | optional | optional | optional | freshness extension |

## Model coverage tracker

| Model family | Arbitration gap | Calibration sweep | Checkpoint analysis | Notes |
| --- | --- | --- | --- | --- |
| Pythia | open | optional | open | checkpoint-resolved |
| OLMo | open | optional | open | checkpoint-resolved |
| Llama-3.1-8B | open | open | n/a | strong base model |
| Qwen-2.5-7B | open | open | n/a | strong open model |
| Qwen-2.5-32B | open | open | n/a | larger scale point |
| Mistral-7B | open | optional | n/a | robustness |
| Phi-3-medium | open | optional | n/a | robustness |
| DeepSeek-R1-distill | optional | open | n/a | reasoning stress test |

## Figure tracker

### Figure 1: Bayes oracle vs model arbitration

Needed:

- at least 3 benchmarks
- at least 5 models
- one diagonal reference line
- one fitted trend line or grouped family trend

Status: `open`

### Figure 2: Fixed-policy regret

Needed:

- always-context
- always-parametric
- fixed interpolation
- heuristic adaptive baseline
- Bayes-style rule

Status: `open`

### Figure 3: CoT calibration under conflict

Needed:

- conflict split
- no-conflict split
- deterministic decoding
- at least one reasoning family and one base family

Status: `open`

### Figure 4: Scaling or checkpoint dynamics

Needed:

- Pythia or OLMo checkpoints
- one benchmark where conflict dynamics are measurable

Status: `open`

### Figure 5: Mitigation

Needed:

- bagging / self-consistency or confidence-decoupled reasoning
- measured reduction in Brier / ECE on conflict subset

Status: `open`

## Immediate go/no-go milestones

### Milestone A

We have a synthetic oracle plot where the Bayes-optimal rule is clearly better
than fixed policies.

Status: `open`

### Milestone B

We have one real benchmark where model arbitration is visibly misaligned with
the Bayes proxy.

Status: `open`

### Milestone C

We have one real model family where conflict-conditioned ECE worsens with longer
CoT and the effect survives temperature-0 decoding.

Status: `open`

### Milestone D

We have one mitigation that measurably closes the calibration gap.

Status: `open`

## Notes

- If Milestones A and B land but C does not, the paper can still be strong on
  arbitration theory and regret.
- If C lands strongly, the paper becomes much more likely to be headline-worthy.
- If C only lands on a narrow conflict subset, that is still acceptable as long
  as the theorem is written with that boundary condition explicitly.
