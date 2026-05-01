# E1 / E6 Delta Launch Status

This note records the live Delta submissions for the remaining training-heavy empirical items.

## Reprioritization

The older pending jobs for attention / 70B / the first multi-GPU RLCR pass were canceled so the queue could be focused on the remaining asks:

- old `t3_attnint`
- old `p2_r1l70`
- old `t3_rlcr14`

## Active queue

### E6. RLCR-style training-time comparison

- Job ID: `2224893`
- Job name: `t3_rlcr1g`
- Launcher: `scripts/submit_delta_theorem3_e6_rlcr_1gpu.sh`
- Resource shape: `1 GPU`, `16 CPU`, `18h`
- Purpose: cheaper single-GPU rerun of the RLCR-style LoRA calibration job, now with gradient checkpointing plus saved adapter and merged-model exports

### E1. Matched-base objective comparison

The new matched-objective runner trains LoRA checkpoints on the same conflict-heavy `ConflictBank` pool, saves both adapter and merged-model checkpoints, and then launches theorem-3 real-generation evaluation from the merged model.

- `2224894` `e1_l8_dpo`
  - model: `meta-llama/Llama-3.1-8B`
  - objective: `dpo`
  - wall: `14h`
- `2224895` `e1_l8_grpo`
  - model: `meta-llama/Llama-3.1-8B`
  - objective: `grpo` (group-relative verifiable-reward surrogate)
  - wall: `14h`
- `2224896` `e1_q14_dpo`
  - model: `Qwen/Qwen2.5-14B`
  - objective: `dpo`
  - wall: `18h`
- `2224897` `e1_q14_grpo`
  - model: `Qwen/Qwen2.5-14B`
  - objective: `grpo` (group-relative verifiable-reward surrogate)
  - wall: `18h`

## Current queue state at launch check

All five jobs were successfully submitted and were `PENDING` with reason `Priority`.

## Artifacts and code

- Matched-objective trainer:
  - `scripts/run_theorem3_matched_objective_lora.py`
- Matched-objective submit wrapper:
  - `scripts/submit_delta_theorem3_matched_objective_lora.sh`
- Matched-objective suite launcher:
  - `scripts/submit_delta_theorem3_e1_suite.sh`
- Matched-objective sbatch:
  - `slurm/delta/theorem3_matched_objective_lora_delta.sbatch`
- RLCR single-GPU wrapper:
  - `scripts/submit_delta_theorem3_e6_rlcr_1gpu.sh`

## Honest read

- These are now real queued training jobs, not paper-only placeholders.
- They are not finished yet; the remaining blocker is Delta scheduler time.
- The `GRPO` branch is a truthful group-relative verifiable-reward surrogate in the current stack, not a byte-for-byte reproduction of the original DeepSeek training recipe.
