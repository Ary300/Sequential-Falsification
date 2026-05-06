# Bayes-Optimal Knowledge Arbitration: Methods and Experiment Plan

## Purpose

This document connects the theorem story to concrete code and experiments.

It is meant to be the working bridge between the PRD and implementation.

## 1. Method object

We treat arbitration as choosing how much to trust:

- parametric memory;
- retrieved context;
- or a calibrated combination of the two.

At minimum, each evaluated example should expose:

- `question`
- `candidate answers`
- `parametric score` for each candidate
- `contextual score` for each candidate
- `reliability features`
- `ground truth`
- `condition label` such as `aligned`, `conflict`, `irrelevant`, or
  `multi_context_conflict`

## 2. Reliability features to extract

The first feature bank should include:

- retrieval score / rank
- source popularity proxy
- semantic entropy
- closed-book confidence
- context-only confidence
- disagreement magnitude between parametric and contextual beliefs
- temporal freshness proxy when available

These features are not yet "the theorem." They are the observable inputs that a
Bayes-inspired rule can condition on.

## 3. Core experimental conditions

Each benchmark should support as many of these as possible:

| Condition | Meaning |
| --- | --- |
| `closed_book` | no retrieved context |
| `aligned_context` | context agrees with parametric memory |
| `conflict_context` | context conflicts with parametric memory |
| `two_context_conflict` | retrieved sources disagree |
| `irrelevant_noise` | context is off-topic or non-diagnostic |

The calibration-coupling theorem also requires:

| CoT condition | Meaning |
| --- | --- |
| `cot_0` | direct answer, no reasoning |
| `cot_short` | short reasoning budget |
| `cot_medium` | medium reasoning budget |
| `cot_long` | long reasoning budget |

## 4. Primary comparisons

The minimum policy set to compare is:

- always trust parametric memory
- always trust context
- constant-weight interpolation
- heuristic adaptive rule
- Bayes-inspired reliability-aware rule

If available later, compare to:

- Self-RAG-style retrieval triggers
- FLARE-style uncertainty trigger
- CRAG-style retrieval evaluator

## 5. Headline result template

### Theorem 1 figure

Plot:

- x-axis: oracle Bayes preference for context
- y-axis: observed model preference for context

Break out by:

- popularity / prior-strength bins
- dynamicity bins
- benchmark

### Theorem 2 figure

Plot worst-case regret for:

- always context
- always parametric
- constant mix
- heuristic adaptive
- Bayes-inspired rule

### Theorem 3 figure

Plot conflict-split reliability:

- x-axis: CoT budget
- y-axis: ECE or Brier
- lines: conflict vs no-conflict
- models: at least one reasoning family and one base family

## 6. First pilot recommendation

The fastest serious pilot is:

- `PopQA` with popularity bins
- `DynamicQA` with dynamicity bins
- `ConflictBank` subset for explicit conflict
- models:
  - `Llama-3.1-8B`
  - `Qwen-2.5-7B`
  - `DeepSeek-R1-Distill-Qwen-7B`

This pilot is enough to test whether:

- reliability-aware arbitration is measurable;
- fixed policies look obviously suboptimal;
- conflict-conditioned calibration moves in the predicted direction.

## 7. What would count as a strong early win

Any one of these would be a real project accelerant:

- the Bayes-inspired rule clearly beats fixed policies on regret;
- conflict-conditioned ECE rises monotonically with CoT length on at least one
  strong reasoning model;
- checkpoint-family analysis shows a clean prior-strength or staleness effect.

## 8. What would count as a warning sign

- no measurable gap between fixed and adaptive policies;
- no difference between conflict and no-conflict calibration curves;
- empirical behavior varies wildly with trivial prompt changes;
- the theory predicts trends that disappear under deterministic decoding.

If those happen, we should narrow the scope before overbuilding the paper.
