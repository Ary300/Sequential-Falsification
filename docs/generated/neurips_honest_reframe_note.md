# NeurIPS Honest Reframe Note

This note translates the strongest current reviewer-style objections into an
actionable paper framing that matches the empirical package we actually have.

## What We Can Still Claim Strongly

- `Llama-8B GRPO` remains a real theorem-3 discovery result.
  - conflict-minus-no-conflict ECE delta: `+0.3436`
  - 95% CI: `[0.2297, 0.4757]`
- `Llama-8B SFT` is much weaker than `GRPO`.
  - conflict-minus-no-conflict ECE delta: `+0.0287`
  - 95% CI: `[-0.0583, 0.1153]`
  - This means the headline effect is not explained by "extra training" alone.
- The mechanism probe is informative.
  - matched `Llama-8B` answer-margin diff-in-diff (`GRPO - DPO`): `-22.5512`
  - Best interpretation: `GRPO` changes which answer state gets probability
    mass on conflict prompts; `DPO` does not.
- `RLCR + eta` is a real intervention result.
  - On `ConflictBank / conflict_context / cot=1024`:
    - accuracy `0.0625 -> 0.5313`
    - ECE `0.9036 -> 0.4311`
    - Brier `0.8862 -> 0.4148`
- `DeepSeek-R1-Distill-Llama-70B` is a strong large-model lineage replication.
  - conflict-minus-no-conflict ECE delta: `+0.3881`
- Plain scale does not rescue the effect.
  - `Llama-3.1-70B-Instruct`: `-0.0418`

## What We Should Stop Overselling

- The `Llama-8B GRPO` matched-base result is not yet a low-variance estimate.
  - extra seeds:
    - seed `43`: `+0.0424`
    - seed `44`: `-0.0647`
  - The clean claim is discovery / existence proof, not stable family average.
- `Phi-3` is no longer a missing-cell objection, but it is not the clean second
  matched-family replication.
  - matched `SFT`: `+0.2069`
  - matched `DPO`: `+0.0030`
  - matched `GRPO`: `+0.2088`
  - So `Phi-3` does not support `GRPO > SFT`; it supports a broader
    "post-training can induce the split" read.
- `DeepSeek-Llama-8B` also fails as the clean second matched-family
  replication.
  - matched `DPO`: `+0.0258`
  - matched `GRPO`: `-0.1239`
  - So the strongest clean matched-base RL family is still `Llama-8B`.
- `Qwen` is not a good causal anchor.
  - matched `DPO`: `+0.0652`
  - matched `GRPO`: `+0.0082`
  - Best read: mixed / pre-saturated family.
- Paper 2 free-form open-QA is not a dominance result.
  - It now exists and is no longer missing, but the strongest wins are still
    the poisoned-context, reliability-ablation, multi-doc conflict, and
    latency/cost pieces.

## What The Theory Should Emphasize

- Lead with `Theorem 2`, `Theorem 6`, and `Theorem 7`.
  - `Theorem 2`: the cleanest uniqueness/characterization statement
  - `Theorem 6`: the strongest theorem-to-empirics bridge
  - `Theorem 7`: the cleanest intervention theorem
- Demote `Theorem 1` from "deep uniqueness" rhetoric to "conditional
  log-linear derivation."
- Demote `Theorem 5` from load-bearing headline theorem to conditional
  descriptive statement with empirical support on restricted slices.

## What Still Matters Empirically

- The strongest empirical theorem-3 package is now:
  - `Llama-8B GRPO` discovery result
  - `Llama-8B SFT` negative control
  - mechanism probe on matched `Llama-8B`
  - `RLCR + eta` intervention result
  - `DeepSeek-Llama-70B` strong lineage replication
  - plain `Llama-70B` flat scale-only control
- The remaining high-value empirical swing result is:
  - no longer a pending matched `DeepSeek-Llama-8B` recovery
  - instead, the main open question becomes whether to live with a single clean
    matched-base family and reframe accordingly, or to run an entirely new
    matched family if the venue absolutely requires it.

## Recommended Paper-Level Reframe

- Present the paper as:
  - a geometric-pooling characterization (`Theorem 2`)
  - a calibration intervention result (`Theorem 7`)
  - a strong matched-base single-family discovery on `Llama-8B`
  - a mechanistic answer-margin explanation
  - plus large-model lineage replication and negative controls
- Do **not** present it as:
  - a solved universal theorem about all post-training families
  - a low-variance causal estimate over many seeds
  - a broad free-form open-QA win over all adaptive baselines
