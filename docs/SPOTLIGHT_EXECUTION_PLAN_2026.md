# Engineering a Spotlight-Tier Knowledge Arbitration Paper

## Purpose

This document converts the April 2026 strategy audit into an execution plan.

It is not a claim that the paper is already spotlight-tier. It records the
strongest honest path from the current repo state to a submission that could
reasonably compete for spotlight at ICML / NeurIPS / ICLR.

## Bottom line

- The current draft is publishable, but not yet spotlight-tier.
- The strongest parts of the project are still theorem 1 and theorem 2.
- The weakest and most scoop-exposed part is theorem 3 in its original form.
- The highest-leverage move is to rewrite theorem 3 around a two-regime
  self-correction / misspecified-Bayes story rather than a simple
  conflict-only monotone calibration claim.

## Venue strategy

Primary venue target:

- `ICML 2026`

Fallback / next-wave targets:

- `NeurIPS 2026`
- `ICLR 2027`
- `NeurIPS 2027`

## Theorem 3 rewrite

Recommended replacement:

`Theorem 3' (Two-Regime Self-Correction Under Conflict).`

Working interpretation:

- longer reasoning can amplify overconfidence through misspecified sequential
  updates;
- smaller models can show partial recovery at long CoT;
- larger models can instead saturate into near-maximal overconfidence on hard
  controlled conflict families;
- the effect should be framed using generalized Bayes /
  misspecified-posterior ideas, not just empirical “more CoT hurts” language.

Theory anchors to cite:

- `Berk (1966)`
- `Kleijn & van der Vaart (2006)`
- `Grunwald & van Ommen (2017)`
- `Bissiri, Holmes, Walker (2016)`
- `Esponda & Pouzo (2016)`
- `Fudenberg, Lanzani, Strack (2021)`

## Experimental floor for spotlight contention

Minimum spotlight-shaped matrix to target:

- `5` model families
- `5` benchmarks
- `6+` serious baselines
- `3` seeds
- `4+` targeted ablations

### Models to prioritize

- `Llama-3.1-8B-Instruct`
- `Llama-3.1-70B-Instruct`
- `Qwen2.5-7B-Instruct`
- `Qwen2.5-14B-Instruct`
- `Qwen2.5-32B-Instruct` or `Qwen3-8B`
- `Mistral-7B-Instruct-v0.3`
- `DeepSeek-R1-Distill-Qwen-7B`

### Benchmarks to prioritize

- `ConflictBank`
- `NQ-Swap`
- `MemoTrap`
- `PopQA`
- `FaithEval`

High-value additions:

- `WikiContradict`
- `AmbigDocs` or `RAMDocs`
- `ClashEval`

### Baselines to prioritize

- `CAD`
- `AdaCAD`
- `CoCoA`
- `Self-RAG`
- `CRAG`
- `Astute RAG`

## Headline-number standards

Numbers that would read as spotlight-credible:

- a `>= 5` point absolute gain over `heuristic_adaptive` on at least three of
  five benchmarks, with paired-bootstrap CI excluding zero;
- or a clearly dominant Pareto story on regret vs compute / conflict density;
- or a sharp theorem-3 number such as a replicated size threshold for loss of
  self-correction or a calibrated-decoding rescue on the pathological 14B
  conflict slice.

## 26-week execution plan

### Weeks 1–4

- Re-verify the 7B / 14B asymmetry across at least one more family.
- Rewrite theorem 3 sketches around the two-regime self-correction story.
- Tighten positioning against `AdaCAD`, `CoCoA`, and the Bayesian-RAG name
  collisions.

### Weeks 5–10

- Expand to the 5-model / 5-benchmark matrix.
- Run the non-negotiable baseline panel.
- Refresh the headline bundle around regret, calibration, and scope coverage.

### Weeks 11–16

- Run the targeted ablations.
- Execute theorem-3 falsification / intervention experiments.
- Decide whether theorem 3 remains a co-headline or becomes a secondary
  section.

### Weeks 17–22

- Build the paper figures around one killer 2x2 panel:
  regret-compute Pareto, conflict-density sweep, reliability diagram,
  two-regime reasoning curves.
- Expand related work and sharpen the novelty paragraph.

### Weeks 23–26

- Full draft freeze.
- Internal review.
- Reproducibility and appendix cleanup.

## Immediate repo actions implied by this plan

1. Keep theorem 1 / theorem 2 as the project floor.
2. Treat theorem 3 as a rewrite problem, not just an experiment problem.
3. Move the official venue target to:
   `ICML 2026 primary, NeurIPS 2026 fallback, ICLR / NeurIPS 2027 continuation`.
4. Expand the benchmark and baseline registry to include the spotlight-floor
   comparator set.
