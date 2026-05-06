# Bayes-Optimal Knowledge Arbitration

This repository has been pivoted to a new active research direction:

> Bayes-optimal knowledge arbitration under context-memory conflict.

The current goal is a theory-plus-empirics paper about how LLMs should arbitrate
between parametric memory and retrieved context, with special emphasis on:

- Bayes-optimal arbitration rules,
- minimax suboptimality of fixed trust policies,
- calibration under knowledge conflict and long chain-of-thought.

## Active repo direction

The active planning and scaffold files are:

- [docs/PROJECT_AIMS_SCOPE_OVERVIEW.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/PROJECT_AIMS_SCOPE_OVERVIEW.md)
- [docs/PROJECT_REQUIREMENTS_DOCUMENT.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/PROJECT_REQUIREMENTS_DOCUMENT.md)
- [docs/KNOWLEDGE_ARBITRATION_METHODS_AND_EXPERIMENTS.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/KNOWLEDGE_ARBITRATION_METHODS_AND_EXPERIMENTS.md)
- [docs/KNOWLEDGE_ARBITRATION_RESULTS_TRACKER.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/KNOWLEDGE_ARBITRATION_RESULTS_TRACKER.md)
- [src/knowledge_arbitration](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration)
- [src/configs/knowledge_arbitration_experiments.yaml](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/configs/knowledge_arbitration_experiments.yaml)
- [scripts/arbitration_pilot.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/arbitration_pilot.py)

## What the repo currently contains

### Current / active

- top-level project docs for the arbitration paper
- a benchmark registry for conflict / arbitration datasets
- a first-pass Bayes-inspired arbitration scaffold
- arbitration-specific regret and KL metrics
- a pilot manifest builder for the new experiment matrix

### Legacy / archived

This repo still contains substantial earlier work on Sequential Falsification
and Track B capacity. That material is **not** the active paper direction now.
It remains here because some utilities may still be reused.

Legacy-heavy areas include:

- [paper/](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper)
- [src/capacity.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/capacity.py)
- [src/verifiers/](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/verifiers)
- [scripts/estimate_capacity.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/estimate_capacity.py)
- [scripts/capacity_pilot.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/capacity_pilot.py)
- [docs/METHODS_DETAILED.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/METHODS_DETAILED.md)
- [docs/RESULTS_DETAILED_UP_TO_NOW.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/RESULTS_DETAILED_UP_TO_NOW.md)

## Quick start for the active project

Build the current arbitration experiment manifest:

```bash
python3 scripts/arbitration_pilot.py
```

That writes a dry-run manifest summarizing:

- benchmark coverage
- model families
- conditions
- CoT budgets
- self-consistency settings
- rough example counts

The default config is:

```text
src/configs/knowledge_arbitration_experiments.yaml
```

## Immediate next work

The repo is not claiming headline arbitration results yet. The current active
priorities are:

1. theorem statements for the Bayes-optimal rule, fixed-policy lower bound, and
   conflict-conditioned calibration theorem
2. real data loaders for `PopQA`, `DynamicQA`, and `ConflictBank`
3. a synthetic Bayes-oracle experiment
4. conflict vs no-conflict calibration pilots on real models

## Legacy manuscript note

The existing LaTeX manuscript under [paper/](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/paper)
is an archived manuscript for the older Sequential Falsification project. It is
retained for reference and utility reuse, but it is not the live manuscript for
the active arbitration paper.
