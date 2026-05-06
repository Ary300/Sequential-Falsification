# Retraining Extension Plan

This is the concrete next-wave plan for the optional retraining-style extension beyond eta-tempered decoding.

## Why This Is The Right Next Step

- The current method-only intervention already improves `ConflictBank` 14B conflict from accuracy `0.0367` to `0.4400` and overconfidence gap `0.9372` to `0.5205`.
- The current method-only intervention already improves `WikiContradict` conflict from gap `0.3283` to `0.3182`.
- The remaining gap is therefore no longer “missing a method”; it is the classic RLCR-style question of whether training can repair the residual calibration pathology that test-time eta scaling cannot fully remove.

## Priority Models

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- `deepseek-ai/DeepSeek-R1-Distill-Llama-70B`

## Priority Benchmarks

- `ConflictBank`
- `WikiContradict`
- `GPQA`
- `CLIMATEX`

## Training Recipe

- Objective: accuracy reward plus explicit Brier-style calibration reward.
- Avoid: pure binary GRPO reward without uncertainty credit.
- Reward terms:
- `verifiable answer correctness`
- `negative Brier score on reported answer probability`
- `optional penalty for confidence when the answer is wrong`

Comparison arms:
- `baseline reasoning model`
- `eta-tempered decoding only`
- `Brier-reward finetune only`
- `Brier-reward finetune plus eta-tempered decoding`

## Success Targets

- `ConflictBank` 14B conflict overconfidence-gap target: `<= 0.35`.
- `ConflictBank` 14B conflict accuracy floor: `>= 0.44`.
- `WikiContradict` conflict overconfidence-gap target: `<= 0.3`.
- The retrained model should beat the method-only eta-tempered run on the `ConflictBank` 14B conflict slice.

## Honest Constraint

- This extension requires fresh external training compute and cannot be truthfully completed from the current local-only session.
- What is finished here is the concrete experimental recipe, targets, and comparison arms, so the remaining blocker is only compute, not ambiguity.
