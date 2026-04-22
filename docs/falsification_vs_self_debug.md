# Falsification vs Self-Debug Audit

This note exists to answer the most obvious reviewer question in the current project:

"Why is this not just self-debugging with extra steps?"

## Short answer

It is not self-debugging because the falsification path in this repository is now:

- population-based rather than single-candidate
- elimination-based rather than repair-based
- probe-driven rather than error-message-driven
- confidence-producing rather than confidence-free

## What self-debug does here

The local self-debug baseline in [`src/baselines.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/baselines.py) works by:

- evaluating the first candidate on public tests
- if that candidate fails, searching later candidates for one that passes public tests
- selecting that fallback candidate and then evaluating it on hidden tests

This is a lightweight repair-style baseline. It exploits a small amount of execution feedback, but it does not maintain a population-level elimination trace and it does not generate adversarial probes targeted at the current survivor pool.

## What falsification does here

The falsification path in [`src/falsify.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/falsify.py):

- starts from the full candidate pool in `sequential_falsify_candidates`
- keeps all candidates alive initially as records with trace state
- builds probe families from public tests, mutation probes, edge-case probes, random-stress probes, and disagreement-driven differential probes
- chooses probes against the current survivor pool in `_choose_best_probe`
- executes the entire survivor pool on the chosen probe
- eliminates failing candidates when `eliminate_on_detection=True`
- ranks surviving candidates by confidence/selection score only after elimination

That means the core unit of computation is the candidate population, not a single evolving draft.

## The key architectural difference

Self-debug:

- Candidate -> execution feedback -> revised candidate

Falsification:

- Candidate pool -> adversarial probe -> eliminate inconsistent candidates -> select from survivors

Those are different algorithms with different failure modes.

## Why the new differential probes matter

The strongest objection to a weak falsification implementation is that it can collapse into "rerun public tests and hope."

To reduce that risk, the current code now includes disagreement-driven differential probes in [`src/falsify.py`](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/falsify.py):

- candidate inputs are synthesized around public tests
- a probe is only admitted to the differential bank if the current survivor pool actually disagrees on that input
- the input is then labeled with the benchmark reference solution before elimination

This makes the probe family explicitly population-aware. It is much closer to "selection from diversity" than to candidate-local debugging.

## What would still make the methods look too similar

Reviewers would still be right to worry if:

- falsification used only public tests
- falsification repaired candidates instead of eliminating them
- adaptive probe choice were disabled everywhere
- differential and generated probes never changed selection outcomes

That is exactly why the repo now includes:

- probe-family ablations
- adaptive-vs-nonadaptive component ablations
- elimination-vs-no-elimination ablations
- survival-only vs wealth-based ranking ablations

## Bottom line

If falsification still only ties self-debug after the corrected population-level and differential-probe reruns, the right conclusion is not "pretend they are different anyway." The right conclusion is:

- either falsification needs stronger probes
- or the paper should pivot toward calibration and diagnosis rather than raw accuracy gains

That is the honest standard this repository should be judged against.
