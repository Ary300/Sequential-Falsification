# Sequential Falsification Project: Aims, Scope, and Overview

## Purpose of this document

This file is the high-level project map for the repository. It is meant to
answer, in one place:

- what the project is trying to prove;
- what is in scope for the paper and repository;
- what the strongest current claims are;
- what is explicitly not yet claimable;
- what work remains before the project can support a top-tier main-track
  submission.

This document is intentionally conservative. The repository has several strong
results, but it also has unfinished rows, partial seed coverage, and a recent
math-validity correction that changes how some older rows should be interpreted.

## One-sentence project thesis

Sequential falsification uses execution-grounded, population-level elimination
to recover much of the oracle gap left open by agreement-based test-time
scaling in code generation.

## Longer project thesis

Standard test-time scaling for code generation often relies on agreement:
generate multiple candidates, cluster or vote over them, and hope correctness is
correlated with frequency. That assumption can fail badly, especially on
reasoning-oriented code models where surface diversity is high and majority vote
can be worse than greedy decoding. This project studies a different selection
primitive:

1. Generate a diverse candidate pool.
2. Construct benchmark-safe probes.
3. Execute the candidate population against those probes.
4. Eliminate inconsistent candidates.
5. Select from the surviving pool.

The intended scientific story is not merely "more tests help." The intended
story is that active, sequential, execution-grounded elimination can outperform
agreement-based selection and provide a useful confidence signal for
within-pool ranking.

The strongest current technical direction inside the repository is now
population-consensus differential falsification:

- generate a large candidate pool;
- find inputs on which surviving candidates disagree;
- require a strong output consensus among the population;
- eliminate the minority candidates that disagree with that consensus.

That is the main mechanism the project is now leaning on to create genuine
separation from single-candidate repair methods.

## Main project goals

### Goal 1: Establish falsification as a real alternative to agreement-based TTS

The first goal is to show that sequential falsification is not just a cosmetic
variant of majority vote or generated-test filtering. The code path therefore
emphasizes:

- population-level elimination, not single-candidate repair;
- multiple probe families, not just repeated public tests;
- adaptive probe choice, not one-shot fixed filtering;
- survivor ranking after elimination, not before.

### Goal 2: Diagnose where agreement-based methods fail

A strong secondary goal is scientific diagnosis. Even where falsification does
not yet beat every strong sequential baseline, the repository already supports
an important result:

- majority voting can fail catastrophically on reasoning-oriented code models;
- active elimination can recover most of the oracle gap on those same rows.

That diagnosis is likely publishable even if the final framing becomes more
measured than the original "headline-breakthrough" ambition.

### Goal 3: Build a benchmark-aware, reproducible experimental stack

The project is also a systems build:

- benchmark loaders for EvalPlus, LiveCodeBench, and answer-only math sets;
- unified evaluation for function-completion and stdin/stdout code tasks;
- cluster launchers for DeltaAI and Anvil;
- reporting, readiness audits, and publication-bundle generation.

### Goal 4: Explore confidence/calibration, carefully

The original vision included anytime-valid statistical confidence grounded in
e-values. The current repository is more careful than that:

- confidence is currently an empirical ranking signal;
- calibration diagnostics are computed and reported;
- a fully justified anytime-valid guarantee is not yet claimed.

This means confidence remains part of the project, but not yet the sole or
primary novelty claim.

## What the project currently claims

These claims are supported by the repository as it exists now.

### Supported claims

- Sequential falsification is implemented as a population-based,
  elimination-based selector for code generation.
- The repository supports multiple probe families: public tests, mutation
  probes, edge-case probes, random-stress probes, and differential probes.
- Majority vote can underperform greedy decoding on some reasoning-oriented
  code rows.
- On the strongest HumanEval+ rows currently available, falsification recovers
  most of the majority-vote-to-oracle gap.
- The repository includes reviewer-facing baselines beyond greedy and majority
  vote, including self-debug, generated-test filtering, and local executable
  CodeT/S* proxies.
- The project now contains explicit readiness and coverage audits so the paper
  does not have to rely on memory or informal status updates.

### Not-yet-supported claims

- Falsification universally beats self-debugging.
- Falsification universally beats generated-test filtering.
- The confidence score is formally anytime-valid.
- The current math path is a true adversarial falsification method.
- Local proxy baselines are equivalent to external SkyThought S* or Microsoft
  CodeT.
- The benchmark matrix is complete and seed-clean across all targeted rows.

## Scope of the current repository

### In scope

- Code-generation test-time scaling.
- Population-level selection from multiple candidates.
- Execution-guided elimination.
- Confidence diagnostics for selection quality.
- Benchmark-aware evaluation infrastructure.
- Cluster orchestration and result recovery.
- NeurIPS/ICLR-style baseline/readiness audits.

### Supporting scope

- Answer-only math benchmarks as evaluation targets.
- PRM-style and verifier-style baselines as future integrations.
- Paper framing, readiness, and publication-bundle generation.

### Explicitly out of scope for now

- Training new models from scratch.
- Claiming a new foundation model architecture.
- Claiming a complete theorem-backed statistics paper.
- Treating current answer-only math consensus as equivalent to code
  falsification.

## Benchmark scope

The repository currently supports these benchmark loaders:

| Benchmark | Type | Status |
| --- | --- | --- |
| `humaneval_plus` | code | core benchmark |
| `mbpp_plus` | code | core benchmark |
| `livecodebench_v6` | code | core benchmark |
| `math500` | math | supported, but selection currently consensus-based |
| `gsm8k` | math | supported, but selection currently consensus-based |
| `aime2024` | math | supported, but selection currently consensus-based |
| `aime2025` | math | supported, but selection currently consensus-based |
| `codecontests` | code | loader added; main paper runs still pending |

## Model scope

The project currently targets three main open-weight model families:

| Model | Role |
| --- | --- |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | small reasoning-oriented model |
| `Qwen/Qwen2.5-Coder-14B-Instruct` | medium code-specialized model |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` | strongest showcase model |

This 7B / 14B / 32B spread is enough to support a meaningful scaling story if
the results are clean.

## Baseline scope

### Baselines implemented inside the repository

| Baseline | Status | Interpretation |
| --- | --- | --- |
| `greedy` | complete | canonical floor |
| `majority_vote` | complete | agreement-based TTS baseline |
| `self_debug` | complete | lightweight local self-debug proxy |
| `generated_test_filter` | complete | one-shot generated-test baseline |
| `falsification` | complete | main method |
| `oracle` | complete | pass@N upper bound |
| `s_star` | complete as local proxy | not external SkyThought |
| `code_t` | complete as local proxy | not external Microsoft CodeT |
| `prm_best_of_n` | placeholder | not paper-ready |

### External baselines staged but not yet integrated

See `docs/external_baseline_status.md` for the current status of:

- SkyThought / S*
- Microsoft CodeT
- ThinkPRM
- AceCoder
- OpenR

These matter for a strong final paper, but they are not yet claimable as
completed external comparisons.

## Current strongest empirical story

The strongest current story is code-focused and has three parts.

## Important methodological correction

The repository's code-task `majority_vote` baseline has now been corrected to
cluster by public execution behavior rather than by raw candidate source text.
Older stored majority-vote numbers generated before this correction should be
treated as legacy rows until rerun.

### Part 1: Majority voting can fail badly

The current HumanEval+ rows show that majority vote can be dramatically worse
than stronger execution-guided selectors, especially on reasoning-oriented
models.

### Part 2: Falsification can recover most of the oracle gap

The strongest live and materialized HumanEval+ rows show falsification reaching
roughly 90% to 97% of oracle performance, depending on model and row state.

### Part 3: The self-debug comparison is still the hard question

The current project is not yet in a position to claim clean dominance over
self-debug. That comparison remains the main scientific and acceptance-critical
challenge.

## Current weakest points

### 1. Self-debug remains highly competitive

On several important rows, self-debug ties or slightly beats falsification.
This limits how aggressively the final paper can frame raw-accuracy novelty.

### 2. Generated-test-filter is acceptance-critical

If a simpler one-shot generated-test filter matches or beats falsification, the
sequential/adaptive story weakens significantly. This is why the Priority 1
audit and targeted reruns exist.

### 3. Math support is now valid but conservative

The repository recently removed oracle leakage from math selection. That fix was
necessary, but it means math rows should now be treated as supporting-scope
results until a real verifier or PRM is integrated.

### 4. Benchmark coverage is incomplete

Some rows still have:

- only one complete seed;
- only 100 problems where the target is 400 or 500;
- missing baseline columns;
- missing large-model coverage.

## Scientific posture of the project

The right scientific posture is:

- ambitious in infrastructure;
- strong in code-focused selection evidence;
- careful in statistical claims;
- explicit about what is still unresolved.

That posture is much safer for a strong main-track paper than trying to squeeze
every current asset into a single maximal claim.

## Paper-ready framing options

### Framing A: code-focused falsification paper

Best if Priority 1 reruns are favorable.

Core claim:

> Execution-grounded sequential falsification outperforms agreement-based
> selection and recovers most of the oracle gap on code generation benchmarks.

### Framing B: failure diagnosis + falsification

Best if falsification strongly beats majority vote but only ties self-debug.

Core claim:

> Agreement-based TTS fails on reasoning-oriented code models; sequential
> falsification is a practical execution-grounded alternative that recovers most
> of the oracle gap.

### Framing C: generated-test filtering + confidence

Best if generated-test filtering remains as strong as or stronger than
falsification.

Core claim:

> Generated-test filtering is an underexplored code-TTS baseline, and
> sequential falsification adds adaptive elimination and confidence analysis on
> top of that baseline surface.

## Concrete success criteria

The project becomes materially stronger for a main-track submission if it can
show all of the following:

- 3-seed clean HumanEval+ rows for 7B, 14B, and 32B;
- completed 32B LiveCodeBench and 32B MATH/GSM/AIME support rows;
- full 7B LiveCodeBench and fuller math coverage;
- generated-test-filter comparisons on the key code rows;
- at least some external-faithful baseline coverage;
- calibration artifacts computed from nontrivial benchmark slices;
- a final manuscript that does not rely on deprecated math-selection claims.

## Immediate project priorities

In order:

1. Finish acceptance-critical P1 code reruns.
2. Complete missing 32B code coverage rows.
3. Clean seed coverage to 3 seeds where targeted.
4. Backfill missing code baselines.
5. Only then broaden to more ablations, broader math, and full spotlight-style
   packaging.

## Related repository docs

- `docs/falsification_vs_self_debug.md`
- `docs/priority1_generated_filter_audit.md`
- `docs/math_verification_validity.md`
- `docs/reviewer_baseline_audit.md`
- `docs/novelty_audit_2026.md`
- `docs/external_baseline_status.md`

## Bottom line

This is already a serious and interesting project. The repository supports a
real code-generation test-time-scaling method, a meaningful baseline surface,
and several strong code results. What it does not yet support is a maximal
"everything is solved" claim. The strongest version of the project is the one
that keeps that distinction clear while continuing to push the code rows toward
cleaner headline evidence.
