# Project Requirements Document

Project: Sequential Candidate Elimination + Information-Theoretic TTS Capacity

Status: Active research

Target venue: NeurIPS 2026 main conference

Ambition: Main-track acceptance with spotlight-tier upside

Last updated: 2026-04-22

## Purpose

This document is the long-horizon execution plan for the repository. It is the
single planning document that ties together:

- the existing sequential falsification method;
- the broader "spotlight-tier" framing for a top conference submission;
- the theoretical extension toward information-theoretic TTS capacity;
- the experimental matrix required to move from poster-tier scope to
  spotlight-tier scope;
- the concrete near-term decisions the project must get right.

This document is deliberately more ambitious than
`docs/PROJECT_AIMS_SCOPE_OVERVIEW.md`. The overview doc describes what the
repository can honestly claim today. This PRD describes what we are trying to
build over the next phase of work.

## Executive summary

The project now has two compatible research tracks.

Track A: Sequential Candidate Elimination (SCE).

- Population-level, execution-grounded falsification for code generation.
- Generate a pool of candidates, synthesize separating probes, eliminate
  inconsistent candidates, and rank survivors using a confidence trace.
- This is the existing implemented method in the repository.

Track B: Information-theoretic TTS capacity.

- Define a reasoning-capacity quantity for a generator-verifier-problem triple.
- Prove that this quantity upper-bounds achievable test-time-scaling accuracy
  at a given compute budget.
- Show that adaptive verification procedures, with SCE as a concrete instance,
  are near-optimal protocols under that lens.

The intended high-level submission is not "an e-value paper." The intended
submission is a Track B capability paper:

> Anytime-valid, compute-aware test-time scaling for code generation.

In that framing:

- e-values are a mechanism;
- execution-grounded adaptive verification is the capability;
- SCE is the main empirical algorithmic instance;
- capacity theory is the unifying explanation.

Project decision as of 2026-04-22:

- Track B is the primary paper direction.
- Track A remains in the repository only as the main empirical adaptive
  protocol and validation engine.
- Method-only wins are still valuable, but they are no longer the terminal
  framing target.

## Core research questions

Primary questions:

- Is there a single information-theoretic quantity that upper-bounds TTS
  performance as a function of compute?
- Can that bound be matched, at least up to constants or log factors, by an
  adaptive verification protocol?
- Does SCE recover a large fraction of that optimal capacity in practice?
- Can we estimate verifier capacity from data tightly enough to predict TTS
  gains?

Secondary questions:

- Does survivor-conditioned population-consensus differential probing create a
  real empirical gap over non-adaptive generated-test filtering?
- Does SCE provide a confidence signal that is empirically calibrated enough to
  support selective prediction and risk control?
- Under what conditions does population-level elimination beat repair-based
  methods such as self-debug?

## Success criteria

Minimum acceptable outcome:

- SCE cleanly beats majority vote and compute-matched generated-test filtering
  on the strongest code rows.
- The confidence trace yields useful calibration artifacts.
- A capacity pilot shows meaningful spread across verifiers and benchmarks.

Target outcome:

- SCE ties or beats self-debug on the strongest acceptance-critical rows.
- Capacity estimates predict observed test-time-scaling gains reasonably well.
- The paper can lead with "anytime-valid compute-optimal TTS for code
  generation" rather than with "calibrated confidence via e-values."

Stretch outcome:

- A clean theorem+experiment story around puncturing a verification ceiling.
- A compute-matched Pareto figure that materially dominates multiple baselines.
- Enough breadth and clarity to be argued as a spotlight-tier submission.

## Current reality check

The repository already contains a serious code path and real results, but it is
not yet spotlight-ready.

What is already strong:

- Code-generation falsification is implemented end-to-end.
- Reviewer-facing baselines are present locally.
- The 32B HumanEval+ story is strong enough to justify continued work.
- The repo now has safer math validity boundaries and stronger majority-vote
  implementation.

What still blocks a strong main-track claim:

- SCE does not yet robustly beat self-debug across enough important rows.
- Generated-test-filter remains dangerously competitive on some MBPP+ settings.
- External baselines are staged but not fully integrated.
- Spotlight-tier breadth across six or seven benchmarks is not complete.
- The capacity theory track is not yet implemented.

## Immediate technical pivot

The main near-term method change is now explicit:

Population-consensus differential falsification.

Instead of treating differential probes as mostly reference-labeled generated
tests, the method now:

1. builds disagreement-inducing candidate inputs;
2. executes the survivor population on those inputs;
3. requires a supermajority-style consensus threshold;
4. ranks probes by pairwise disagreement plus consensus strength;
5. eliminates only the minority that disagrees with the consensus output.

This is the current best shot at creating a real structural gap over
single-candidate repair methods.

## Current active pilot jobs

As of 2026-04-22, the repository has two active Delta pilots directly targeting
the new architectural change:

- `2179176`: `headline_differential_r1_7b_mbpp`
- `2179179`: `headline_differential_r1_32b_humaneval`

These are one-seed pilot runs with:

- `N = 64`
- `temperature = 0.8`
- `n_rounds = 4`
- `max_tiebreak_rounds = 8`
- stronger differential probe budgets
- explicit consensus thresholds

These jobs are the immediate go/no-go test for whether the new population-based
mechanism materially improves the acceptance-critical rows.

## Research tracks

### Track A: Sequential Candidate Elimination

Scope:

- code generation;
- pool-level execution-based elimination;
- adaptive probe selection;
- confidence diagnostics and selective prediction;
- comparison to greedy, majority vote, generated-test filter, self-debug, and
  external-faithful baselines where possible.

Current claim hierarchy:

1. SCE beats majority vote on core code benchmarks.
2. SCE recovers much of the majority-vote-to-oracle gap.
3. SCE can outperform compute-matched non-adaptive filtering.
4. SCE can tie or beat self-debug.
5. SCE can match or beat stronger external baselines.

Only the lower levels of that hierarchy are safely supported today.

### Track B: Capacity theory

Scope:

- define a reasoning-capacity quantity for TTS;
- prove an upper bound on achievable accuracy at compute budget `B`;
- construct a matching or near-matching sequential protocol;
- place existing methods on a common capacity-fraction taxonomy;
- show SCE as a near-optimal adaptive verification protocol.

This track is not implemented yet, but it is the strongest route to a
spotlight-tier framing if the theorems land cleanly.

## Theoretical roadmap

The intended theorem stack is:

1. Adaptive survival bound for incorrect candidates.
2. E-process or approximate e-process control for wealth traces.
3. Family-wise false-rejection control across candidate pools.
4. Separation of adaptive survivor-conditioned elimination from non-adaptive
   filtering on a synthetic family.
5. Information-theoretic capacity upper bound for TTS protocols.
6. Matching or near-matching protocol via sequential likelihood-ratio style
   verification.
7. Capacity-fraction taxonomy for common methods.
8. Finite-sample capacity estimation guarantees.
9. SCE-as-optimal-instance corollary within an adaptive verification class.

The first few items are closest to the current codebase. The later items belong
to the broader Track B program and are best treated as a second-phase effort
after the feasibility pilot.

## Experimental breadth needed for a spotlight-tier attempt

Minimum breadth for serious contention:

- 6+ models preferred, 3 models minimum for Track A-only framing.
- 6+ benchmarks preferred, including at least:
  - HumanEval+
  - MBPP+
  - LiveCodeBench v6
  - CodeContests
  - GSM8K
  - AIME 2024/2025
- 6+ baselines with a clean story around which are local proxies and which are
  external-faithful.

Required baseline families:

- greedy
- majority vote / self-consistency
- generated-test filter
- self-debug
- CodeT-style agreement
- S*-style adaptive distinguishing
- PRM-based best-of-N
- oracle

Required ablations:

- candidate-count scaling
- falsification-round scaling
- probe-family decomposition
- sequential vs. one-shot compute-matched comparison
- calibration / confidence-mode ablation
- family-diversity scheduling ablation

## Immediate empirical priorities

In order:

1. Evaluate the live `N=64` differential-consensus pilots.
2. If they help, rerun the acceptance-critical matrix:
   - 7B HumanEval+
   - 7B MBPP+
   - 14B MBPP+
   - 32B HumanEval+
3. Clean all targeted headline rows to 3 seeds.
4. Backfill missing baseline columns on those rows.
5. Extend to broader code coverage:
   - 32B LiveCodeBench
   - CodeContests
6. Only after the code story is stronger, expand math breadth and capacity
   measurement.

## Capacity-theory feasibility pilot

Before committing to the full Track B proof-and-experiment program, run a
two-week feasibility pilot:

- estimate capacity-like verifier information on HumanEval+ and MBPP+;
- use at least three models and several verifier types;
- test whether the estimated quantity meaningfully varies across verifiers;
- test whether it correlates with realized TTS gains.

Go/no-go criterion:

- if the quantity is flat or nearly redundant with existing metrics, do not
  let Track B swallow the project;
- if it separates verifiers and predicts gains, Track B becomes the main paper
  direction.

## Writing and framing rules

If the current method story strengthens:

- lead with capability, not tool;
- say "anytime-valid compute-aware TTS for code generation";
- treat e-values as the mechanism, not the headline.

If method gains remain mixed:

- do not oversell raw pass@1 dominance;
- frame the paper around adaptive verification, compute-aware selection, and
  calibrated risk rather than universal wins;
- be explicit about which baselines are local proxies.

If Track B matures:

- title and abstract should foreground the capacity result;
- SCE becomes the constructive adaptive protocol that validates the theory.

## Risks

Main scientific risks:

- population-consensus differential probes still fail to separate from strong
  simpler baselines;
- capacity theory only yields a loose or non-adaptive upper bound;
- calibration is useful but not strong enough to be "free" in the empirical
  sense.

Main operational risks:

- Delta billing-minute and queue friction;
- benchmark breadth outruns the available GPU budget;
- external baselines take longer to integrate than expected.

## Decision tree

If the active pilots improve the key rows:

- keep pushing Track A aggressively;
- use the stronger method as the empirical core for Track B.

If the active pilots do not improve the key rows:

- stop trying to force a method-dominance narrative;
- either pivot to a narrower Track A phenomenon paper or move the repository
  into Track B mode where SCE is mainly a validation vehicle.

If Track B feasibility is weak:

- do not over-invest in theory for theory's sake;
- ship the best honest method paper or phenomenon paper the code supports.

## Deliverables checklist

Method-track deliverables:

- clean 3-seed main table on core code benchmarks;
- compute-matched comparison against generated-test filtering;
- external baseline status made explicit;
- calibration and selective prediction figures;
- publication bundle regenerated from final runs.

Theory-track deliverables:

- `src/capacity.py`
- `src/matching.py`
- verifier adapters
- capacity pilot artifacts
- theorem appendix draft
- revised paper framing around capacity and compute-aware TTS

## Related docs

- `docs/PROJECT_AIMS_SCOPE_OVERVIEW.md`
- `docs/METHODS_DETAILED.md`
- `docs/RESULTS_DETAILED_UP_TO_NOW.md`
- `docs/falsification_vs_self_debug.md`
- `docs/priority1_generated_filter_audit.md`
- `docs/external_baseline_status.md`
- `docs/novelty_audit_2026.md`

## Changelog

- v0.1: Initial PRD added to repository, consolidating Track A method execution,
  Track B capacity-theory ambition, spotlight-tier breadth requirements, and
  the active 2026-04-22 pilot status.
