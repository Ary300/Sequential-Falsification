# DeepSeek-Llama-8B Refresh Wave

Status date: `2026-05-06`

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
3. rerun the matched `DPO/GRPO` sweep with the completed DeepSeek-native
   theorem-3 eval protocol, since the standalone native rerun improved the
   headline from negative to mildly positive

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

## Native-eval matched-pair redo

The first refresh sweep still inherited the generic theorem-3 eval defaults.
That is now an avoidable mismatch because the matched-objective launcher can
forward:

- `EVAL_REQUEST_FORMAT=completion`
- `EVAL_PROMPT_PROTOCOL=deepseek_native`

Dedicated launcher:

- [submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh)

Completed native matched-pair redo:

- `2248710` `r1l8dn_native_b005g8w2`
  - matched `DPO`, Pair A
  - conflict-minus-no-conflict: `-0.0870`
- `2248711` `r1l8gn_native_b005g8w2`
  - matched `GRPO`, Pair A
  - conflict-minus-no-conflict: `-0.0229`
- `2248712` `r1l8dn_native_b002g8w2`
  - matched `DPO`, Pair B
  - conflict-minus-no-conflict: `-0.0405`
- `2248713` `r1l8gn_native_b002g8w2`
  - matched `GRPO`, Pair B
  - conflict-minus-no-conflict: `+0.0716`

## May 6 rescue wave

After the native matched sweep finished, we found a real submit-path bug in the
generic matched-objective Delta launcher:

- `WARMSTART_EPOCHS` was not being exported through
  [submit_delta_theorem3_matched_objective_lora.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_matched_objective_lora.sh)
- consequence:
  the earlier tags that were meant to test stronger `warmstart=2` settings
  almost certainly ran with the default `warmstart=1` on Delta

That means the native matched sweep was still useful, but it did **not**
faithfully test the stronger warmstart settings we thought we had already
covered.

Corrected rescue launcher:

- [submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh)
- eval-only checkpoint launcher for any promising intermediate rescue snapshot:
  [submit_delta_theorem3_deepseek_llama8_checkpoint_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_checkpoint_eval.sh)
- multi-checkpoint sweep helper for a finished rescue run:
  [submit_delta_theorem3_deepseek_llama8_checkpoint_eval_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_checkpoint_eval_sweep.sh)

Submitted `2026-05-06`:

- initial rescue jobs `2251775`–`2251779` were cancelled before start after the
  launcher hardening landed, so the live queue now uses the corrected rerun IDs
- second rescue wave `2251792`–`2251799` was then cancelled too once a new
  infrastructure blocker was confirmed:
  `/work` was fully saturated, so even corrected training jobs were still at
  risk of failing on cache or output writes
- live corrected rescue jobs now use node-local `/tmp` staging with compact
  sync-back to `/u/adas17/tts_results_staging`
- live corrected rescue jobs:
- `2251840` `r1l8dr_nativefix_b002g8w2`
  - `DPO`
  - reruns the previously best native pocket with the intended
    `warmstart=2` now actually forwarded
- `2251841` `r1l8gr_nativefix_b002g8w2`
  - `GRPO`
  - same corrected `warmstart=2` rerun
- `2251842` `r1l8dr_nativerescue_b001g12w3`
  - `DPO`
  - softer regularization, larger group, `warmstart=3`
- `2251843` `r1l8gr_nativerescue_b001g12w3`
  - `GRPO`
  - softer regularization, larger group, `warmstart=3`
- `2251844` `r1l8gr_nativerescue_b001g16t06w3s43`
  - `GRPO`
  - exploratory cooler-sampling leg with a fresh seed
- completed headlines so far from the staged rescue wave:
  - `2251840` final `DPO`: `-0.0629`
  - `2251842` final `DPO`: `-0.2074`
  - `2251841` final `GRPO`: `+0.0315`
  - `2251843` final `GRPO`: `+0.0455`
  - `2251844` final `GRPO`: `-0.0330`
- best completed checkpoint reads so far:
  - `2251840` `warmstart_sft_epoch_01`: `-0.0085`
  - `2251844` `warmstart_sft_epoch_01`: `+0.0331`

Dependent checkpoint-eval sweep jobs also queued:

- `2251847` `r1l8ckfixd_dep2`
- `2251848` `r1l8ckfixg_dep2`
- `2251849` `r1l8ckrescued_dep2`
- `2251850` `r1l8ckrescueg_dep2`
- `2251851` `r1l8ckrescueg2_dep2`

Read:

- each dependency job waits for its paired rescue run to finish cleanly
- then it scans the staged `intermediate_checkpoints/` tree under
  `/u/adas17/tts_results_staging` and submits DeepSeek-native theorem-3 eval
  jobs for every saved checkpoint automatically

Checkpoint read:

- the older curriculum-audit runs do exist on HDD, but they did **not** save
  usable `intermediate_checkpoints/` directories
- that means there is no cheap “retroactive checkpoint salvage” from the old
  audit jobs
- the new rescue wave is therefore the first DeepSeek path where we have both:
  - corrected warmstart forwarding
  - a ready eval-only launcher for any intermediate checkpoint that looks
    better than the final merged adapter

Read:

- this is the cleanest remaining attempt to improve the `DeepSeek-Llama-8B`
  matched-base story without changing the training objective itself
- the completed native sweep does improve the family from uniformly weak to
  mixed
- the strongest native matched result is `GRPO` Pair B at `+0.0716`
- even after that improvement, the right conclusion is still that
  `DeepSeek-Llama-8B` is genuinely mixed rather than merely
  protocol-mismatched
- the new rescue wave is justified because it is not “rerunning the same weak
  settings”; it is correcting a real warmstart-forwarding bug and then widening
  the GRPO search pocket slightly
- the checkpoint-eval path is now materially stronger too:
  checkpoint eval jobs no longer point vLLM directly at adapter-only
  directories; they first merge the PEFT adapter into a standalone local model
  before theorem-3 evaluation
- active GRPO continuation sweep also queued around the best surviving native
  pocket:
  - `2252260` `r1l8gc_nativeplus_b002g8w3`
  - `2252261` `r1l8gc_nativeplus_b002g8w3e2`
  - `2252262` `r1l8gc_nativeplus_b001g8w3`
 - completed continuation headlines:
  - `2252260` final `GRPO`: `+0.0532`
  - `2252261` final `GRPO`: `-0.0071`
  - `2252262` final `GRPO`: `-0.0358`

Final read as of `2026-05-06`:

- the rescue wave does improve the bad `DeepSeek-Llama-8B` story from mixed to
  mildly positive on several native `GRPO` settings
- the strongest completed final headline is now `+0.0532`
- that is materially better than the earlier bad runs, but it still does **not**
  become a clean `Llama-8B`-scale replication

## Read

- This is a legitimate redo because it preserves matched-family symmetry.
- It does **not** guarantee a positive `GRPO` result.
- It is the strongest honest attempt to recover a cleaner `DeepSeek-Llama-8B`
  matched-family story without pretending the first negative run did not
  happen.
- The result is now numerically closed:
  - the family is no longer purely negative under native eval
  - but it still does **not** become a clean second `8B` matched-base
    replication of the `Llama-8B` effect
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
