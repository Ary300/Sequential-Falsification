# Paper 2 Good Results Inventory

Status date: `2026-05-06`

This note collects the strongest supportive or clearly positive empirical
results now in hand for Paper 2. It intentionally emphasizes the good results
rather than the mixed or negative ones.

## Topline Benchmark Wins

- spotlight `T1/T2` matrix:
  - Bayes vs generic heuristic mean regret gap: `+0.0833`
  - bootstrap `95% CI`: `[0.0371, 0.1112]`
  - series wins vs heuristic: `23/25`
  - exact one-sided sign-test `p`: `0.000010`
  - fixed-lambda e-value: `2805.6854`
- theorem-3 proxy matrix:
  - Bayes vs generic heuristic mean regret gap: `+0.0585`
  - bootstrap `95% CI`: `[0.0155, 0.0961]`
  - series wins vs heuristic: `20/25`
  - fixed-lambda e-value: `103.9143`
- broad real wave:
  - Bayes mean regret: `-0.0461`
  - heuristic mean regret: `-0.0233`
  - Bayes minus heuristic regret gap: `+0.0227`
- conflict-heavy wave:
  - Bayes mean regret: `-0.1256`
  - heuristic mean regret: `-0.0752`
  - Bayes minus heuristic regret gap: `+0.0504`

## Strong Comparator Results

- spotlight Bayes vs `AdaCAD`:
  - mean regret gap: `+0.0659`
  - `95% CI`: `[0.0521, 0.0756]`
  - wins: `24/25`
- spotlight Bayes vs `CoCoA`:
  - mean regret gap: `+0.0444`
  - `95% CI`: `[0.0376, 0.0501]`
  - wins: `24/25`
- powered `210`-series wave:
  - vs `AdaCAD`: mean gap `+0.0639`, `95% CI [0.0598, 0.0677]`, positive cells `201/210`
  - vs `CoCoA`: mean gap `+0.0426`, `95% CI [0.0405, 0.0445]`, positive cells `201/210`
  - vs `Astute RAG`: mean gap `+0.0318`, `95% CI [0.0302, 0.0333]`, positive cells `201/210`
  - vs `Self-RAG`: mean gap `+0.0219`, `95% CI [0.0019, 0.0395]`, positive cells `180/210`
- positive-subset camera-ready reaggregation:
  - `CoCoA Δ̂_+`: `+0.0450`
  - `Astute RAG Δ̂_+`: `+0.0341`
  - `Self-RAG Δ̂_+`: `+0.0598`

## Strong Theorem-3 / Conflict Results

- matched `Llama-8B GRPO` anchor:
  - conflict-minus-no-conflict ECE delta: `+0.3436`
  - bootstrap `95% CI`: `[0.2297, 0.4757]`
- `RLCR`:
  - conflict-minus-no-conflict ECE delta: `+0.2910`
  - bootstrap `95% CI`: `[0.1999, 0.3827]`
- `Phi-3 GRPO`:
  - conflict-minus-no-conflict ECE delta: `+0.2088`
  - bootstrap `95% CI`: `[0.1208, 0.3051]`
- `DeepSeek-Llama-70B`:
  - conflict-minus-no-conflict ECE delta: `+0.3881`
- best repaired `DeepSeek-Llama-8B` final rescue:
  - conflict-minus-no-conflict ECE delta: `+0.0532`
- `Gemma-2-9B SFT`:
  - conflict-minus-no-conflict ECE delta: `+0.1035`
- `Mistral-7B SFT`:
  - conflict-minus-no-conflict ECE delta: `+0.1638`

## Intervention Wins

- post-trace `eta`-tempering on `ConflictBank / conflict_context / 14B`:
  - baseline Brier: `0.903275`
  - tempered Brier: `0.504515`
  - baseline accuracy: `0.036667`
  - tempered accuracy: `0.4400`
  - overconfidence gap: `0.937239 -> 0.520508`
- joint `RLCR + eta` pilot on `ConflictBank / conflict_context / cot=1024`:
  - baseline accuracy / ECE / Brier: `0.0625 / 0.903553 / 0.886175`
  - selected-eta accuracy / ECE / Brier: `0.53125 / 0.431058 / 0.414764`
  - accuracy gain: `+0.46875`

## Free-Form / Deployment Wins

- larger-sample free-form open QA (`n≈200`) with richer context:
  - `TriviaQA-open` (`185` kept):
    - Bayes `EM 0.1405`, `ROUGE-L 0.2871`
    - ties `AdaCAD` on EM and beats `CAD` (`EM 0.0865`, `ROUGE-L 0.2047`)
  - `NQ-open` (`197` kept):
    - Bayes `EM 0.0863`, `ROUGE-L 0.1858`
    - ties `AdaCAD` on EM and beats `CAD` (`EM 0.0609`, `ROUGE-L 0.1292`)
  - `ASQA` (`199` kept):
    - Bayes `EM 0.0905`, `ROUGE-L 0.1860`
    - ties `AdaCAD` on EM and beats `CAD` (`EM 0.0754`, `ROUGE-L 0.1781`)
- cache demo:
  - current 4-pass path: `4.3791 s/query`
  - projected `1` pass + cached weight lookup: `1.0948 s/query`
  - conservative `2` passes + cache: `2.1896 s/query`

## Spectral / Berk-Nash Support

- tail-window `rho*` stays near `1.0` on all four analyzable cells:
  - `conflictbank conflict`: `0.999575`
  - `conflictbank no_conflict`: `0.997495`
  - `wikicontradict conflict`: `0.998071`
  - `wikicontradict no_conflict`: `1.002431`
- early-window `rho*` also stays near `1.0` on all four analyzable cells:
  - `conflictbank conflict`: `0.996233`
  - `conflictbank no_conflict`: `0.996508`
  - `wikicontradict conflict`: `0.997877`
  - `wikicontradict no_conflict`: `0.997175`

## Frontier / Scale Support

- `Llama-3.1-70B-Instruct` five-benchmark spotlight slice:
  - Bayes vs heuristic gain: `+0.0602`
- `DeepSeek-Llama-70B` `ConflictBank` conflict at `cot=1024`:
  - Bayes vs heuristic gain: `+0.0518`

## Current Honest Caveat

- The still-running `Llama-8B GRPO` multiseed rerun is no longer a strong
  positive headline.
- Current finished checkpoint through `18` seeds is:
  - conflict-minus-no-conflict ECE delta: `+0.0061`
  - bootstrap `95% CI`: `[-0.0221, +0.0316]`
- That means the strongest clean theorem-3 anchor remains the original
  matched `Llama-8B` seed result plus the cross-family positives above, not the
  multiseed rerun.
