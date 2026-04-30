# Knowledge Arbitration Detailed Methodology

This file records the current empirical methodology as implemented in the repo and reflected in the finished result artifacts on disk as of `2026-04-29`.

## 1. Overall Study Design

The repo currently supports three layers of empirical evidence:

1. Broad arbitration waves for Theorem 1 and Theorem 2.
2. Focused theorem-3 real-generation and calibration studies.
3. Auxiliary deployment-style and synthetic validation studies.

The main paper-facing summary artifact is [knowledge_arbitration_headline_bundle.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_headline_bundle.md). This methodology file expands how those results were produced.

## 2. Benchmark Scope

### 2.1 Main arbitration benchmark stack

The completed extended stack includes the following benchmark families:

- `ConflictBank`
- `WikiContradict`
- `PopQA`
- `NQ-Swap`
- DynamicQA-family extensions
- `HotpotQA`
- `TriviaQA`
- `TabMWP`
- `GPQA`
- `CLIMATEX`

### 2.2 Theorem-3 focused stack

The theorem-3 real-generation path uses a narrower set of explicit conflict/no-conflict conditions:

- `ConflictBank`
- `WikiContradict`
- `TriviaQA` control

For theorem-3 runs, conditions are generally one or more of:

- `closed_book`
- `aligned_context`
- `conflict_context`

### 2.3 Auxiliary benchmark stack

- `MQuAKE-Remastered` for multi-hop conflict propagation
- Retrieval-backed `WikiContradict` corpus slices for the BM25 deployment demo
- Synthetic oracle environment for exact Bayes-rule recovery

## 3. Model Scope

### 3.1 Extended arbitration stack

The completed extended package covers `13` wired models spanning:

- Llama
- Qwen
- DeepSeek
- Mistral
- Gemma
- a closed-model API slice

### 3.2 Theorem-3 core models

The current theorem-3 package includes:

- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- `deepseek-ai/DeepSeek-R1-Distill-Llama-70B`
- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-14B-Instruct`
- `Qwen/Qwen2.5-32B-Instruct`
- `meta-llama/Llama-3.1-8B-Instruct`
- `meta-llama/Llama-3.1-70B-Instruct`

The currently running Delta audit wave adds denser coverage for:

- multi-seed R1-Distill-Qwen `7B` and `14B`
- Qwen2.5 `7B` and `14B`
- `DeepSeek-R1-Distill-Llama-70B`
- temperature-sweep variants
- a pending `QwQ-32B` job
- a pending `Qwen2.5-72B-Instruct` job

## 4. Baseline Scope

The completed user-facing baseline panel includes `15` baselines overall, with the spotlight-facing baselines explicitly surfaced as:

- `CAD`
- `AdaCAD`
- `CoCoA`
- `Self-RAG`
- `Astute RAG`
- `JuICE`
- `NWCAD`
- `MADAM-RAG`
- `CRAG`
- heuristic adaptive
- simulated model

For theorem-3 calibration follow-up work, post-hoc calibration baselines additionally include:

- raw identity confidence
- global temperature scaling
- eta-tempered answer-token calibration
- Platt scaling
- isotonic regression

## 5. Theorem 1 and Theorem 2 Methodology

### 5.1 Broad real and conflict-heavy waves

Theorem 1 and Theorem 2 are supported by two main summary waves:

- `broad_real_headline_wave_reestimated_v3`
- `conflict_headline_wave_reestimated_v3`

These waves aggregate series-level mean regret comparisons across multiple models and benchmark slices. The reported policies include Bayes proxy, heuristic adaptive, simulated model, fixed trust, and always-trust extremes.

### 5.2 Spotlight matrix

The spotlight matrix is the most important comparative layer for the paper story:

- `5 x 5` benchmark-model matrix
- `25` series total
- used for:
  - bootstrap CIs
  - sign tests
  - e-values
  - comparator-panel reads

Statistical methods already implemented and reported:

- paired bootstrap (`10,000` resamples in the spotlight summaries)
- exact one-sided sign tests
- fixed-lambda e-values

## 6. Theorem 3 Real-Generation Methodology

### 6.1 Real-generation engine

Primary implementation paths:

- [real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/real_generation.py)
- [run_theorem3_real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_real_generation.py)
- [submit_delta_theorem3_real_generation.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_real_generation.sh)

This path runs actual generation traces rather than only proxy arbitration outputs. It records per-row:

- benchmark
- split / condition
- CoT length
- confidence
- outcome
- reasoning word count
- response word count
- context-answer match
- parametric-answer match

### 6.2 CoT budgets

Finished theorem-3 headline results use:

- `cot=0`
- `cot=128`
- `cot=1024`

The currently running Tier A/B/C audit expansion densifies this axis with larger grids, including:

- `0`
- `64`
- `128`
- `256`
- `1024`
- `4096`

and additional temperature or model-family axes depending on job family.

### 6.3 Metrics

The theorem-3 reporting path computes:

- accuracy
- mean confidence
- overconfidence gap
- ECE
- Brier score
- AUROC
- calibration bins
- context-match rate
- parametric-match rate
- reasoning-word and response-word summaries

The reporting script is:

- [report_theorem3_real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/report_theorem3_real_generation.py)

## 7. Eta-Tempered Decoding Methodology

### 7.1 Intervention

The eta-tempered decoding method implements the “method that follows from the theory” requirement:

- apply an answer-token-only post-trace tempering step
- sweep candidate `eta` values
- select `eta` by held-out Brier optimization

Primary implementation paths:

- [eta_tempering.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/eta_tempering.py)
- [run_theorem3_eta_tempered_decoding.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_eta_tempered_decoding.py)

### 7.2 Selection rule

The current paper-facing method uses:

- sample-split held-out Brier optimization
- grid over `eta in {0.0, 0.1, ..., 1.0}`

The repo also records a more conservative “largest no-harm eta” read, but the paper-facing method result is the Brier-selected rule.

## 8. Confidence-Head Pilot Methodology

The confidence-head pilot is a lightweight retraining-style calibration experiment, not full RLCR.

Implementation path:

- [run_theorem3_confidence_head_pilot.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_confidence_head_pilot.py)

Design:

- reuse frozen theorem-3 trace rows from the worst-case `ConflictBank` 14B conflict slice
- extract hidden-state features
- train a small confidence head with Brier-loss supervision
- evaluate calibration metrics on held-out rows

Current metadata on disk:

- source rows: `300`
- train / val / eval split: `180 / 60 / 60`
- epochs: `20`
- learning rate: `0.001`

## 9. Synthetic Oracle Methodology

The synthetic oracle experiment anchors the theory in an exactly known environment:

- analytically known oracle arbitration rule
- empirical estimator fit from finite calibration samples
- held-out `R^2` between estimated and oracle arbitration weights

Current headline result:

- held-out `R^2 = 0.9984` at calibration size `2048`

This is used as the exact-verifiability anchor rather than a deployment benchmark.

## 10. MQuAKE Multi-hop Methodology

Implementation support was added directly in the data loader stack:

- MQuAKE rows are rendered into aligned-context and conflict-context forms
- gold answer corresponds to the edited/new answer
- parametric answer corresponds to the stale/original answer

The proxy compounding note then computes chain success/error by depth from policy probabilities rather than by running multi-hop free-form generation.

Current configured metadata:

- benchmark: `mquake_remastered`
- condition: `aligned_context`
- depths: `1, 2, 3`
- max examples: `256`
- seed: `42`

## 11. Retrieval-backed Demo Methodology

The retrieval-backed demo is intentionally modest and honest:

- it is a benchmark-contained BM25-style retrieval demo
- not a full open-Wikipedia production RAG stack

Current implementation:

- derive a retrieval corpus from aligned and conflicting `WikiContradict` passages
- retrieve top-`k` passages per question
- measure:
  - top-1 aligned retrieval rate
  - top-1 conflict retrieval rate
  - whether top-5 contains both aligned and conflicting evidence

The current note uses:

- benchmark: `wikicontradict`
- retriever: `bm25`
- examples: `253`
- corpus docs: `506`

## 12. Delta Compute Provenance

### 12.1 Completed extended wave

Finished extended-wave results are already local and summarized in:

- [delta_extended_wave_completion_summary.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/delta_extended_wave_completion_summary.md)

Completed completed-wave counts:

- `18` completed variants
- `13` models
- `10` benchmarks
- `15` baselines
- explicit seeds `[42, 43, 44]`

### 12.2 Live theorem-3 audit wave

Submission entry point:

- [submit_delta_theorem3_audit_tiers.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_audit_tiers.sh)

Current wave content:

- Tier A: seeds, denser CoT grids, controls, and 70B sweep
- Tier B: second RLVR family and stronger baseline checks
- Tier C: temperature sweeps and Yoon-reconciliation-style controls

As of the latest status check:

- Running: `2215664` to `2215674` except queued jobs, plus `2215677` to `2215680`
- Pending: `2215675`, `2215676`, `2215681`
- Pending reason: `QOSGrpBillingMinutes`

## 13. Scope Boundary for Current Claims

The methodology above supports the finished current headline package. It does **not** yet justify claiming that the still-running Tier A/B/C audit wave has completed. Those new denser-grid theorem-3 results should be treated as in-progress until final result artifacts land from Delta.
