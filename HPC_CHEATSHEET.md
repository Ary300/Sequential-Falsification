# Anvil HPC Cheatsheet

This project is set up around the `gpu` partition because the current `bio260046-gpu` allocation is authorized there. The `ai` partition exists on Anvil, but this account is not currently associated with it.

The current Anvil path uses a project-local conda env at `/anvil/projects/x-bio260046/conda-envs/tts` rather than `~/.conda/envs/tts`, because installing `torch` and related GPU dependencies in home hit quota limits. The clean rerun campaign also now defaults to the repo's direct `transformers` backend on Anvil instead of a local `vllm` server, because recent `vllm` wheels were not compatible with Anvil's glibc.

## Connect

```bash
ssh -i ~/.ssh/anvil_ed25519 -o IdentitiesOnly=yes x-adas17@anvil.rcac.purdue.edu
```

## Project root on Anvil

```bash
cd /anvil/projects/x-bio260046/tts-falsification
```

## Sync this repo to Anvil

```bash
bash scripts/anvil_sync.sh
```

If you want to pull remote Anvil/Delta result trees back to this machine and
then rebuild all local paper artifacts in one step, use:

```bash
bash scripts/harvest_cluster_results.sh
```

If `results/paper_*` directories are present after the sync, the finalization
step will prefer those for the paper bundle automatically.

That preference now also includes `results/paperplus_*`,
`results/paperproxy_*`, and `results/reviewer_*`, so the newer Delta paper and
reviewer runs are not silently dropped from the local publication bundle.

Skip a cluster if its login path is down:

```bash
bash scripts/harvest_cluster_results.sh --skip-delta
bash scripts/harvest_cluster_results.sh --skip-anvil
```

## Bootstrap the environment

```bash
bash scripts/anvil_bootstrap.sh
```

Or submit the checked-in bootstrap job:

```bash
bash scripts/anvil_submit.sh slurm/bootstrap_env.sbatch
```

For package installs and data prep, prefer the CPU bootstrap path so GPU allocation is reserved for model runs:

```bash
bash scripts/anvil_submit_cpu.sh slurm/bootstrap_env_cpu.sbatch
```

## Clone external baseline repos on Anvil

```bash
bash scripts/anvil_clone_repos.sh
```

Or via Slurm on CPU:

```bash
bash scripts/anvil_submit_cpu.sh slurm/clone_external_repos_cpu.sbatch
```

## Prepare benchmark exports on Anvil

```bash
bash scripts/anvil_submit_cpu.sh slurm/prepare_benchmarks_cpu.sbatch
```

## Submit checked-in jobs

```bash
bash scripts/anvil_submit.sh slurm/test_vllm.sbatch
bash scripts/anvil_submit.sh slurm/pilot_experiment.sbatch
bash scripts/anvil_submit.sh slurm/full_experiment.sbatch
bash scripts/anvil_submit.sh slurm/ablation_sweep.sbatch
```

## Launch the full ablation matrix on Anvil

The repo now has a config-driven ablation launcher that expands the named sweeps in `src/configs/experiments.yaml`, submits one GPU job per seed, chains CPU-side progress recovery/report jobs, and then merges the seed runs into a single reported artifact per experiment.

Run the default reviewer-facing ablation pack:

```bash
bash scripts/submit_anvil_ablation_campaign.sh
```

Dry-run it first to inspect the exact submissions without touching the queue:

```bash
bash scripts/submit_anvil_ablation_campaign.sh --dry-run
```

If you made local code changes immediately before launching, sync first in the same command:

```bash
bash scripts/submit_anvil_ablation_campaign.sh --sync-first --dry-run
```

Run only a subset:

```bash
bash scripts/submit_anvil_ablation_campaign.sh \
  --experiment-name n_scaling_mbpp_7b \
  --experiment-name round_ablation_mbpp_7b \
  --experiment-prefix probe_family_ablation_
```

Override the seed list if you want a quick pilot before the full 3-seed pass:

```bash
SEEDS=42 bash scripts/submit_anvil_ablation_campaign.sh --dry-run
```

The generic `slurm/ablation_sweep.sbatch` is also no longer a `synthetic_demo` toy job. It now runs selected named experiments from `src/configs/experiments.yaml` and supports backend overrides, so it is usable for direct config-driven ablation runs on Anvil.

If you need to gate the ablation campaign on an environment repair or data-prep job, chain it with `--afterok`:

```bash
bash scripts/submit_anvil_ablation_campaign.sh --afterok 12345678 --dry-run
```

## DeltaAI notes

DeltaAI helper scripts live under `scripts/delta_*.sh` and `slurm/delta/`. The Delta ablation path now mirrors the Anvil one:

```bash
bash scripts/submit_delta_ablation_campaign.sh --dry-run
```

And the same `--sync-first` guard exists there too:

```bash
bash scripts/submit_delta_ablation_campaign.sh --sync-first --dry-run
```

Current limitation: this environment cannot non-interactively log into DeltaAI because the cluster is asking for live Kerberos + Duo authentication. The checked-in Delta helper scripts are ready, but they assume you already have a working login path on this machine.

## Current clean rerun pattern

After the adaptive-population falsification fix, the safest rerun pattern on Anvil is:

- use the `gpu` partition
- submit one benchmark per job
- start with one seed per job
- keep walltimes modest enough to avoid `AssocGrpGRESMinutes` and similar accounting blocks
- chain a CPU-side report job with `afterany`

Example 7B HumanEval+ clean rerun:

```bash
sbatch --parsable \
  --account=bio260046-gpu \
  --partition=gpu \
  --gpus-per-node=1 \
  --cpus-per-task=32 \
  --time=08:00:00 \
  --job-name=sf_r1_7b_he_s42 \
  --export=ALL,ANVIL_CONDA_ENV=/anvil/projects/x-bio260046/conda-envs/tts,BACKEND=transformers,MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B,BENCHMARKS=humaneval_plus,METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle,OUTPUT_DIR=results/anvil_fix_r1_7b_humaneval_s42,SEEDS=42,MAX_PROBLEMS=164,N_CANDIDATES=16,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE=1 \
  slurm/anvil_full_experiment.sbatch
```

Example chained report job:

```bash
sbatch --parsable \
  --account=bio260046 \
  --partition=shared \
  --dependency=afterany:<experiment_job_id> \
  --job-name=sf_r1_7b_he_s42_rep \
  --export=ALL,RESULTS_FILE=results/anvil_fix_r1_7b_humaneval_s42/results.json,PROGRESS_DIR=results/anvil_fix_r1_7b_humaneval_s42,OUTPUT_DIR=figures/sf_r1_7b_he_s42 \
  slurm/report_results_cpu.sbatch
```

Current clean campaign bootstrap:

- `16294900`: `bootstrap_tts_cpu` completed successfully

Current working Anvil rerun jobs:

- `16294901`: `sf_r1_7b_he_s42`
- `16294903`: `sf_r1_7b_mbpp_s42`
- `16294905`: `sf_qwen14b_he_s42`
- `16294907`: `sf_qwen14b_mbpp_s42`
- later jobs in the same submission wave continue through the 32B shard runs

Current chained merge/refresh jobs:

- `16294980`: merged refresh for 7B and Qwen14B runs
- `16294981`: merge 32B HumanEval+ outputs
- `16294982`: merge 32B MBPP+ outputs
- `16294983`: grand publication refresh after all merged outputs complete

If large multi-seed jobs get stuck with `AssocGrpGRESMinutes`, cancel only those blocked submissions and fall back to the single-seed pattern above.

For larger 32B runs, the checked-in Anvil job now supports benchmark sharding with `PROBLEM_OFFSET` and `MAX_PROBLEMS`. Example:

```bash
sbatch --parsable \
  --account=bio260046-gpu \
  --partition=gpu \
  --gpus-per-node=2 \
  --cpus-per-task=48 \
  --time=08:00:00 \
  --job-name=sf_r1_32b_he_s42_shard0 \
  --export=ALL,MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B,BENCHMARKS=humaneval_plus,METHODS=greedy:majority_vote:self_debug:falsification:oracle,OUTPUT_DIR=results/anvil_fix_r1_32b_humaneval_s42_shard0,SEEDS=42,PROBLEM_OFFSET=0,MAX_PROBLEMS=64,N_CANDIDATES=16,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE=2 \
  slurm/anvil_full_experiment.sbatch
```

Shard outputs can be recombined with:

```bash
python scripts/merge_seed_results.py \
  --run-dir results/anvil_fix_r1_32b_humaneval_s42_shard0 \
  --run-dir results/anvil_fix_r1_32b_humaneval_s42_shard1 \
  --run-dir results/anvil_fix_r1_32b_humaneval_s42_shard2 \
  --output-file results/anvil_fix_r1_32b_humaneval_s42_merged/results.json
```

## Run a one-off command remotely

```bash
bash scripts/anvil_run.sh 'cd /anvil/projects/x-bio260046/tts-falsification && pwd && hostname'
```

## Monitor jobs

```bash
bash scripts/anvil_monitor.sh
bash scripts/anvil_monitor.sh 12345678,12345679
```

## Check accounting state

```bash
bash scripts/anvil_sacct.sh 12345678,12345679
```

## Tail a Slurm log

```bash
bash scripts/anvil_tail_log.sh slurm-12345678.out
```

## Find result files

```bash
bash scripts/anvil_find_results.sh
```

## Notes

- The helper scripts read defaults from `scripts/anvil_env.sh`.
- The current clean rerun campaign has already cleared its environment dependency: bootstrap job `16294900` completed, and the queued GPU jobs are now waiting on scheduler priority rather than env setup.
- Override values at invocation time if needed, for example:

```bash
ANVIL_PROJECT_ROOT=/anvil/projects/x-bio260046/other-project bash scripts/anvil_monitor.sh
```
