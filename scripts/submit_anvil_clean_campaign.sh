#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"
GPU_ACCOUNT="${GPU_ACCOUNT:-bio260046-gpu}"
CPU_ACCOUNT="${CPU_ACCOUNT:-bio260046}"
CONDA_ENV_PATH="${CONDA_ENV_PATH:-/anvil/scratch/x-adas17/tts-runtime/conda-envs/tts}"

if [[ "${1:-}" == "--afterok" ]]; then
  AFTEROK_DEPENDENCY="${2:-}"
  shift 2
fi

dep_args=()
if [[ -n "$AFTEROK_DEPENDENCY" ]]; then
  dep_args=(--dependency="afterok:${AFTEROK_DEPENDENCY}")
fi

submit_report() {
  local exp_job="$1"
  local job_name="$2"
  local output_dir="$3"
  sbatch --parsable \
    --account="$CPU_ACCOUNT" \
    --partition=shared \
    --dependency="afterany:${exp_job}" \
    --job-name="${job_name}_rep" \
    --export=ALL,RESULTS_FILE="${output_dir}/results.json",PROGRESS_DIR="${output_dir}",OUTPUT_DIR="figures/${job_name}" \
    slurm/report_results_cpu.sbatch
}

submit_single_seed() {
  local gpus="$1"
  local cpus="$2"
  local wall="$3"
  local job_name="$4"
  local model="$5"
  local benchmark="$6"
  local output_dir="$7"
  local tp_size="$8"
  local max_problems="$9"
  local seed="${10}"
  local jid rid
  jid=$(sbatch --parsable \
    --account="$GPU_ACCOUNT" \
    --partition=gpu \
    "${dep_args[@]}" \
    --gpus-per-node="$gpus" \
    --cpus-per-task="$cpus" \
    --time="$wall" \
    --job-name="$job_name" \
    --export=ALL,BACKEND=transformers,MODEL="$model",BENCHMARKS="$benchmark",METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle,OUTPUT_DIR="$output_dir",SEEDS="$seed",MAX_PROBLEMS="$max_problems",N_CANDIDATES=16,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE="$tp_size" \
    slurm/anvil_full_experiment.sbatch)
  rid=$(submit_report "$jid" "$job_name" "$output_dir")
  echo "$jid $rid"
}

submit_shard_seed() {
  local gpus="$1"
  local cpus="$2"
  local wall="$3"
  local job_name="$4"
  local model="$5"
  local benchmark="$6"
  local output_dir="$7"
  local tp_size="$8"
  local max_problems="$9"
  local seed="${10}"
  local problem_offset="${11}"
  local jid rid
  jid=$(sbatch --parsable \
    --account="$GPU_ACCOUNT" \
    --partition=gpu \
    "${dep_args[@]}" \
    --gpus-per-node="$gpus" \
    --cpus-per-task="$cpus" \
    --time="$wall" \
    --job-name="$job_name" \
    --export=ALL,BACKEND=transformers,MODEL="$model",BENCHMARKS="$benchmark",METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle,OUTPUT_DIR="$output_dir",SEEDS="$seed",PROBLEM_OFFSET="$problem_offset",MAX_PROBLEMS="$max_problems",N_CANDIDATES=16,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE="$tp_size" \
    slurm/anvil_full_experiment.sbatch)
  rid=$(submit_report "$jid" "$job_name" "$output_dir")
  echo "$jid $rid"
}

declare -a merge_refresh_report_ids=()
declare -a he32_report_ids=()
declare -a mbpp32_report_ids=()

for seed in 42 43 44; do
  read -r jid rid <<<"$(submit_single_seed 1 32 08:00:00 "sf_r1_7b_he_s${seed}" deepseek-ai/DeepSeek-R1-Distill-Qwen-7B humaneval_plus "results/anvil_fix_r1_7b_humaneval_s${seed}" 1 164 "$seed")"
  merge_refresh_report_ids+=("$rid")
  echo "queued sf_r1_7b_he_s${seed} exp=${jid} rep=${rid}"

  read -r jid rid <<<"$(submit_single_seed 1 32 12:00:00 "sf_r1_7b_mbpp_s${seed}" deepseek-ai/DeepSeek-R1-Distill-Qwen-7B mbpp_plus "results/anvil_fix_r1_7b_mbpp_s${seed}" 1 378 "$seed")"
  merge_refresh_report_ids+=("$rid")
  echo "queued sf_r1_7b_mbpp_s${seed} exp=${jid} rep=${rid}"

  read -r jid rid <<<"$(submit_single_seed 1 32 10:00:00 "sf_qwen14b_he_s${seed}" Qwen/Qwen2.5-Coder-14B-Instruct humaneval_plus "results/anvil_fix_qwen14b_humaneval_s${seed}" 1 164 "$seed")"
  merge_refresh_report_ids+=("$rid")
  echo "queued sf_qwen14b_he_s${seed} exp=${jid} rep=${rid}"

  read -r jid rid <<<"$(submit_single_seed 1 32 16:00:00 "sf_qwen14b_mbpp_s${seed}" Qwen/Qwen2.5-Coder-14B-Instruct mbpp_plus "results/anvil_fix_qwen14b_mbpp_s${seed}" 1 378 "$seed")"
  merge_refresh_report_ids+=("$rid")
  echo "queued sf_qwen14b_mbpp_s${seed} exp=${jid} rep=${rid}"
done

for seed in 42 43 44; do
  while read -r offset limit wall shard; do
    read -r jid rid <<<"$(submit_shard_seed 2 48 "$wall" "sf_r1_32b_he_s${seed}_${shard}" deepseek-ai/DeepSeek-R1-Distill-Qwen-32B humaneval_plus "results/anvil_fix_r1_32b_humaneval_s${seed}_${shard}" 2 "$limit" "$seed" "$offset")"
    he32_report_ids+=("$rid")
    echo "queued sf_r1_32b_he_s${seed}_${shard} exp=${jid} rep=${rid}"
  done <<'EOF'
0 64 08:00:00 sh0
64 64 08:00:00 sh1
128 36 06:00:00 sh2
EOF

  while read -r offset limit wall shard; do
    read -r jid rid <<<"$(submit_shard_seed 2 48 "$wall" "sf_r1_32b_mbpp_s${seed}_${shard}" deepseek-ai/DeepSeek-R1-Distill-Qwen-32B mbpp_plus "results/anvil_fix_r1_32b_mbpp_s${seed}_${shard}" 2 "$limit" "$seed" "$offset")"
    mbpp32_report_ids+=("$rid")
    echo "queued sf_r1_32b_mbpp_s${seed}_${shard} exp=${jid} rep=${rid}"
  done <<'EOF'
0 64 10:00:00 sh0
64 64 10:00:00 sh1
128 64 10:00:00 sh2
192 64 10:00:00 sh3
256 64 10:00:00 sh4
320 58 09:00:00 sh5
EOF
done

dep_merge_refresh=$(IFS=:; echo "${merge_refresh_report_ids[*]}")
merge_refresh_job=$(sbatch --parsable \
  --account="$CPU_ACCOUNT" \
  --partition=shared \
  --dependency="afterany:${dep_merge_refresh}" \
  --job-name=sf_merge_refresh_7b14b \
  --output=logs/sf_merge_refresh_7b14b_%j.out \
  --wrap="cd /anvil/projects/x-bio260046/tts-falsification && module purge && module load conda && CONDA_BASE=\$(conda info --base) && source \${CONDA_BASE}/etc/profile.d/conda.sh && conda activate ${CONDA_ENV_PATH} && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_r1_7b_humaneval_s42 --run-dir results/anvil_fix_r1_7b_humaneval_s43 --run-dir results/anvil_fix_r1_7b_humaneval_s44 --output-file results/anvil_fix_r1_7b_humaneval_merged/results.json && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_r1_7b_mbpp_s42 --run-dir results/anvil_fix_r1_7b_mbpp_s43 --run-dir results/anvil_fix_r1_7b_mbpp_s44 --output-file results/anvil_fix_r1_7b_mbpp_merged/results.json && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_qwen14b_humaneval_s42 --run-dir results/anvil_fix_qwen14b_humaneval_s43 --run-dir results/anvil_fix_qwen14b_humaneval_s44 --output-file results/anvil_fix_qwen14b_humaneval_merged/results.json && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_qwen14b_mbpp_s42 --run-dir results/anvil_fix_qwen14b_mbpp_s43 --run-dir results/anvil_fix_qwen14b_mbpp_s44 --output-file results/anvil_fix_qwen14b_mbpp_merged/results.json && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_r1_7b_humaneval_merged/results.json --output-dir figures/anvil_fix_r1_7b_humaneval_merged && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_r1_7b_mbpp_merged/results.json --output-dir figures/anvil_fix_r1_7b_mbpp_merged && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_qwen14b_humaneval_merged/results.json --output-dir figures/anvil_fix_qwen14b_humaneval_merged && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_qwen14b_mbpp_merged/results.json --output-dir figures/anvil_fix_qwen14b_mbpp_merged" \
)
echo "queued merge_refresh_7b14b=${merge_refresh_job}"

dep_he32=$(IFS=:; echo "${he32_report_ids[*]}")
dep_mbpp32=$(IFS=:; echo "${mbpp32_report_ids[*]}")

merge_he32_job=$(sbatch --parsable \
  --account="$CPU_ACCOUNT" \
  --partition=shared \
  --dependency="afterany:${dep_he32}" \
  --job-name=sf_merge_r1_32b_he_full \
  --output=logs/sf_merge_r1_32b_he_full_%j.out \
  --wrap="cd /anvil/projects/x-bio260046/tts-falsification && module purge && module load conda && CONDA_BASE=\$(conda info --base) && source \${CONDA_BASE}/etc/profile.d/conda.sh && conda activate ${CONDA_ENV_PATH} && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_r1_32b_humaneval_s42_sh0 --run-dir results/anvil_fix_r1_32b_humaneval_s42_sh1 --run-dir results/anvil_fix_r1_32b_humaneval_s42_sh2 --run-dir results/anvil_fix_r1_32b_humaneval_s43_sh0 --run-dir results/anvil_fix_r1_32b_humaneval_s43_sh1 --run-dir results/anvil_fix_r1_32b_humaneval_s43_sh2 --run-dir results/anvil_fix_r1_32b_humaneval_s44_sh0 --run-dir results/anvil_fix_r1_32b_humaneval_s44_sh1 --run-dir results/anvil_fix_r1_32b_humaneval_s44_sh2 --output-file results/anvil_fix_r1_32b_humaneval_merged/results.json && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_r1_32b_humaneval_merged/results.json --output-dir figures/anvil_fix_r1_32b_humaneval_merged" \
)
echo "queued merge_r1_32b_he_full=${merge_he32_job}"

merge_mbpp32_job=$(sbatch --parsable \
  --account="$CPU_ACCOUNT" \
  --partition=shared \
  --dependency="afterany:${dep_mbpp32}" \
  --job-name=sf_merge_r1_32b_mbpp_full \
  --output=logs/sf_merge_r1_32b_mbpp_full_%j.out \
  --wrap="cd /anvil/projects/x-bio260046/tts-falsification && module purge && module load conda && CONDA_BASE=\$(conda info --base) && source \${CONDA_BASE}/etc/profile.d/conda.sh && conda activate ${CONDA_ENV_PATH} && ${CONDA_ENV_PATH}/bin/python scripts/merge_seed_results.py --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh0 --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh1 --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh2 --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh3 --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh4 --run-dir results/anvil_fix_r1_32b_mbpp_s42_sh5 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh0 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh1 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh2 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh3 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh4 --run-dir results/anvil_fix_r1_32b_mbpp_s43_sh5 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh0 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh1 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh2 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh3 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh4 --run-dir results/anvil_fix_r1_32b_mbpp_s44_sh5 --output-file results/anvil_fix_r1_32b_mbpp_merged/results.json && ${CONDA_ENV_PATH}/bin/python src/report.py --results-file results/anvil_fix_r1_32b_mbpp_merged/results.json --output-dir figures/anvil_fix_r1_32b_mbpp_merged" \
)
echo "queued merge_r1_32b_mbpp_full=${merge_mbpp32_job}"

grand_refresh_job=$(sbatch --parsable \
  --account="$CPU_ACCOUNT" \
  --partition=shared \
  --dependency="afterany:${merge_refresh_job}:${merge_he32_job}:${merge_mbpp32_job}" \
  --job-name=sf_grand_refresh_full \
  --output=logs/sf_grand_refresh_full_%j.out \
  --wrap="cd /anvil/projects/x-bio260046/tts-falsification && module purge && module load conda && CONDA_BASE=\$(conda info --base) && source \${CONDA_BASE}/etc/profile.d/conda.sh && conda activate ${CONDA_ENV_PATH} && ${CONDA_ENV_PATH}/bin/python scripts/refresh_publication_state.py --results-file results/anvil_fix_r1_7b_humaneval_merged/results.json --results-file results/anvil_fix_r1_7b_mbpp_merged/results.json --results-file results/anvil_fix_qwen14b_humaneval_merged/results.json --results-file results/anvil_fix_qwen14b_mbpp_merged/results.json --results-file results/anvil_fix_r1_32b_humaneval_merged/results.json --results-file results/anvil_fix_r1_32b_mbpp_merged/results.json" \
)
echo "queued grand_refresh_full=${grand_refresh_job}"
