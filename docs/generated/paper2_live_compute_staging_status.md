# Paper 2 Live Compute Staging Status

Status date: `2026-05-05` (late)

This note records the remaining live-compute Paper 2 items in a single place so
the bottleneck is explicit: launcher readiness versus cluster access.

## Fully staged launch paths

### DeepSeek-Llama-8B failure diagnosis

- native theorem-3 rerun:
  [submit_delta_theorem3_deepseek_llama8_native_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_eval.sh)
- token-level answer-margin / entropy mechanism probe:
  [submit_delta_deepseek_llama8_objective_followups.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_deepseek_llama8_objective_followups.sh)
- checkpointed curriculum audit:
  [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)
- local tokenizer / context sanity checker:
  [check_deepseek_llama8_tokenizer_context_sanity.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/check_deepseek_llama8_tokenizer_context_sanity.py)
- tokenizer / context note:
  [deepseek_llama8_tokenizer_context_sanity_check_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_tokenizer_context_sanity_check_note.md)

### Third independent matched-base RL pair beyond Llama lineage

- `Mistral-7B` matched `SFT/DPO/GRPO` trio:
  [submit_delta_theorem3_e1_mistral7_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_e1_mistral7_suite.sh)
- status note:
  [mistral7_matched_base_trio_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/mistral7_matched_base_trio_status.md)
- `Gemma-2-9B` matched `SFT/DPO/GRPO` trio:
  [submit_delta_theorem3_e1_gemma9_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_e1_gemma9_suite.sh)
- status note:
  [gemma9_matched_base_trio_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/gemma9_matched_base_trio_status.md)

### Early-`t` `\hat\rho^\star` and polynomial-tail checks

- dense tail trajectory:
  [submit_delta_theorem3_berk_nash_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_berk_nash_tail.sh)
- corrected dependent analysis:
  [submit_delta_berk_nash_rate_analysis.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_berk_nash_rate_analysis.sh)
- analyzer now supports both `tail` and `early` windows:
  [build_berk_nash_rate_empirical.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/build_berk_nash_rate_empirical.py)
- early-window readiness note:
  [berk_nash_early_window_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/berk_nash_early_window_status.md)

### Fourth-family spectral envelope

- `Llama-3.1-70B-Instruct` dense-tail launcher:
  [submit_delta_theorem3_llama70b_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_llama70b_tail.sh)

### 30-seed Llama-8B GRPO rerun

- multiseed launcher:
  [submit_delta_theorem3_llama8_grpo_30seed.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_llama8_grpo_30seed.sh)

### Larger-sample free-form open QA

- full free-form runner:
  [run_paper2_freeform_eval.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/run_paper2_freeform_eval.py)
- Delta submit wrapper:
  [submit_delta_paper2_freeform.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_paper2_freeform.sh)

## Already closed without new compute

- positive-subset `\hat{\Delta}_+` summaries
- eta-pool distribution summary from currently materialized local slices
- curvature proxy for the `C_{\mathrm{rob}}` shift story
- manuscript-side DPO citation, `\eta`-box architecture update, reproducibility
  checklist, anonymization sweep, broader impact

## Still missing as substantive results

- live results for the staged DeepSeek diagnostic reruns
- live results for the Mistral matched-base trio
- full dense-tail `W=100` `\hat\rho^\star` table
- fourth-family spectral-envelope output
- 30-seed Llama-8B GRPO aggregate CI
- larger-sample free-form `n=200` verdict is now in hand; the remaining free-form
  work is only if we want broader-domain expansion beyond `ASQA / NQ-open /
  TriviaQA-open`

## New live HDD-backed rerun wave

The original NVMe-backed reruns were being killed by allocation-quota writes on
`/work/nvme/bgvi`, not by model-side failures. The active recovery wave now
targets `/work/hdd/bgvi/adas17/tts_results` instead.

Submitted `2026-05-05`:

- `2245550`, `2245551`, `2245552`
  - `Mistral-7B` `SFT/DPO/GRPO` matched trio on HDD
- `2245553`
  - Qwen-14B dense tail rerun on HDD
- `2245554`, `2245555`, `2245556`
  - `Gemma-2-9B` `SFT/DPO/GRPO` matched trio on HDD
- `2245557`
  - `Llama-3.1-70B-Instruct` dense tail rerun on HDD
- `2245558`–`2245584`
  - `Llama-8B GRPO` seeds `45–71` on HDD
- `2245586`
  - DeepSeek native theorem-3 eval on HDD
- `2245587`
  - DeepSeek mechanism probe on HDD
- `2245588`, `2245589`
  - DeepSeek curriculum-audit pair on HDD

Current live read:

- running:
  - `2245550`, `2245551`, `2245552` (`Mistral-7B` HDD trio)
  - `2245553` (Qwen-14B dense tail on HDD)
  - `2245557` (`Llama-3.1-70B-Instruct` dense tail on HDD)
  - `2245587` (DeepSeek mechanism probe on HDD)
- pending:
  - `2245586` (DeepSeek native eval)
  - `2245588`, `2245589` (DeepSeek curriculum-audit pair)
  - `2245591` (HDD Berk–Nash dependent analysis, correctly held on dependency)
  - `2245558`–`2245584` (Llama-8B GRPO seeds `45–71`)
- blocked by model access rather than experiment logic:
  - `Gemma-2-9B` HDD trio hit gated Hugging Face access on Delta
  - so `Mistral-7B` is currently the active third-family recovery path

## Bottleneck

The missing ingredient is no longer code or Delta access.

Current verified bottlenecks:

- cluster queue time for the new HDD-backed rerun wave
- the over-quota NVMe allocation, which is why outputs were rerouted to HDD
- gated-model access for `google/gemma-2-9b-it` on Delta
