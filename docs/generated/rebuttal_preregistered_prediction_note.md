# Rebuttal-Timestamped Prediction Note

This note freezes two new prospective predictions before the remaining matched-family follow-up jobs finish. The timestamp is the Git commit that first introduces this note.

## Predictions

- `P4` (`DeepSeek-Llama-8B matched GRPO recovery`):
  - On the completed matched-base `DeepSeek-R1-Distill-Llama-8B` family, the recovered `GRPO` theorem-3 run will show a positive conflict-minus-no-conflict ECE separation of at least `+0.20`.
  - Stronger version: the recovered `GRPO` separation will exceed the finished matched `DPO` separation by at least `+0.15`.
  - Reference finished `DPO` value: `+0.0258`.

- `P5` (`Phi-3 matched SFT control`):
  - The new matched `Phi-3 SFT` control will remain weak, with conflict-minus-no-conflict ECE separation below `+0.08`.
  - Therefore the already-finished matched `Phi-3 GRPO` row (`+0.2088`) will exceed the matched `SFT` control by at least `+0.12`, preserving the family-level ordering `GRPO > SFT`.

## Linked jobs

- `DeepSeek-Llama-8B GRPO` eval recovery: `r1l8_grev`
- `Phi-3` matched `SFT` control: `e1_p3_sft`

## Why these are the right predictions

- `P4` directly targets the biggest remaining theorem-3 replication complaint: a second matched-base RL family.
- `P5` converts the existing `Phi-3 GRPO` row from an incomplete two-point family into a matched-family ordering test.

## Read

- This is not meant to erase the earlier post-hoc `P3` stain.
- It is meant to add a clean prospective timestamped prediction tied to runs that are not yet resolved at commit time.
