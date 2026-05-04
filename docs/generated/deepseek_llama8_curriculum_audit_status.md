# DeepSeek-Llama-8B Curriculum Audit Status

Status date: `2026-05-03`

This note tracks the missing intermediate-checkpoint part of the
`DeepSeek-R1-Distill-Llama-8B` failure diagnosis.

## Why this audit exists

The first matched-base `DeepSeek-Llama-8B` pair closed numerically, but it left
one real blind spot:

- we had final `DPO` / `GRPO` endpoints
- we did **not** have saved adapters after each warmstart / objective epoch
- so we could not inspect whether the failure appears immediately, during the
  warmstart, or only after the `GRPO` objective step

That makes “distillation curriculum mismatch” plausible, but not yet
directly testable from the saved artifacts alone.

## New support now wired

The matched-objective trainer now supports per-epoch checkpoint persistence:

- runner:
  [run_theorem3_matched_objective_lora.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_matched_objective_lora.py)
- Delta submit path:
  [submit_delta_theorem3_matched_objective_lora.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_matched_objective_lora.sh)
- Delta batch file:
  [theorem3_matched_objective_lora_delta.sbatch](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/slurm/delta/theorem3_matched_objective_lora_delta.sbatch)

When `SAVE_INTERMEDIATE_CHECKPOINTS=1`, the run now writes:

- `intermediate_checkpoints/warmstart_sft_epoch_XX/`
- `intermediate_checkpoints/dpo_epoch_XX/`
- `intermediate_checkpoints/grpo_epoch_XX/`
- per-checkpoint `checkpoint_metadata.json`

## Dedicated launcher

The dedicated DeepSeek curriculum launcher is:

- [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)

It stages:

- matched `DPO` with checkpoint persistence
- matched `GRPO` with checkpoint persistence
- same `800 / 560 / 80 / 80` source / train / val / eval budget
- theorem-3 eval on `WikiContradict + ConflictBank`

## What this resolves

This does **not** guarantee a positive DeepSeek result.

It does resolve the instrumentation complaint:

- if the family still fails, we can now say **when** in training it fails
- if the family flips sign late, we can separate warmstart behavior from
  objective-stage behavior
- if the answer-margin mechanism only appears at the final objective stage, we
  can compare checkpoints directly instead of inferring from the endpoints

## Bottom line

The remaining DeepSeek blocker is no longer “we forgot to save the trajectory.”
It is now purely a compute / Delta-access problem.
