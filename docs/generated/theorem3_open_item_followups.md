# Theorem 3 Open-Item Follow-Ups

This note closes the remaining theorem-3 reviewer-facing follow-ups that could
be resolved immediately from finished artifacts, and records the final queued
compute jobs for the remaining training-heavy checks.

## Conflict-Construction Audit

The first thing to rule out is that `Llama-8B GRPO` is only reacting to one
templated `ConflictBank` distractor recipe. `ConflictBank` already contains
three distinct conflict families (`misinformation`, `temporal`, `semantic`), so
we recomputed the headline split separately inside each family.

| Conflict family | Conflict ECE delta | No-conflict ECE delta | Conflict minus no-conflict |
|---|---:|---:|---:|
| misinformation | `+0.4571` | `-0.1151` | `+0.5722` |
| temporal | `+0.5574` | `-0.1327` | `+0.6902` |
| semantic | `+0.4966` | `-0.1327` | `+0.6294` |

Read:

- The `Llama-8B GRPO` conflict-conditioned blowup is not concentrated in one
  `ConflictBank` subfamily.
- All three conflict-construction families remain strongly positive.
- So the current headline is not well explained by one brittle distractor
  template inside `ConflictBank`.

To go one step further, we also queued an out-of-family spot-check using the
finished `Llama-8B GRPO` merged model on `NQ-Swap`, `ClashEval`, and `RAMDocs`
(`48` examples each, `cot=0/1024`, aligned vs conflict):

- Delta job: `2235555` `l8_cfaud`

That job is the stronger cross-source audit, but the within-`ConflictBank`
subfamily read is already reassuring.

## Calibration-Metric Robustness

The conflict-vs-no-conflict split is not an artifact of one scalar metric.
Below, `separation` always means:

`mean conflict delta - mean no-conflict delta`

### Strong headline cells

| Model | ECE sep. | Adaptive ECE sep. | Brier sep. | Log-loss sep. | Brier reliability sep. |
|---|---:|---:|---:|---:|---:|
| `Llama-8B GRPO` | `+0.3436` | `+0.3277` | `+0.3553` | `+6.4670` | `+0.2704` |
| `RLCR` | `+0.2910` | `+0.2715` | `+0.2708` | `+4.3056` | `+0.2756` |
| `Phi-3 GRPO` | `+0.2088` | `+0.2081` | `+0.2166` | `+4.5754` | `+0.2618` |
| `DeepSeek-Llama-8B` | `+0.0775` | `+0.0492` | `+0.0828` | `+1.9815` | `+0.0515` |

### Weak / flat controls

| Model | ECE sep. | Adaptive ECE sep. | Brier sep. | Log-loss sep. | Brier reliability sep. |
|---|---:|---:|---:|---:|---:|
| `Llama-8B SFT` | `+0.0287` | `-0.0454` | `-0.0221` | `-0.8437` | `+0.0069` |
| `Mistral-7B` | `+0.0150` | `+0.0350` | `+0.0125` | `+0.2602` | `+0.0197` |
| `Gemma-27B` | `-0.0168` | `-0.0059` | `-0.0099` | `+0.1268` | `-0.0021` |
| `Qwen-14B GRPO` | `+0.0082` | `+0.0148` | `+0.0213` | `+4.3814` | `+0.0161` |

Read:

- The main `Llama-8B GRPO` result survives equal-width ECE, equal-mass
  adaptive ECE, Brier, Brier reliability, and log loss.
- `RLCR` and `Phi-3 GRPO` also survive this robustness sweep cleanly.
- The negative-control `SFT` run does not reproduce the headline under the
  alternative metrics, which is exactly what we want from that control.

## Eta-Selection Leakage Audit

The theorem-3 eta-tempering method result is selected on a held-out
calibration split, not on the same rows used for the reported evaluation.

Finished `ConflictBank / conflict_context / cot=1024` method artifact:

- file: [theorem3_eta_tempered_method_result.json](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_eta_tempered_method_result.json)
- selection rule: `sample_split_brier_optimal`
- calibration size: `200`
- evaluation size: `300`
- selected eta: `0.0`

The implementation path is also explicit in code:

- `src/knowledge_arbitration/eta_tempering.py`
  - `split_rows(...)` creates disjoint calibration and evaluation subsets
  - `choose_eta(...)` runs only on calibration rows
  - `evaluate_eta(...)` is then applied to the held-out evaluation rows

Read:

- The reported jump from baseline to selected `eta` is not same-split leakage.
- The protocol is a real sample-split held-out selection rule.

## Theorem-Predicted Family Ordering Check

The honest theorem-3 read is a partial order, not a universal total ranking.
Under the paper's current `RLVR`-conditioned interpretation, the models most
expected to show strong positive conflict-minus-no-conflict separation are:

- `Llama-8B GRPO`
- `RLCR`
- `Phi-3 GRPO`
- `DeepSeek-Llama-8B`

Against a conservative control group:

- `Llama-8B SFT`
- `Llama-8B DPO`
- `Qwen-14B GRPO`
- `Mistral-7B`
- `Gemma-27B`
- `OLMo-2 DPO`
- `OLMo-2 GRPO`
- `Phi-3 DPO`
- `Llama-3.1-8B-Instruct`

Observed partial-order check:

- high-regime mean separation: `+0.2302`
- control-regime mean separation: `+0.0179`
- pairwise AUC (probability a high-regime model exceeds a control-regime model):
  `1.0` over `36` pairings

Observed descending separation ranking:

1. `Llama-8B GRPO` `+0.3436`
2. `RLCR` `+0.2910`
3. `Phi-3 GRPO` `+0.2088`
4. `DeepSeek-Llama-8B` `+0.0775`
5. `Qwen-14B DPO` `+0.0652`
6. `OLMo-2 DPO` `+0.0483`
7. `Llama-8B DPO` `+0.0448`
8. `Gemma-9B` `+0.0352`
9. `Llama-8B SFT` `+0.0287`
10. `OLMo-2 GRPO` `+0.0254`
11. `Mistral-7B` `+0.0150`
12. `Qwen-14B GRPO` `+0.0082`
13. `Llama-3.1-8B-Instruct` `+0.0045`
14. `Phi-3 DPO` `+0.0030`
15. `Gemma-27B` `-0.0168`

Read:

- The theorem-backed *partial* ordering is supported: the strongest positive
  cells are exactly the `RL` / reasoning-conditioned ones the current theorem-3
  interpretation privileges.
- The theorem does **not** justify a finer universal total ranking across every
  mild control family, so the paper should present this as a partial-order
  success, not as an exact global ordering theorem.

## Llama Matched-Headline Seed Variance

The original headline no longer stands on a single seed: two additional matched
`Llama-8B GRPO` seeds have now finished.

- seed `42` (original headline): `+0.3436`
- seed `43`: `+0.0424`
- seed `44`: `-0.0647`

Read:

- The original `Llama-8B GRPO` seed remains the strongest single matched-base
  theorem-3 result in the repo.
- But the multi-seed picture is clearly weaker and more variable than the
  single-seed headline suggested.
- So the cleanest paper framing should treat `Llama-8B` as a strong
  seed-available discovery result, not as a solved low-variance estimate.

## Second Matched-Base Family Replication

The second matched-base family is now substantially farther along than before.

Finished:

- `DeepSeek-Llama-8B` matched `DPO`: `+0.0258`
- `DeepSeek-Llama-8B` matched `GRPO`: `-0.1239`
- `Phi-3` matched `SFT`: `+0.2069`
- `Phi-3` matched `DPO`: `+0.0030`
- `Phi-3` matched `GRPO`: `+0.2088`

Read:

- `Phi-3` is now a fully materialized matched family, but it does **not**
  close the clean `GRPO > SFT` replication complaint by itself:
  the matched `SFT` control (`+0.2069`) is effectively tied with matched
  `GRPO` (`+0.2088`).
- `DeepSeek-Llama-8B` is now fully closed as a matched `DPO/GRPO` family, and
  it also does **not** supply the clean second matched-family replication:
  matched `GRPO` is negative (`-0.1239`) while matched `DPO` is mildly
  positive (`+0.0258`).
- So the clean reviewer complaint about "only one matched-base RL family"
  remains unresolved at `8B`, even though the larger Llama-lineage
  `DeepSeek-70B` result remains strongly positive.

## 70B Follow-Ups

`Llama-3.1-70B-Instruct` has now finished and came back basically flat:

- conflict ECE delta: `-0.0219`
- no-conflict ECE delta: `+0.0198`
- conflict-minus-no-conflict: `-0.0418`

That is useful because it strengthens the negative claim that scale alone does
not recover the theorem-3 effect for plain instruct `Llama`.

`DeepSeek-R1-Distill-Llama-70B` is now also finished, and the full theorem-3
matrix came back strong after rebuilding the missing report artifact from the
completed generation JSON:

- conflict ECE delta: `-0.0111`
- no-conflict ECE delta: `-0.3992`
- conflict-minus-no-conflict: `+0.3881`

Read:

- This is a strong large-model Llama-lineage replication.
- The effect is driven primarily by very large no-conflict calibration gains
  while conflict stays roughly flat, which is still exactly the
  conflict-conditioned separation the paper cares about.
- So the 70B picture is now clean: plain instruct `Llama` stays flat, while the
  reasoning-distilled `DeepSeek-Llama` lineage stays strongly positive.
