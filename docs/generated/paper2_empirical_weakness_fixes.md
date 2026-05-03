# Paper 2 Empirical Weakness Fixes

This note consolidates the empirical follow-ups that can be landed immediately while the matched-base GRPO/DPO and RLCR jobs remain queued.

## New empirical answers

- `AdaCAD` head-to-head is now explicit: mean Bayes advantage `0.0659`, CI `[0.0521, 0.0756]`.
- `Self-RAG` is now explicitly marked as the weakest powered comparator: mean gap `0.0266`, CI `[-0.0379, 0.0686]`, wins `20/25`.
- Conditional-independence diagnostic now has numbers: sampled `WikiContradict` conflict passages contain the gold answer verbatim at rate `0.5336`, while sampled `ConflictBank` conflict passages contain the conflicting answer verbatim at rate `0.9466` and the gold answer only `0.0391`.
- Closed-model slice is now broken down per benchmark/model and explicitly labeled as a proxy scaffold rather than a direct API-logprob experiment.
- The do-no-harm `eta=0` case is now diagnosed directly: baseline accuracy `0.036667` improves to `0.44` while Brier drops from `0.903275` to `0.504515`.
- Free-form latency/cost is now explicit: measured Delta runs fit about `4.3791` s per kept query after a `38.9527` s fixed load overhead, and the current sequence-mixture harness uses `4` model passes/query versus `1` for a single-pass decoder.
- Free-form open-QA check is now real, not just planned:
  - `triviaqa_open` (`n=27`): Bayes EM / ROUGE-L `0.0000` / `0.0802` vs `CAD` `0.0000` / `0.0794` and `AdaCAD` `0.0000` / `0.0754`.
  - `nq_open` (`n=32`): Bayes EM / ROUGE-L `0.0000` / `0.0357` vs `CAD` `0.0000` / `0.0348` and `AdaCAD` `0.0000` / `0.0339`.
  - `asqa` (`n=32`): Bayes EM / ROUGE-L `0.0000` / `0.0608` vs `CAD` `0.0000` / `0.0630` and `AdaCAD` `0.0000` / `0.0608`.

## Still waiting on Delta

- Matched-base `GRPO` vs `DPO` (`E1`): still pending.
- RLCR head-to-head (`E6`): still pending.

## Honest read

- The immediate empirical package is now much better on the reviewer-facing weak points that do not require new GPU training.
- The only truly unresolved causal claims are still the two training-heavy ones: matched-base objective control and RLCR head-to-head.