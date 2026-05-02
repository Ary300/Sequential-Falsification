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

## Submitted Delta Job

- Job id: `2230787`
- Job name: `rlcr_eta_joint`
- State at submission check: `PENDING`
- Reason: `Priority`
- Time limit: `08:00:00`
- Requested resources: `1 GPU`, `16 CPU`, `191592M` RAM

## Why This Closes The Measurement Gap

This is the direct joint pilot reviewers ask for:
- eta-only is already measured
- RLCR-only is already measured
- this run measures whether the two compose constructively on the same
  `14B ConflictBank conflict` slice

## Honest Status

The pilot is now defined and queued against the exact finished RLCR artifacts.
The remaining blocker is scheduler time, not missing code or experiment design.
