# Mistral-7B Matched-Base Trio Status

Status date: `2026-05-03`

This note tracks the third independent matched-base family launched beyond the
Llama lineage.

## Why Mistral-7B

`Mistral-7B` is the cleanest fast third-family candidate in the current stack:

- smaller and cheaper than `Gemma-2-9B`
- already present throughout the repo as a stable control family
- does not introduce the extra interpretation wrinkle of another larger dense
  family while the goal is simply to close the matched-base complaint

## Live jobs

- `2238132` `e1_m7_sft`
  - matched `SFT` control
  - output dir: `results/e1_mistral7_sft_control`

- `2238136` `e1_m7_dpo`
  - matched `DPO`
  - output dir: `results/e1_mistral7_dpo`

- `2238139` `e1_m7_grpo`
  - matched `GRPO`
  - output dir: `results/e1_mistral7_grpo`

## Shared setup

- model: `mistralai/Mistral-7B-Instruct-v0.3`
- source / train / val / eval rows: `800 / 560 / 80 / 80`
- theorem-3 eval:
  - `WikiContradict` max `96`
  - `ConflictBank` max `128`
  - `cot=0/128/1024`

Control / objective schedule:

- `SFT` control:
  - warmstart epochs: `2`
  - objective epochs: `0`
- `DPO`:
  - warmstart epochs: `1`
  - objective epochs: `1`
- `GRPO`:
  - warmstart epochs: `1`
  - objective epochs: `1`

## Read

- This is the fastest honest route to a third independent matched-base family.
- It does not assume the result will be positive.
- It exists to replace the current situation where only `Llama-8B` is a clean
  matched-base anchor and both `DeepSeek-Llama-8B` and `Phi-3` leave ambiguity.
