# Gemma-2-9B Matched-Base Trio Status

Status date: `2026-05-05`

This note defines the dedicated Paper 2 matched-base `SFT/DPO/GRPO` launcher
for `Gemma-2-9B`, mirroring the existing `Mistral-7B` trio structure so we can
run a third independent family beyond the Llama lineage with the same training
budget and theorem-3 readout.

## Purpose

- close the “single clean matched-base family” complaint with a second
  non-Llama-lineage controlled trio
- keep the setup aligned with the existing `Llama-8B` and `Mistral-7B` matched
  objective runs
- preserve a like-for-like theorem-3 output layout for downstream comparison

## Shared setup

- launcher: `scripts/submit_delta_theorem3_e1_gemma9_suite.sh`
- model: `google/gemma-2-9b-it`
- source / train / val / eval rows: `800 / 560 / 80 / 80`
- decoding:
  - temperature: `0.8`
  - top-p: `0.95`
  - max model len: `4096`
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

## Expected output dirs

- `SFT` control:
  - `results/e1_gemma9_sft_control`
- `DPO`:
  - `results/e1_gemma9_dpo`
- `GRPO`:
  - `results/e1_gemma9_grpo`

Expected job names:

- `e1_g9_sft`
- `e1_g9_dpo`
- `e1_g9_grpo`

## Recovery outcome

The initial cache-backed theorem-3 eval path failed uniformly because the local
VLLM / OpenAI compatibility layer rejected `system` role messages.

The recovery path switched Gemma theorem-3 eval to completion-mode requests and
then reran evaluation on Delta. Final recovered theorem-3 headlines:

- `SFT`: conflict-minus-no-conflict `+0.1035`
- `DPO`: conflict-minus-no-conflict `+0.0143`
- `GRPO`: conflict-minus-no-conflict `-0.0680`

Read:

- this closes the `Gemma-2-9B` matched-base family with real theorem-3 numbers
- the family is mixed rather than giving the clean `GRPO > SFT` replication we
  wanted
- it still materially improves the Paper 2 “third independent family”
  evidence because the cells are now closed rather than pending

## Read

- This launcher is a direct Gemma analogue of the Mistral matched-base trio.
- It does not assume the result will be positive.
- It exists to give Paper 2 a dedicated non-Llama matched-base family with the
  same control/objective structure and output conventions as the other trio
  launchers.
