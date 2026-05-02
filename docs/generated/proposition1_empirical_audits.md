# Proposition 1 Empirical Audits

This note packages the two empirical audits implied by proposition 1's
real-decoding reduction assumptions into one reviewer-facing reference. The
goal is not to prove the autoregressive regularity conditions directly, but to
check the two load-bearing empirical surrogates in the exact theorem-3
real-generation setting:

1. answer stability across CoT budgets, which operationalizes the local
   stable-answer requirement used by lemma 4 / theorem 3(a)
2. trace-likelihood separation, which operationalizes the self-confirming
   evidence condition under the current answer state

## Audit 1: Answer Stability Across CoT Budgets

Source:
- [theorem3_answer_stability_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_answer_stability_note.md)

Setting:
- model: `DeepSeek-R1-Distill-Qwen-14B`
- checkpoints: `cot=0`, `cot=128`, `cot=1024`
- benchmarks: `ConflictBank`, `WikiContradict`

Headline:
- `ConflictBank` conflict fully stable across `0/128/1024`: `0.08`
- `ConflictBank` conflict stable across `0 -> 128`: `0.098`
- `ConflictBank` conflict stable across `128 -> 1024`: `0.364`
- on the stable `0 -> 128` subset:
  - mean confidence delta: `+0.0908`
  - mean accuracy delta: `0.0`
  - mean gap delta: `+0.0908`
- on the stable `0 -> 1024` subset:
  - mean confidence delta: `+0.1025`
  - mean accuracy delta: `0.0`
  - mean gap delta: `+0.1025`

Read:
- the stable-answer condition is empirically narrow, not generic
- but on the subset where proposition-1-style local stability is actually
  satisfied, the predicted confidence-gap widening appears without any matching
  accuracy growth
- that is the right empirical check for the reduction's local smoothness story:
  when the answer state does not jump, extra trace budget mostly sharpens belief
  rather than changing correctness

## Audit 2: Trace-Likelihood Separation

Source:
- [theorem3_trace_separation_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_trace_separation_note.md)

Setting:
- model: `DeepSeek-R1-Distill-Qwen-14B`
- benchmark: `ConflictBank`
- split: `conflict_context`
- CoT length: `1024`
- scored examples: `100`

Headline:
- current-answer state beats strongest competing state: `0.81`
- mean margin: `10.7513`
- median margin: `8.4565`
- correct-example win fraction: `1.0`
- incorrect-example win fraction: `0.8081`

Read:
- traces are usually more likely under the model's current answer state than
  under the strongest competing answer state
- the high incorrect-example win fraction means this is self-confirming
  evidence, not just truth-tracking
- that is exactly the empirical direction needed for the proposition-1-style
  endogenous-evidence mechanism to be relevant in the real decoding regime

## Scope

These audits do not turn proposition 1 into a transformer-specific theorem.
What they do is stronger than merely stating the assumptions:

- they show the stable-answer condition holds on a measurable subset of real
  trajectories
- they show the self-confirming separation condition is empirically active in
  the exact conflict regime the theorem-3 mechanism is meant to explain

So the honest conclusion is:
- proposition 1's reduction hypotheses are not universally verified
- but they are now empirically checked in the relevant real-decoding slices,
  rather than left as untested assumptions
