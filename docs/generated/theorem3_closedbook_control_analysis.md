# Theorem 3 Closed-Book Control Analysis

## Bottom line

- Decision: `not A`
- Read: the corrected `closed_book` control also becomes more overconfident with
  longer CoT.
- Consequence: the strict conflict-conditioned sign-flip version of theorem 3
  is ruled out by the finished real-generation control.
- Supported theorem: longer reasoning amplifies overconfidence on hard
  knowledge QA, and explicit conflict changes the shape and severity of that
  amplification in benchmark-family- and scale-dependent ways.

## Corrected control setup

The earlier "no-conflict" comparison was based on `aligned_context`, which is a
supportive-context condition rather than a true no-context baseline. The
corrected control uses `closed_book` generations on the same `7B` and `14B`
DeepSeek-R1-Distill runs:

- `ConflictBank`: `500` examples
- `WikiContradict`: `200` examples
- CoT budgets: `0`, `128`, `1024`

## Closed-book trajectories

### `DeepSeek-R1-Distill-Qwen-7B`

- `ConflictBank` closed-book: `0.4885 -> 0.7220 -> 0.6235`
- `WikiContradict` closed-book: `0.4950 -> 0.6220 -> 0.6499`

### `DeepSeek-R1-Distill-Qwen-14B`

- `ConflictBank` closed-book: `0.4917 -> 0.8168 -> 0.7890`
- `WikiContradict` closed-book: `0.5044 -> 0.5879 -> 0.6938`

## Conflict versus closed-book

### `ConflictBank`

- `7B` conflict: `0.5505 -> 0.7531 -> 0.5308`
- `7B` closed-book: `0.4885 -> 0.7220 -> 0.6235`
- `14B` conflict: `0.5876 -> 0.9449 -> 0.9513`
- `14B` closed-book: `0.4917 -> 0.8168 -> 0.7890`

This is the strongest surviving conflict-specific slice. At `14B`, explicit
conflict clearly amplifies and prolongs overconfidence beyond the closed-book
baseline. At `7B`, conflict is worse at short/medium CoT but not at the longest
budget.

### `WikiContradict`

- `7B` conflict: `0.2923 -> 0.4825 -> 0.4429`
- `7B` closed-book: `0.4950 -> 0.6220 -> 0.6499`
- `14B` conflict: `0.2717 -> 0.4516 -> 0.3750`
- `14B` closed-book: `0.5044 -> 0.5879 -> 0.6938`

`WikiContradict` does not support a conflict-specific worsening story. The
closed-book control is already more overconfident than the explicit-conflict
condition across all three CoT budgets for both models.

## Weighted model-level read

Weighting `ConflictBank` by `500` examples and `WikiContradict` by `200`
examples gives:

### `DeepSeek-R1-Distill-Qwen-7B`

- Conflict weighted gap: `0.4767 -> 0.6758 -> 0.5057`
- Closed-book weighted gap: `0.4904 -> 0.6934 -> 0.6310`

### `DeepSeek-R1-Distill-Qwen-14B`

- Conflict weighted gap: `0.4973 -> 0.8039 -> 0.7867`
- Closed-book weighted gap: `0.4953 -> 0.7514 -> 0.7618`

So even after fixing the control, there is no honest path to option `A`.

## Decision

The corrected control rejects the original theorem-3 target:

> "Under conflict, CoT worsens calibration, while the no-conflict control is
> flat or improving."

What survives is weaker but still real:

- CoT amplifies overconfidence even in `closed_book` mode on hard knowledge QA.
- On `ConflictBank`, especially at `14B`, explicit conflict amplifies that
  failure further and prevents long-CoT recovery.
- On `WikiContradict`, the dominant effect is hard-QA overconfidence rather than
  clean conflict-specific amplification.

## Paper consequence

The theorem-3 sentence should now be:

> Extended reasoning amplifies overconfidence on hard knowledge tasks.
> Under explicit controlled conflict, larger reasoning models can become even
> more pathological, saturating near maximal overconfidence rather than
> self-correcting.
