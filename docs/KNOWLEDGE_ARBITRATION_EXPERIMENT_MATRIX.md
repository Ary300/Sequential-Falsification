# Bayes-Optimal Knowledge Arbitration: Experiment Matrix

## Purpose

This file is the compact experiment table for the active arbitration project.

It complements the PRD by making the first wave concrete enough to schedule and
track.

## Primary pilot wave

| Experiment | Benchmarks | Models | Conditions | CoT lengths | Self-consistency | Max examples |
| --- | --- | --- | --- | --- | --- | --- |
| `arbitration_pilot_prior_strength` | `PopQA`, `DynamicQA` | `Llama-3.1-8B`, `Qwen-2.5-7B`, `DeepSeek-R1-Distill-7B` | `closed_book`, `aligned_context`, `conflict_context` | `0`, `128`, `512` | `1`, `8` | `512` |
| `arbitration_pilot_gold_conflict` | `WikiContradict`, `NQ-Swap` | `Llama-3.1-8B`, `Qwen-2.5-7B`, `DeepSeek-R1-Distill-7B` | `closed_book`, `conflict_context`, `two_context_conflict` | `0`, `128`, `512`, `2048` | `1`, `8` | `512` |
| `arbitration_pilot_cot_calibration` | `DynamicQA`, `ConflictBank` | `DeepSeek-R1-Distill-7B`, `Qwen-3-8B` | `aligned_context`, `conflict_context`, `irrelevant_noise` | `0`, `64`, `256`, `1024`, `4096` | `1`, `8`, `32` | `1024` |
| `arbitration_checkpoint_family` | `TempLAMA`, `DynamicQA` | `Pythia`, `OLMo-2-7B` | `closed_book`, `aligned_context`, `conflict_context` | `0`, `128` | `1` | `1024` |

## Theorem alignment

| Theorem | Best early experiment |
| --- | --- |
| Theorem 1: Bayes-optimal arbitration rule | `arbitration_pilot_prior_strength` |
| Theorem 2: fixed-policy suboptimality | `arbitration_pilot_gold_conflict` + synthetic oracle |
| Theorem 3: CoT calibration coupling | `arbitration_pilot_cot_calibration` |

## Priority order

1. `arbitration_pilot_prior_strength`
2. `arbitration_pilot_cot_calibration`
3. `arbitration_pilot_gold_conflict`
4. `arbitration_checkpoint_family`

## Spotlight-scale next wave

The pilot wave is no longer enough for spotlight contention. The next execution
target is defined in:

- [knowledge_arbitration_spotlight.yaml](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/configs/knowledge_arbitration_spotlight.yaml)
- [build_arbitration_spotlight_manifest.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_arbitration_spotlight_manifest.py)

That wave is designed to clear the spotlight-floor matrix:

- `5+` model families
- `5+` benchmarks
- `6+` serious baselines
- `4+` ablations

Core spotlight experiments:

| Experiment | Purpose |
| --- | --- |
| `arbitration_spotlight_t12_matrix` | theorem-1/theorem-2 headline matrix |
| `arbitration_spotlight_t3_size_scaling` | theorem-3 scale verification |
| `arbitration_spotlight_t3_eta_ablation` | theorem-3 rewrite and intervention scaffold |
| `arbitration_spotlight_api_headline_subset` | API comparator slice if budget allows |

## Headline-result gate

We do not have a headline result until at least one of these happens:

- a Bayes-inspired rule clearly beats all fixed policies on regret;
- conflict-conditioned calibration worsens with CoT length on real models while
  no-conflict calibration does not;
- checkpoint-family evidence shows a clear prior-strength or staleness effect
  that the theory predicts.
