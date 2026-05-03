# Llama vs Qwen Family Explanation Note

This note records the current best evidence-backed explanation for why the
`Llama` matched-objective results are clean while the `Qwen` matched-objective
results remain mixed.

## Headline

- `Llama-8B` is the cleanest family-level objective split:
  - `DPO`: conflict ECE delta `-0.1051`, no-conflict ECE delta `-0.1499`
  - `GRPO`: conflict ECE delta `+0.2641`, no-conflict ECE delta `-0.0796`
  - conflict-minus-no-conflict `+0.3436`
- `Qwen-14B` is not a clean replication:
  - `DPO`: conflict ECE delta `+0.1838`, no-conflict ECE delta `+0.1185`
  - `GRPO`: conflict ECE delta `+0.0108`, no-conflict ECE delta `+0.0026`

## Best Current Explanation

The simplest explanation consistent with the finished same-family sweeps is:

1. `Qwen2.5` is already conflict-saturated on `ConflictBank`.
2. `Llama` is not conflict-saturated in the same way.
3. `GRPO` therefore creates a large new conflict-vs-no-conflict separation in
   `Llama`, but only a weak or noisy marginal change in `Qwen`.

That means `Qwen` should be treated as a boundary-case family rather than the
 family that defines the whole theorem-3 story.

## Evidence: Qwen Conflict Saturation

From the completed same-family theorem-3 sweep:

- `Qwen2.5-7B`, `ConflictBank`, `conflict`:
  - `cot=0`: `0.9856`
  - `cot=128`: `0.9849`
  - `cot=1024`: `0.9693`
- `Qwen2.5-14B`, `ConflictBank`, `conflict`:
  - `cot=0`: `0.9776`
  - `cot=128`: `0.9731`
  - `cot=1024`: `0.9584`
- `Qwen2.5-32B`, `ConflictBank`, `conflict`:
  - `cot=0`: `0.9484`
  - `cot=128`: `0.9307`
  - `cot=1024`: `0.8871`

The long-CoT conflict gap remains catastrophically high through `32B`. That is
why the same-family threshold summary reports:

- controlled-conflict recovery threshold for `Qwen2.5` on `ConflictBank`
  conflict: `None`
- persistent models above `0.85` long-CoT gap: `[7, 14, 32]`

So `Qwen` enters the matched-objective comparison with a strong pre-existing
conflict pathology.

## Evidence: DeepSeek-Qwen Is More Conditional

The `DeepSeek-R1-Distill-Qwen` family does not behave the same way across
scales:

- `DeepSeek-R1-Distill-Qwen-7B`, `ConflictBank`, `conflict`:
  - `0.5505 -> 0.7531 -> 0.5308`
- `DeepSeek-R1-Distill-Qwen-14B`, `ConflictBank`, `conflict`:
  - `0.5876 -> 0.9449 -> 0.9513`

That family splits by scale:

- `7B`: peak then full recovery
- `14B`: persistent or saturating conflict pathology

So the data are already telling us that training type and scale interact, not
just model family names.

## Why Llama Looks Better

The current best explanation for `Llama` is that it sits in a regime where:

- no-conflict rows still benefit meaningfully from longer reasoning
- conflict rows are still vulnerable to context-overtrust under `GRPO`
- the objective therefore produces a strong separation instead of just nudging
  an already-saturated failure mode

That is exactly the pattern we observe in the matched-objective `Llama-8B`
comparison.

## Third-Family Support

`Phi-3 GRPO` gives benchmark-level support for the Llama-style story on
`ConflictBank`:

- `conflict`: ECE `0.8969 -> 0.9676`
- `no_conflict`: ECE `0.7448 -> 0.2307`

So the main paper claim does not rest on `Qwen` anymore.

## Practical Positioning

The cleanest paper framing is:

- `Llama`: strongest family-level objective-effect headline
- `Phi-3`: benchmark-level replication of conflict-conditioned `GRPO`
  pathology
- `Qwen`: mixed/outlier family with pre-existing conflict saturation
- `RLCR + eta`: strongest mitigation result
