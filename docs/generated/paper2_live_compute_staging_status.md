# Paper 2 Live Compute Staging Status

Status date: `2026-05-04`

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

### Third independent matched-base RL pair beyond Llama lineage

- `Mistral-7B` matched `SFT/DPO/GRPO` trio:
  [submit_delta_theorem3_e1_mistral7_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_e1_mistral7_suite.sh)
- status note:
  [mistral7_matched_base_trio_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/mistral7_matched_base_trio_status.md)

### Early-`t` `\hat\rho^\star` and polynomial-tail checks

- dense tail trajectory:
  [submit_delta_theorem3_berk_nash_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_berk_nash_tail.sh)
- corrected dependent analysis:
  [submit_delta_berk_nash_rate_analysis.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_berk_nash_rate_analysis.sh)

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
- larger-sample free-form `n=200` verdict

## Bottleneck

The missing ingredient is no longer code. It is live Delta access: the current
cluster blocker is authentication failing before Duo, so the compute cannot be
polled or resubmitted from this shell until login succeeds.
