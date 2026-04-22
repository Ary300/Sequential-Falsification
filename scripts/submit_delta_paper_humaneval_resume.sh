#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

GPU_ACCOUNT="${GPU_ACCOUNT:-$DELTA_ACCOUNT}"
GPU_PARTITION="${GPU_PARTITION:-$DELTA_PARTITION}"
GPU_QOS="${GPU_QOS:-$DELTA_QOS}"
REPORT_ACCOUNT="${REPORT_ACCOUNT:-$DELTA_ACCOUNT}"
REPORT_PARTITION="${REPORT_PARTITION:-ghx4-interactive}"
REPORT_QOS="${REPORT_QOS:-}"
DELTA_7B_WALL="${DELTA_7B_WALL:-12:00:00}"
DELTA_14B_WALL="${DELTA_14B_WALL:-12:00:00}"
DELTA_32B_GPUS="${DELTA_32B_GPUS:-2}"
DELTA_32B_CPUS="${DELTA_32B_CPUS:-32}"
DELTA_32B_WALL="${DELTA_32B_WALL:-24:00:00}"
DELTA_32B_TP_SIZE="${DELTA_32B_TP_SIZE:-2}"
DELTA_32B_MAX_MODEL_LEN="${DELTA_32B_MAX_MODEL_LEN:-16384}"
ENABLE_7B="${ENABLE_7B:-1}"
ENABLE_14B="${ENABLE_14B:-1}"
ENABLE_32B="${ENABLE_32B:-1}"
SYNC_FIRST=0
DRY_RUN=0
DELTA_LOCAL_MODE=0

host_name="$(hostname 2>/dev/null || true)"
if [[ "${host_name}" == gh-login* || "${host_name}" == dtai-login* || "${PWD}" == /u/${DELTA_USER}/* ]]; then
  DELTA_LOCAL_MODE=1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sync-first)
      SYNC_FIRST=1
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

if [[ "${SYNC_FIRST}" -eq 1 && "${DELTA_LOCAL_MODE}" -eq 0 ]]; then
  rsync -av \
    --exclude '.git/' \
    --exclude '__pycache__/' \
    --exclude 'results/' \
    --exclude 'figures/' \
    --exclude 'logs/' \
    --exclude 'checkpoints/' \
    -e "ssh ${DELTA_SSH_KEY:+-i ${DELTA_SSH_KEY}} ${DELTA_SSH_OPTS}" \
    "${ROOT_DIR}/" \
    "${DELTA_LOGIN}:${DELTA_PROJECT_ROOT}/"
fi

submit_remote() {
  local cmd="$1"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    local fake_id="dryrun_${RANDOM}_${RANDOM}"
    echo "DRYRUN[${fake_id}] ${cmd}" >&2
    echo "${fake_id}"
  elif [[ "${DELTA_LOCAL_MODE}" -eq 1 ]]; then
    bash -lc "${cmd}"
  else
    delta_ssh_base "${cmd}"
  fi
}

submit_resume_job() {
  local job_name="$1"
  local model="$2"
  local output_dir="$3"
  local seed="$4"
  local gpus="$5"
  local cpus="$6"
  local wall="$7"
  local tp_size="$8"
  local max_model_len="$9"

  local cmd
  cmd=$(
    cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
sbatch --parsable --account="${GPU_ACCOUNT}" --partition="${GPU_PARTITION}" --qos="${GPU_QOS}" \
  --gpus-per-node="${gpus}" --cpus-per-task="${cpus}" --time="${wall}" --job-name="${job_name}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},BACKEND=openai,MODEL=${model},BENCHMARKS=humaneval_plus,METHODS=greedy:majority_vote:self_debug:falsification:oracle,OUTPUT_DIR=${output_dir},SEEDS=${seed},MAX_PROBLEMS=164,N_CANDIDATES=8,N_ROUNDS=2,TEMPERATURE=0.7,MAX_TOKENS=512,TP_SIZE=${tp_size},MAX_MODEL_LEN=${max_model_len},DATA_ROOT=data \
  slurm/delta/full_experiment_delta.sbatch
EOF
  )
  submit_remote "${cmd}"
}

submit_report_job() {
  local dependency_id="$1"
  local job_name="$2"
  local progress_dir="$3"
  local figure_dir="$4"
  local report_qos_arg=""
  if [[ -n "${REPORT_QOS}" ]]; then
    report_qos_arg="--qos=\"${REPORT_QOS}\""
  fi

  local cmd
  cmd=$(
    cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
sbatch --parsable --account="${REPORT_ACCOUNT}" --partition="${REPORT_PARTITION}" ${report_qos_arg} \
  --dependency="afterok:${dependency_id}" --job-name="${job_name}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},RESULTS_FILE=${progress_dir}/results.json,PROGRESS_DIR=${progress_dir},OUTPUT_DIR=${figure_dir} \
  slurm/delta/report_results_delta.sbatch
EOF
  )
  submit_remote "${cmd}"
}

declare -a rows=()
if [[ "${ENABLE_7B}" == "1" ]]; then
  rows+=("resume_he7b_s43|deepseek-ai/DeepSeek-R1-Distill-Qwen-7B|results/paper_r1_7b_humaneval_full|43|1|16|${DELTA_7B_WALL}|1|16384|report_he7b_s43|figures/paper_r1_7b_humaneval_full")
fi
if [[ "${ENABLE_14B}" == "1" ]]; then
  rows+=("resume_he14b_s44|Qwen/Qwen2.5-Coder-14B-Instruct|results/paper_qwen14b_humaneval_full|44|1|16|${DELTA_14B_WALL}|1|16384|report_he14b_s44|figures/paper_qwen14b_humaneval_full")
fi
if [[ "${ENABLE_32B}" == "1" ]]; then
  rows+=("resume_he32b_s44|deepseek-ai/DeepSeek-R1-Distill-Qwen-32B|results/paper_r1_32b_humaneval_full|44|${DELTA_32B_GPUS}|${DELTA_32B_CPUS}|${DELTA_32B_WALL}|${DELTA_32B_TP_SIZE}|${DELTA_32B_MAX_MODEL_LEN}|report_he32b_s44|figures/paper_r1_32b_humaneval_full")
fi

if [[ "${#rows[@]}" -eq 0 ]]; then
  echo "No resume jobs selected; enable at least one of ENABLE_7B, ENABLE_14B, ENABLE_32B." >&2
  exit 1
fi

declare -a all_job_ids=()
for row in "${rows[@]}"; do
  IFS='|' read -r run_job model output_dir seed gpus cpus wall tp_size max_model_len report_job figure_dir <<< "${row}"
  run_id="$(submit_resume_job "${run_job}" "${model}" "${output_dir}" "${seed}" "${gpus}" "${cpus}" "${wall}" "${tp_size}" "${max_model_len}")"
  report_id="$(submit_report_job "${run_id}" "${report_job}" "${output_dir}" "${figure_dir}")"
  echo "${run_job}=${run_id}"
  echo "${report_job}=${report_id}"
  all_job_ids+=("${run_id}" "${report_id}")
done

job_csv="$(IFS=,; echo "${all_job_ids[*]}")"
if [[ "${DRY_RUN}" -eq 0 ]]; then
  submit_remote "squeue -j ${job_csv} -O jobid,state,reason,name,timeused,timeleft"
fi
