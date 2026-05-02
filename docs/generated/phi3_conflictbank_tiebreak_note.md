# Phi-3 ConflictBank Tie-Break Note

This note records the benchmark-level `Phi-3` tie-break result that is partly
hidden by the pooled theorem-3 summary.

## Why This Note Exists

The pooled `Phi-3 GRPO` headline averages over both `ConflictBank` and
`WikiContradict`, which makes the result look less Llama-like than it is on the
mechanistic conflict benchmark we care about most.

## Phi-3 GRPO on ConflictBank

`ConflictBank`, `conflict` split:

- `cot=0`: accuracy `0.0156`, ECE `0.8969`, overconfidence gap `0.8969`
- `cot=128`: accuracy `0.0078`, ECE `0.9674`, overconfidence gap `0.9674`
- `cot=1024`: accuracy `0.0078`, ECE `0.9676`, overconfidence gap `0.9676`

Read:

- longer CoT worsens calibration on the `ConflictBank` conflict split
- ECE rises by about `+0.0707` from `cot=0` to `cot=1024`

`ConflictBank`, `no_conflict` split:

- `cot=0`: accuracy `0.2031`, ECE `0.7448`, overconfidence gap `0.7448`
- `cot=128`: accuracy `0.7812`, ECE `0.2152`, overconfidence gap `0.2152`
- `cot=1024`: accuracy `0.7656`, ECE `0.2307`, overconfidence gap `0.2307`

Read:

- longer CoT dramatically improves the `ConflictBank` no-conflict split
- ECE drops by about `-0.5141` from `cot=0` to `cot=1024`

So on `ConflictBank`, `Phi-3 GRPO` shows a strong Llama-like separation:

- conflict gets worse
- no-conflict gets much better
- the conflict-vs-no-conflict separation is very large

## Phi-3 DPO on ConflictBank

`ConflictBank`, `conflict` split:

- `cot=0`: ECE `0.8261`
- `cot=1024`: ECE `0.8828`
- delta: `+0.0567`

`ConflictBank`, `no_conflict` split:

- `cot=0`: ECE `0.8547`
- `cot=1024`: ECE `0.9099`
- delta: `+0.0552`

Read:

- `Phi-3 DPO` is not a clean negative control on `ConflictBank`
- but unlike `GRPO`, its worsening is roughly symmetric across conflict and
  no-conflict

## Practical Interpretation

The benchmark-level `Phi-3` read is stronger than the pooled summary:

- `GRPO` does replicate the conflict-conditioned pathology on `ConflictBank`
- `DPO` does not show the same conflict-specific separation

That means `Phi-3` is useful third-family evidence in favor of a
benchmark-conditioned `GRPO` story, even though the fully pooled headline over
all benchmarks looks more mixed.
