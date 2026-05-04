# Paper 2 Checklist Closeout

This note maps the reviewer-style Paper 2 checklist directly onto the finished
artifacts and live Delta jobs.

Status date: `2026-05-03`

## 1. `DeepSeek-R1-Distill-Llama-8B` matched `DPO/GRPO` pair

Status: `done`, with diagnostic rerun wave active

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
  - DeepSeek refresh wave:
    [deepseek_llama8_refresh_wave.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/deepseek_llama8_refresh_wave.md)
  - DeepSeek diagnosis note:
    [deepseek_llama8_failure_diagnosis_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_failure_diagnosis_note.md)
  - DeepSeek curriculum-audit status:
    [deepseek_llama8_curriculum_audit_status.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/docs/generated/deepseek_llama8_curriculum_audit_status.md)
  - DeepSeek mechanism launcher:
    [submit_delta_deepseek_llama8_objective_followups.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_deepseek_llama8_objective_followups.sh)
  - DeepSeek checkpointed curriculum launcher:
    [submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_curriculum_audit.sh)
  - DeepSeek-native theorem-3 eval rerun:
    [submit_delta_theorem3_deepseek_llama8_native_eval.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_eval.sh)

## 2. Real `\hat{\rho}^\star` values for the Berk-Nash empirical table

Status: `in progress`

What is already done:

- Analysis script added:
  [build_berk_nash_rate_empirical.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_berk_nash_rate_empirical.py)
- Dense-tail launcher added:
  [submit_delta_theorem3_berk_nash_tail.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_berk_nash_tail.sh)

Live jobs:

- `2237713` `r1_14b_tail`
  - dense `R1-14B` theorem-3 trajectory run
- `2237950` `bn14b_ana`
  - corrected dependent analysis job that will build the rate note from the
    finished rows

Current coarse sanity check on the old `3`-point artifact:

- source rows: `/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl`
- cells analyzed: `4`
- tail steps available: only `3`, so the current coarse pass can estimate a
  local spectral radius but not the requested `W=100` log-TV or polynomial
  tail cleanly

Read:

- The missing thing was not “bad numbers”; it was missing dense trajectory
  instrumentation.
- A submission-path bug in the first dependent analysis job was fixed before
  tail completion; the live follow-up now uses the correct `--json-out` /
  `--md-out` flags expected by the analyzer.
- This item is now on the right path and should resolve as soon as
  `2237713 -> 2237950` completes.

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

## 7. Free-form open-QA larger sample (`n=8 -> n=200+`)

Status: `in progress`

What is already done:

- the free-form runner is real and Delta-safe:
  [run_paper2_freeform_eval.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_paper2_freeform_eval.py)
- smaller sequence-mixture runs are already on disk:
  [paper2_freeform_sequence_mixture_smoke_v2.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_freeform_sequence_mixture_smoke_v2.md)

Live jobs:

- `2237724` `p2f200a`
  - `n=200`, current best sequence-mixture config
- `2237725` `p2f200b`
  - `n=200`, richer retrieval/context variant

Current small-sample read:

- `ASQA`: mixed but positive for Bayes vs `CAD`
- `NQ-open`: improved from the earlier zero-EM branch
- `TriviaQA-open`: still weak

Read:

- The free-form objection is no longer “missing experiment.”
- The remaining question is whether the larger sample cleans up the mixed
  small-sample direction strongly enough for a headline claim.

## 8. Polynomial-rate empirical check (Lemma E.21)

Status: `in progress`

This is coupled to item `2`.

What is already done:

- the new rate script fits both:
  - a log-linear `TV(p_t, p_K)` cross-check for `\hat{\rho}^\star`
  - a polynomial tail of the form `C / (q_1 + t)`

Live jobs:

- `2237713` `r1_14b_tail`
- `2237950` `bn14b_ana`

Read:

- Once the dense-tail rows land, the polynomial-rate check will be computed in
  the same analysis pass as the Berk-Nash table.
- So items `2` and `8` are now blocked by the same queued trajectory artifact,
  not by missing code.

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

- `2`, `7`, `8`

The only remaining blockers on this exact checklist are therefore:

- dense `R1-14B` tail trajectories finishing
- the larger `n=200` free-form runs finishing

That means the remaining work is compute-bound rather than implementation-bound.
