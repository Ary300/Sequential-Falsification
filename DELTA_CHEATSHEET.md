# DeltaAI Cheatsheet

This project can also run on DeltaAI. The currently validated submission paths are:

- account: `bgvi-dtai-gh`
- partition: `ghx4`
- qos: `bgvi-dtai-gh`
- report / merge fallback partition: `ghx4-interactive`
- report / merge jobs still need `--gpus-per-node=1` on DeltaAI; pure CPU
  jobs are rejected for this account on this cluster

## Connect

```bash
ssh adas17@dtai-login.delta.ncsa.illinois.edu
```

DeltaAI uses password + Duo MFA rather than SSH keys for general users.

## Project root on DeltaAI

```bash
cd ~/tts-falsification
```

## Quick environment setup

```bash
module load python/anaconda3/2.10.0
python -m venv --system-site-packages ~/venvs/tts-delta
source ~/venvs/tts-delta/bin/activate
export HF_HOME=/work/nvme/bgvi/adas17/hf_cache
pip install transformers evalplus SciencePlots vllm
```

`confseq` may fail to build on the ARM/Grace login environment due missing Boost headers. The current codebase does not require it for the default prototype path because the current confidence logic is implemented locally.

Keep model caches under `/work/nvme/bgvi/adas17/hf_cache`, not under `~/.cache/huggingface`. Delta home quota is small enough that model downloads can make result writes fail.

## Run one-off remote command

```bash
bash scripts/delta_run.sh 'cd ~/tts-falsification && pwd && hostname'
```

## Pull results back and refresh the paper bundle locally

From the local repo checkout, use:

```bash
bash scripts/harvest_cluster_results.sh
```

This will try to sync `results/`, `figures/`, `logs/`, and `paper/generated/`
from both clusters and then run `python3 scripts/finalize_project.py`.

The finalizer now auto-prefers publication-scoped result trees under:

- `results/paper_*`
- `results/paperplus_*`
- `results/paperproxy_*`
- `results/reviewer_*`

If DeltaAI is temporarily unreachable, you can still harvest only Anvil:

```bash
bash scripts/harvest_cluster_results.sh --skip-delta
```

## Submit a DeltaAI GPU job

```bash
bash scripts/delta_submit.sh slurm/delta/test_vllm_delta.sbatch
bash scripts/delta_submit.sh slurm/delta/prepare_benchmarks_delta.sbatch
bash scripts/delta_submit.sh slurm/delta/pilot_experiment_delta.sbatch
```

## Monitor jobs

```bash
bash scripts/delta_monitor.sh
bash scripts/delta_monitor.sh 2096460,2096461
```

## Accounting

```bash
bash scripts/delta_sacct.sh 2096460,2096461
```

## Checked-in Delta templates

- `slurm/delta/test_vllm_delta.sbatch`: validate GPU visibility plus `torch`/`vllm`/`evalplus` imports.
- `slurm/delta/prepare_benchmarks_delta.sbatch`: export local benchmark caches under `data/`, using pickle when needed.
- `slurm/delta/pilot_experiment_delta.sbatch`: launches local vLLM, then runs an 8-problem HumanEval+ pilot.
- `slurm/delta/full_experiment_delta.sbatch`: launches local vLLM, then runs a capped multi-benchmark Delta validation sweep. It is parameterized through environment variables.
- `slurm/delta/report_results_delta.sbatch`: generates report payloads and PDF figures from a completed or partially completed results JSON. On DeltaAI, the safe default is now a short `ghx4-interactive` single-GPU follow-up job rather than a CPU-only report job.

If `results.json` is missing, the report job now falls back to `src/collect_progress.py`, which merges `*_seed*_progress.json` files into `results_from_progress.json` before calling `src/report.py`. This makes long runs safer: a failed or interrupted sweep can still leave useful tables and figures.

Resume mode is method-aware: it only reuses progress rows that already contain all methods requested for the current run. This avoids the earlier failure mode where a truncated run with only `greedy` could be mistaken for complete progress.

LiveCodeBench uses stdin/stdout execution. Its loader disables function-entry-point requirements for stdin tasks so generated standalone scripts can be parsed and evaluated correctly. Its generation path also uses an explicit standalone-program prompt rather than HumanEval-style continuation prompting.

## Parameterized Full Runs

The full-run template accepts environment variables, which makes it reusable for model pilots and benchmark slices:

```bash
sbatch --export=ALL,\
MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B,\
BENCHMARKS=humaneval_plus:mbpp_plus:livecodebench_v6:math500,\
OUTPUT_DIR=results/full_delta,\
SEEDS=42:43:44,\
MAX_PROBLEMS=16,\
N_CANDIDATES=8,\
N_ROUNDS=2 \
slurm/delta/full_experiment_delta.sbatch
```

Important: use colons, not commas, in `--export` list values. Slurm treats commas as environment-variable separators. The batch script converts colon-delimited `BENCHMARKS`, `METHODS`, and `SEEDS` back to comma-delimited CLI arguments internally.

Useful variables:

- `MODEL`: Hugging Face model id served by vLLM.
- `BENCHMARKS`: comma-separated benchmark names.
- `METHODS`: comma-separated method names.
- `OUTPUT_DIR`: destination for `results.json` and progress files.
- `SEEDS`: comma-separated random seeds.
- `MAX_PROBLEMS`: cap for validation/debug runs.
- `N_CANDIDATES`: number of samples per problem.
- `N_ROUNDS`: falsification rounds.
- `MAX_TOKENS`: generation token cap passed to `src/evaluate.py`.
- `MAX_MODEL_LEN`: vLLM context cap.
- `GPU_MEMORY_UTILIZATION`: vLLM memory fraction.
- `MAX_TIEBREAK_ROUNDS`: extra survivor-only differential rounds used after
  the main falsification budget when multiple candidates still remain alive.

## Headline rerun wave

For the current strongest paper-facing reruns, use:

```bash
bash scripts/submit_delta_headline_wave.sh --sync-first
```

This submits a targeted high-budget wave with:

- `N_CANDIDATES=16`
- `N_ROUNDS=4`
- `MAX_TIEBREAK_ROUNDS=6`

and three result families:

- `paperheadline_*`: main falsification/self-debug/oracle rows
- `paperheadlineproxy_*`: local CodeT/S* proxy rows
- `paperheadlinegtf_*`: generated-test-filter comparison rows

The intent is to strengthen the hardest HumanEval+/MBPP+ rows without spending
the same budget immediately on the already healthier LiveCodeBench/math slices.

## Audit-Driven Gap Closure

After running `python3 scripts/finalize_project.py`, inspect
`paper/generated/neurips_readiness_current.md`. It is the conservative checklist
for NeurIPS-readiness gaps. To submit a broad but non-overwriting closure pack:

```bash
bash scripts/submit_delta_neurips_gap_closure.sh --sync-first
```

The launcher writes to fresh prefixes and avoids overwriting existing results:

- `paperneugap_proxy_*` for local CodeT/S* proxy baselines on HumanEval+/MBPP+
- `paperneugap_gtf_*` for generated-test-filter comparisons on HumanEval+/MBPP+
- `paperneugap_*` for LiveCodeBench/MATH coverage rows
- `delta_neurips_ablations/*` for N-scaling, rounds, probe-family, component,
  temperature, and compute-matched ablations

Use `--skip-baselines`, `--skip-coverage`, or `--skip-ablations` if the billing
cap is tight and you want to stage the wave in smaller pieces.

If the queue falls back behind `QOSGrpBillingMinutes`, the checked-in launchers
also accept `AFTEROK_DEPENDENCY`. That lets us queue the next wave behind an
already-running long job instead of paying for free-standing pending rows:

```bash
AFTEROK_DEPENDENCY=2165730 \
bash scripts/submit_delta_neurips_gap_closure.sh --sync-first --skip-baselines
```

That pattern is now the preferred way to stage LiveCodeBench/MATH coverage and
the MBPP+ ablation pack when the account has budget but the live queue is tight.

## Completed April 10 DeltaAI Pilot Chain

The latest corrected pilot chain is complete and the queue was empty at the final check:

```text
2106097  qwen14b_pilot_correct              completed  Qwen2.5-Coder-14B HumanEval+/MBPP+
2106098  report_qwen14b_correct             completed
2106099  r1_32b_pilot_correct               completed  R1-32B HumanEval+ plus invalid old-prompt MBPP diagnostic
2106100  report_r1_32b_correct              completed
2106625  livecodebench_7b_completion_fixed  completed  corrected stdin/stdout LiveCodeBench prompt
2106626  report_lcb_completion_fixed        completed
2106670  r1_32b_mbpp_fixed                  completed  corrected MBPP code-only prompt
2106671  report_r1_32b_mbpp_fixed           completed
2106799  r1_7b_mbpp_fixed                   completed  corrected MBPP code-only prompt
2106800  report_r1_7b_mbpp_fixed            completed
2106801  r1_7b_math500_pilot                completed
2106802  report_r1_7b_math500               completed
```

Report jobs use `afterany` dependencies so partial artifacts are still generated if an experiment exits nonzero after writing progress files.

Job `2106093` was intentionally canceled after preserving progress to `results/full_delta/results_from_progress_current.json` because it was running MBPP with the stale pre-fix prompt. Its HumanEval+ progress remains useful; its partial MBPP rows should be treated as diagnostic only.

Previous jobs `2103490` and `2103779` failed because home quota was exhausted by the Hugging Face cache. Their progress files were preserved and converted into partial report artifacts under `figures/full_delta_partial`.

Jobs `2103839`--`2103846` completed after the quota fix, but they revealed the Slurm comma-splitting issue: exported comma-separated values were truncated. The corrected jobs above use colon-separated values and fresh `v2` output directories for the 14B/32B pilots.

LiveCodeBench jobs before `2106625` should be treated as invalid diagnostics. They exposed two bugs that are now fixed: cached LiveCodeBench tests lost `testtype="stdin"`, and R1 chat generation spent the budget on reasoning instead of code. The corrected path uses stdin/stdout execution plus a completion prompt that starts inside a Python code fence.

The fallback path was smoke-tested on Delta with:

```bash
python src/collect_progress.py \
  --progress-dir results/full_delta \
  --output-file results/full_delta/results_from_progress_smoke.json

python src/report.py \
  --results-file results/full_delta/results_from_progress_smoke.json \
  --output-dir figures/full_delta_progress_smoke
```

## Current Preliminary Signal

These are capped validation slices, not paper-scale results:

```text
DeepSeek-R1-Distill-Qwen-7B, HumanEval+, 16 problems, 3 seeds:
  falsification 68.8%, greedy 37.5%, majority 25.0%, self_debug 75.0%, oracle 75.0%

Qwen2.5-Coder-14B, HumanEval+, 8 problems, 3 seeds:
  falsification 41.7%, greedy 33.3%, majority 33.3%, oracle 41.7%

Qwen2.5-Coder-14B, MBPP+, 8 problems, 3 seeds:
  falsification 100.0%, greedy 91.7%, majority 91.7%, oracle 100.0%

DeepSeek-R1-Distill-Qwen-32B, HumanEval+, 8 problems, 3 seeds:
  falsification 87.5%, greedy 41.7%, majority 33.3%, oracle 95.8%

DeepSeek-R1-Distill-Qwen-32B, MBPP+, 8 problems, 3 seeds, corrected prompt:
  falsification 54.2%, greedy 29.2%, majority 29.2%, oracle 54.2%

DeepSeek-R1-Distill-Qwen-7B, LiveCodeBench v6, 16 problems, 1 seed, corrected stdin prompt:
  falsification 12.5%, greedy 6.2%, majority 6.2%, oracle 12.5%

DeepSeek-R1-Distill-Qwen-7B, MATH-500-style subset, 16 problems, 3 seeds:
  falsification 97.9%, greedy 79.2%, majority 95.8%, oracle 97.9%
```

The next paper-quality step is to scale these corrected configurations to the full benchmark matrix and the planned `N={1,4,8,16,32,64}` sweeps.

## April 12 Adaptive-Falsification Reboot

The falsification path was updated on April 12 to address the main scientific
concern in the earlier prototype:

- falsification now defaults to `adaptive_population`
- hidden tests are disabled for probe selection by default
- candidate elimination is population-level rather than candidate-by-candidate
- labeled mutation probes are synthesized from public tests when a reference
  solution is available

This means the older paper tables should be treated as provisional. They still
show a real signal, but the clean publication path now runs through the
adaptive-population reruns below.

Fresh reruns submitted after the fix:

```text
2119692  sfix_he_7b         -> results/fix_r1_7b_humaneval_full/
2119693  report_sfix_he_7b  -> figures/fix_r1_7b_humaneval_full/

2119694  sfix_mbpp_7b         -> results/fix_r1_7b_mbpp_full/
2119695  report_sfix_mbpp_7b  -> figures/fix_r1_7b_mbpp_full/

2119696  sfix_he_14b         -> results/fix_qwen14b_humaneval_full/
2119697  report_sfix_he_14b  -> figures/fix_qwen14b_humaneval_full/

2119698  sfix_mbpp_14b         -> results/fix_qwen14b_mbpp_full/
2119699  report_sfix_mbpp_14b  -> figures/fix_qwen14b_mbpp_full/

2119700  sfix_he_32b         -> results/fix_r1_32b_humaneval_full/
2119701  report_sfix_he_32b  -> figures/fix_r1_32b_humaneval_full/

2119702  sfix_mbpp_32b         -> results/fix_r1_32b_mbpp_full/
2119703  report_sfix_mbpp_32b  -> figures/fix_r1_32b_mbpp_full/

2119704  refresh_fix_bundle
```

At submission time these jobs were pending under `QOSGrpBillingMinutes`. The
refresh job `2119704` is chained after all six report jobs and will rebuild the
paper-facing publication bundles automatically once the reruns complete.

On April 18, 2026, the incomplete HumanEval paper seeds were resumed directly
in place on DeltaAI:

```text
2155288  resume_he7b_s43     -> results/paper_r1_7b_humaneval_full/
2155289  report_he7b_s43     -> figures/paper_r1_7b_humaneval_full/

2155290  resume_he14b_s44    -> results/paper_qwen14b_humaneval_full/
2155291  report_he14b_s44    -> figures/paper_qwen14b_humaneval_full/

2155292  resume_he32b_s44    -> results/paper_r1_32b_humaneval_full/
2155293  report_he32b_s44    -> figures/paper_r1_32b_humaneval_full/
```

Reusable launcher:

```bash
bash scripts/submit_delta_paper_humaneval_resume.sh
```

After a repo sync fixed the stale remote `evaluate.py`, the active HumanEval
resume state became:

```text
2156104  resume_he14b_s44     -> completed
2156105  report_he14b_s44     -> completed

2156126  resume_he32b_s44_1g  -> completed
2156127  report_he32b_s44_1g  -> completed

2160243  resume_he7b_s43      -> requeued at 18h after timeout
2160244  report_he7b_s43      -> dependency on 2160243
```

The `*_1g` 32B job is an explicit single-GPU GH200 fallback with
`TP_SIZE=1` and `MAX_MODEL_LEN=8192`, used because the earlier 2-GPU 32B
resume remained stuck behind `QOSGrpBillingMinutes`.

That fallback is now reflected in the local ready bundle as a finished 32B
HumanEval+ single-seed row:

```text
falsification 82.9
self_debug    82.3
oracle        84.8
majority_vote 29.9
greedy        44.5
```

To add the missing paper-style `generated_test_filter` baseline on DeltaAI, use:

```bash
bash scripts/submit_delta_generated_filter_matrix.sh
```

The first queued reviewer-critical augmentation jobs from that launcher are:

```text
2157600  gtf_r1_7b_mbpp        -> results/reviewer_gtf_r1_7b_mbpp_full/
2157601  report_gtf_r1_7b_mbpp -> figures/reviewer_gtf_r1_7b_mbpp_full/

2157602  gtf_qwen14b_mbpp        -> results/reviewer_gtf_qwen14b_mbpp_full/
2157603  report_gtf_qwen14b_mbpp -> figures/reviewer_gtf_qwen14b_mbpp_full/

2160266  gtf_r1_32b_mbpp        -> results/reviewer_gtf_r1_32b_mbpp_full/
2160267  report_gtf_r1_32b_mbpp -> figures/reviewer_gtf_r1_32b_mbpp_full/

2160268  gtf_r1_7b_he        -> results/reviewer_gtf_r1_7b_humaneval_full/
2160269  report_gtf_r1_7b_he -> figures/reviewer_gtf_r1_7b_humaneval_full/

2160270  gtf_qwen14b_he        -> results/reviewer_gtf_qwen14b_humaneval_full/
2160271  report_gtf_qwen14b_he -> figures/reviewer_gtf_qwen14b_humaneval_full/

2160272  gtf_r1_32b_he        -> results/reviewer_gtf_r1_32b_humaneval_full/
2160273  report_gtf_r1_32b_he -> figures/reviewer_gtf_r1_32b_humaneval_full/
```

For broader paper-style benchmark coverage on DeltaAI, use:

```bash
bash scripts/submit_delta_paper_matrix.sh
```

The first queued coverage jobs from that launcher are:

```text
2160274  paper_r1_7b_lcb       -> results/paperplus_r1_7b_livecodebench_full/
2160275  report_paper_r1_7b_lcb

2160276  paper_r1_7b_math      -> results/paperplus_r1_7b_math500_full/
2160277  report_paper_r1_7b_math

2160228  paper_qwen14b_lcb      -> results/paperplus_qwen14b_livecodebench_full/
2160229  report_paper_qwen14b_lcb

2160230  paper_qwen14b_math     -> results/paperplus_qwen14b_math500_full/
2160231  report_paper_qwen14b_math

2160232  paper_r1_32b_lcb       -> results/paperplus_r1_32b_livecodebench_full/
2160233  report_paper_r1_32b_lcb

2160234  paper_r1_32b_math      -> results/paperplus_r1_32b_math500_full/
2160235  report_paper_r1_32b_math
```

For appendix-style proxy baseline tables using the local executable `S*` and
`CodeT` proxies, use:

```bash
bash scripts/submit_delta_proxy_matrix.sh
```

The first queued proxy-matrix jobs are:

```text
2160283  proxy_r1_7b_he        -> results/paperproxy_r1_7b_humaneval_full/
2160284  report_proxy_r1_7b_he

2160285  proxy_r1_7b_mbpp      -> results/paperproxy_r1_7b_mbpp_full/
2160286  report_proxy_r1_7b_mbpp

2160287  proxy_qwen14b_he      -> results/paperproxy_qwen14b_humaneval_full/
2160288  report_proxy_qwen14b_he

2160289  proxy_qwen14b_mbpp    -> results/paperproxy_qwen14b_mbpp_full/
2160290  report_proxy_qwen14b_mbpp

2160291  proxy_r1_32b_he       -> results/paperproxy_r1_32b_humaneval_full/
2160292  report_proxy_r1_32b_he

2160293  proxy_r1_32b_mbpp     -> results/paperproxy_r1_32b_mbpp_full/
2160294  report_proxy_r1_32b_mbpp
```

For a stronger follow-up wave that keeps the current paper evidence intact and
writes upgraded reruns into distinct publication buckets, use:

```bash
bash scripts/submit_delta_neurips_upgrade.sh
```

This launcher submits three families of stronger jobs:

- `paperproxystrong_*`: proxy-baseline reruns at `N=16`, `T=3`
- `reviewerstrong_*`: generated-test-filter reruns at `N=16`, `T=3`
- `paperplusstrong_*`: stronger 14B/32B LiveCodeBench and MATH coverage jobs

If those long jobs fall back behind `QOSGrpBillingMinutes`, the checked-in
interactive fallback for the highest-value weak rows is:

```bash
bash scripts/submit_delta_neurips_chunk_wave.sh
```

That launcher submits 2-hour `ghx4-interactive` strong chunks for:

- 7B HumanEval proxy
- 14B HumanEval proxy
- 7B MBPP generated-test-filter
- 14B MBPP generated-test-filter

## Billing-Minute Workaround

DeltaAI's project QoS for this account currently exposes a relatively small
`GrpTRESMins` budget (`billing=4080...` at the latest check in
`sacctmgr show qos bgvi-dtai-gh`).
That is small enough that a handful of long 18h--30h GH200 jobs can deadlock
the queue under `QOSGrpBillingMinutes`, even when the jobs themselves are valid.

Two practical mitigations worked:

1. Cancel clearly stale pending 32B jobs that are already superseded by newer
   outputs or fallback runs.
2. For progress-friendly resume work, switch from `ghx4` to the
   `ghx4-interactive` partition and run short chunks that append to the same
   `results/` directory.

A checked-in helper now exists for that lower-billing path:

```bash
bash scripts/submit_delta_interactive_chunk.sh --dry-run
```

In practice, 1-hour chunks plus `AFTERANY_DEPENDENCY` have been more reliable
than naive 2-hour bursts because they stay in `Dependency` until billing room
actually opens. Example HumanEval+ 14B proxy rescue chunk:

```bash
AFTERANY_DEPENDENCY=2165728 \
WALL=01:00:00 \
JOB_NAME=spx_qwen14b_he_i1h_dep \
MODEL=Qwen/Qwen2.5-Coder-14B-Instruct \
BENCHMARKS=humaneval_plus \
METHODS=greedy:majority_vote:generated_test_filter:self_debug:code_t:s_star:falsification:oracle \
OUTPUT_DIR=results/paperproxystrongi2h_qwen14b_humaneval_full \
SEEDS=42 \
MAX_PROBLEMS=164 \
N_CANDIDATES=16 \
N_ROUNDS=3 \
MAX_TIEBREAK_ROUNDS=6 \
bash scripts/submit_delta_interactive_chunk.sh
```

Example HumanEval+ 7B resume chunk:

```bash
JOB_NAME=resume_he7b_s43_i2h \
MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
BENCHMARKS=humaneval_plus \
METHODS=greedy:majority_vote:self_debug:falsification:oracle \
OUTPUT_DIR=results/paper_r1_7b_humaneval_full \
SEEDS=43 \
MAX_PROBLEMS=164 \
bash scripts/submit_delta_interactive_chunk.sh
```

Example 7B MBPP+ `generated_test_filter` chunk:

```bash
JOB_NAME=gtf_r1_7b_mbpp_i2h \
MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
BENCHMARKS=mbpp_plus \
METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle \
OUTPUT_DIR=results/reviewer_gtf_r1_7b_mbpp_full \
SEEDS=42 \
MAX_PROBLEMS=378 \
bash scripts/submit_delta_interactive_chunk.sh
```

The first confirmed working interactive workaround jobs are:

```text
2161503  resume_he7b_s43_i2h      -> COMPLETED on ghx4-interactive
2161504  gtf_r1_7b_mbpp_i2h       -> FAILED quickly due port/model mismatch on a shared node
2165719  gtf_r1_7b_mbpp_i2h_fix   -> rerun with per-job API port, using the corrected Delta runtime
2165722  report_gtf_r1_7b_mbpp_i2h_fix -> chained interactive report job

The root cause of `2161504` was not benchmark logic. The older Delta runtime
hardcoded port `8000` for the local OpenAI-compatible vLLM server, which is
unsafe on shared interactive nodes. The corrected runtime now derives a
per-job `API_PORT` from `SLURM_JOB_ID`.

As of the latest queue check, the currently active Delta submission wave is:

```text
2165719  gtf_r1_7b_mbpp_i2h_fix     ghx4-interactive
2165724  paper_qwen14b_lcb          ghx4
2165726  paper_qwen14b_math         ghx4
2165728  gtf_qwen14b_mbpp           ghx4
2165730  gtf_r1_32b_he              ghx4
2165742  proxy_r1_7b_he             ghx4
2165744  proxy_r1_7b_mbpp           ghx4
```

and their report jobs are chained on `ghx4-interactive`.
```

More recent rescue runs also showed that when the project is close to the
billing cap, dependency-gated 1-hour chunks are safer than free-standing
interactive jobs. The checked-in `submit_delta_neurips_chunk_wave.sh` helper
now defaults to `CHUNK_WALL=01:00:00` semantics via environment overrides and
supports per-row dependency injection:

```bash
CHAIN_LENGTH=2 \
CHUNK_WALL=01:00:00 \
HE_14B_DEPENDENCY=2165728 \
HE_7B_DEPENDENCY=2165730 \
bash scripts/submit_delta_neurips_chunk_wave.sh
```

The paper bundle now also emits extra reviewer-facing artifacts:

- `paper/generated/publication_completion_table_current.tex`
- `paper/generated/publication_completion_table_ready.tex`
- `paper/generated/publication_gap_recovery_table_current.tex`
- `paper/generated/publication_gap_recovery_table_ready.tex`
- `paper/generated/publication_method_coverage_current.md`
- `paper/generated/publication_method_coverage_ready.md`
- `paper/generated/publication_highlights_current.md`
- `paper/generated/publication_highlights_ready.md`

## Larger Corrected Sweeps Queued on April 10

The next set of corrected 7B sweeps was submitted after the capped validation slices:

```text
2107493  seqfals_he_7b_full      -> results/paper_r1_7b_humaneval_full/
2107494  report_he_7b_full       -> figures/paper_r1_7b_humaneval_full/

2107495  seqfals_mbpp_7b_full    -> results/paper_r1_7b_mbpp_full/
2107496  report_mbpp_7b_full     -> figures/paper_r1_7b_mbpp_full/

2107497  seqfals_lcb_7b_100      -> results/paper_r1_7b_livecodebench_100/
2107498  report_lcb_7b_100       -> figures/paper_r1_7b_livecodebench_100/

2107499  seqfals_math_7b_100     -> results/paper_r1_7b_math100/
2107500  report_math_7b_100      -> figures/paper_r1_7b_math100/
```

These jobs use the corrected prompt and execution paths, not the earlier invalid LiveCodeBench or stale-prompt MBPP runs.

At the last check, the four experiment jobs above had all started on GH200 nodes and were actively writing `*_progress.json` files.

Since then:

- `2107497` / `2107498` completed successfully for `paper_r1_7b_livecodebench_100`
- `2107499` / `2107500` completed successfully for `paper_r1_7b_math100`
- `2107493` and `2107495` remain the active long HumanEval+/MBPP+ runs

Additional larger corrected comparison runs were then queued:

```text
2110203  seqfals_qwen14b_he_full     -> results/paper_qwen14b_humaneval_full/
2110204  report_seqfals_qwen14b_he_full

2110205  seqfals_qwen14b_mbpp_full   -> results/paper_qwen14b_mbpp_full/
2110206  report_seqfals_qwen14b_mbpp_full

2110207  seqfals_r132b_he_full       -> results/paper_r1_32b_humaneval_full/
2110208  report_seqfals_r132b_he_full

2110209  seqfals_r132b_mbpp_full     -> results/paper_r1_32b_mbpp_full/
2110210  report_seqfals_r132b_mbpp_full
```

## Publication Bundle Commands

To merge the known-good completed runs into one paper-ready summary table on DeltaAI:

```bash
python - <<'PY'
import json
from pathlib import Path
src = Path('results/full_delta/results_from_progress_current.json')
dst = Path('results/full_delta/results_from_progress_current_labeled.json')
payload = json.loads(src.read_text())
payload.setdefault('metadata', {})['model'] = 'deepseek-ai/DeepSeek-R1-Distill-Qwen-7B'
dst.write_text(json.dumps(payload, indent=2), encoding='utf-8')
PY

python scripts/build_publication_bundle.py \
  --results-file results/full_delta/results_from_progress_current_labeled.json \
  --results-file results/qwen14b_pilot_v2/results.json \
  --results-file results/r1_32b_pilot_v2/results.json \
  --results-file results/r1_32b_mbpp_fixed/results.json \
  --results-file results/livecodebench_delta_v6_completion/results.json \
  --results-file results/r1_7b_math500_pilot/results.json \
  --results-file results/r1_7b_mbpp_fixed/results.json \
  --output-dir figures/publication_bundle_known_good_labeled
```

This produces:

- `figures/publication_bundle_known_good_labeled/publication_main_table.tex`
- `figures/publication_bundle_known_good_labeled/publication_summary.csv`
- `figures/publication_bundle_known_good_labeled/publication_summary.json`

For the current paper path, keep two bundle modes:

```bash
# Publication-ready only: excludes partial progress-derived rows by default.
python scripts/build_publication_bundle.py \
  --results-file results/paper_r1_7b_humaneval_full/results_from_progress.json \
  --results-file results/paper_r1_7b_mbpp_full/results_from_progress.json \
  --results-file results/paper_r1_7b_livecodebench_100/results.json \
  --results-file results/paper_r1_7b_math100/results.json \
  --results-file results/qwen14b_pilot_v2/results.json \
  --results-file results/r1_32b_pilot_v2/results.json \
  --results-file results/r1_32b_mbpp_fixed/results.json \
  --output-dir figures/publication_bundle_ready

# Monitoring bundle: intentionally includes in-progress rows from running jobs.
python scripts/build_publication_bundle.py \
  --include-partial \
  --results-file results/paper_r1_7b_humaneval_full/results_from_progress.json \
  --results-file results/paper_r1_7b_mbpp_full/results_from_progress.json \
  --results-file results/paper_r1_7b_livecodebench_100/results.json \
  --results-file results/paper_r1_7b_math100/results.json \
  --results-file results/qwen14b_pilot_v2/results.json \
  --results-file results/r1_32b_pilot_v2/results.json \
  --results-file results/r1_32b_mbpp_fixed/results.json \
  --output-dir figures/publication_bundle_current
```

Or refresh the whole paper state in one command:

```bash
python scripts/refresh_publication_state.py \
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

This updates:

- `results/*/results_from_progress.json` for any listed progress dirs that have seed-progress files
- `figures/<run_name>/` report artifacts
- `figures/publication_bundle_ready/`
- `figures/publication_bundle_current/`
- `paper/generated/publication_main_table_ready.tex`
- `paper/generated/publication_main_table_current.tex`
- `paper/generated/publication_completion_table_ready.tex`
- `paper/generated/publication_completion_table_current.tex`
- `paper/generated/publication_method_coverage_ready.md`
- `paper/generated/publication_method_coverage_current.md`
