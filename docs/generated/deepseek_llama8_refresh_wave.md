# DeepSeek-Llama-8B Refresh Wave

Status date: `2026-05-03`

This note tracks the redo wave for the matched-base `DeepSeek-R1-Distill-Llama-8B`
family after the first finished `DPO/GRPO` pair came back weak / negative.

## Why this redo exists

The finished matched-family numbers were:

- matched `DPO`: `+0.0258`
- matched `GRPO`: `-0.1239`

That result is numerically closed, but the `GRPO` row comes from the local
matched-objective surrogate rather than the original DeepSeek training stack,
and the `GRPO` headline was materialized through an eval-recovery path.

So the honest redo is:

1. rerun `DPO` through the same eval-recovery path for a cleaner apples-to-apples
   comparison
2. run a small paired matched `DPO/GRPO` refresh sweep with softer `GRPO`
   settings rather than treating one surrogate configuration as final

## Live jobs

- `2238060` `r1l8_drev`
  - eval-only recovery for `DeepSeek-Llama-8B DPO`
  - output target: `results/e1_deepseek_llama8_dpo/theorem3_eval_recovery_v2`

- `2238062` `r1l8d_b005g8w2`
  - matched `DPO` refresh, Pair A

- `2238063` `r1l8g_b005g8w2`
  - matched `GRPO` refresh, Pair A

- `2238064` `r1l8d_b002g8w2`
  - matched `DPO` refresh, Pair B

- `2238065` `r1l8g_b002g8w2`
  - matched `GRPO` refresh, Pair B

## Refresh settings

All refresh jobs use the same matched source split and evaluation setup:

- model: `deepseek-ai/DeepSeek-R1-Distill-Llama-8B`
- benchmark: `ConflictBank`
- source / train / val / eval rows: `800 / 560 / 80 / 80`
- warmstart SFT epochs: `2`
- objective epochs: `1`
- theorem-3 eval:
  - `WikiContradict` max `96`
  - `ConflictBank` max `128`
  - `cot=0/128/1024`

Pair A:

- `beta=0.05`
- `group_size=8`
- `temperature=0.7`

Pair B:

- `beta=0.02`
- `group_size=8`
- `temperature=0.7`

## Read

- This is a legitimate redo because it preserves matched-family symmetry.
- It does **not** guarantee a positive `GRPO` result.
- It is the strongest honest attempt to recover a cleaner `DeepSeek-Llama-8B`
  matched-family story without pretending the first negative run did not
  happen.
- The paired reviewer-facing diagnosis path is now wired too:
  [submit_delta_deepseek_llama8_objective_followups.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_deepseek_llama8_objective_followups.sh)
  launches the same token-level answer-margin / entropy probe used for the
  matched `Llama-8B` mechanism note, but on the DeepSeek pair.
- The intermediate-checkpoint curriculum path is also wired now:
  [deepseek_llama8_curriculum_audit_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_curriculum_audit_status.md)
  and
  [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)
  let us inspect whether the failure shows up during warmstart or only after
  the objective stage.
