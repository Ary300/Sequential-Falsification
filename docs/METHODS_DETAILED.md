# Sequential Falsification: Detailed Methods

## Purpose of this document

This file is the detailed methods reference for the repository. It is meant to
be much more explicit than the paper draft and much more stable than scattered
commentary in issues, commits, or chat logs.

It describes:

- how candidates are generated;
- how probes are built;
- how falsification proceeds round by round;
- how baselines are implemented locally;
- how benchmarks are loaded and evaluated;
- how math tasks are handled after the oracle-leakage fix;
- how calibration metrics are computed;
- how cluster execution is organized.

Where appropriate, this file also explains why the implementation takes a given
form and what the current limitations are.

## Conceptual overview

Sequential falsification is a population-level selection procedure.

Instead of:

- generating one candidate,
- debugging that candidate,
- and iteratively revising it,

the repository's main method:

- generates many candidates,
- probes the candidate population with benchmark-safe tests,
- eliminates inconsistent candidates,
- and finally selects from the survivors.

This distinction matters because the intended advantage comes from *selection
from diversity*, not from incremental repair of a single draft.

## Repository-level method components

The method is spread across several core files:

| File | Role |
| --- | --- |
| `src/generate.py` | candidate generation |
| `src/falsify.py` | probe construction, sequential elimination, confidence traces |
| `src/baselines.py` | comparison baselines |
| `src/evaluate.py` | end-to-end benchmark execution |
| `src/utils/sandbox.py` | code execution and benchmark scoring |
| `src/utils/data_loading.py` | benchmark loading and normalization |
| `src/utils/metrics.py` | accuracy, calibration, selective prediction metrics |
| `src/selection.py` | final candidate selection logic |

## Candidate generation

### Generation backends

The repository supports multiple backends:

- `mock`
- `echo`
- `openai`-compatible API serving
- `transformers`

In practice, the important cluster backends are:

- a local OpenAI-compatible inference stack on DeltaAI;
- direct `transformers` execution on Anvil when `vllm` is inconvenient.

### Generation interface

Candidate generation is configured through `GenerationConfig` in
`src/generate.py` and exposed through `generate_candidates(problem, n, config)`.

The generation step is benchmark-aware:

- code prompts preserve function-completion structure when appropriate;
- stdin/stdout competitive-programming tasks are prompted as full Python
  programs;
- math prompts ask for final-answer-only output.

### Math output normalization

For math tasks, generated text is normalized by:

- stripping markdown fences;
- extracting the last `\boxed{...}` answer if present;
- otherwise taking the last non-empty line.

This normalization is important because answer-only evaluation is otherwise too
brittle.

## Benchmark loading and normalization

### Supported benchmark families

`src/utils/data_loading.py` currently supports:

- `humaneval_plus`
- `mbpp_plus`
- `livecodebench_v6`
- `math500`
- `gsm8k`
- `aime2024`
- `aime2025`
- `codecontests`
- local benchmark files under `data/`

### Normalized problem format

All problems are normalized into a common dictionary structure with fields such
as:

- `id`
- `benchmark`
- `type`
- `prompt`
- `difficulty`
- `entry_point`
- `reference_solution`
- `reference_answer`
- `public_tests`
- `hidden_tests`

This normalization is what allows the same evaluation and selection machinery
to work across multiple benchmark families.

### Code benchmark normalization

For code tasks:

- function-completion tasks preserve `entry_point`;
- stdin/stdout tasks store tests as stdin/output examples and do not require an
  entry point;
- when available, `reference_solution` is used only to label generated probe
  inputs, not to score candidate outputs directly.

### Math benchmark normalization

For math tasks:

- `reference_answer` is stored for final evaluation and oracle scoring;
- there are no executable public or hidden tests in the usual code sense;
- selection now explicitly avoids calling answer checks during deployable
  methods.

## Code execution and evaluation

### Execution paths

`src/utils/sandbox.py` exposes benchmark-aware execution:

- `run_code_test(...)` for function-completion tasks;
- `run_code_stdin_test(...)` for stdin/stdout tasks;
- `execute_code_function(...)` for direct reference-solution execution when
  labeling generated probe inputs;
- `execute_stdin_program(...)` for raw program execution.

### Public vs hidden evaluation

`evaluate_candidate(problem, code, use_hidden=...)` is the core scoring entry
point.

For code tasks:

- `use_hidden=False` evaluates on public tests only;
- `use_hidden=True` evaluates on public plus hidden tests.

For math tasks after the validity fix:

- `use_hidden=False` returns a `no_public_oracle` result with zero public tests;
- `use_hidden=True` compares the normalized candidate answer to
  `reference_answer`.

This was a deliberate change to eliminate answer leakage from selection.

## Falsification configuration

`FalsificationConfig` in `src/falsify.py` defines the main method's control
surface.

Important fields:

| Field | Meaning |
| --- | --- |
| `n_rounds` | main falsification rounds |
| `max_tiebreak_rounds` | extra differential-only rounds after ambiguity remains |
| `delta` | testing-inspired per-round false-alarm proxy |
| `timeout` | execution timeout |
| `alpha` | confidence calibration parameter |
| `probe_strategy` | probe family regime |
| `adaptive_probe_selection` | adaptive or first-usable probe choice |
| `eliminate_on_detection` | whether detected candidates are eliminated |
| `confidence_mode` | `wealth`, `survival_only`, or `none` |
| `max_*_probes` | family-specific probe bank caps |
| `consensus_min_fraction` | minimum fraction needed for unlabeled consensus elimination |
| `consensus_min_margin` | minimum gap between top two outputs for unlabeled consensus elimination |
| `consensus_min_votes` | minimum absolute votes required for unlabeled consensus elimination |
| `allow_hidden_test_probes` | disabled by default |
| `enforce_round_family_diversity` | whether rounds target different families |

## Probe families

The probe bank is the heart of the method.

### 1. Public test probes

These are benchmark-provided tests copied directly from `public_tests`.

Role:

- provide the most conservative initial filtering signal;
- serve as the starting point for mutation and edge-case generation.

Limitation:

- public tests alone are too weak to justify the project's main claims.

### 2. Mutation probes

Mutation probes take public test inputs and perturb them.

Examples:

- increment or decrement integers;
- flip sign;
- double values;
- mutate strings;
- perturb list structure;
- reverse argument order in simple cases.

These probes are labeled by executing the benchmark's `reference_solution` on
the mutated input.

Important limitation:

- stdin/stdout tasks currently skip this path because safe structured mutation
  for arbitrary competitive-programming input formats is not yet implemented.

### 3. Edge-case probes

Edge-case probes systematically move inputs toward likely failure boundaries.

Examples:

- zero, one, minus one;
- empty strings or empty lists;
- singleton lists;
- reversed lists;
- duplicated short strings;
- sign and magnitude boundaries.

Like mutation probes, they are labeled through the benchmark reference
solution.

### 4. Random-stress probes

Random-stress probes generate plausible perturbed inputs using a deterministic
seed derived from the underlying input.

Purpose:

- broaden coverage beyond hand-crafted edge cases;
- inject extra diversity into the probe bank;
- serve as a third round family distinct from edge cases and mutations.

### 5. Differential probes

Differential probes are the most distinctive family in the current
implementation, and they now lean much harder on the candidate population
itself.

Current procedure:

1. Enumerate candidate inputs derived from public tests.
2. Execute the current surviving candidate pool on those candidate inputs.
3. Keep only inputs on which the survivor pool actually disagrees.
4. Require a supermajority-style consensus on the output before elimination.
5. Eliminate the minority candidates that disagree with the consensus output.

The implementation records, for each candidate differential input:

- output diversity;
- consensus fraction;
- consensus margin over the runner-up output;
- pairwise disagreement count across the survivor population.

Those statistics are then used to rank the differential bank so late-round
budget is spent on probes that separate many candidate pairs while still having
a stable consensus anchor.

This is the structural mechanism self-debug cannot use: the signal comes from
cross-candidate disagreement and survivor-population consensus, not from
iteratively repairing a single draft.

## Probe strategy modes

The repository supports multiple strategy regimes through
`probe_strategy`.

### `adaptive_population`

The default and intended main method.

Enabled families:

- public
- mutation
- edge_case
- random_stress
- differential

This is the most faithful implementation of the paper's intended method.

### `generated_only`

A non-public generated-probe regime used mainly for compute-matched comparisons
against generated-test filtering.

### Single-family ablations

Available as:

- `public_only`
- `mutation_only`
- `edge_case`
- `random_stress`
- `differential_only`

These are useful for ablations and for understanding whether gains come from a
single family or from family diversity.

## Round-family diversity schedule

One of the most important recent fixes is explicit round-family diversity.

For the main adaptive path, the default schedule is:

1. `edge_case`
2. `mutation`
3. `random_stress`
4. `differential`

If more rounds exist, the schedule cycles.

Why this matters:

- without it, sequential rounds could repeatedly choose near-duplicate probes;
- that makes falsification empirically collapse toward one-shot generated-test
  filtering;
- the acceptance-critical generated-test-filter comparison motivated this fix.

## Probe scoring and selection

### High-level logic

At each round, the method considers unused probes and chooses one that best
separates the current survivor pool.

The core routine is `_choose_best_probe(...)`.

### Labeled probes

For probes with known outputs:

- each candidate is executed on the probe;
- a candidate is marked detected if it fails the probe;
- probes that detect nobody or everybody are ignored;
- informative probes are scored by:
  - number detected;
  - output diversity;
  - novelty bonus for non-public families;
  - number of survivors retained.

### Unlabeled / consensus probes

For probes without explicit labels:

- candidates are executed;
- the code computes consensus fraction, consensus margin, and pairwise
  disagreement count;
- only probes with sufficiently strong consensus are considered safe enough for
  elimination;
- if no sufficiently strong consensus exists, the probe is ignored.

This is mostly relevant for survivor-conditioned disagreement checks.

## Sequential elimination

### Candidate record structure

Each candidate becomes a record with fields such as:

- `candidate_order`
- `survived`
- `rejected`
- `wealth`
- `confidence`
- `selection_score`
- `rounds_survived`
- `trace`

### Main elimination loop

For each round:

1. choose a probe against the current survivor pool;
2. execute the pool on that probe;
3. compute per-candidate detection flags;
4. update the confidence trace;
5. eliminate detected candidates if `eliminate_on_detection=True`.

### Tiebreak rounds

If ambiguity remains after the main round budget, the method can spend extra
compute on differential-only tiebreak rounds.

These are important because they preserve the falsification framing:

- they do not repair candidates;
- they continue to challenge the remaining pool;
- they are only used when ambiguity remains.

## Confidence and selection score

### Current status

The repository's confidence score is explicitly empirical and conservative.

It is inspired by testing-by-betting and e-values, but the code does **not**
currently claim a fully justified anytime-valid correctness guarantee.

### E-value-inspired trace

Each round uses:

- `compute_e_value(...)`
- `estimate_detection_probability(...)`
- multiplicative wealth updates.

This produces a `wealth` trace for each candidate.

### Important caveat

If a candidate has no actual falsification trace, the repository now forces the
base confidence contribution to zero. This prevents no-probe cases, especially
for math tasks, from receiving artificial high confidence merely from
initialization.

### Selection score components

For surviving candidates, the final score may combine:

- calibrated-confidence proxy;
- public-test score;
- trace strength;
- exclusivity bonus when few survivors remain.

Weights:

- confidence: `0.55`
- public score: `0.35`
- trace strength: `0.10`

These can be changed through config if needed.

## Math handling after the validity fix

### What was wrong before

Older math falsification used answer checks during selection. That is oracle
leakage.

### What happens now

For math tasks:

- `_build_probe_bank(...)` returns no answer-check probes;
- public evaluation does not compare against `reference_answer`;
- falsification uses answer agreement among candidates as a fallback signal;
- oracle and final evaluation still use `reference_answer`.

### Consequence

Math rows are now scientifically safer, but less ambitious:

- they are valid evaluation rows;
- they are not yet strong evidence for adversarial falsification;
- they need a verifier, PRM, or symbolic-check layer before the paper should
  make stronger math claims.

## Baselines in detail

### Greedy

Select the first candidate and evaluate it on hidden tests.

Purpose:

- canonical floor;
- sanity check for whether test-time scaling helps at all.

### Majority vote

For code tasks, cluster by public execution behavior and pick the largest
cluster. For math tasks, cluster by normalized final answer text.

For code, the execution signature is derived from the public-test details:

- pass/fail status per test;
- observed output when available;
- stdout fallback for stdin/stdout tasks.

Purpose:

- canonical agreement-based selection baseline.

### Self-debug

The local self-debug implementation is intentionally lightweight:

1. evaluate the first candidate on public tests;
2. if it passes, keep it;
3. otherwise search later candidates for one that passes public tests;
4. evaluate the selected candidate on hidden tests.

Important note:

- this is a local executable proxy, not an attempt to exactly reproduce every
  self-debug paper's procedure.

### Generated-test filter

This baseline is crucial because it isolates the value of adaptivity.

Procedure:

1. build a one-shot generated probe bank;
2. exclude raw public probes;
3. choose a family-balanced subset;
4. filter candidates once;
5. select from survivors.

Key design choice:

- default budget is compute-matched to the main falsification recipe.

### S* proxy

This is a local adaptive-elimination proxy inspired by S*.

It:

- uses adaptive elimination;
- removes the calibrated-ranking layer;
- is executable locally.

It is **not** the external SkyThought implementation.

### CodeT proxy

This is a local agreement-scoring proxy inspired by CodeT.

It:

- builds generated and differential probes;
- scores candidates by agreement across those probes;
- selects the highest-scoring candidate.

It is **not** the external Microsoft CodeT implementation.

### Oracle

The oracle baseline simply asks whether any candidate passes hidden evaluation.

Purpose:

- upper bound on candidate-pool quality;
- denominator for oracle-gap recovery analysis.

## End-to-end evaluation

`src/evaluate.py` orchestrates:

1. benchmark loading;
2. candidate generation;
3. method execution;
4. pass@k computation;
5. summary statistics;
6. calibration metrics;
7. progress checkpointing.

Important outputs include:

- per-problem method decisions;
- pass@k estimates;
- benchmark summaries;
- calibration bins;
- selective prediction curves.

## Metrics

The current metrics layer includes:

- accuracy;
- pass@k;
- expected calibration error (ECE);
- maximum calibration error (MCE);
- Brier score;
- AUROC;
- selective prediction curves.

These are mainly used as descriptive diagnostics rather than as the basis for a
formal theorem claim.

## Cluster execution model

### DeltaAI

Delta is currently the main live large-run path.

Important files:

- `slurm/delta/full_experiment_delta.sbatch`
- `scripts/submit_delta_*`

### Anvil

Anvil is used as a clean rerun path and for some ablation/coverage work.

Important files:

- `slurm/anvil_full_experiment.sbatch`
- `scripts/submit_anvil_*`

### Progress and recovery

Runs write seed-level progress JSON files. This is critical because:

- long runs can time out or be interrupted;
- reporting can be reconstructed from progress even when final merge jobs do
  not complete;
- the paper bundle can therefore be updated from partially materialized runs.

## Recent method corrections

The most important recent corrections are:

1. explicit round-family diversity;
2. compute-matched generated-test-filter baseline;
3. math oracle-leakage removal;
4. alpha/delta/timeout wiring through configs and SLURM launchers;
5. oracle-leakage audits added to the repository.

These changes matter because they affect not just code quality, but the
scientific validity of the final claims.

## Known limitations

### 1. Self-debug comparison remains hard

The method is conceptually distinct from self-debug, but the empirical
separation is not yet consistently strong enough across all rows.

### 2. External baselines are not yet fully integrated

The local proxy baselines are useful, but they are not a substitute for final
external-faithful comparisons.

### 3. Math falsification is not yet mature

Math support is valid but conservative. It should not yet carry the main paper
story.

### 4. Probe quality for stdin/stdout tasks is still less expressive

Reference-labeled structured mutation is easier for function-completion tasks
than for arbitrary stdin/stdout programs.

## Recommended reading alongside this file

- `docs/falsification_vs_self_debug.md`
- `docs/priority1_generated_filter_audit.md`
- `docs/math_verification_validity.md`
- `docs/external_baseline_status.md`

## Bottom line

Methodologically, the repository now implements a real population-level
falsification system for code generation. It is more than majority vote, more
than public-test filtering, and different in kind from self-debug. The remaining
question is no longer whether a method exists, but whether the full benchmark
matrix will show that this method is strong enough, often enough, to carry the
final paper's headline claim.
