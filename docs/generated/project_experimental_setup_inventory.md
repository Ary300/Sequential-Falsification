# Project Experimental Setup Inventory

Status date: `2026-05-06`

This note turns the repository's current experimental setup into an appendix-ready
inventory for the Bayes-optimal knowledge arbitration / Paper 2 package.

It answers:

> For this specific project, what experimental setup, hyperparameters, splits,
> decoding settings, compute settings, and statistical procedures should be
> documented in a NeurIPS appendix?

The note is grounded in the actual code and generated artifacts in the repo, not
in generic advice.

## 1. Experimental Families In This Repo

The active empirical package has five main parts.

### A. Theorem 1 / 2 arbitration matrices

These are the broad arbitration benchmark sweeps comparing Bayes-style
arbitration against fixed and heuristic baselines.

Primary config:
- [knowledge_arbitration_spotlight.yaml](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/configs/knowledge_arbitration_spotlight.yaml)

Headline matrix:
- experiment: `arbitration_spotlight_t12_matrix`
- benchmarks:
  - `conflictbank`
  - `popqa`
  - `nq_swap`
  - `memotrap`
  - `faitheval`
- models:
  - `meta-llama/Llama-3.1-8B-Instruct`
  - `meta-llama/Llama-3.1-70B-Instruct`
  - `Qwen/Qwen2.5-7B-Instruct`
  - `Qwen/Qwen2.5-14B-Instruct`
  - `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- conditions:
  - `closed_book`
  - `aligned_context`
  - `conflict_context`
  - `irrelevant_noise`
- CoT lengths: `0, 128, 512, 2048`
- self-consistency values: `1, 8`
- max examples per slice: `512`

Baselines in the spotlight matrix:
- `bayes_proxy`
- `heuristic_adaptive`
- `always_context`
- `always_parametric`
- `fixed_50`
- `simulated_model`
- `cad`
- `adacad`
- `cocoa`
- `self_rag`
- `crag`
- `astute_rag`

### B. Theorem 3 real-generation sweeps

These are the conflict-vs-no-conflict calibration experiments with explicit
reasoning traces and CoT budgets.

Primary runner:
- [run_theorem3_real_generation.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_real_generation.py)

Default runner settings:
- backend: `openai`
- request timeout: `180.0`
- temperature: `0.0`
- top-p: `1.0`
- seed: `42`
- request format: `chat`
- prompt protocol: `generic`
- benchmarks: `wikicontradict,conflictbank`
- conditions: `aligned_context,conflict_context`
- benchmark maxima:
  - `wikicontradict_max=200`
  - `conflictbank_max=500`
  - `triviaqa_max=200`
- CoT lengths: `0, 128, 1024`
- ConflictBank screening pool: `1200`
- ambiguity band:
  - low: `0.2`
  - high: `0.8`

In the matched-objective theorem-3 evaluation path, the evaluation subset is
smaller and more standardized:
- `wikicontradict_max=96`
- `conflictbank_max=128`
- conditions: `aligned_context, conflict_context`
- CoT lengths: `0, 128, 1024`

That standardized evaluation produces `1344` theorem-3 rows per completed run:
- `(96 + 128) * 2 conditions * 3 cot lengths = 1344`

Evidence:
- [theorem3_matched_objective_lora_delta.sbatch](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/slurm/delta/theorem3_matched_objective_lora_delta.sbatch)
- [llama8_grpo_18seed_theorem3_ci.json](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/llama8_grpo_18seed_theorem3_ci.json)

### C. Matched-base objective comparisons

These are the controlled same-base `DPO` / `GRPO` / matched-`SFT` comparisons.

Core wrapper:
- [submit_delta_theorem3_matched_objective_lora.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_matched_objective_lora.sh)

Core training runner:
- [run_theorem3_matched_objective_lora.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_theorem3_matched_objective_lora.py)

Common defaults across the matched-objective path:
- benchmark for training data construction: `conflictbank`
- max source rows: `1200`
- max train rows: `800`
- max val rows: `120`
- max eval rows: `120`
- max prompt length: `768`
- max answer length: `24`
- objective epochs: `1`
- warmstart epochs: `1`
- learning rate: `5e-5`
- weight decay: `1e-4`
- beta: `0.1`
- GRPO group size: `4`
- sampling temperature: `0.8`
- top-p: `0.95`
- LoRA rank: `8`
- LoRA alpha: `16`
- LoRA dropout: `0.05`
- seed: `42`
- torch dtype: `bfloat16`
- evaluation after training: enabled
- vLLM max model length: `12288` unless overridden

### D. Eta-tempering / post-hoc decoding intervention

Primary launcher:
- [submit_delta_theorem3_eta_tempered.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_eta_tempered.sh)

Materialized method result:
- [theorem3_eta_tempered_method_result.json](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_eta_tempered_method_result.json)

Materialized setup:
- model: `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- benchmark: `conflictbank`
- condition: `conflict_context`
- CoT length: `1024`
- calibration size: `200`
- evaluation size: `300`
- eta grid:
  - `0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0`
- seed: `42`
- selection rule: `sample_split_brier_optimal`

### E. Free-form and retrieval evaluations

Free-form open-QA runner:
- [run_paper2_freeform_eval.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_paper2_freeform_eval.py)

Materialized free-form eval metadata:
- [paper2_freeform_eval.json](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_freeform_eval.json)

Materialized setup:
- model:
  - `/work/nvme/bgvi/adas17/hf_cache/hub/models--deepseek-ai--DeepSeek-R1-Distill-Llama-8B/snapshots/6a6f4aa4197940add57724a7707d069478df56b1`
- datasets:
  - `triviaqa_open`
  - `nq_open`
  - `asqa`
- max examples per dataset: `32`
- Wikipedia search limit: `6`
- top-k contexts: `3`

Dense retrieval evaluation:
- [build_production_rag_eval_e5.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_production_rag_eval_e5.py)
- [production_rag_eval_e5.json](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/production_rag_eval_e5.json)

Materialized setup:
- benchmark source: `wikicontradict`
- max examples: `20`
- live Wikipedia search limit: `12`
- reranked top-k: `5`
- encoder model: `intfloat/multilingual-e5-small`

## 2. Benchmark And Condition Inventory

Primary active benchmark set across the paper:
- `ConflictBank`
- `WikiContradict`
- `PopQA`
- `NQ-Swap`
- `FaithEval`
- `MemoTrap`
- `AmbigDocs`
- `RAMDocs`
- `DynamicQA`
- `ASQA`
- `NQ-open`
- `TriviaQA-open`

Condition labels used in the repo:
- `closed_book`
- `aligned_context`
- `conflict_context`
- `irrelevant_noise`
- `two_context_conflict`

Reasoning / CoT budgets used in active configs:
- theorem-1/2 spotlight:
  - `0, 128, 512, 2048`
- theorem-3 size-scaling spotlight:
  - `0, 128, 1024`
- real-generation focus configs elsewhere in the repo:
  - `0, 64, 256, 1024, 4096`

Self-consistency settings used in active configs:
- `1`
- `8`
- `32` in some theorem-3 focus manifests

Primary sources:
- [knowledge_arbitration_spotlight.yaml](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/configs/knowledge_arbitration_spotlight.yaml)
- [knowledge_arbitration_experiments.yaml](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/configs/knowledge_arbitration_experiments.yaml)
- [loaders.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/src/knowledge_arbitration/loaders.py)

## 3. Model And Checkpoint Inventory

Main model families used in the active empirical package:
- `meta-llama/Llama-3.1-8B-Instruct`
- `meta-llama/Llama-3.1-70B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen2.5-14B-Instruct`
- `Qwen/Qwen2.5-32B-Instruct`
- `Qwen/Qwen3-8B`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
- `deepseek-ai/DeepSeek-R1-Distill-Qwen-14B`
- `deepseek-ai/DeepSeek-R1-Distill-Llama-8B`
- `deepseek-ai/DeepSeek-R1-Distill-Llama-70B`
- `mistralai/Mistral-7B-Instruct-v0.3`
- `google/gemma-2-9b-it`
- `microsoft/Phi-3-mini-4k-instruct`
- `allenai/OLMo-2-7B`
- `EleutherAI/pythia-6.9b`

Notable model-specific evaluation overrides:
- `Gemma-2-9B`:
  - request format: `completion`
  - prompt protocol: `generic`
  - vLLM max model len: `4096`
- `DeepSeek-Llama-8B` rescue runs:
  - request format: `completion`
  - prompt protocol: `deepseek_native`
  - vLLM max model len: `4096`
- `Mistral-7B`:
  - vLLM max model len: `4096`
- `Phi-3-mini-4k`:
  - vLLM max model len: `4096`

Primary sources:
- [submit_delta_theorem3_e1_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_suite.sh)
- [submit_delta_theorem3_e1_mistral7_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_mistral7_suite.sh)
- [submit_delta_theorem3_e1_gemma9_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_gemma9_suite.sh)
- [submit_delta_theorem3_e1_phi3_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_phi3_suite.sh)
- [submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh)

## 4. Family-Specific Matched-Base Settings

### Llama-8B / Qwen-14B original E1 suite

Source:
- [submit_delta_theorem3_e1_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_suite.sh)

`Llama-3.1-8B`
- wall time: `14:00:00`
- max source rows: `900`
- max train rows: `640`
- max val rows: `96`
- max eval rows: `96`

`Qwen-2.5-14B`
- wall time: `18:00:00`
- max source rows: `1200`
- max train rows: `800`
- max val rows: `120`
- max eval rows: `120`

### Mistral-7B matched trio

Source:
- [submit_delta_theorem3_e1_mistral7_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_mistral7_suite.sh)

Shared settings:
- wall time: `12:00:00`
- max source rows: `800`
- max train rows: `560`
- max val rows: `80`
- max eval rows: `80`
- temperature: `0.8`
- top-p: `0.95`
- vLLM max model len: `4096`

Matched control:
- implemented as `objective=dpo` with `warmstart_epochs=2` and `epochs=0`

Matched DPO / GRPO pair:
- both use `warmstart_epochs=1`
- both use `epochs=1`

### Gemma-2-9B matched trio

Source:
- [submit_delta_theorem3_e1_gemma9_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_gemma9_suite.sh)

Shared settings:
- wall time: `12:00:00`
- max source rows: `800`
- max train rows: `560`
- max val rows: `80`
- max eval rows: `80`
- temperature: `0.8`
- top-p: `0.95`
- vLLM max model len: `4096`
- evaluation protocol:
  - request format: `completion`
  - prompt protocol: `generic`

Matched control:
- `warmstart_epochs=2`
- `epochs=0`

Matched DPO / GRPO pair:
- `warmstart_epochs=1`
- `epochs=1`

### Phi-3 matched pair

Source:
- [submit_delta_theorem3_e1_phi3_suite.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_e1_phi3_suite.sh)

Shared settings:
- wall time: `12:00:00`
- max source rows: `800`
- max train rows: `560`
- max val rows: `80`
- max eval rows: `80`
- temperature: `0.8`
- vLLM max model len: `4096`

### DeepSeek-Llama-8B rescue sweep

Source:
- [submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_theorem3_deepseek_llama8_native_rescue_sweep.sh)

Shared rescue settings:
- model: `deepseek-ai/DeepSeek-R1-Distill-Llama-8B`
- wall time: `14:00:00`
- max source rows: `900`
- max train rows: `640`
- max val rows: `96`
- max eval rows: `96`
- top-p: `0.95`
- save intermediate checkpoints: enabled
- evaluation protocol:
  - request format: `completion`
  - prompt protocol: `deepseek_native`
- storage path:
  - node-local staging enabled
  - sync-back to `/u/adas17/tts_results_staging`

Explored rescue pockets:
- `nativefix_b002g8w2`
  - beta: `0.02`
  - group size: `8`
  - temperature: `0.7`
  - warmstart epochs: `2`
  - seed: `42`
- `nativerescue_b001g12w3`
  - beta: `0.01`
  - group size: `12`
  - temperature: `0.7`
  - warmstart epochs: `3`
  - seed: `42`
- `nativerescue_b001g16t06w3s43`
  - beta: `0.01`
  - group size: `16`
  - temperature: `0.6`
  - warmstart epochs: `3`
  - seed: `43`

## 5. Free-Form And Retrieval Setup

### Free-form open-QA

Source:
- [run_paper2_freeform_eval.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/run_paper2_freeform_eval.py)
- [submit_delta_paper2_freeform.sh](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/submit_delta_paper2_freeform.sh)

Materialized run metadata:
- datasets: `triviaqa_open`, `nq_open`, `asqa`
- max examples: `32`
- search limit: `6`
- top-k contexts: `3`
- individual-context candidates: `0`
- decode mode: `candidate_rescore`
- max new tokens: `96`
- batch size: `4`
- torch dtype: `bfloat16`
- retrieval cache file:
  - `docs/generated/paper2_freeform_retrieval_cache.json`

The runner uses:
- live Wikipedia search through the Wikipedia API
- open-QA metrics:
  - exact match
  - ROUGE-L F1

### Production retrieval eval

Source:
- [build_production_rag_eval_e5.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_production_rag_eval_e5.py)

Materialized metadata:
- max examples: `20`
- search limit: `12`
- top-k reranked contexts: `5`
- sleep between requests: `0.25` seconds
- max retries: `5`
- encoder model: `intfloat/multilingual-e5-small`

The reranker uses:
- live Wikipedia search candidates
- dense E5 query/document embeddings
- max tokenization length for encoder: `512`

## 6. Statistical Reporting And Aggregation

### Spotlight and head-to-head summaries

Materialized summaries:
- [knowledge_arbitration_results_detailed.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/knowledge_arbitration_results_detailed.md)
- [paper2_camera_ready_reaggregations.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/paper2_camera_ready_reaggregations.md)

Currently materialized reporting includes:
- mean regret gaps
- bootstrap confidence intervals
- exact one-sided sign tests
- fixed-lambda e-values
- positive-subset `Δ̂_+` summaries
- eta-tempering median / IQR / max summaries
- finite-difference curvature proxy for `∂²_{ww}R`

### Theorem-3 uncertainty reporting

Main sources:
- [theorem3_review_followups.md](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/docs/generated/theorem3_review_followups.md)
- [build_theorem3_multiseed_ci.py](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/scripts/build_theorem3_multiseed_ci.py)

Current procedure:
- headline statistic:
  - conflict-minus-no-conflict ECE delta
- also reports:
  - mean conflict ECE delta
  - mean no-conflict ECE delta
- seed aggregation:
  - bootstrap resampling over seeds
- default bootstrap count in the multiseed builder: `10000`
- default bootstrap random seed: `42`

Theorem-3 per-family bootstrap tables currently report:
- conflict delta with 95% CI
- no-conflict delta with 95% CI
- conflict-minus-no-conflict delta with 95% CI

## 7. Compute / Runtime Setup

Primary cluster path:
- Delta

Main cluster launchers:
- [theorem3_matched_objective_lora_delta.sbatch](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/slurm/delta/theorem3_matched_objective_lora_delta.sbatch)
- [theorem3_rlcr_style_lora_delta.sbatch](/Users/aryavdas/Downloads/Sequential%20Falsification%20with%20Calibrated%20Confidence/slurm/delta/theorem3_rlcr_style_lora_delta.sbatch)

Matched-objective Delta defaults:
- account: `bgvi-dtai-gh`
- partition: `ghx4`
- qos: `bgvi-dtai-gh`
- GPUs: `1`
- CPUs: `16`
- wall time: `18:00:00`

RLCR Delta defaults:
- GPUs: `4`
- CPUs: `32`
- wall time: `20:00:00`

Runtime / cache details that matter for reproducibility:
- Python env loaded from a Delta venv under `/u/.../venvs/tts-delta`
- Hugging Face cache defaults to `/work/nvme/bgvi/adas17/hf_cache`
- XDG cache defaults to `/work/nvme/bgvi/adas17/.cache`
- XDG config defaults to `/work/nvme/bgvi/adas17/.config`
- some recovery jobs override this to:
  - node-local `/tmp`
  - then sync compact outputs back to persistent staging

vLLM inference defaults in the matched-objective path:
- tensor parallel size: `1`
- gpu memory utilization: `0.9`
- generation config mode: `vllm`

## 8. What The Appendix Should Explicitly Say

If we want a reviewer-friendly experimental appendix for this repo, the clean
minimum is:

1. a benchmark table:
   - benchmark
   - condition labels
   - max examples
   - whether the setting is closed-book / aligned / conflict / noise

2. a model table:
   - exact checkpoint string
   - family
   - instruct/distilled/reasoning status
   - context length override if any
   - request format / prompt protocol override if any

3. a matched-objective hyperparameter table:
   - objective
   - source/train/val/eval rows
   - epochs
   - warmstart epochs
   - learning rate
   - weight decay
   - beta
   - group size
   - temperature
   - top-p
   - LoRA rank / alpha / dropout
   - seed

4. a theorem-3 evaluation table:
   - eval benchmarks
   - eval conditions
   - CoT lengths
   - per-benchmark maxima
   - decoding settings

5. a statistics subsection:
   - bootstrap unit
   - number of bootstrap draws
   - sign tests
   - e-values
   - how multiseed aggregation is done

6. a compute subsection:
   - Delta account/partition family
   - GPU counts
   - wall times
   - node-local staging overrides where used

## 9. Current Known Gaps

What is fully materialized in code is stronger than what is fully narrated in
the paper appendix right now.

The main remaining gap is documentation synthesis, not missing setup code:
- the code paths and generated summaries already contain most of the information
- the manuscript appendix still needs one single consolidated subsection that
  presents it in reviewer order

The biggest thing to avoid in the paper is mixing:
- generic runner defaults
- family-specific overrides
- actually materialized run metadata

Those three levels should be reported separately, exactly as in this note.
