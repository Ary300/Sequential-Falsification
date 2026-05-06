# Theorem 3 Conflict Control Analysis

## Bottom line

- Decision: `B`
- Read: no-conflict overconfidence also rises with CoT, but overall it rises
  less and/or recovers faster than the conflict gap.
- Consequence: the strict sign-flip version of theorem 3 is dead.
- Supported theorem: reasoning amplifies overconfidence generally, but the
  amplification is stronger and more persistent on hard conflict families,
  especially `ConflictBank` and especially at `14B`.

## Weighted model-level read

These averages weight `ConflictBank` by `500` examples and `WikiContradict` by
`200` examples, matching the finished runs.

### `DeepSeek-R1-Distill-Qwen-7B`

- Conflict weighted gap: `0.4767 -> 0.6758 -> 0.5057`
- No-conflict weighted gap: `0.1467 -> 0.3407 -> -0.1422`
- Interaction:
  - `0 -> 128`: `+0.0051`
  - `128 -> 1024`: `+0.3128`
  - net `0 -> 1024`: `+0.3179`

### `DeepSeek-R1-Distill-Qwen-14B`

- Conflict weighted gap: `0.4973 -> 0.8039 -> 0.7867`
- No-conflict weighted gap: `0.1340 -> 0.3428 -> 0.1927`
- Interaction:
  - `0 -> 128`: `+0.0978`
  - `128 -> 1024`: `+0.1329`
  - net `0 -> 1024`: `+0.2307`

## Per-benchmark read

### `ConflictBank`

- `7B` conflict: `0.5505 -> 0.7531 -> 0.5308`
- `7B` no-conflict: `0.0996 -> 0.2754 -> -0.3724`
- `14B` conflict: `0.5876 -> 0.9449 -> 0.9513`
- `14B` no-conflict: `0.0691 -> 0.3108 -> 0.1032`

This is the cleanest theorem-3 evidence in the project. Both models show
stronger and more persistent overconfidence amplification on the conflict
slice than on the no-conflict slice. The `14B` result is especially strong:
long CoT stays near maximally overconfident under conflict.

### `WikiContradict`

- `7B` conflict: `0.2923 -> 0.4825 -> 0.4429`
- `7B` no-conflict: `0.2643 -> 0.5038 -> 0.4331`
- `14B` conflict: `0.2717 -> 0.4516 -> 0.3750`
- `14B` no-conflict: `0.2963 -> 0.4229 -> 0.4164`

`WikiContradict` does not support a clean conflict-vs-no-conflict separation.
Both splits get more overconfident with CoT, and the short-CoT jump is not
consistently larger under conflict. What survives is the family-level result:
`WikiContradict` keeps the peak-and-partial-recovery shape, while `ConflictBank`
conflict becomes much more pathological at larger scale.

## Decision

This is not outcome `A`.

It is best read as outcome `B`:

- CoT amplifies overconfidence generally.
- On the hardest controlled conflict family, that amplification is larger
  and more persistent under conflict.
- The theorem-3 contribution is therefore an interaction claim, not a pure
  sign-flip claim.

## Paper consequence

The theorem-3 sentence should now be:

> Under knowledge conflict, extended reasoning amplifies overconfidence.
> This amplification is benchmark-family and scale dependent: smaller models
> can partially self-correct at long CoT, while larger models may instead
> saturate near maximal overconfidence.
