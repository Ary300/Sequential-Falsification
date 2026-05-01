# Tier 1 / Tier 2 Experiment Closeout

This note records the status of the additional empirical asks requested after the theorem-3 audit.

## Finished now

### E2. Direct calibration of `eta_hat_eff`

Artifact:
- `docs/generated/theorem3_eta_proxy_identification.md`

Headline:
- Spearman correlation between true `eta` and mean `eta_hat_eff`: `1.0`
- Mean estimate is strictly monotone across `eta in {0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0}`
- Max mean relative error across the sweep: `0.0203`
- Grid points within 10% on the seed-mean estimate: `7/7`

Read:
- In the synthetic exponential-tilting environment, `eta_hat_eff` is not merely directional; it is a calibrated proxy at the aggregate level.

### E3. `sigma_r^2(c) * V(c)` correction term in KL units

Artifact:
- `docs/generated/theorem1_variance_correction_note.md`

Headline:
- Mean empirical correction KL: `1e-06` nat
- Max empirical correction KL: `1.4e-05` nat
- All analyzed bins are below `0.02` nat and below `0.10` nat

Read:
- On the benchmark-conditioned conflict scaffold, the variance correction is empirically tiny.
- This materially supports the practical use of the theorem-1 Bayes-optimal framing.

### E4. Powered head-to-head against `CoCoA`, `Astute RAG`, `Self-RAG`

Artifact:
- `docs/generated/powered_baseline_headtohead.md`

Headline:
- Powered comparison size: `7 benchmarks x 10 models x 3 seeds = 210 seeded series per baseline`
- Bayes vs `CoCoA`: mean regret gap `0.0426`, 95% bootstrap CI `[0.0405, 0.0445]`, wins `201/210`
- Bayes vs `Astute RAG`: mean regret gap `0.0318`, 95% bootstrap CI `[0.0302, 0.0333]`, wins `201/210`
- Bayes vs `Self-RAG`: mean regret gap `0.0219`, 95% bootstrap CI `[0.0019, 0.0395]`, wins `180/210`

Read:
- This closes the earlier "too much depends on small spotlight slicing" objection.
- `Self-RAG` still has the explicit `PopQA` reversal, but that now appears as a benchmark-specific caveat rather than an aggregate failure.

### E5. Frontier-scale validation promoted out of appendix status

Artifact:
- `docs/generated/frontier_validation_note.md`

Headline:
- Open-weight frontier-ish slices summarized: `Qwen2.5-32B-Instruct`, `Llama-3.1-70B-Instruct`, `DeepSeek-R1-Distill-Llama-70B`
- Closed API slices summarized: `GPT-4o-mini`, `Claude-3.5-Haiku`, `Gemini-1.5-Flash`
- All six model slices are positive on mean Bayes-vs-heuristic gain

Read:
- This is not the same as a fresh `405B` / `72B` experiment.
- It is still enough to support a stronger body-level frontier generalization paragraph than the previous appendix-only framing.

## Already finished earlier and still relevant

- Open Wikipedia retrieval probe:
  - `docs/generated/open_wikipedia_rag_probe_10.md`
- Spanish transfer probe:
  - `docs/generated/spanish_wikicontradict_probe_5.md`
- Theorem-3 proof support:
  - `docs/generated/theorem3_trace_separation_note.md`
  - `docs/generated/theorem3_answer_stability_note.md`
- Dense-grid theorem-3 headline read:
  - `docs/generated/theorem3_multiseed_headline_note.md`

## Not finished yet because they still require live training / long GPU runs

### E1. Clean matched-base `GRPO` vs `DPO`

Current status:
- Not completed
- No finished matched-base `GRPO` / `DPO` checkpoints exist in this repo yet

Why:
- This needs fresh training runs, not just analysis on existing artifacts

### E6. RLCR head-to-head

Current status:
- Not completed
- The full RLCR-style training-time jobs are still pending on Delta

Live Delta queue:
- `2224459` `t3_attnint` -> `PENDING`
- `2224460` `p2_r1l70` -> `PENDING`
- `2224461` `t3_rlcr14` -> `PENDING`

Reason:
- Scheduler `Priority`, not broken setup

## Honest bottom line

- The highest-feasibility empirical objections are now substantially closed with real finished artifacts.
- The two remaining asks that still need new long-running training are the matched-base `GRPO` vs `DPO` comparison and the full RLCR head-to-head.
- Everything else in this pass is no longer a to-do; it is now a committed result.
