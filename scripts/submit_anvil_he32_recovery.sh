#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/anvil_env.sh"

GPU_ACCOUNT="${GPU_ACCOUNT:-${ANVIL_ACCOUNT}}"
GPU_PARTITION="${GPU_PARTITION:-${ANVIL_PARTITION}}"
CPU_ACCOUNT="${CPU_ACCOUNT:-bio260046}"
CPU_PARTITION="${CPU_PARTITION:-shared}"
AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"
SYNC_FIRST=0
SUBMIT_BOOTSTRAP=1
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --afterok)
      AFTEROK_DEPENDENCY="$2"
      SUBMIT_BOOTSTRAP=0
      shift 2
      ;;
    --sync-first)
      SYNC_FIRST=1
      shift
      ;;
    --no-bootstrap)
      SUBMIT_BOOTSTRAP=0
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

submit_local() {
  local cmd="$1"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    local fake_id="dryrun_${RANDOM}_${RANDOM}"
    echo "DRYRUN[${fake_id}] ${cmd}" >&2
    echo "${fake_id}"
  else
    eval "${cmd}"
  fi
}

submit_remote() {
  local cmd="$1"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    local fake_id="dryrun_${RANDOM}_${RANDOM}"
    echo "DRYRUN[${fake_id}] ${cmd}" >&2
    echo "${fake_id}"
  else
    anvil_ssh_base "${cmd}"
  fi
}

if [[ "${SYNC_FIRST}" -eq 1 ]]; then
  bash "${SCRIPT_DIR}/anvil_sync.sh"
fi

if [[ -z "${AFTEROK_DEPENDENCY}" && "${SUBMIT_BOOTSTRAP}" -eq 1 ]]; then
  AFTEROK_DEPENDENCY="$(
    submit_local "bash \"${SCRIPT_DIR}/anvil_submit_cpu.sh\" slurm/bootstrap_env_cpu.sbatch"
  )"
  echo "queued bootstrap=${AFTEROK_DEPENDENCY}"
fi

declare -a base_dep_args=()
if [[ -n "${AFTEROK_DEPENDENCY}" ]]; then
  base_dep_args=(--dependency="afterok:${AFTEROK_DEPENDENCY}")
fi

submit_report() {
  local exp_id="$1"
  local job_name="$2"
  local output_dir="$3"
  local cmd
  cmd=$(
    cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${CPU_ACCOUNT}" --partition="${CPU_PARTITION}" \
  --dependency="afterany:${exp_id}" --job-name="${job_name}_rep" \
  --export=ALL,ANVIL_CONDA_ENV=${ANVIL_CONDA_ENV},RESULTS_FILE=${output_dir}/results.json,PROGRESS_DIR=${output_dir},OUTPUT_DIR=figures/${job_name} \
  slurm/report_results_cpu.sbatch
EOF
  )
  submit_remote "${cmd}"
}

declare -a report_ids=()

for seed in 42 43 44; do
  while read -r offset limit wall shard; do
    job_name="sf_r1_32b_he_recover_s${seed}_${shard}"
    output_dir="results/anvil_fix_r1_32b_humaneval_s${seed}_${shard}"
    exp_cmd=$(
      cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${GPU_ACCOUNT}" --partition="${GPU_PARTITION}" \
  ${base_dep_args:+${base_dep_args[*]}} \
  --gpus-per-node=2 --cpus-per-task=48 --time="${wall}" --job-name="${job_name}" \
  --export=ALL,ANVIL_CONDA_ENV=${ANVIL_CONDA_ENV},BACKEND=transformers,MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B,BENCHMARKS=humaneval_plus,METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle,OUTPUT_DIR=${output_dir},SEEDS=${seed},PROBLEM_OFFSET=${offset},MAX_PROBLEMS=${limit},N_CANDIDATES=16,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE=2 \
  slurm/anvil_full_experiment.sbatch
EOF
    )
    exp_id="$(submit_remote "${exp_cmd}")"
    rep_id="$(submit_report "${exp_id}" "${job_name}" "${output_dir}")"
    report_ids+=("${rep_id}")
    echo "queued ${job_name} exp=${exp_id} rep=${rep_id}"
  done <<'EOF'
0 64 08:00:00 sh0
64 64 08:00:00 sh1
128 36 06:00:00 sh2
EOF
done

dep_chain=$(IFS=:; echo "${report_ids[*]}")
merge_job_name="sf_r1_32b_he_remerge"
merge_output="results/anvil_fix_r1_32b_humaneval_merged/results.json"
merge_fig_dir="figures/anvil_fix_r1_32b_humaneval_merged"
merge_wrap="cd ${ANVIL_PROJECT_ROOT} && export ANVIL_HOME=${ANVIL_HOME} HOME=${ANVIL_HOME} PYTHONNOUSERSITE=1 && mkdir -p ${ANVIL_HOME} && module purge && module load conda && CONDA_BASE=\$(conda info --base) && source \${CONDA_BASE}/etc/profile.d/conda.sh && conda activate ${ANVIL_CONDA_ENV} && ${ANVIL_CONDA_ENV}/bin/python scripts/merge_seed_results.py"
for seed in 42 43 44; do
  for shard in sh0 sh1 sh2; do
    merge_wrap+=" --run-dir results/anvil_fix_r1_32b_humaneval_s${seed}_${shard}"
  done
done
merge_wrap+=" --output-file ${merge_output} && ${ANVIL_CONDA_ENV}/bin/python src/report.py --results-file ${merge_output} --output-dir ${merge_fig_dir}"

merge_cmd=$(
  cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${CPU_ACCOUNT}" --partition="${CPU_PARTITION}" \
  --dependency="afterany:${dep_chain}" --job-name="${merge_job_name}" \
  --output="logs/${merge_job_name}_%j.out" \
  --wrap='${merge_wrap}'
EOF
)
merge_id="$(submit_remote "${merge_cmd}")"
echo "queued ${merge_job_name} merge=${merge_id}"
