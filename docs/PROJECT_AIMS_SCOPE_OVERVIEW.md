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
- a corrected benchmark-backed headline wave with a de-oracled Bayes proxy:
  [`results/arbitration_real_headline_wave_reestimated_v3/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_real_headline_wave_reestimated_v3/report/summary.md);
- a focused `WikiContradict` contradiction report:
  [`results/arbitration_wikicontradict_focus/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_wikicontradict_focus/report/summary.md);
- a corrected conflict-heavy benchmark wave:
  [`results/arbitration_conflict_headline_wave_reestimated_v3/report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_headline_wave_reestimated_v3/report/summary.md);
- a theorem-3 diagnosis with ambiguity filtering and sample rows:
  [`results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/arbitration_conflict_focus_compact_v2/theorem3_diagnosis/summary.md).

The strongest current empirical signal is theorem-1/theorem-2 shaped:

- in the corrected broad real wave, `bayes_proxy` now beats the generic
  heuristic honestly rather than by construction:
  `-0.0461` mean regret versus `-0.0233` for `heuristic_adaptive`;
- `simulated_model` is materially worse at `0.1408`;
- `fixed_50` is worse again at `0.3650`;
- naive fixed trust policies are dramatically worse:
  `always_context = 7.2237`, `always_parametric = 5.9356`.

The conflict-focused theorem-2 wave is even cleaner:

- `bayes_proxy = -0.1256`;
- `heuristic_adaptive = -0.0752`;
- `simulated_model = 0.1104`;
- `fixed_50 = 0.3037`;
- `always_context = 5.9037`;
- `always_parametric = 7.1329`.

The theorem-3 situation is more mixed:

- broad real pilot mean conflict ECE delta is `-0.0054`, so the wide benchmark
  mix does **not** yet support the headline that longer CoT broadly worsens
  calibration under conflict;
- ambiguity-filtered proxy diagnosis did **not** rescue `ConflictBank` or
  `DynamicQA`, while `WikiContradict` stayed positive;
- that diagnosis pointed to the real blocker: the old theorem-3 path was still
  proxy-based and did not contain actual generated reasoning traces.

What is now newly real:

- a resumable real-generation theorem-3 runner:
  [`scripts/run_theorem3_real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_real_generation.py);
- a theorem-3-specific real-generation backend:
  [`src/knowledge_arbitration/real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/real_generation.py);
- a focused theorem-3 summary renderer:
  [`scripts/report_theorem3_real_generation.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/report_theorem3_real_generation.py);
- a local smoke report proving the real-generation path and reporting stack are
  executable end-to-end:
  [`results/theorem3_real_generation_mock_smoke/theorem3_report/summary.md`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/results/theorem3_real_generation_mock_smoke/theorem3_report/summary.md);
- a dedicated Delta launch path:
  [`scripts/submit_delta_theorem3_real_generation.sh`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_real_generation.sh)
  and
  [`slurm/delta/theorem3_real_generation_delta.sbatch`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/slurm/delta/theorem3_real_generation_delta.sbatch).

The live focused Delta job is:

- `2185966` `theorem3_real`
- model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- benchmarks: `WikiContradict` and ambiguity-screened `ConflictBank`
- conditions: real `no_cot`, `short_cot`, `long_cot`
- target size: `200` `WikiContradict` examples and `500` `ConflictBank`
  examples after screening

So the project is no longer blocked on infrastructure. It is now blocked on
the outcome of the real-generation theorem-3 run itself.

## Current real-generation status

The first focused DeepSeek real-generation run did real work but did not finish
cleanly.

What completed on Delta before failure:

- `ConflictBank` ambiguity screening:
  `results/theorem3_real_generation_r1_7b/conflictbank_screening.jsonl`
- `ConflictBank` screening summary:
  `results/theorem3_real_generation_r1_7b/conflictbank_screening_summary.json`
- partial real-generation rows:
  `results/theorem3_real_generation_r1_7b/theorem3_generation_rows.jsonl`

What the partial rows show right now:

- `WikiContradict` real generations completed through all three CoT settings;
- `ConflictBank` generation rows did not complete yet;
- the partial real signal is **not** conflict-specific in the way theorem 3
  originally wanted.

On the completed `WikiContradict` slice:

- conflict, `cot=0`: accuracy `0.2299`, mean confidence `0.5492`
- conflict, `cot=128`: accuracy `0.2299`, mean confidence `0.7264`
- conflict, `cot=1024`: accuracy `0.2011`, mean confidence `0.6522`
- no-conflict, `cot=0`: accuracy `0.3143`, mean confidence `0.5783`
- no-conflict, `cot=128`: accuracy `0.2171`, mean confidence `0.7223`
- no-conflict, `cot=1024`: accuracy `0.2126`, mean confidence `0.6677`

The honest reading of that partial real run is:

- CoT is increasing confidence while accuracy stays very poor;
- that is a real overconfidence effect;
- but it currently appears in both conflict and no-conflict conditions, so it
  does **not** yet support the original conflict-conditioned theorem-3
  headline.

Because the first Delta run failed after the `WikiContradict` portion, the
current priority is still to finish the real `ConflictBank` generation before
making the final theorem-3 decision.

The recovery job now queued on Delta is:

- `2190333` `theorem3_resume`

That recovery run is intended to resume from the existing JSONL files and spend
its budget on the unfinished `ConflictBank` generations rather than replaying
the completed `WikiContradict` slice.

## Emerging theorem-3 landing from real traces

The resumed `srun` recovery wave moved theorem 3 into a clearer shape. The
original monotone claim,

`longer CoT under conflict -> higher calibration error`,

is still too strong. The real pattern emerging from actual `DeepSeek-R1-Distill-Qwen-7B`
traces is:

`intermediate CoT -> peak overconfidence`, followed by partial recovery at
very long CoT.

This is now visible in the completed `4200`-row real-generation run across both
`WikiContradict` and `ConflictBank`.

On `WikiContradict`:

- conflict overconfidence gap: `0.2923 -> 0.4825 -> 0.4429`
- no-conflict overconfidence gap: `0.2643 -> 0.5038 -> 0.4331`

On `ConflictBank`:

- conflict overconfidence gap: `0.5505 -> 0.7531 -> 0.5308`
- no-conflict overconfidence gap: `0.0996 -> 0.2754 -> -0.3724`

So the strongest defensible theorem-3 reading is now:

- `cot=128` is the peak-overconfidence bucket across all observed slices;
- `cot=1024` does not continue the monotone rise and instead partially
  self-corrects;
- the peak effect is especially sharp on `ConflictBank` conflict rows, where
  the gap rises by `+0.2026` from `cot=0` to `cot=128`;
- the same non-monotone pattern also appears on `WikiContradict`, where the
  conflict gap rises by `+0.1902` from `cot=0` to `cot=128` and then drops by
  `-0.0396` from `cot=128` to `cot=1024`.

This means theorem 3 can land as a **non-monotone calibration-coupling
theorem** rather than the original monotone long-CoT version.

The exact completed 7B theorem-3 picture is:

- `ConflictBank` conflict:
  `ece 0.5505 -> 0.7531 -> 0.5308`,
  `gap 0.5505 -> 0.7531 -> 0.5308`
- `ConflictBank` no-conflict:
  `ece 0.1312 -> 0.5774 -> 0.4044`,
  `gap 0.0996 -> 0.2754 -> -0.3724`
- `WikiContradict` conflict:
  `ece 0.3823 -> 0.5075 -> 0.4429`,
  `gap 0.2923 -> 0.4825 -> 0.4429`
- `WikiContradict` no-conflict:
  `ece 0.3543 -> 0.5238 -> 0.4331`,
  `gap 0.2643 -> 0.5038 -> 0.4331`

The next replication target is already defined but the first 14B launch failed
for an operational reason, not a scientific one:

- Delta job `2193155`
- model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- failure reason: `OSError: [Errno 122] Disk quota exceeded`
- immediate fix: reroute theorem-3 outputs to `/work/nvme/bgvi/adas17/...`
  instead of quota-limited home storage before relaunching

That relaunch is now in progress:

- Delta job `2193269`
- working tree moved to:
  `/work/nvme/bgvi/adas17/tts-falsification`
- output root:
  `/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3`

The ambiguity-filter diagnosis sharpens the interpretation:

- filtering to `parametric_score in [0.2, 0.8]` does **not** flip
  `ConflictBank` or `DynamicQA`;
- `WikiContradict` stays clearly positive after filtering;
- the best current reading is that theorem 3 may hold for naturalistic source
  ambiguity but not for every synthetic or easily-detectable conflict setup.

There is also one important remaining limitation:

- the theorem-3 pipeline is still proxy-based, so it does not contain raw
  generated reasoning traces and cannot yet tell us whether longer CoT buckets
  correspond to genuine extended reasoning versus filler text.

That means the project now has a real benchmark-backed arbitration signal, but
not yet the broad conflict-conditioned CoT headline needed for the full paper.

## Reality check

This is a stronger idea than the previous direction, but it is also less built.

What is honest today:

- the repo has been pivoted at the planning layer;
- arbitration loaders and benchmark-backed proxy experiments now run end to end;
- there is already a real early theorem-1/theorem-2-style signal;
- theorem statements now exist in a clean draft form;
- the theorem-3 headline is still incomplete.

What must happen before we can talk about a serious main-track paper:

- theorem statements need to be written cleanly;
- theorem sketches need to be upgraded into actual proofs;
- the broad theorem-3 effect needs to land outside a single contradiction slice;
- the theorem-3 pipeline needs raw reasoning traces instead of proxy-only CoT;
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
