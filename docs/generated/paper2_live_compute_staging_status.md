# Paper 2 Live Compute Staging Status

Status date: `2026-05-06`

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
- native matched `DPO/GRPO` redo with completion-mode theorem-3 eval:
  [submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh)
- corrected rescue sweep after warmstart-export bug fix:
  [submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh)
- eval-only checkpoint launcher for rescue snapshots:
  [submit_delta_theorem3_deepseek_llama8_checkpoint_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_checkpoint_eval.sh)
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

- full dense-tail `W=100` `\hat\rho^\star` table
- corrected fourth-family spectral-envelope output for the intended
  `Llama-3.1-70B-Instruct` tail run
- 30-seed Llama-8B GRPO aggregate CI
- a clean third matched-base RL-family replication with the same direction as
  `Llama-8B`
- larger-sample free-form `n=200` verdict is already in hand; the remaining
  free-form work is only if we want broader-domain expansion beyond
  `ASQA / NQ-open / TriviaQA-open`

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

- completed:
  - `2245550`, `2245551`, `2245552`
    - `Mistral-7B` HDD trio is finished
    - headline separations:
      - `SFT`: `+0.1638`
      - `DPO`: `-0.0316`
      - `GRPO`: `-0.0324`
    - read: this closes the third-family cell numerically, but it is **not**
      the hoped-for clean `GRPO` replication
  - `2245586`
    - DeepSeek native theorem-3 eval finished at `+0.0760`
  - `2245587`
    - DeepSeek mechanism probe finished
    - answer-margin diff-in-diff: `-14.6593`
    - read: this is again a margin-reallocation story, not an entropy-collapse
      story
  - `2245588`, `2245589`
    - DeepSeek curriculum-audit pair finished
    - final separations:
      - `DPO` curriculum audit: `-0.0699`
      - `GRPO` curriculum audit: `-0.0795`
  - `2246040`, `2246041`, `2246042`
    - initial cache-backed `Gemma-2-9B` trio finished training but the theorem-3
      eval path produced `1344` generation errors per run
    - root cause: local VLLM/OpenAI chat path rejected `system` role messages
      (`400: System role not supported`)
- completed:
  - `2245553`
    - Qwen-14B dense tail on HDD
    - final scheduler state: `TIMEOUT` after `18:00:09`
    - the important point is that the run still materialized a much larger
      dense dump before timing out
    - current regenerated analysis uses `16186` rows across `4` analyzable
      cells
    - early-window `rho*` remains very close to `1.0` on all four cells
    - tail-window `rho*` also remains close to `1.0`, though the current
      log-linear fits are still noisy
  - `2246302`
    - fresh `Llama-3.1-70B-Instruct` dense-tail rerun after cache-root fix
    - current state is now running
    - it is already writing screening and theorem-3 generation rows on HDD
    - direct VLLM log read shows repeated `POST /v1/chat/completions 200 OK`
    - current rows on disk: `19535`
    - latest live partial theorem-3 summary is now on disk from the refreshed
      dense dump on `WikiContradict`:
      conflict-minus-no-conflict `-0.0880`
- completed:
  - `2246218`
    - `Gemma-2-9B SFT` completion-mode theorem-3 recovery job finished
    - theorem-3 headline is now real:
      conflict-minus-no-conflict `+0.1035`
  - `2246219`
    - `Gemma-2-9B DPO` completion-mode recovery job finished
    - theorem-3 headline is now real:
      conflict-minus-no-conflict `+0.0143`
  - `2246220`
    - `Gemma-2-9B GRPO` completion-mode recovery job finished
    - theorem-3 headline is now materially real, not just partial:
      conflict-minus-no-conflict `-0.0680`
- completed:
  - `2248710`–`2248713`
    - DeepSeek-native matched `DPO/GRPO` redo pair
    - `2248710` `r1l8dn_native_b005g8w2`: `DPO` `-0.0870`
    - `2248711` `r1l8gn_native_b005g8w2`: `GRPO` `-0.0229`
    - `2248712` `r1l8dn_native_b002g8w2`: `DPO` `-0.0405`
    - `2248713` `r1l8gn_native_b002g8w2`: `GRPO` `+0.0716`
    - read:
      this was the cleanest remaining protocol-aligned attempt to rescue the
      weak `DeepSeek-Llama-8B` matched-family story
    - outcome:
      the native matched sweep improves the family from uniformly weak to mixed
      with one mildly positive `GRPO` configuration, but it still does **not**
      become a clean `Llama-8B`-scale replication
- pending:
  - `2251775`
    - `r1l8dr_nativefix_b002g8w2`
    - corrected `DPO` rerun of the best prior native pocket with the intended
      `warmstart=2` now actually forwarded
  - `2251776`
    - `r1l8gr_nativefix_b002g8w2`
    - corrected `GRPO` rerun of the best prior native pocket with the intended
      `warmstart=2` now actually forwarded
  - `2251777`
    - `r1l8dr_nativerescue_b001g12w3`
    - softer-regularization `DPO` rescue leg with larger group budget and
      `warmstart=3`
  - `2251778`
    - `r1l8gr_nativerescue_b001g12w3`
    - softer-regularization `GRPO` rescue leg with larger group budget and
      `warmstart=3`
  - `2251779`
    - `r1l8gr_nativerescue_b001g16t06w3s43`
    - exploratory cooler-sampling `GRPO` rescue leg with a fresh seed
  - read:
    these jobs exist because a real submit-path bug was found:
    `WARMSTART_EPOCHS` was not being exported through the generic
    matched-objective Delta wrapper, so the earlier native sweep likely ran
    under a weaker warmstart than intended
- pending:
  - `2251744`
    - direct HDD Berk–Nash tail analysis rerun after the dense generator
      timeout
  - `2251745`
    - direct HDD Berk–Nash early-window analysis rerun after the dense
      generator timeout
  - `2248714`–`2248743`
    - re-armed `Llama-8B GRPO` seed block covering seeds `42–71`
    - read:
      the earlier queue cancellations were tactical; this block is now back in
      the queue so the 30-seed anchor CI can close once cluster priority allows
- completed:
  - `2246377`
    - shorter-wall `Llama-3.1-70B-Instruct` standard theorem-3 companion run
    - finished with a real fourth-family headline:
      conflict-minus-no-conflict `-0.0648`
    - read:
      this closes the quicker fourth-family path numerically, but the result is
      currently negative rather than headline-strength positive
- deliberately deprioritized to free billing budget for higher-leverage jobs:
  - `2246047`–`2246054`
    - running `Llama-8B` seeds `49–56` were cancelled
  - `2246043`–`2246046`
    - running `Llama-8B` seeds `45–48` were also cancelled once it was clear
      they were blocking the `Gemma`/`70B` recovery queue
  - `2246055`–`2246069`
    - remaining queued `Llama-8B` seeds `57–71` were cancelled as well so the
      corrected `Gemma` and lighter `70B` jobs could start immediately
  - read:
    - this was a conscious queue tradeoff, not a failure of the seed path
    - the goal was to let the third-family and fourth-family closeout jobs
      actually start instead of sitting behind the 30-seed block
- corrected after launch-path diagnosis:
  - `2245557` completed, but it was **not** the intended fourth-family run
  - root cause: the wrapper exported `TAIL_*` names while the downstream submit
    script only read `MODEL/OUTPUT_DIR/...`, so the job silently fell back to
    the default `DeepSeek-R1-Distill-Qwen-7B` real-generation path
  - fixed locally and on GitHub in
    [submit_delta_theorem3_llama70b_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_llama70b_tail.sh)
- corrected after model-access diagnosis:
  - `Gemma-2-9B` and the expanded `Llama-8B` seed jobs originally failed on
    gated Hugging Face fetches
  - both launchers now resolve cached local snapshot paths from
    `~/.cache/huggingface/hub` before falling back to repo IDs
- corrected after backend-format diagnosis:
  - matched-objective theorem-3 evals can now choose `EVAL_REQUEST_FORMAT` and
    `EVAL_PROMPT_PROTOCOL`
  - the `Gemma-2-9B` suite now defaults to completion-mode eval to avoid the
    unsupported `system`-role chat path
  - the recovery path is now producing stable theorem-3 output:
    - `SFT` final (`1344` rows):
      conflict-minus-no-conflict `+0.1035`
    - `DPO` final (`1344` rows):
      conflict-minus-no-conflict `+0.0143`
    - `GRPO` recovery is now complete (`1344` rows):
      conflict-minus-no-conflict `-0.0680`
- corrected after queue-shape diagnosis:
  - the original `4`-GPU `Llama-3.1-70B-Instruct` rerun was cancelled
  - it was replaced with a lighter `2`-GPU / `TP=2` variant so the
    fourth-family job could start sooner under the Delta billing budget
  - the first lighter rerun (`2246249`) still failed at startup because VLLM /
    Torch compilation caches were defaulting to quota-constrained space
  - the shared real-generation sbatch now routes `HF_HOME`, `XDG_CACHE_HOME`,
    `TORCHINDUCTOR_CACHE_DIR`, and `TRITON_CACHE_DIR` under
    `DELTA_RESULTS_ROOT/runtime_cache`
  - clean cache-fixed rerun submitted as `2246302` and is now running
  - live log evidence confirms the server is healthy rather than silently
    failing at startup
  - shorter-wall companion theorem-3 run submitted as `2246377`

## Bottleneck

The missing ingredient is no longer code or Delta access.

Current verified bottlenecks:

- cluster queue time for the remaining Delta jobs
- completion time for the running dense `Llama-3.1-70B-Instruct` rerun
- completion time for the re-armed multiseed `Llama-8B` block
- final direct Berk–Nash tail/early analysis completion after the materialized
  Qwen dense dump
