# Priority 1 Audit: Falsification vs. Generated-Test Filtering

This note tracks the acceptance-critical comparison between the proposed
sequential falsification method and the simpler `generated_test_filter`
baseline. If generated-test filtering matches or beats falsification, the paper
cannot honestly claim that adaptivity, sequential rounds, or confidence scoring
are buying accuracy.

## What Generated-Test Filtering Does

`generated_test_filter` is a one-shot selection baseline:

1. Build a generated probe bank from public examples.
2. Use non-public generated probe families only; public tests are excluded.
3. Run the same fixed probe set against the candidate pool.
4. Eliminate candidates that fail labeled probes or disagree with consensus.
5. Select from survivors by public-test score.

After the Priority 1 fix, this baseline is compute-matched by default:

- Probe budget: 4 probes.
- Probe schedule: family-balanced one-shot bank.
- Adaptivity: none.
- Survivor-conditioned differential synthesis: none.
- Confidence/e-process trace: none.

This makes it the correct baseline for the question:

> Do generated tests alone explain the gains?

## What Sequential Falsification Does Differently

`falsification` now has an explicit sequential diversity schedule:

1. Round 1 targets `edge_case` probes.
2. Round 2 targets `mutation` probes.
3. Round 3 targets `random_stress` probes.
4. Round 4 targets `differential` probes between surviving candidates.
5. Extra tie-break rounds synthesize survivor-only differential probes.

Within each round, probe selection is still adaptive: it scores available probes
against the current survivor pool and chooses a probe that separates candidates.
The key empirical bet is that later rounds should test different failure modes
than earlier rounds, rather than repeatedly choosing near-duplicate generated
tests.

## Why The Old Comparison Was Weak

The old implementation allowed two confounds:

- Falsification selected from one mixed probe bank, so multiple rounds could
  repeatedly target the same kind of failure mode.
- `generated_test_filter` could use a larger effective probe budget than the
  main falsification loop, making the simpler baseline artificially strong.

Those confounds made it possible for one-shot filtering to beat the proposed
method on MBPP+ rows, which is a paper-killing result if left unresolved.

## Current Code Fix

Implemented in:

- `src/falsify.py`
- `src/baselines.py`
- `src/evaluate.py`

The default falsification config now enables `enforce_round_family_diversity`.
The CLI also exposes:

```bash
--no-enforce-round-family-diversity
```

so the old behavior can be recovered for ablation.

## Targeted Validation Jobs

The first reruns are intentionally small, targeted pilots on the rows that
determine the paper framing:

| Job | Row | Purpose |
| --- | --- | --- |
| `2173829` | 7B MBPP+ | Previously falsification trailed generated-test filtering. |
| `2173834` | 14B MBPP+ | Previously falsification trailed generated-test filtering. |
| `2173837` | 7B HumanEval+ | Previously falsification trailed self-debug. |

These jobs are dependency-gated behind the active 32B run to avoid wasting
DeltaAI billing minutes while the queue is tight.

## Go / No-Go Criteria

Promote the fix to full reruns only if the pilots show one of:

- Falsification beats generated-test filtering on MBPP+ pilots.
- Falsification is within 1 point of generated-test filtering but has materially
  better calibration/selective-prediction behavior.
- Falsification beats self-debug on the 7B HumanEval+ pilot.

If none of these hold, the paper must be reframed:

- `generated_test_filter` becomes the practical accuracy mode.
- sequential falsification becomes the confidence/selective-prediction mode.
- claims about sequential adaptivity improving raw accuracy should be removed
  or limited to rows where the evidence supports them.

## Next Actions

1. Wait for `2173829 -> 2173834 -> 2173837`.
2. Harvest `results/p1fix_*`.
3. Compare falsification, generated-test-filter, and self-debug on the pilot
   slices.
4. Only then decide whether to launch full reruns or reframe the paper.
