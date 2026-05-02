# P3 Post-Hoc Failure Analysis

This note explains the failed preregistered `P3` prediction from the held-out test family.

## Prediction

`P3` predicted that the long-CoT calibration shift would be larger on conflict slices than on aligned-context slices.

## Result

`P3` was not supported on the held-out families.

Held-out model rows:

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
  - mean conflict ECE delta: `-0.1615`
  - mean no-conflict ECE delta: `-0.0215`
  - conflict-minus-no-conflict: `-0.1400`
- `Qwen/Qwen2.5-14B-Instruct`
  - mean conflict ECE delta: `-0.1125`
  - mean no-conflict ECE delta: `-0.0323`
  - conflict-minus-no-conflict: `-0.0802`
- `meta-llama/Llama-3.1-8B-Instruct`
  - mean conflict ECE delta: `-0.1438`
  - mean no-conflict ECE delta: `-0.0215`
  - conflict-minus-no-conflict: `-0.1223`

So on the held-out families, longer reasoning improved calibration more on conflict than on aligned slices, which is the opposite of the directional theorem-3 expectation.

## Best Explanation

The cleanest post-hoc explanation is benchmark geometry.

- The original theorem-3 evidence is strongest on controlled contradiction settings such as `ConflictBank`, where the contextual evidence is explicitly salient and wrong.
- The held-out preregistered families appear to behave more like generic uncertainty tasks than like adversarial contradiction tasks.
- In those held-out families, extra reasoning seems to act as a caution mechanism rather than a self-confirming one, reducing overconfidence on the harder conflict slices instead of amplifying it.

## What This Means

- The preregistered failure does not invalidate the main theorem-1 / theorem-2 story.
- It does weaken any universal version of theorem-3.
- The honest updated scope is that theorem-3 is regime-dependent: it is strongest in explicit contradiction benchmarks and can reverse on held-out families whose conflict structure is less adversarial.

## Practical Read

- `P1` and `P2` still succeeded on the held-out families.
- `P3` failed because the held-out conflict families were not strong replicas of the original contradiction regime.
- This is evidence for a narrower, benchmark-geometry-sensitive theorem-3 claim rather than a global long-CoT pathology claim.
