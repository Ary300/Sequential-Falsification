# Paper 2 Empirical Weakness Fixes

This note consolidates the empirical follow-ups that can be landed immediately
while the remaining matched-base reruns and dense-trajectory jobs are queued.

## New empirical answers

- `AdaCAD` head-to-head is now explicit: mean Bayes advantage `0.0659`, CI `[0.0521, 0.0756]`.
- `Self-RAG` is now explicitly marked as the weakest powered comparator: mean gap `0.0266`, CI `[-0.0379, 0.0686]`, wins `20/25`.
- Conditional-independence diagnostic now has numbers: sampled `WikiContradict` conflict passages contain the gold answer verbatim at rate `0.5336`, while sampled `ConflictBank` conflict passages contain the conflicting answer verbatim at rate `0.9466` and the gold answer only `0.0391`.
- Closed-model slice is now broken down per benchmark/model and explicitly labeled as a proxy scaffold rather than a direct API-logprob experiment.
- The do-no-harm `eta=0` case is now diagnosed directly: baseline accuracy `0.036667` improves to `0.44` while Brier drops from `0.903275` to `0.504515`.
- Free-form latency/cost is now explicit: measured Delta runs fit about `4.3791` s per kept query after a `38.9527` s fixed load overhead, and the current sequence-mixture harness uses `4` model passes/query versus `1` for a single-pass decoder.
- A stable-distribution cache demo is now on disk: precomputing the arbitration weight offline reduces the online path from `4` model passes to about `1.5–2` effective passes, with projected latency in the `~1.1–2.2 s/query` range on the measured free-form timing.
- Larger-sample free-form open-QA is now landed at `n≈200`, not just `n=8`:
  - strongest run: `paper2_freeform_eval_n200_seqmix_ctx.json`
  - `triviaqa_open` (`185` kept): Bayes EM / ROUGE-L `0.1405` / `0.2871`
    vs `CAD` `0.0865` / `0.2047`, `AdaCAD` `0.1405` / `0.2808`,
    closed-book `0.1405` / `0.2641`
  - `nq_open` (`197` kept): Bayes EM / ROUGE-L `0.0863` / `0.1858`
    vs `CAD` `0.0609` / `0.1292`, `AdaCAD` `0.0863` / `0.1863`,
    closed-book `0.0609` / `0.1758`
  - `asqa` (`199` kept): Bayes EM / ROUGE-L `0.0905` / `0.1860`
    vs `CAD` `0.0754` / `0.1781`, `AdaCAD` `0.0905` / `0.1898`,
    closed-book `0.0854` / `0.1958`
- Partial early/tail `\hat{\rho}^\star` recovery is now on disk from the failed
  Qwen-14B dense run rather than waiting on a fresh completion:
  - tail-window `wikicontradict conflict`: spectral radius `0.6780`, `rho*`
    `1.0046`
  - tail-window `wikicontradict no_conflict`: spectral radius `0.0148`, `rho*`
    `0.9970`
  - early-window `wikicontradict conflict`: spectral radius `0.3438`, `rho*`
    `0.9983`
  - early-window `wikicontradict no_conflict`: spectral radius `0.4285`,
    `rho*` `0.9965`

## Still waiting on Delta

- HDD-backed matched-base reruns:
  - `Mistral-7B` `SFT/DPO/GRPO`
  - `Gemma-2-9B` `SFT/DPO/GRPO`
- HDD-backed DeepSeek diagnosis reruns:
  - native eval
  - mechanism probe
  - curriculum-audit pair
- HDD-backed dense trajectory reruns:
  - Qwen-14B tail
  - Llama-70B tail
- expanded Llama-8B GRPO multiseed block (`45–71`)

## Honest read

- The immediate empirical package is now much better on the reviewer-facing weak
  points that do not require new training.
- The free-form story improved materially with the larger sample: Bayes now
  ties `AdaCAD` on EM across the three open-QA datasets and consistently beats
  plain `CAD`, which is a much stronger result than the earlier `n=8` probe.
- The honest remaining caveat is that closed-book remains competitive, and the
  partial early/tail `\hat{\rho}^\star` recovery is informative but still not
  the final dense-table answer.
