# Arbitration Manuscript Plan

## Purpose

This file is the bridge between the current repo state and the eventual
Bayes-optimal knowledge arbitration manuscript.

The goal is to make it obvious how to replace the archived Sequential
Falsification paper tree with a paper that matches the current results.

## Current paper-ready headline

The strongest honest headline today is:

1. A Bayes-style reliability-aware arbitration rule beats a generic adaptive
   heuristic and dramatically outperforms fixed trust policies.
2. Fixed trust policies are minimax-bad in practice on conflict-heavy slices.
3. Calibration failure under reasoning is real, but the corrected control means
   it should now be written as a harder and narrower theorem: hard-QA
   overconfidence amplification with conflict-sensitive persistence, not a
   clean conflict-only sign flip.

## Current empirical backbone

### Theorem 1

- Broad corrected wave:
  [`results/arbitration_real_headline_wave_reestimated_v3/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_real_headline_wave_reestimated_v3/report/summary.md)
- Headline numbers:
  - `bayes_proxy = -0.0461`
  - `heuristic_adaptive = -0.0233`
  - `fixed_50 = 0.3650`
  - `always_context = 7.2237`
  - `always_parametric = 5.9356`

### Theorem 2

- Conflict-heavy corrected wave:
  [`results/arbitration_conflict_headline_wave_reestimated_v3/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_headline_wave_reestimated_v3/report/summary.md)
- Headline numbers:
  - `bayes_proxy = -0.1256`
  - `heuristic_adaptive = -0.0752`
  - `simulated_model = 0.1104`
  - `fixed_50 = 0.3037`
  - `always_context = 5.9037`
  - `always_parametric = 7.1329`

### Theorem 3

- Real-trace 7B result summary:
  [`docs/generated/theorem3_real_7b_final.json`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_real_7b_final.json)
- Headline pattern:
  - `ConflictBank` conflict gap `0.5505 -> 0.7531 -> 0.5308`
  - `WikiContradict` conflict gap `0.2923 -> 0.4825 -> 0.4429`
- Write this as theorem `3c / 3c'`, not as the old monotone theorem.

## Current caveats the paper must state explicitly

- The theorem-1/2 benchmark waves are benchmark-backed proxy evaluations, not
  full real-generation sweeps.
- The broad-wave Bayes win has one clear exception:
  `Qwen2.5-14B-Instruct` slightly favors the heuristic.
- The conflict-wave has one near-tie:
  `pythia-6.9b` is essentially tied between the Bayes proxy and simulated
  model.
- The next real question is not whether theorem 3 exists at all, but whether it
  can be rewritten into a novelty-bearing two-regime result and then
  replicated beyond the current DeepSeek panel.

## Recommended section mapping

### Title

Use one of:

1. `When Should LLMs Trust Retrieval? Bayes-Optimal Knowledge Arbitration`
2. `Fixed Trust Policies Are Wrong: Bayes-Optimal Knowledge Arbitration for LLMs`
3. `Knowledge Arbitration Under Conflict: Bayes-Optimal Rules and Two-Regime Reasoning Calibration`

### Abstract

Base from:

- [../docs/PAPER_HEADLINE_DRAFT.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/PAPER_HEADLINE_DRAFT.md)

### Introduction

Must say plainly:

- retrieval should not be trusted by default;
- parametric memory should not be trusted by default;
- arbitration is a posterior-predictive decision problem;
- fixed trust policies fail badly enough that this is not just a tuning issue;
- theorem 3 should be rewritten around the corrected closed-book control, not
  left as the old peak-only story.

### Theory section

Subsections:

1. Posterior-predictive setup and notation.
2. Theorem 1: Bayes-optimal arbitration rule.
3. Theorem 2: minimax suboptimality of fixed policies.
4. Theorem 3 rewrite: two-regime self-correction / misspecified-Bayes
   overconfidence amplification.

### Experiments section

Main-paper figures should be:

1. Corrected regret bars for theorem 1/2.
2. Oracle-vs-model arbitration gap.
3. Theorem-3 real-trace curves on `ConflictBank` and `WikiContradict`.
4. Per-model Bayes-vs-heuristic gains with the `Qwen2.5-14B-Instruct`
   exception visible.

## Concrete migration tasks

1. Replace the title and abstract in [main.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/main.tex).
2. Rewrite [sections/introduction.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/introduction.tex) around the new project.
3. Replace [sections/method.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/method.tex) with arbitration theory and experimental protocol.
4. Replace [sections/experiments.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/experiments.tex) with the corrected theorem-1/2 tables and theorem-3 figures.
5. Rewrite [sections/conclusion.tex](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper/sections/conclusion.tex) to match the current honest landing.
6. Rebuild bibliography around the arbitration literature map before any paper freeze.

## The one thing still not “finished”

The manuscript can be drafted now, but the empirical project is only fully
finished once the 14B theorem-3 replication is harvested and slotted into the
theorem-3 section.
