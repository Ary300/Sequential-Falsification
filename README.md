# Sequential Falsification with Empirical Confidence Calibration

Research scaffold and runnable prototype for sequential falsification with empirical confidence scoring in test-time scaling workloads.

## What is included

- A full project layout matching the implementation plan.
- Core Python modules for candidate generation, sequential falsification, calibration, selection, baselines, and evaluation.
- Built-in non-adaptive generated-test filtering, local S*/CodeT proxy baselines, disagreement-driven differential probes, and component-ablation controls for adaptive probe choice, elimination, and confidence-based ranking.
- Config-driven sweeps for N-scaling, falsification rounds, probe families, temperature sensitivity, and compute-matched comparisons, with report builders for those artifacts.
- Optional integrations for `vllm`, direct `transformers` generation, `evalplus`, `confseq`, and plotting libraries.
- SLURM job templates for Anvil/Delta-style GPU runs.
- Prompt templates, config files, and a paper scaffold.
- A synthetic benchmark path so the pipeline can be smoke-tested without cluster dependencies.

## Quick start

The code is designed to degrade gracefully if the cluster stack is not installed yet.

```bash
python3 src/evaluate.py \
  --benchmark synthetic_demo \
  --methods greedy,majority_vote,falsification,oracle \
  --n-candidates 4 \
  --n-falsification-rounds 2 \
  --output-dir results/pilot
```

```bash
python3 src/run_full_pipeline.py \
  --config src/configs/experiments.yaml \
  --output-root results/full
```

To refresh all paper-facing artifacts from whatever results are currently on
disk, use:

```bash
python3 scripts/finalize_project.py
```

That command scans `results/`, rebuilds any `results_from_progress.json`
artifacts it can infer from progress files, regenerates per-run report outputs,
builds publication-ready and monitoring publication bundles, and copies the
current paper tables/status files into `paper/generated/`. If publication-style
artifacts are present under directories that start with `paper` or `reviewer`
(for example `paper_*`, `paperplus_*`, `paperproxy_*`, `paperproxystrong_*`,
or `reviewerstrong_*`), it automatically prefers those for the publication
bundles so smoke runs and stale placeholder results do not crowd out the real
paper table.

If you want the repo to first pull remote result trees from Anvil and Delta,
then finalize locally in one pass, use:

```bash
bash scripts/harvest_cluster_results.sh
```

That command attempts to sync `results/`, `figures/`, `logs/`, and
`paper/generated/` from the configured Anvil/Delta project roots, then runs the
same final local refresh. It degrades gracefully if one cluster is temporarily
unreachable.

## Repository layout

```text
src/
  generate.py
  falsify.py
  calibrate.py
  selection.py
  evaluate.py
  baselines.py
  run_full_pipeline.py
  collect_progress.py
  report.py
  utils/
  configs/
  prompts/
slurm/
paper/
data/
results/
figures/
logs/
checkpoints/
```

## Notes

- Config files use `.yaml` names but are written as JSON-compatible YAML so they can be loaded with the stdlib `json` module when `PyYAML` is unavailable.
- The synthetic benchmark is intentionally tiny and deterministic; it exists only to verify the pipeline wiring.
- The `s_star` and `code_t` methods are executable local proxies, not the original external SkyThought or Microsoft implementations. Their result metadata is labeled `s_star_proxy` and `code_t_proxy` so paper tables can stay honest.
- `scripts/build_publication_bundle.py` now understands both merged
  `benchmarks` payloads and config-run `experiments` payloads, so ablation runs
  and merged seed bundles can flow through the same paper-facing summarizer.
- The publication bundle now emits extra reviewer-facing artifacts beyond the
  main table:
  - `publication_completion_table*.tex`
  - `publication_gap_recovery_table*.tex`
  - `publication_method_coverage*.md`
  - `publication_highlights*.md`
  - `neurips_readiness*.md/json`
- Real benchmark loaders currently support EvalPlus HumanEval+/MBPP+, LiveCodeBench v6, MATH-500-style Hendrycks MATH subsets, GSM8K, and AIME 2024 when the optional dependencies/data sources are available.
- DeltaAI was the original large-run path for this project, but the current clean rerun campaign has been moved to Anvil.
- The Anvil templates default to the `gpu` partition because the current Anvil account is authorized there. On Anvil, the clean rerun path now uses a project-local conda environment and the repo's `transformers` backend because recent `vllm` wheels were incompatible with the cluster's system glibc.
- LiveCodeBench stdin/stdout tests are executed as standalone scripts; HumanEval+/MBPP+ tests are executed through their function entry points.
- LiveCodeBench generation uses an explicit "complete Python 3 program, code only" prompt. HumanEval+/MBPP+ generation keeps continuation-style prompting so function bodies remain aligned with their starter code.
- Progress-file resume only reuses completed rows that contain every requested method, preventing stale partial runs from silently skipping missing baselines.
- Anvil helper scripts live in `scripts/`, and the cluster workflow summary is in `HPC_CHEATSHEET.md`.
- DeltaAI helper scripts live alongside them in `scripts/`, with cluster notes in `DELTA_CHEATSHEET.md`.
- DeltaAI batch templates live under `slurm/delta/`.
- The falsification selector now supports additional survivor-only
  differential tie-break rounds via `--max-tiebreak-rounds`, so stronger runs
  can spend extra test-time compute on separating the remaining candidate pool
  instead of stopping as soon as the main falsification budget is exhausted.

For a quick regression check of that stronger selector without cluster
dependencies, run:

```bash
python3 scripts/check_headline_selector.py
```

For the current high-budget DeltaAI headline rerun recipe, use:

```bash
bash scripts/submit_delta_headline_wave.sh --sync-first
```

That launcher submits:

- stronger `paperheadline_*` HumanEval+/MBPP+ reruns for the main paper rows
- stronger `paperheadlineproxy_*` HumanEval+/MBPP+ local CodeT/S* proxy rows
- stronger `paperheadlinegtf_*` HumanEval+/MBPP+ generated-test-filter rows

with `N=16`, `T=4`, and `MAX_TIEBREAK_ROUNDS=6`.

When DeltaAI falls back behind `QOSGrpBillingMinutes`, the practical rescue
path is now dependency-gated 1-hour interactive chunks rather than large
free-standing reruns. The checked-in helper supports that directly:

```bash
CHAIN_LENGTH=2 \
CHUNK_WALL=01:00:00 \
HE_14B_DEPENDENCY=2165728 \
HE_7B_DEPENDENCY=2165730 \
bash scripts/submit_delta_neurips_chunk_wave.sh
```

That keeps the first chunk in `Dependency` until a running long job frees
budget, then appends progress into the same `results/` directory with the
stronger selector configuration.

The finalizer also writes a conservative NeurIPS readiness audit. Treat
`paper/generated/neurips_readiness_current.md` as the checklist for what is
still missing or too weak: it flags partial rows, missing core baselines, thin
seed coverage, missing proxy baselines, low oracle-gap recovery, and cases
where falsification trails self-debug or generated-test filtering.

For the literature-facing novelty boundary, use
`docs/novelty_audit_2026.md`. It keeps the paper from making claims that are
too broad relative to newer TTS/calibration papers.

To submit the audit-driven closure pack after current long jobs free budget:

```bash
bash scripts/submit_delta_neurips_gap_closure.sh --sync-first
```

If DeltaAI is back under `QOSGrpBillingMinutes`, stage that same closure wave
behind an active long job instead of submitting it free-standing:

```bash
AFTEROK_DEPENDENCY=2165730 \
bash scripts/submit_delta_neurips_gap_closure.sh --sync-first --skip-baselines
```

That launcher writes to fresh `paperneugap*` and `delta_neurips_ablations`
prefixes and covers the core missing surfaces: HumanEval+/MBPP+ proxy baselines,
generated-test-filter rows, LiveCodeBench/MATH coverage, and the MBPP+ 7B
ablation pack.

## Current DeltaAI Status

As of April 10, 2026, the DeltaAI validation stack is provisioned and the current pilot queue is complete. The core environment, vLLM serving, HumanEval+/MBPP+/LiveCodeBench caches, and a local `math500` cache are available under `~/tts-falsification` on DeltaAI.

As of April 12, 2026, the falsification method has been upgraded from a
candidate-local `public_then_hidden` path to a population-level
`adaptive_population` path. The new default:

- disables hidden-test probe selection by default
- selects probes that separate the surviving candidate pool
- synthesizes labeled mutation probes from public tests when a reference
  solution is available

This change is scientifically important: older paper tables should now be
treated as provisional signals rather than final publication numbers, because
the clean publication path runs through the new adaptive-population reruns.

Model caches on DeltaAI now live at `/work/nvme/bgvi/adas17/hf_cache`, with `~/.cache/huggingface` symlinked there. Keep it this way: storing models in home exhausted quota and caused result writes to fail.

Corrected DeltaAI pilot outputs now available:

```text
results/full_delta/results_from_progress_current.json
figures/full_delta_progress_current/
  DeepSeek-R1-Distill-Qwen-7B, HumanEval+, 16 problems, 3 seeds
  falsification 68.8%, greedy 37.5%, majority 25.0%, self_debug 75.0%, oracle 75.0%

results/qwen14b_pilot_v2/results.json
figures/qwen14b_pilot_v2/
  Qwen2.5-Coder-14B, HumanEval+, 8 problems, 3 seeds
  falsification 41.7%, greedy 33.3%, majority 33.3%, oracle 41.7%
  Qwen2.5-Coder-14B, MBPP+, 8 problems, 3 seeds
  falsification 100.0%, greedy 91.7%, majority 91.7%, oracle 100.0%

results/r1_32b_pilot_v2/results.json
figures/r1_32b_pilot_v2/
  DeepSeek-R1-Distill-Qwen-32B, HumanEval+, 8 problems, 3 seeds
  falsification 87.5%, greedy 41.7%, majority 33.3%, oracle 95.8%

results/r1_32b_mbpp_fixed/results.json
figures/r1_32b_mbpp_fixed/
  DeepSeek-R1-Distill-Qwen-32B, MBPP+, 8 problems, 3 seeds
  falsification 54.2%, greedy 29.2%, majority 29.2%, oracle 54.2%

results/livecodebench_delta_v6_completion/results.json
figures/livecodebench_delta_v6_completion/
  DeepSeek-R1-Distill-Qwen-7B, LiveCodeBench v6, 16 problems, 1 seed
  falsification 12.5%, greedy 6.2%, majority 6.2%, oracle 12.5%

results/r1_7b_math500_pilot/results.json
figures/r1_7b_math500_pilot/
  DeepSeek-R1-Distill-Qwen-7B, MATH-500-style subset, 16 problems, 3 seeds
  falsification 97.9%, greedy 79.2%, majority 95.8%, oracle 97.9%
```

Larger corrected DeltaAI runs now also available:

```text
results/paper_r1_7b_livecodebench_100/results.json
figures/paper_r1_7b_livecodebench_100/
  DeepSeek-R1-Distill-Qwen-7B, LiveCodeBench v6, 100 problems, 1 seed
  falsification 8.0%, greedy 3.0%, majority 3.0%, oracle 8.0%

results/paper_r1_7b_math100/results.json
figures/paper_r1_7b_math100/
  DeepSeek-R1-Distill-Qwen-7B, math500, 100 problems, 3 seeds
  falsification 33.7 ± 1.7, greedy 11.7 ± 2.3, majority 23.0 ± 2.1, oracle 33.7 ± 1.7
```

The remaining paper-quality step is to let the corrected full HumanEval+ and MBPP+ three-seed runs finish, then merge those outputs into the publication bundle and final manuscript tables.

As of April 13, 2026, the fresh Anvil bootstrap job `16294900` completed successfully, provisioning the project-local environment under `/anvil/projects/x-bio260046/conda-envs/tts`. The current clean rerun campaign now begins at jobs `16294901+`, which are scheduler-eligible and waiting on normal queue priority rather than broken environment dependencies.

Fresh adaptive-population reruns submitted on April 12:

```text
2119692 / 2119693  fix_r1_7b_humaneval_full
2119694 / 2119695  fix_r1_7b_mbpp_full
2119696 / 2119697  fix_qwen14b_humaneval_full
2119698 / 2119699  fix_qwen14b_mbpp_full
2119700 / 2119701  fix_r1_32b_humaneval_full
2119702 / 2119703  fix_r1_32b_mbpp_full
2119704            refresh_fix_bundle
```

At submission time these were pending under `QOSGrpBillingMinutes`. The
refresh job `2119704` is chained after all six report jobs so the paper-facing
bundles update automatically once the reruns complete.

On April 18, 2026, three targeted DeltaAI HumanEval resume jobs were submitted
to finish the incomplete paper runs in place:

```text
2155288 / 2155289  resume_he7b_s43    -> results/paper_r1_7b_humaneval_full/
2155290 / 2155291  resume_he14b_s44   -> results/paper_qwen14b_humaneval_full/
2155292 / 2155293  resume_he32b_s44   -> results/paper_r1_32b_humaneval_full/
```

These are thin resume-only submissions over the existing `paper_*` progress
dirs, not fresh full sweeps. The helper script for reissuing that exact chain
is:

```bash
bash scripts/submit_delta_paper_humaneval_resume.sh
```

After syncing the updated local CLI surface to DeltaAI, the corrected active
HumanEval recovery chain became:

```text
2156104 / 2156105  resume_he14b_s44    -> completed / reported
2156126 / 2156127  resume_he32b_s44_1g -> completed / reported
2160243 / 2160244  resume_he7b_s43     -> requeued at 18h after timeout
```

The 32B fallback uses a leaner single-GPU profile with `TP_SIZE=1` and a lower
`MAX_MODEL_LEN`, and that path is now the reason the local ready bundle contains
a finished 32B HumanEval+ row at `falsification 82.9`, `self_debug 82.3`,
`oracle 84.8`, `majority vote 29.9`, and `greedy 44.5`.

To close the most obvious reviewer-facing baseline gap, a dedicated DeltaAI
launcher now exists for paper-style runs that include the non-adaptive
`generated_test_filter` baseline:

```bash
bash scripts/submit_delta_generated_filter_matrix.sh
```

The first targeted MBPP+ augmentation jobs from that path are:

```text
2157600 / 2157601  reviewer_gtf_r1_7b_mbpp_full
2157602 / 2157603  reviewer_gtf_qwen14b_mbpp_full
2160266 / 2160267  reviewer_gtf_r1_32b_mbpp_full
2160268 / 2160269  reviewer_gtf_r1_7b_humaneval_full
2160270 / 2160271  reviewer_gtf_qwen14b_humaneval_full
2160272 / 2160273  reviewer_gtf_r1_32b_humaneval_full
```

For broader paper-style benchmark coverage on DeltaAI, a second launcher now
exists:

```bash
bash scripts/submit_delta_paper_matrix.sh
```

The first queued coverage jobs from that matrix launcher are:

```text
2160274 / 2160275  paperplus_r1_7b_livecodebench_full
2160276 / 2160277  paperplus_r1_7b_math500_full
2160228 / 2160229  paperplus_qwen14b_livecodebench_full
2160230 / 2160231  paperplus_qwen14b_math500_full
2160232 / 2160233  paperplus_r1_32b_livecodebench_full
2160234 / 2160235  paperplus_r1_32b_math500_full
```

For appendix-style proxy baseline tables using the local `S*` and `CodeT`
executables, a third DeltaAI launcher now exists:

```bash
bash scripts/submit_delta_proxy_matrix.sh
```

The first proxy-matrix jobs from that path are:

```text
2160283 / 2160284  paperproxy_r1_7b_humaneval_full
2160285 / 2160286  paperproxy_r1_7b_mbpp_full
2160287 / 2160288  paperproxy_qwen14b_humaneval_full
2160289 / 2160290  paperproxy_qwen14b_mbpp_full
2160291 / 2160292  paperproxy_r1_32b_humaneval_full
2160293 / 2160294  paperproxy_r1_32b_mbpp_full
```

For a stronger NeurIPS-style rerun wave that preserves the existing evidence
and writes higher-compute results into separate publication buckets, use:

```bash
bash scripts/submit_delta_neurips_upgrade.sh
```

That launcher submits:

- `paperproxystrong_*` proxy reruns with `N=16`, `T=3`
- `reviewerstrong_*` generated-test-filter reruns with `N=16`, `T=3`
- `paperplusstrong_*` LiveCodeBench and MATH coverage reruns for the missing 14B/32B rows

If the long `ghx4` jobs get pushed back under `QOSGrpBillingMinutes`, use the
interactive fallback wave for the highest-value weak rows:

```bash
bash scripts/submit_delta_neurips_chunk_wave.sh
```

That submits 2-hour `ghx4-interactive` strong chunks for:

- 7B HumanEval proxy
- 14B HumanEval proxy
- 7B MBPP generated-test-filter
- 14B MBPP generated-test-filter

When DeltaAI blocks the longer `ghx4` jobs under `QOSGrpBillingMinutes`, the
repo now also has a low-billing workaround for progress-friendly resumes and
single-seed chunks:

```bash
bash scripts/submit_delta_interactive_chunk.sh --dry-run
```

That helper submits to `ghx4-interactive` with a 2-hour walltime by default and
is designed to keep appending progress into an existing `results/` directory.
The first confirmed working chunk jobs are:

```text
2161503  resume_he7b_s43_i2h
2161504  gtf_r1_7b_mbpp_i2h
```

Both were accepted with `Reason=None` and moved to `RUNNING` while the longer
`ghx4` jobs remained stuck behind the billing-minute cap.

If a long cluster run exits before writing the final `results.json`, use `src/collect_progress.py` to merge `*_seed*_progress.json` files into a reportable payload, then run `src/report.py` on that merged file.

The publication bundle script now separates publication-ready tables from monitoring tables:

- Default behavior excludes partial in-progress progress-derived rows.
- Pass `--include-partial` only when you intentionally want a live monitoring table built from running jobs.

To refresh the current paper state in one step, use:

```bash
python3 scripts/refresh_publication_state.py \
  --progress-dir results/paper_r1_7b_humaneval_full \
  --progress-dir results/paper_r1_7b_mbpp_full \
  --progress-dir results/paper_qwen14b_humaneval_full \
  --progress-dir results/paper_qwen14b_mbpp_full \
  --progress-dir results/paper_r1_32b_humaneval_full \
  --progress-dir results/paper_r1_32b_mbpp_full \
  --results-file results/paper_r1_7b_livecodebench_100/results.json \
  --results-file results/paper_r1_7b_math100/results.json \
  --results-file results/qwen14b_pilot_v2/results.json \
  --results-file results/r1_32b_pilot_v2/results.json \
  --results-file results/r1_32b_mbpp_fixed/results.json
```

This regenerates progress-derived `results_from_progress.json` files, report artifacts under `figures/`, both publication bundles, and paper-facing table files under `paper/generated/`.

For a broader local sweep over every results artifact currently available in the
workspace, `scripts/finalize_project.py` wraps the same refresh path and writes:

- `figures/publication_bundle_ready/`
- `figures/publication_bundle_current/`
- `paper/generated/publication_main_table_ready.tex`
- `paper/generated/publication_main_table_current.tex`
- `paper/generated/publication_completion_table_ready.tex`
- `paper/generated/publication_completion_table_current.tex`
- `paper/generated/publication_status_ready.md`
- `paper/generated/publication_status_current.md`
- `paper/generated/publication_method_coverage_ready.md`
- `paper/generated/publication_method_coverage_current.md`

When `results/paper_*` directories exist, those are used as the preferred
source set for the publication bundles; otherwise the script falls back to all
available results files.

When submitting DeltaAI jobs with `sbatch --export`, pass list-valued variables with colons, for example `SEEDS=42:43:44` and `BENCHMARKS=humaneval_plus:mbpp_plus`. Slurm splits `--export` on commas, and the Delta batch script converts colons back to comma-delimited CLI arguments internally.
