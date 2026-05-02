# Joint RLCR + Eta-Tempering Pilot Status

This note records the direct measurement setup for the joint training-time plus
test-time intervention that had previously been predicted but not measured.

## Pilot Definition

We measure `RLCR + eta-tempering` by running the existing theorem-3
eta-tempered decoding scorer on:

- the saved merged RLCR model
- the saved full-matrix RLCR theorem-3 generation rows
- the same headline slice used for the method-only eta result:
  - `ConflictBank`
  - `conflict_context`
  - `cot=1024`

Concretely:
- training-time intervention: RLCR-style LoRA calibration fine-tune
- test-time intervention: post-trace eta-tempering on the RLCR model's own
  answer-state scores

## Source Artifacts

- RLCR merged model:
  `/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/merged_model`
- RLCR theorem-3 rows:
  `/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/theorem3_eval_full_v3/theorem3_generation_rows.jsonl`

## Measured Result

The corrected rerun completed as:

- Job id: `2231030`
- Job name: `rlcr_eta_j2`
- State: `COMPLETED`

Evaluation headline on `ConflictBank / conflict_context / cot=1024`:

- Baseline `eta=1.0`
  - Accuracy: `0.0625`
  - ECE: `0.903553`
  - Brier: `0.886175`
  - Overconfidence gap: `0.903553`
- Selected `eta=0.0`
  - Accuracy: `0.53125`
  - ECE: `0.431058`
  - Brier: `0.414764`
  - Overconfidence gap: `0.431058`

Read:
- the joint intervention materially improves this hardest headline slice
- accuracy increases by `+0.46875`
- ECE and Brier are each cut by about half

## Why This Closes The Measurement Gap

This is the direct joint pilot reviewers ask for:
- eta-only is already measured
- RLCR-only is already measured
- this run measures whether the two compose constructively on the same
  `14B ConflictBank conflict` slice

## Honest Status

The original queued pilot was followed by a corrected rerun after fixing an
evaluation-split bug. The result is now measured, not just predicted.
