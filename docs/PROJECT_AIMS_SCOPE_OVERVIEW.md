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

The project is now centered on Track B: a compute-aware, information-theoretic
view of test-time scaling, with sequential falsification serving as the main
adaptive verification protocol used to validate that theory on code generation.

## Longer project thesis

The target paper is now a Track B paper about information, compute, and
verification in test-time scaling. The central question is:

- how much useful information about correctness does a verifier extract from a
  candidate pool, and how well does that information predict achievable
  selection accuracy under a fixed compute budget?

Sequential falsification remains in the repository because it is the strongest
adaptive execution-grounded verifier currently implemented here, but it is no
longer the paper's main identity. It is one verifier surface inside a larger
capacity program alongside:

- execution-output majority clustering;
- public-test verification;
- future PRM and judge-based verifier surfaces;
- a matching protocol that should approximate the information-theoretic ceiling.

The intended scientific story is therefore:

1. define a benchmark- and model-dependent verifier capacity;
2. estimate it from data;
3. show that capacity predicts selector performance and oracle gap closure;
4. use adaptive execution-grounded verification as one strong empirical
   instantiation of a high-capacity verifier.

That framing is much closer to a headline Track B result than a narrow method
paper about one adaptive elimination loop.

## Main project goals

### Goal 0: Make Track B the paper

The repository is no longer being organized around a standalone falsification
method paper.

Instead, the target submission is:

- a Track B paper about capacity, compute-aware TTS, and verifier information;
- with sequential falsification retained as the strongest empirical adaptive
  protocol currently implemented in the repo.

### Goal 1: Measure verifier capacity cleanly

The first goal is to estimate how informative each verifier is about hidden
correctness on a fixed benchmark/model pair. The current Track B stack focuses
on three primary verifier surfaces:

- execution-output majority clustering;
- public-test execution;
- SCE-trace adaptive execution verification.

The immediate objective is not just ranking these qualitatively, but measuring
their capacity numerically and attaching uncertainty to that estimate.

### Goal 2: Predict selector performance from verifier information

Track B only becomes compelling if the information quantity predicts something
real. So the second goal is to line up:

- pool oracle accuracy;
- verifier capacity;
- observed selector accuracy;
- the gap between predicted and observed performance.

That is the bridge from theory object to headline empirical result.

### Goal 3: Build a benchmark-aware, reproducible experimental stack

The project is also a systems build:

- benchmark loaders for EvalPlus, LiveCodeBench, and answer-only math sets;
- unified evaluation for function-completion and stdin/stdout code tasks;
- cluster launchers for DeltaAI and Anvil;
- reporting, readiness audits, and publication-bundle generation.

### Goal 4: Use adaptive verification as the strongest empirical instantiation

Sequential falsification is still valuable here, but as a means rather than the
paper destination. Its role in Track B is:

- serve as the adaptive verifier with the richest execution signal;
- test whether adaptive verification actually yields larger measured capacity;
- anchor the empirical "high-capacity verifier" part of the theory paper.

### Goal 5: Expand breadth toward headline Track B evidence

Headline Track B results need more than one model and one benchmark. The repo
is therefore moving toward:

- 7B / 14B / 32B code-model coverage for the code-primary capacity pilot;
- LiveCodeBench and code-style breadth after HE+/MBPP+;
- math-scope pilots only after the code capacity story is materially stronger.

## Active Track B wave

The current active DeltaAI capacity jobs are:

- `2179462` `capacity_code_primary`
- `2179463` `capacity_code_mid`
- `2179464` `capacity_code_large`

These are the current headline Track B pilot jobs and supersede the older
stale-path capacity submissions that were cancelled.

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

1. Finish the live differential-consensus pilots and decide whether the new
   architecture is strong enough to keep as the Track B empirical core.
2. Build Track B infrastructure: verifiers, capacity estimation, and matching.
3. Run the first capacity pilot on core code benchmarks.
4. Expand benchmark and baseline breadth in service of the Track B story.
5. Treat method-only reruns as support work, not as the main project.

## Active status

As of 2026-04-22, the repository has two live Delta pilots testing the new
population-consensus differential path:

- `2179176`: `headline_differential_r1_7b_mbpp`
- `2179179`: `headline_differential_r1_32b_humaneval`

These are the immediate decision point for whether the new architecture
materially improves the acceptance-critical rows.

## Related repository docs

- `docs/falsification_vs_self_debug.md`
- `docs/priority1_generated_filter_audit.md`
- `docs/math_verification_validity.md`
- `docs/reviewer_baseline_audit.md`
- `docs/novelty_audit_2026.md`
- `docs/external_baseline_status.md`
- `docs/PROJECT_REQUIREMENTS_DOCUMENT.md`

## Bottom line

This is already a serious and interesting project. The repository supports a
real code-generation test-time-scaling method, a meaningful baseline surface,
and several strong code results. What it does not yet support is a maximal
"everything is solved" claim. The strongest version of the project is the one
that keeps that distinction clear while continuing to push the code rows toward
cleaner headline evidence.
