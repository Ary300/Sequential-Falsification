# Paper 2 Checklist Closeout

This note maps the reviewer-style Paper 2 checklist directly onto the finished
artifacts and live Delta jobs.

Status date: `2026-05-06`

## 1. `DeepSeek-R1-Distill-Llama-8B` matched `DPO/GRPO` pair

Status: `done`, with diagnostic rerun wave finished, native matched refresh closed, and a corrected rescue wave now active

Finished matched-base results:

- `DPO`
  - conflict ECE delta: `+0.0687`
  - no-conflict ECE delta: `+0.0429`
  - conflict-minus-no-conflict: `+0.0258`
- `GRPO`
  - conflict ECE delta: `+0.0687`
  - no-conflict ECE delta: `+0.1925`
  - conflict-minus-no-conflict: `-0.1239`

Read:

- This item is numerically closed.
- It does **not** give the desired second matched-base replication of the
  `Llama-8B` headline.
- The result is still useful because it rules out the stronger claim that the
  matched-base `GRPO` effect simply reproduces across every Llama-lineage `8B`
  family.
- The active follow-up is now diagnostic rather than rhetorical:
- The diagnostic wave now has real outputs, not just staging:
  - DeepSeek-native theorem-3 eval: conflict-minus-no-conflict `+0.0760`
  - DeepSeek mechanism probe: answer-margin diff-in-diff `-14.6593`
  - DeepSeek curriculum audits:
    - `DPO`: `-0.0699`
    - `GRPO`: `-0.0795`
- A final protocol-aligned matched-pair redo was also launched:
  - [submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh)
  - completed on Delta as:
    - `2248710` `r1l8dn_native_b005g8w2`: `DPO` `-0.0870`
    - `2248711` `r1l8gn_native_b005g8w2`: `GRPO` `-0.0229`
    - `2248712` `r1l8dn_native_b002g8w2`: `DPO` `-0.0405`
    - `2248713` `r1l8gn_native_b002g8w2`: `GRPO` `+0.0716`
  - read:
    this keeps the matched-objective training setup but swaps theorem-3 eval to
    DeepSeek-native completion-mode prompting, which is the cleanest remaining
    attempt to improve the `8B` story without changing the objective itself
- Updated read:
  - the earlier negative `GRPO` headline was partly protocol-sensitive
  - the DeepSeek-native matched sweep recovers a modest positive separation in
    one configuration (`GRPO` Pair B, `+0.0716`)
  - but it still does **not** rise to the clean `Llama-8B`-scale replication
    we were hoping for
- New May 6 update:
  - a real submit-path bug was found in the generic matched-objective Delta
    launcher:
    `WARMSTART_EPOCHS` was not being exported, so the earlier “extra
    warmstart” native sweep likely ran with `warmstart=1`
  - that means the weak native matched sweep is still informative, but it did
    not faithfully test the stronger warmstart settings it claimed to test
  - corrected rescue wave is now submitted:
    - initial IDs `2251775`–`2251779` were cancelled before start after the
      launcher-hardening pass landed
    - live corrected IDs are now:
      - `2251792` `r1l8dr_nativefix_b002g8w2`
      - `2251793` `r1l8gr_nativefix_b002g8w2`
      - `2251794` `r1l8dr_nativerescue_b001g12w3`
      - `2251798` `r1l8gr_nativerescue_b001g12w3`
      - `2251799` `r1l8gr_nativerescue_b001g16t06w3s43`
  - read:
    this is the strongest remaining honest attempt to repair the weak
    `DeepSeek-Llama-8B` matched-family story without changing the objective
    family itself
- The active follow-up is now diagnostic rather than rhetorical:
  - DeepSeek refresh wave:
    [deepseek_llama8_refresh_wave.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/deepseek_llama8_refresh_wave.md)
  - DeepSeek diagnosis note:
    [deepseek_llama8_failure_diagnosis_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_failure_diagnosis_note.md)
  - DeepSeek tokenizer / context sanity note:
    [deepseek_llama8_tokenizer_context_sanity_check_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_tokenizer_context_sanity_check_note.md)
  - DeepSeek curriculum-audit status:
    [deepseek_llama8_curriculum_audit_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_curriculum_audit_status.md)
  - DeepSeek mechanism launcher:
    [submit_delta_deepseek_llama8_objective_followups.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_deepseek_llama8_objective_followups.sh)
  - DeepSeek checkpointed curriculum launcher:
    [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)
  - DeepSeek-native theorem-3 eval rerun:
    [submit_delta_theorem3_deepseek_llama8_native_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_eval.sh)
  - DeepSeek-native matched-pair sweep:
    [submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_matched_sweep.sh)

## 2. Real `\hat{\rho}^\star` values for the Berk-Nash empirical table

Status: `in progress`, with updated dense-window read already recovered from the timed-out HDD dump

What is already done:

- Analysis script added:
  [build_berk_nash_rate_empirical.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_berk_nash_rate_empirical.py)
- Dense-tail launcher added:
  [submit_delta_theorem3_berk_nash_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_berk_nash_tail.sh)
- The analyzer now supports both:
  - tail-window fitting on the last `W` dense steps
  - early-window fitting on the first `W` dense steps for the requested
    non-asymptotic `\hat{\rho}^\star` check
- Early-window readiness note:
  [berk_nash_early_window_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/berk_nash_early_window_status.md)

Recovered dense-window read from the HDD rerun:

- source rows:
  `/work/hdd/bgvi/adas17/tts_results/results/theorem3_r1_14b_tail_trajectory_hdd_v1/theorem3_generation_rows.jsonl`
- latest regenerated analysis now uses `16186` rows
- cells analyzable from that live partial dump: `4`
- tail-window partial note:
  - `conflictbank conflict`: spectral radius `0.1396`, `rho*` `0.9996`
  - `conflictbank no_conflict`: spectral radius `0.1172`, `rho*` `0.9975`
  - `wikicontradict conflict`: spectral radius `0.3877`, `rho*` `0.9981`
  - `wikicontradict no_conflict`: spectral radius `0.4839`, `rho*` `1.0024`
- early-window partial note:
  - `conflictbank conflict`: spectral radius `0.3300`, `rho*` `0.9962`
  - `conflictbank no_conflict`: spectral radius `0.2465`, `rho*` `0.9965`
  - `wikicontradict conflict`: spectral radius `0.8157`, `rho*` `0.9979`
  - `wikicontradict no_conflict`: spectral radius `0.3590`, `rho*` `0.9972`

Current rerun status:

- the original NVMe-backed dense job failed because `/work/nvme/bgvi` was over
  allocation quota, not because the diagnostic itself was invalid
- corrected HDD-backed rerun submitted:
  - `2245553` `r1_14b_hdd`
  - scheduler end state: `TIMEOUT`
- direct analysis reruns submitted against the materialized HDD dump:
  - `2251744` `bn14htail`
  - `2251745` `bn14hearly`

Read:

- The missing thing was not “bad numbers”; it was dense trajectory completion
  under a quota-safe output path.
- Even the recovered live partial dump is already informative:
  early-window `rho*` stays very close to `1.0` across all four currently
  analyzable cells rather than collapsing immediately away from the
  tail, which is exactly the non-asymptotic direction we were hoping to see.
- The final `W=100` table still needs the direct analysis jobs to finish
  cleanly on Delta, but this item is no longer blocked on missing code or
  missing instrumentation.

## 3. Inference-cache demo for `\hat w`

Status: `done`

Source:
- [paper2_cache_demo_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_cache_demo_note.md)

Headline:

- cached queries covered: `91 / 91`
- current 4-pass incremental cost: `4.3791 s/query`
- projected `1` pass + cached weight lookup: `1.0948 s/query`
- conservative `2` passes + cached weight lookup: `2.1896 s/query`

Read:

- This objection is now directly answered with measured numbers.
- The deployment story is no longer “four passes forever”; it is “four passes
  in the current research harness, but about `1.5–2` effective passes online
  under stable retrieval with cached `\hat w`.”

## 4. `Phi-3` matched `SFT + DPO` with existing `GRPO`

Status: `done`

Finished matched-family results:

- `SFT`: conflict-minus-no-conflict `+0.2069`
- `DPO`: conflict-minus-no-conflict `+0.0030`
- `GRPO`: conflict-minus-no-conflict `+0.2088`

Read:

- This completes the missing row.
- It does **not** give the clean `GRPO > SFT` replication we hoped for, since
  `SFT` and `GRPO` are effectively tied at the family headline level.
- It still closes the “missing matched-family cells” complaint.

## 5. `DeepSeek-R1-Distill-Llama-70B` theorem-3 matrix

Status: `done`

Finished theorem-3 headline:

- conflict ECE delta: `-0.0111`
- no-conflict ECE delta: `-0.3992`
- conflict-minus-no-conflict: `+0.3881`

Read:

- This is a strong large-model Llama-lineage replication.
- It is one of the best surviving theorem-3 results in the repo.
- It strengthens the “reasoning/RL-conditioned Llama lineage” story even
  though the `8B` matched-family replication did not land cleanly.

## 5b. Third independent matched-base RL pair beyond Llama lineage

Status: `partially closed`

Finished `Mistral-7B` matched-base trio:

- `SFT`: `+0.1638`
- `DPO`: `-0.0316`
- `GRPO`: `-0.0324`

Read:

- This closes the missing third-family cells numerically.
- It does **not** provide the desired “third clean matched-base RL
  replication.”
- The next live recovery path is the corrected cache-backed `Gemma-2-9B`
  trio:
  - first cache-backed trio (`2246040`–`2246042`) finished training but the
    theorem-3 eval failed uniformly with `System role not supported`
  - eval-only completion-mode salvage jobs are now live:
    - `2246218` `g9sfix` has now completed
    - `2246219` `g9dfix` has now completed
    - `2246220` `g9gfix` has now completed
  - direct VLLM log read now shows repeated successful completion requests,
    confirming the backend mismatch is fixed
  - the recovery path is now producing real theorem-3 output:
    - `SFT` final (`1344` rows):
      conflict-minus-no-conflict `+0.1035`
    - `DPO` final (`1344` rows):
      conflict-minus-no-conflict `+0.0143`
    - `GRPO` completion-mode recovery is fully finished (`1344` rows):
      conflict-minus-no-conflict `-0.0680`
  - to give those higher-leverage `Gemma` and corrected `70B` jobs room to
    start, the expanded `Llama-8B` multiseed block was deliberately
    deprioritized by cancelling seeds `45–71` mid-queue

`Llama-3.1-70B-Instruct` fourth-family follow-up:

- the first lighter `2`-GPU rerun (`2246249`) still failed at startup, but the
  failure was infrastructural, not a model result:
  - VLLM / Torch compilation caches were still landing on quota-constrained
    space and triggered `[Errno 122] Disk quota exceeded`
  - that failure then surfaced in theorem-3 as `APIConnectionError:
    Connection refused`
- the shared real-generation Delta sbatch is now patched so heavyweight cache
  roots follow `DELTA_RESULTS_ROOT/runtime_cache`
- clean cache-fixed rerun submitted:
  - `2246302` `l3170h4`
  - this rerun has now started successfully
  - live Delta reads now show both screening rows and theorem-3 generation
    rows on disk, plus repeated `200 OK` chat completions from VLLM
  - current dense rows on disk: `19535`
  - latest theorem-3 partial is now on disk from the refreshed dense dump on
    `WikiContradict`:
    - conflict-minus-no-conflict `-0.0880`
- shorter-wall companion theorem-3 run submitted:
  - `2246377` `l3170t3`
  - this run has now completed with a real fourth-family headline:
    - conflict-minus-no-conflict `-0.0648`
  - purpose: get a fourth-family headline sooner while the dense-tail run
    continues, even if the result is currently negative

## 6. `Llama-3.1-8B GRPO` seeds `43, 44`

Status: `done`

Finished seed summaries:

- seed `42`: `+0.3436`
- seed `43`: `+0.0424`
- seed `44`: `-0.0647`

Read:

- This closes the single-seed objection numerically.
- The honest consequence is that the original seed is a strong discovery
  result, but the low-variance claim is weaker than the one-seed table
  suggested.
- The expanded corrected multiseed block is now live on Delta using cached
  local model snapshots instead of gated online pulls:
  - the earlier sweep was intentionally paused by cancelling seeds `45–71` so
    the higher-leverage `Gemma` and corrected `70B` runs could start under the
    available billing budget
  - the full seed block has now been re-armed on Delta as `2248714`–`2248743`
    so the 30-seed CI can close once queue priority allows it

## 7. Free-form open-QA larger sample (`n=8 -> n=200+`)

Status: `done`

What is already done:

- the free-form runner is real and Delta-safe:
  [run_paper2_freeform_eval.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_paper2_freeform_eval.py)
- smaller sequence-mixture runs are already on disk:
  [paper2_freeform_sequence_mixture_smoke_v2.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_freeform_sequence_mixture_smoke_v2.md)

Completed larger-sample runs:

- `2237724` `p2f200a`
  - sequence mixture baseline context build
- `2237725` `p2f200b`
  - richer retrieval/context variant

Best `n=200` read (`p2f200b`, richer context):

- `triviaqa_open` (`185` kept)
  - `Bayes`: EM `0.1405`, ROUGE-L `0.2871`
  - `AdaCAD`: EM `0.1405`, ROUGE-L `0.2808`
  - `CAD`: EM `0.0865`, ROUGE-L `0.2047`
  - `closed_book`: EM `0.1405`, ROUGE-L `0.2641`
- `nq_open` (`197` kept)
  - `Bayes`: EM `0.0863`, ROUGE-L `0.1858`
  - `AdaCAD`: EM `0.0863`, ROUGE-L `0.1863`
  - `CAD`: EM `0.0609`, ROUGE-L `0.1292`
  - `closed_book`: EM `0.0609`, ROUGE-L `0.1758`
- `asqa` (`199` kept)
  - `Bayes`: EM `0.0905`, ROUGE-L `0.1860`
  - `AdaCAD`: EM `0.0905`, ROUGE-L `0.1898`
  - `CAD`: EM `0.0754`, ROUGE-L `0.1781`
  - `closed_book`: EM `0.0854`, ROUGE-L `0.1958`

Read:

- The free-form objection is no longer “missing experiment,” and it is no
  longer an `n=8` anecdote either.
- On the larger sample, Bayes ties `AdaCAD` on EM across all three datasets,
  beats plain `CAD` across the board, and is clearly stronger than the earlier
  tiny-sample picture suggested.
- The honest remaining caveat is that closed-book remains competitive, so this
  is a strong “Bayes is viable and competitive in free-form” result rather
  than a universal “Bayes dominates every comparator on every metric” claim.

## 8. Polynomial-rate empirical check (Lemma E.21)

Status: `in progress`, with partial read already recovered

This is coupled to item `2`.

What is already done:

- the Qwen dense tail is now rerunning quota-safely on HDD:
  - `2245553` `r1_14b_hdd`
- direct follow-on analysis jobs are now submitted after the generator timeout:
  - `2251744` `bn14htail`
  - `2251745` `bn14hearly`
- the partial early/tail notes recovered from the materialized HDD dump are
  now a stronger preview than before because they cover `4` analyzable cells:
  - tail:
    - `conflictbank conflict`: spectral radius `0.1396`, `rho*` `0.9996`
    - `conflictbank no_conflict`: spectral radius `0.1172`, `rho*` `0.9975`
    - `wikicontradict conflict`: spectral radius `0.3877`, `rho*` `0.9981`
    - `wikicontradict no_conflict`: spectral radius `0.4839`, `rho*` `1.0024`
  - early:
    - `conflictbank conflict`: spectral radius `0.3300`, `rho*` `0.9962`
    - `conflictbank no_conflict`: spectral radius `0.2465`, `rho*` `0.9965`
    - `wikicontradict conflict`: spectral radius `0.8157`, `rho*` `0.9979`
    - `wikicontradict no_conflict`: spectral radius `0.3590`, `rho*` `0.9972`

- the new rate script fits both:
  - a log-linear `TV(p_t, p_K)` cross-check for `\hat{\rho}^\star`
  - a polynomial tail of the form `C / (q_1 + t)`

Read:

- The partial dense dump already shows that the polynomial fit is much weaker
  than the `rho*` cross-check on the currently available `WikiContradict`
  cells, so this is shaping up as a nuanced empirical story rather than an
  automatic win.
- The final answer still needs the HDD-backed dense rerun, but this item is
  now in “interpret the completed artifact” territory rather than “build the
  tooling first.”

## Strongest Finished Paper 2 Results

Already closed and good:

- poisoned/adversarial context:
  - Bayes context weight `0.9011 -> 0.3058`
  - `CAD` context weight `0.7910 -> 0.6963`
  - Bayes regret `0.3448` vs `CAD` `1.1714`
- counterfactual reliability ablation:
  - Spearman(noise rate, Bayes context weight) `-1.0`
- multi-document conflict scaling:
  - Bayes context weight falls `0.3534 -> 0.2967` as conflicting docs grow
- cache/latency story:
  - `4.3791 s/query` current 4-pass path
  - `~1.0948–2.1896 s/query` cached online projection
- large-model theorem-3 support:
  - `DeepSeek-Llama-70B` conflict-minus-no-conflict `+0.3881`

## Bottom Line

New low-compute camera-ready reaggregation note:

- [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)
  - powered `Δ̂_+` positive-subset summaries for `CoCoA`, `Astute RAG`, and
    `Self-RAG`
  - current local eta-tempering distribution summary
  - empirical finite-difference curvature proxy for the `C_rob` shift story

Closed now:

- `1`, `3`, `4`, `5`, `6`

Actively resolving now on Delta:

- `1` protocol-followup is now closed too:
  - `2248710`–`2248713` DeepSeek-native matched refresh sweep
- third-family reruns on HDD:
  - `2245550`, `2245551`, `2245552` Mistral `SFT/DPO/GRPO`
  - `2245554`, `2245555`, `2245556` Gemma `SFT/DPO/GRPO`
- dense/window reruns on HDD:
  - `2245553` Qwen-14B dense tail materialized and then timed out
  - `2251744`, `2251745` follow-on Berk–Nash tail/early analyses
  - `2246302` corrected Llama-70B dense tail still running
- multiseed expansion:
  - `2248714`–`2248743` Llama-8B GRPO seeds `42–71`

The only remaining blockers on this exact checklist are therefore:

- the HDD-backed matched-base reruns finishing
- the HDD-backed dense trajectory reruns finishing
- the full multiseed block finishing

That means the remaining work is compute-bound rather than implementation-bound.
