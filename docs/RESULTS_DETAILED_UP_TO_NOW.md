# Sequential Falsification: Detailed Results Snapshot

## Purpose of this document

This file is the detailed results ledger for the repository *as of the current
state of the project*. It is designed to be explicit about three things:

- which rows are materially available right now;
- which rows are valid but partial or provisional;
- which older rows should no longer be used as primary evidence.

This is intentionally not a polished camera-ready results section. It is a
working research snapshot.

It also predates the newer population-consensus differential upgrade in
`src/falsify.py`. Any forthcoming reruns with stronger supermajority-style
differential elimination should be treated as a new methodological generation,
not as minor noise around the rows below.

## Important baseline note

As of the current code state, `majority_vote` on code tasks has been corrected
to cluster candidates by **execution behavior on the public test slice** rather
than by raw source-text identity. That means many older stored majority-vote
rows in `paper/generated/*` and historical result bundles should be treated as
**legacy text-cluster majority rows** until they are rerun with the corrected
baseline.

## How to read this file

### Row states

- **Materialized**: a row exists as a local results artifact and can be cited
  directly.
- **Live monitored**: a row is visible through progress files / cluster checks
  but is not yet the final frozen publication row.
- **Partial coverage**: the row exists, but benchmark size is smaller than the
  target benchmark size.
- **Deprecated for falsification claims**: older math-selection rows from before
  the oracle-leakage fix should not be used as evidence for adversarial
  falsification.

### Validity policy

After the recent math fix:

- code benchmark rows remain the main falsification evidence;
- math benchmark rows are valid evaluation rows, but should currently be
  interpreted as consensus-based supporting scope unless a real verifier is
  added.

## Source artifacts used for this snapshot

Primary local sources:

- `paper/generated/publication_main_table_ready.tex`
- `paper/generated/neurips_readiness_ready.md`
- `paper/generated/publication_method_coverage_ready.md`
- `results/*/results.json`
- `results/*/results_from_progress.json`

Additional live monitoring note:

- the active Delta 32B HumanEval+ generated-test-filter / self-debug /
  falsification run was manually checked on 2026-04-22 and is included below as
  a live monitored row.

## Table A: Current materialized benchmark matrix

This table summarizes the strongest materialized rows currently available in the
local repository bundle. Values are percentages.

| Model | Method | HumanEval+ | LiveCodeBench v6 | Math500 | MBPP+ | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-Coder-14B | greedy | 27.4 | -- | 22.7 +- 0.33 | 70.5 +- 0.38 | HumanEval row materialized as single-seed local ready row |
| Qwen2.5-Coder-14B | majority vote | 23.2 | -- | 24.1 +- 0.13 | 71.6 +- 0.32 |  |
| Qwen2.5-Coder-14B | generated-test filter | -- | -- | 34.3 +- 0.67 | -- | math row exists but should be treated conservatively |
| Qwen2.5-Coder-14B | self-debug | 43.9 | -- | 34.3 +- 0.67 | 75.2 +- 0.35 |  |
| Qwen2.5-Coder-14B | falsification | 43.9 | -- | 34.3 +- 0.67 | 75.1 +- 0.26 |  |
| Qwen2.5-Coder-14B | oracle | 45.7 | -- | 34.3 +- 0.67 | 80.3 +- 0.18 |  |
| DeepSeek-R1-Distill-Qwen-32B | greedy | 44.5 | -- | -- | 31.0 +- 0.31 | HumanEval row materialized as single-seed local ready row |
| DeepSeek-R1-Distill-Qwen-32B | majority vote | 29.9 | -- | -- | 30.8 +- 0.32 |  |
| DeepSeek-R1-Distill-Qwen-32B | self-debug | 82.3 | -- | -- | 64.6 +- 1.50 |  |
| DeepSeek-R1-Distill-Qwen-32B | falsification | 82.9 | -- | -- | 64.4 +- 1.63 | strongest materialized code row in local ready bundle |
| DeepSeek-R1-Distill-Qwen-32B | oracle | 84.8 | -- | -- | 66.8 +- 1.23 |  |
| DeepSeek-R1-Distill-Qwen-7B | greedy | 34.8 | 3.0 +- 0.00 | 11.7 +- 2.33 | 11.2 +- 0.35 | LiveCodeBench and math rows are partial-coverage |
| DeepSeek-R1-Distill-Qwen-7B | majority vote | 32.9 | 3.0 +- 0.00 | 23.0 +- 2.08 | 10.8 +- 0.23 |  |
| DeepSeek-R1-Distill-Qwen-7B | self-debug | 72.6 | -- | -- | 33.8 +- 1.04 |  |
| DeepSeek-R1-Distill-Qwen-7B | falsification | 70.7 | 8.0 +- 0.00 | 33.7 +- 1.67 | 33.8 +- 1.04 | HumanEval row is weaker than self-debug |
| DeepSeek-R1-Distill-Qwen-7B | oracle | 74.4 | 8.0 +- 0.00 | 33.7 +- 1.67 | 34.8 +- 1.28 |  |

## Table B: Acceptance-critical comparisons from the materialized matrix

This table isolates the comparisons reviewers will care about most.

| Model | Benchmark | Majority | Generated-test filter | Self-debug | Falsification | Oracle | F recovery | F - SD | F - GTF |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-Coder-14B | HumanEval+ | 23.2 | -- | 43.9 | 43.9 | 45.7 | 92.0% | 0.0 | -- |
| Qwen2.5-Coder-14B | MBPP+ | 71.6 | -- | 75.2 | 75.1 | 80.3 | 40.2% | -0.1 | -- |
| Qwen2.5-Coder-14B | Math500 | 24.1 | 34.3 | 34.3 | 34.3 | 34.3 | 100.0% | 0.0 | 0.0 |
| DeepSeek-R1-Distill-Qwen-32B | HumanEval+ | 29.9 | -- | 82.3 | 82.9 | 84.8 | 96.5% | +0.6 | -- |
| DeepSeek-R1-Distill-Qwen-32B | MBPP+ | 30.8 | -- | 64.6 | 64.4 | 66.8 | 93.3% | -0.2 | -- |
| DeepSeek-R1-Distill-Qwen-7B | HumanEval+ | 32.9 | -- | 72.6 | 70.7 | 74.4 | 91.1% | -1.9 | -- |
| DeepSeek-R1-Distill-Qwen-7B | MBPP+ | 10.8 | -- | 33.8 | 33.8 | 34.8 | 95.8% | 0.0 | -- |
| DeepSeek-R1-Distill-Qwen-7B | LiveCodeBench v6 | 3.0 | -- | -- | 8.0 | 8.0 | 100.0% | -- | -- |
| DeepSeek-R1-Distill-Qwen-7B | Math500 | 23.0 | -- | -- | 33.7 | 33.7 | 100.0% | -- | -- |

## Immediate interpretation of Table B

### What is strong

- The 32B HumanEval+ row is genuinely strong.
- The 7B and 32B MBPP+ rows recover most of the oracle gap from majority vote.
- The 7B LiveCodeBench row, while small in absolute value, shows a real gain
  over greedy and majority vote on the corrected stdin/stdout path.

### What is weak

- Falsification does not cleanly beat self-debug on most materialized rows.
- 14B MBPP+ is especially awkward because falsification is only slightly above
  majority vote relative to the oracle and slightly below self-debug.
- Generated-test-filter coverage is still sparse in the materialized bundle.

## Table C: Live monitored Delta row (2026-04-22 check)

The strongest live code result currently being monitored is the DeltaAI
32B HumanEval+ generated-test-filter comparison. This row is important because
it is closer to the actual paper-quality narrative than the older one-seed
materialized row.

### Seed-level status from the live check

| Seed | Completed problems | Greedy | Majority | GTF | Self-debug | Falsification | Oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 164 / 164 | 40.9 | 31.1 | 70.7 | 82.9 | 84.1 | 87.8 |
| 43 | 164 / 164 | 41.5 | 31.7 | 70.7 | 81.7 | 83.5 | 83.5 |
| 44 | 72 / 164 | 34.7 | 16.7 | 68.1 | 80.6 | 80.6 | 81.9 |

### Provisional interpretation

- On the two completed seeds, falsification is above generated-test filter by a
  wide margin.
- On the two completed seeds, falsification is also above self-debug.
- If the third seed stays close, this will be the strongest evidence yet that
  the corrected adaptive falsification path is doing something materially
  better than one-shot generated-test filtering on a flagship row.

This row is still **live monitored**, not yet frozen as the final publication
bundle row.

## Table D: Baseline coverage by current row

This table records which core baselines are actually present in the current
bundle.

| Model | Benchmark | Problems | Complete seeds | Core baselines present | Missing core baselines |
| --- | --- | ---: | ---: | --- | --- |
| Qwen2.5-Coder-14B | HumanEval+ | 164 | 1 | greedy, majority, self-debug, falsification, oracle | generated-test filter |
| Qwen2.5-Coder-14B | MBPP+ | 378 | 3 | greedy, majority, self-debug, falsification, oracle | generated-test filter |
| Qwen2.5-Coder-14B | Math500 | 500 | 0 | greedy, majority, generated-test filter, self-debug, falsification, oracle | none |
| DeepSeek-R1-Distill-Qwen-32B | HumanEval+ | 164 | 1 | greedy, majority, self-debug, falsification, oracle | generated-test filter |
| DeepSeek-R1-Distill-Qwen-32B | MBPP+ | 378 | 3 | greedy, majority, self-debug, falsification, oracle | generated-test filter |
| DeepSeek-R1-Distill-Qwen-7B | HumanEval+ | 164 | 1 | greedy, majority, self-debug, falsification, oracle | generated-test filter |
| DeepSeek-R1-Distill-Qwen-7B | LiveCodeBench v6 | 100 | 1 | greedy, majority, falsification, oracle | generated-test filter, self-debug |
| DeepSeek-R1-Distill-Qwen-7B | Math500 | 100 | 3 | greedy, majority, falsification, oracle | generated-test filter, self-debug |
| DeepSeek-R1-Distill-Qwen-7B | MBPP+ | 378 | 3 | greedy, majority, self-debug, falsification, oracle | generated-test filter |

## Table E: Coverage gaps in the target matrix

This table summarizes what is still incomplete relative to the intended main
paper matrix.

| Model | HumanEval+ | MBPP+ | LiveCodeBench v6 | Math500 | Main issue |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-R1-Distill-Qwen-7B | partial seed-clean | complete | partial coverage | partial coverage, conservative interpretation | weak HumanEval self-debug gap |
| Qwen2.5-Coder-14B | partial seed-clean | complete | missing | immature / conservative interpretation | 14B code matrix incomplete |
| DeepSeek-R1-Distill-Qwen-32B | partial seed-clean but strongest | complete | missing | missing / conservative interpretation | missing 32B breadth |

## Deprecated and caveated rows

### Math rows before the validity fix

Older math-selection behavior used answer checks during selection and should not
be used as primary evidence for adversarial falsification. After the fix:

- math final evaluation remains valid;
- math oracle remains valid;
- math deployable selection is now consensus-based unless a real verifier is
  integrated.

### Proxy baseline rows

Rows produced by local `s_star` and `code_t` implementations are useful for
engineering comparison, but should be labeled as **local proxies** rather than
external-faithful comparisons.

## What the current results already support

### Supported now

- majority-vote failure on important code rows;
- strong oracle-gap recovery on the best HumanEval+ and MBPP+ rows;
- a meaningful corrected LiveCodeBench path for stdin/stdout tasks;
- a serious baseline and readiness surface.

### Not yet supported cleanly enough

- universal superiority over self-debug;
- universal superiority over generated-test filtering;
- final spotlight-style breadth across six or seven benchmarks with complete
  seed coverage.

## Current headline rows

If someone asked, "what are the best rows right now?" the most honest answers
are:

1. **Live monitored 32B HumanEval+**
   - majority around 31
   - falsification around 84
   - oracle around 84 to 88
   - generated-test filter around 71
   - self-debug around 82

2. **Materialized 32B HumanEval+**
   - majority 29.9
   - falsification 82.9
   - self-debug 82.3
   - oracle 84.8

3. **Materialized 14B MBPP+**
   - majority 71.6
   - falsification 75.1
   - self-debug 75.2
   - oracle 80.3

4. **Materialized 32B MBPP+**
   - majority 30.8
   - falsification 64.4
   - self-debug 64.6
   - oracle 66.8

5. **Materialized 7B LiveCodeBench v6, 100 problems**
   - greedy 3.0
   - majority 3.0
   - falsification 8.0
   - oracle 8.0

## Acceptance-critical open questions

The following questions still determine the paper's eventual tier.

### 1. Does falsification separate from generated-test filtering?

This is why the Priority 1 reruns exist. The live 32B HumanEval+ row is
promising, but the key MBPP and 7B HumanEval rows still need clean resolution.

### 2. Does falsification separate from self-debug on enough rows?

Right now the answer is "not yet consistently."

### 3. Can the 32B model be completed across more than one benchmark family?

The 32B model is the strongest showcase. Missing 32B LiveCodeBench and broader
32B math/auxiliary coverage weaken the overall paper matrix.

### 4. Can the missing baseline columns be backfilled cleanly?

A table with missing columns looks undercooked even if the available rows are
strong.

## Recommended usage of this document

Use this file when:

- planning the next rerun wave;
- checking whether a manuscript sentence is too strong;
- deciding whether a row is valid enough for the main paper or appendix;
- answering "what do we actually have right now?"

## Bottom line

The project already has real, nontrivial code-generation evidence. It is not a
toy. The best HumanEval+ and MBPP+ rows are strong enough to matter. But the
full story is still mixed:

- some rows are headline-level;
- some rows are merely decent;
- some rows are incomplete;
- some older math interpretations are no longer acceptable.

That is exactly why this detailed ledger exists: to preserve the good results,
the weak spots, and the scientific corrections in one place.
