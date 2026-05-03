# Final Empirical Results Sheet

This is the compact one-file summary of the current empirical package for the knowledge-arbitration paper.

## Review-Facing Uncertainty Note

Bootstrap-over-prompt confidence intervals are now materialized in:
- [theorem3_review_followups.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_review_followups.md)
- [theorem3_open_item_followups.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_open_item_followups.md)

The practical read is:
- strong positive conflict-conditioned separations that clearly survive the bootstrap:
  - `Llama-8B GRPO`: `+0.3436`, 95% CI `[0.2297, 0.4757]`
  - `RLCR`: `+0.2910`, 95% CI `[0.1999, 0.3827]`
  - `Phi-3 GRPO`: `+0.2088`, 95% CI `[0.1208, 0.3051]`
  - `DeepSeek-Llama-8B`: `+0.0775`, 95% CI `[0.0147, 0.1435]`
- weak / ambiguous small-family separations that should not be over-ordered:
  - `Mistral-7B`: `+0.0150`, CI crosses `0`
  - `Gemma-27B`: `-0.0168`, CI crosses `0`
  - `Qwen GRPO`: `+0.0082`, CI crosses `0`
  - `OLMo-2 DPO/GRPO`: both separation CIs cross `0`

Read:
- the paper should present the small control-family deltas as mostly flat or weak rather than pretending that their exact ranking is meaningful.
- the sharp positive theorem-3 separations survive on the families that matter most for the main story.

## Headline Theorem 3 Results

### Matched-base objective split: `Llama-8B`

- `DPO`
  - Conflict ECE delta: `-0.1051`
  - No-conflict ECE delta: `-0.1499`
- `GRPO`
  - Conflict ECE delta: `+0.2641`
  - No-conflict ECE delta: `-0.0796`
  - Conflict minus no-conflict ECE delta: `+0.3436`

Read:
- This is the strongest clean causal theorem-3 result in the package.
- On the same base family, `DPO` improves or stabilizes calibration, while `GRPO` sharply worsens conflict long-CoT calibration.

### Training-time mitigation: `RLCR`

- Mean conflict ECE delta: `+0.1454`
- Mean no-conflict ECE delta: `-0.1456`
- Conflict minus no-conflict ECE delta: `+0.2911`
- Mean conflict overconfidence-gap delta: `+0.1845`
- Mean no-conflict overconfidence-gap delta: `-0.1527`

Read:
- `RLCR` helps materially on no-conflict slices.
- `RLCR` does not remove the hardest controlled-conflict failure mode.

### Joint pilot: `RLCR + eta-tempering`

- Slice: `ConflictBank / conflict_context / cot=1024`
- Baseline `eta=1.0`
  - Accuracy: `0.0625`
  - ECE: `0.903553`
  - Brier: `0.886175`
- Selected `eta=0.0`
  - Accuracy: `0.53125`
  - ECE: `0.431058`
  - Brier: `0.414764`

Read:
- The joint intervention is now directly measured, not just predicted.
- On the hardest headline slice, the composition helps a lot: accuracy jumps and both ECE and Brier are roughly halved.
- In the full benchmark breakdown, the gain is mostly a `ConflictBank` story rather than a uniform everywhere-improvement story.

### Clean non-RL control: `Mistral-7B`

- Mean conflict ECE delta: `+0.0162`
- Mean no-conflict ECE delta: `+0.0011`
- Conflict minus no-conflict ECE delta: `+0.0150`

Read:
- `Mistral` shows only a small conflict-specific worsening.
- This is useful as a non-RL control family.

### Extra-family controls: `Gemma`

`Gemma-9B`
- Mean conflict ECE delta: `+0.0063`
- Mean no-conflict ECE delta: `-0.0289`
- Conflict minus no-conflict ECE delta: `+0.0352`

`Gemma-27B`
- Mean conflict ECE delta: `-0.0010`
- Mean no-conflict ECE delta: `+0.0159`
- Conflict minus no-conflict ECE delta: `-0.0169`

Read:
- The Gemma results strengthen the family-dependent story.
- Neither Gemma model shows the dramatic conflict-amplified pattern seen in `Llama-8B GRPO`.

### Repaired Qwen results

`Qwen DPO`
- Mean conflict ECE delta: `+0.1838`
- Mean no-conflict ECE delta: `+0.1185`
- Conflict minus no-conflict ECE delta: `+0.0653`

`Qwen GRPO`
- Mean conflict ECE delta: `+0.0108`
- Mean no-conflict ECE delta: `+0.0026`
- Conflict minus no-conflict ECE delta: `+0.0082`

Read:
- `Qwen` is no longer malformed or parser-broken.
- `Qwen` remains mixed and family-specific.
- It is supporting evidence, not the strongest headline family.

### Third-family tie-break: `Phi-3` and `OLMo-2`

Pooled `Phi-3 DPO`:
- Mean conflict ECE delta: `-0.0507`
- Mean no-conflict ECE delta: `-0.0537`
- Conflict minus no-conflict ECE delta: `+0.0030`

Pooled `Phi-3 GRPO`:
- Mean conflict ECE delta: `-0.1000`
- Mean no-conflict ECE delta: `-0.3087`
- Conflict minus no-conflict ECE delta: `+0.2088`

Important benchmark-level note:
- the pooled `Phi-3` summary hides a much sharper `ConflictBank` split
- on `ConflictBank`, `Phi-3 GRPO` worsens the `conflict` split while strongly improving `no_conflict`
- see [phi3_conflictbank_tiebreak_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/phi3_conflictbank_tiebreak_note.md)

Pooled `OLMo-2 DPO`:
- Mean conflict ECE delta: `+0.0952`
- Mean no-conflict ECE delta: `+0.0469`
- Conflict minus no-conflict ECE delta: `+0.0483`

Pooled `OLMo-2 GRPO`:
- Mean conflict ECE delta: `+0.0027`
- Mean no-conflict ECE delta: `-0.0226`
- Conflict minus no-conflict ECE delta: `+0.0254`

Read:
- `OLMo-2` is weaker and less decisive than `Phi-3`.
- It does not give the same sharp benchmark-level replication signal that
  `Phi-3 GRPO` gives on `ConflictBank`.

### Llama-lineage replication: `DeepSeek-R1-Distill-Llama-8B`

- Mean conflict ECE delta: `+0.0080`
- Mean no-conflict ECE delta: `-0.0696`
- Conflict minus no-conflict ECE delta: `+0.0776`
- Mean conflict overconfidence-gap delta: `+0.0007`
- Mean no-conflict overconfidence-gap delta: `-0.0242`

Important benchmark-level note:
- on `ConflictBank`, the split is very clean
- `conflict`: ECE `0.9353 -> 0.9663`
- `no_conflict`: ECE `0.1412 -> 0.0264`

Read:
- This is a useful Llama-lineage replication.
- It does not match the full magnitude of `Llama-8B GRPO`, but it preserves the
  same directional story: conflict stays bad while no-conflict improves a lot.

### Large Llama-lineage replication: `DeepSeek-R1-Distill-Llama-70B`

- Mean conflict ECE delta: `-0.0111`
- Mean no-conflict ECE delta: `-0.3992`
- Conflict minus no-conflict ECE delta: `+0.3881`
- Mean conflict overconfidence-gap delta: `-0.0163`
- Mean no-conflict overconfidence-gap delta: `-0.4000`

Important benchmark-level note:
- this full theorem-3 matrix covers `1344` rows across `ConflictBank` and
  `WikiContradict`
- the separation is driven mainly by very large no-conflict improvement while
  conflict stays near-flat

Read:
- This is a strong large-model Llama-lineage replication.
- It is actually larger than the original `Llama-8B GRPO` separation on the
  pooled theorem-3 headline metric.
- The clean high-level story now is that plain instruct `Llama` stays flat even
  at `70B`, while the reasoning-distilled `DeepSeek-Llama` lineage stays
  strongly positive.

### Plain-scale control: `Llama-3.1-70B-Instruct`

- Mean conflict ECE delta: `-0.0219`
- Mean no-conflict ECE delta: `+0.0198`
- Conflict minus no-conflict ECE delta: `-0.0418`

Read:
- Plain instruct `Llama` stays flat-to-negative even at `70B`.
- This strengthens the claim that scale alone does not recover the
  conflict-conditioned theorem-3 effect; the stronger signal lives in the
  RL/reasoning-conditioned Llama lineage instead.

## Theorem 3 Assumption Audits

### Proposition 1 audit bridge

Source:
- [proposition1_empirical_audits.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/proposition1_empirical_audits.md)

Read:
- The proposition-1 reduction hypotheses are now explicitly audited in the real
  decoding setting through answer stability and trace-likelihood separation.

### Answer stability

Source:
- [theorem3_answer_stability_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_answer_stability_note.md)

Headline:
- `ConflictBank` conflict fully stable across `cot=0/128/1024`: `0.08`
- Stable `0 -> 128`: `0.098`
- Stable `128 -> 1024`: `0.364`
- On stable subsets, confidence gap still rises with `0.0` mean accuracy change

Read:
- The answer-stability condition is narrow, not generic.
- Within the stable subset, the theorem-3 mechanism behaves as predicted.

### Self-confirming trace separation

Source:
- [theorem3_trace_separation_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_trace_separation_note.md)

Headline:
- Current answer state beats strongest competitor: `0.81`
- Mean margin: `10.7513`
- Incorrect-example win fraction: `0.8081`

Read:
- Traces are usually more likely under the currently selected answer state than under the strongest competitor.
- This supports the self-confirming mechanism rather than pure truth-tracking.

## Eta / Calibration Follow-ups

### Eta-proxy identification

Source:
- [theorem3_eta_proxy_identification.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_eta_proxy_identification.md)

Headline:
- Spearman correlation: `1.0`
- Max mean relative error: `0.0203`
- Grid points within `10%`: `7/7`

Read:
- In the controlled exponential-tilting environment, `eta_hat_eff` is a calibrated aggregate proxy.

### Eta-tempered baselines vs standard calibrators

Source:
- [theorem3_calibration_baselines.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_calibration_baselines.md)

Headline on the `14B ConflictBank conflict` slice:
- Identity Brier: `0.924083`
- Eta-tempering Brier: `0.530564`
- Temperature-scaling Brier: `0.67548`
- Platt-scaling Brier: `0.01666`
- Isotonic Brier: `0.016379`

Read:
- Eta-tempering improves materially over the raw identity confidence.
- Standard post-hoc calibrators still beat eta-tempering on pure Brier here.
- The honest method claim is theory-derived post-trace repair, not best generic calibrator.

### Reliability diagrams

Artifacts:
- [build_theorem3_reliability_figure.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_theorem3_reliability_figure.py)

Read:
- Explicit Yoon-style reliability diagrams and matching bin-frequency histograms are part of the theorem-3 reporting path.

### RLCR + eta per-benchmark breakdown

Source:
- [theorem3_review_followups.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_review_followups.md)

Headline:
- `ConflictBank`
  - mean accuracy delta: `+0.3125`
  - mean ECE delta: `-0.3325`
  - mean Brier delta: `-0.3201`
  - aligned-context accuracy delta: `0.0000`
- `WikiContradict`
  - mean accuracy delta: `+0.0260`
  - mean ECE delta: `+0.0051`
  - mean Brier delta: `-0.0237`
  - aligned-context accuracy delta: `0.0312`

Read:
- the global `RLCR + eta` gain is driven mainly by `ConflictBank`, especially the conflict slices.
- it does not appear to hurt aligned-context accuracy on `ConflictBank`.
- on `WikiContradict`, the effect is much smaller and ECE is roughly neutral.

## Theorem 1 / 2 Support

### Log-linearity robustness

Source:
- [theorem1_loglinearity_robustness.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem1_loglinearity_robustness.md)

Headline:
- `rho=0.0`: `R^2=0.9988`
- `rho=0.5`: `R^2=0.9609`
- `rho=1.0`: `R^2=0.7290`

### Variance-correction check

Source:
- [theorem1_variance_correction_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem1_variance_correction_note.md)

Headline:
- Mean correction KL: `1e-06` nat
- Max correction KL: `1.4e-05` nat
- All bins below `0.02` nat

### Powered baseline head-to-head

Source:
- [powered_baseline_headtohead.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/powered_baseline_headtohead.md)

Headline:
- vs `CoCoA`: mean gap `0.0426`, CI `[0.0405, 0.0445]`, wins `201/210`
- vs `Astute RAG`: mean gap `0.0318`, CI `[0.0302, 0.0333]`, wins `201/210`
- vs `Self-RAG`: mean gap `0.0219`, CI `[0.0019, 0.0395]`, wins `180/210`

## Retrieval / Deployment / Held-out

### Held-out preregistered test

Source:
- [preregistered_heldout_test.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/preregistered_heldout_test.md)

Headline:
- `P1` supported
- `P2` supported
- `P3` not supported

Read:
- Bayes-style arbitration generalizes well on held-out conflict families.
- The strongest theorem-3 directional prediction does not universally hold out-of-sample.

### Production-style RAG

Source:
- [production_rag_eval.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/production_rag_eval.md)

Headline:
- BM25 top-1 gold hit: `0.1`
- Hybrid top-1 gold hit: `0.1`
- Top-5 both-hit: `0.1`
- Mean retrieval latency: `3.3208s`
- Throughput: `0.3001 q/s`

### Stronger production retrieval rerun

Source:
- [production_rag_eval_e5.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/production_rag_eval_e5.md)

Headline:
- Top-1 gold hit: `0.15`
- Top-1 conflict hit: `0.05`
- Top-5 both-hit: `0.1`
- Mean retrieval latency: `2.7830s`
- Mean rerank latency: `5.4811s`
- Throughput: `0.121 q/s`

Read:
- The stronger multilingual-E5 rerank stack improves top-1 gold retrieval over
  the earlier `0.10` live production probe.
- This is still not a “deployment solved” result, but it is a real retrieval
  improvement rather than a pure framing change.

### Open Wikipedia probe

Source:
- [open_wikipedia_rag_probe_10.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/open_wikipedia_rag_probe_10.md)

Headline:
- Top-1 gold hit: `0.3`
- Top-5 conflict hit: `0.1`
- Top-5 both-hit: `0.1`

## Multilingual Transfer

### Model-side multilingual theorem-3 transfer

Source:
- [mistral_multilingual_theorem3_note.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/mistral_multilingual_theorem3_note.md)
- [multilingual_theorem3_results_bundle.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/multilingual_theorem3_results_bundle.md)

Headline:
- Model: `Mistral-7B`
- Languages: `de, es, fr, it, pt`
- Rows: `300`
- Mean conflict ECE delta: `+0.0012`
- Mean no-conflict ECE delta: `+0.0014`
- Conflict-minus-no-conflict ECE delta: `-0.0002`

Read:
- This is the first true multilingual theorem-3 transfer result in the repo.
- Across five languages, long CoT is basically flat rather than a
  conflict-specific multilingual blow-up.
- That materially strengthens the empirical answer to the “English-only” scope
  objection beyond retrieval-only probes.

Source:
- [multilingual_wikicontradict_suite.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/multilingual_wikicontradict_suite.md)

Headline:
- Languages run: `5`
- Languages with any top-k gold hit: `3`
- Languages with any top-k conflict hit: `3`
- Mean top-k gold-hit rate: `0.08`
- Mean top-k conflict-hit rate: `0.08`

Per-language:
- Spanish: top-k gold `0.2`, top-k conflict `0.2`
- French: `0.0`, `0.0`
- German: `0.1`, `0.1`
- Italian: `0.1`, `0.1`
- Portuguese: `0.0`, `0.0`

Read:
- This is still a transfer suite rather than a full multilingual theorem-3 benchmark.
- But the empirical package is no longer English-only in any simple sense.

## Final Practical Read

- Strongest theorem-3 headline: `Llama-8B DPO vs GRPO`
- Strongest mitigation headline: `RLCR` improves no-conflict calibration but does not solve controlled conflict
- Cleanest non-RL support: `Mistral`, `Gemma-9B`, `Gemma-27B`
- `Qwen`: fixed, finished, and mixed
- Multilingual limitation: materially reduced with both a five-language
  retrieval-transfer suite and a finished five-language model-side theorem-3
  transfer result on `Mistral-7B`

The empirical package is effectively complete.
