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
AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"
SYNC_FIRST=0
DRY_RUN=0
DELTA_LOCAL_MODE=0

METHODS="${METHODS:-greedy:majority_vote:generated_test_filter:self_debug:code_t:s_star:falsification:oracle}"
PROBE_STRATEGY="${PROBE_STRATEGY:-adaptive_population}"
ADAPTIVE_PROBE_SELECTION="${ADAPTIVE_PROBE_SELECTION:-true}"
ELIMINATE_ON_DETECTION="${ELIMINATE_ON_DETECTION:-true}"
CONFIDENCE_MODE="${CONFIDENCE_MODE:-wealth}"
MAX_DIFFERENTIAL_PROBES="${MAX_DIFFERENTIAL_PROBES:-8}"
CONSENSUS_MIN_FRACTION="${CONSENSUS_MIN_FRACTION:-0.70}"
CONSENSUS_MIN_MARGIN="${CONSENSUS_MIN_MARGIN:-2}"
CONSENSUS_MIN_VOTES="${CONSENSUS_MIN_VOTES:-3}"
DATA_ROOT="${DATA_ROOT:-data}"
RESULT_PREFIX="${RESULT_PREFIX:-paperproxy}"
JOB_PREFIX="${JOB_PREFIX:-}"

N_CANDIDATES="${N_CANDIDATES:-8}"
N_ROUNDS="${N_ROUNDS:-2}"
MAX_TIEBREAK_ROUNDS="${MAX_TIEBREAK_ROUNDS:-4}"
TEMPERATURE="${TEMPERATURE:-0.7}"
MAX_TOKENS="${MAX_TOKENS:-512}"

ENABLE_7B="${ENABLE_7B:-1}"
ENABLE_14B="${ENABLE_14B:-1}"
ENABLE_32B="${ENABLE_32B:-1}"

RUN_HUMANEVAL="${RUN_HUMANEVAL:-1}"
RUN_MBPP="${RUN_MBPP:-1}"
RUN_LIVECODEBENCH="${RUN_LIVECODEBENCH:-0}"
RUN_MATH500="${RUN_MATH500:-0}"

LCB_MAX_PROBLEMS="${LCB_MAX_PROBLEMS:-400}"
MATH_MAX_PROBLEMS="${MATH_MAX_PROBLEMS:-500}"
HUMANEVAL_MAX_PROBLEMS="${HUMANEVAL_MAX_PROBLEMS:-164}"
MBPP_MAX_PROBLEMS="${MBPP_MAX_PROBLEMS:-378}"

DELTA_7B_WALL="${DELTA_7B_WALL:-18:00:00}"
DELTA_14B_WALL="${DELTA_14B_WALL:-20:00:00}"
DELTA_32B_WALL="${DELTA_32B_WALL:-30:00:00}"
DELTA_7B_GPUS="${DELTA_7B_GPUS:-1}"
DELTA_14B_GPUS="${DELTA_14B_GPUS:-1}"
DELTA_32B_GPUS="${DELTA_32B_GPUS:-1}"
DELTA_7B_CPUS="${DELTA_7B_CPUS:-16}"
DELTA_14B_CPUS="${DELTA_14B_CPUS:-16}"
DELTA_32B_CPUS="${DELTA_32B_CPUS:-16}"
DELTA_7B_TP_SIZE="${DELTA_7B_TP_SIZE:-1}"
DELTA_14B_TP_SIZE="${DELTA_14B_TP_SIZE:-1}"
DELTA_32B_TP_SIZE="${DELTA_32B_TP_SIZE:-1}"
DELTA_7B_MAX_MODEL_LEN="${DELTA_7B_MAX_MODEL_LEN:-16384}"
DELTA_14B_MAX_MODEL_LEN="${DELTA_14B_MAX_MODEL_LEN:-16384}"
DELTA_32B_MAX_MODEL_LEN="${DELTA_32B_MAX_MODEL_LEN:-8192}"

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

submit_run_job() {
  local job_name="$1"
  local model="$2"
  local benchmark="$3"
  local output_dir="$4"
  local max_problems="$5"
  local gpus="$6"
  local cpus="$7"
  local wall="$8"
  local tp_size="$9"
  local max_model_len="${10}"

  local cmd
  cmd=$(
    cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
sbatch --parsable --account="${GPU_ACCOUNT}" --partition="${GPU_PARTITION}" --qos="${GPU_QOS}" \
  ${AFTEROK_DEPENDENCY:+--dependency="afterok:${AFTEROK_DEPENDENCY}"} \
  --gpus-per-node="${gpus}" --cpus-per-task="${cpus}" --time="${wall}" --job-name="${job_name}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},BACKEND=openai,MODEL=${model},BENCHMARKS=${benchmark},METHODS=${METHODS},OUTPUT_DIR=${output_dir},SEEDS=42:43:44,MAX_PROBLEMS=${max_problems},N_CANDIDATES=${N_CANDIDATES},N_ROUNDS=${N_ROUNDS},MAX_TIEBREAK_ROUNDS=${MAX_TIEBREAK_ROUNDS},TEMPERATURE=${TEMPERATURE},MAX_TOKENS=${MAX_TOKENS},TP_SIZE=${tp_size},MAX_MODEL_LEN=${max_model_len},PROBE_STRATEGY=${PROBE_STRATEGY},ADAPTIVE_PROBE_SELECTION=${ADAPTIVE_PROBE_SELECTION},ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION},CONFIDENCE_MODE=${CONFIDENCE_MODE},MAX_DIFFERENTIAL_PROBES=${MAX_DIFFERENTIAL_PROBES},CONSENSUS_MIN_FRACTION=${CONSENSUS_MIN_FRACTION},CONSENSUS_MIN_MARGIN=${CONSENSUS_MIN_MARGIN},CONSENSUS_MIN_VOTES=${CONSENSUS_MIN_VOTES},DATA_ROOT=${DATA_ROOT} \
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
  --dependency="afterany:${dependency_id}" --job-name="${job_name}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},RESULTS_FILE=${progress_dir}/results.json,PROGRESS_DIR=${progress_dir},OUTPUT_DIR=${figure_dir} \
  slurm/delta/report_results_delta.sbatch
EOF
  )
  submit_remote "${cmd}"
}

append_model_rows() {
  local short="$1"
  local model="$2"
  local gpus="$3"
  local cpus="$4"
  local wall="$5"
  local tp_size="$6"
  local max_model_len="$7"

  if [[ "${RUN_HUMANEVAL}" == "1" ]]; then
    rows+=("${JOB_PREFIX}proxy_${short}_he|${model}|humaneval_plus|results/${RESULT_PREFIX}_${short}_humaneval_full|${HUMANEVAL_MAX_PROBLEMS}|${gpus}|${cpus}|${wall}|${tp_size}|${max_model_len}|figures/${RESULT_PREFIX}_${short}_humaneval_full")
  fi
  if [[ "${RUN_MBPP}" == "1" ]]; then
    rows+=("${JOB_PREFIX}proxy_${short}_mbpp|${model}|mbpp_plus|results/${RESULT_PREFIX}_${short}_mbpp_full|${MBPP_MAX_PROBLEMS}|${gpus}|${cpus}|${wall}|${tp_size}|${max_model_len}|figures/${RESULT_PREFIX}_${short}_mbpp_full")
  fi
  if [[ "${RUN_LIVECODEBENCH}" == "1" ]]; then
    rows+=("${JOB_PREFIX}proxy_${short}_lcb|${model}|livecodebench_v6|results/${RESULT_PREFIX}_${short}_livecodebench_full|${LCB_MAX_PROBLEMS}|${gpus}|${cpus}|${wall}|${tp_size}|${max_model_len}|figures/${RESULT_PREFIX}_${short}_livecodebench_full")
  fi
  if [[ "${RUN_MATH500}" == "1" ]]; then
    rows+=("${JOB_PREFIX}proxy_${short}_math|${model}|math500|results/${RESULT_PREFIX}_${short}_math500_full|${MATH_MAX_PROBLEMS}|${gpus}|${cpus}|${wall}|${tp_size}|${max_model_len}|figures/${RESULT_PREFIX}_${short}_math500_full")
  fi
}

declare -a rows=()
if [[ "${ENABLE_7B}" == "1" ]]; then
  append_model_rows "r1_7b" "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" "${DELTA_7B_GPUS}" "${DELTA_7B_CPUS}" "${DELTA_7B_WALL}" "${DELTA_7B_TP_SIZE}" "${DELTA_7B_MAX_MODEL_LEN}"
fi
if [[ "${ENABLE_14B}" == "1" ]]; then
  append_model_rows "qwen14b" "Qwen/Qwen2.5-Coder-14B-Instruct" "${DELTA_14B_GPUS}" "${DELTA_14B_CPUS}" "${DELTA_14B_WALL}" "${DELTA_14B_TP_SIZE}" "${DELTA_14B_MAX_MODEL_LEN}"
fi
if [[ "${ENABLE_32B}" == "1" ]]; then
  append_model_rows "r1_32b" "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B" "${DELTA_32B_GPUS}" "${DELTA_32B_CPUS}" "${DELTA_32B_WALL}" "${DELTA_32B_TP_SIZE}" "${DELTA_32B_MAX_MODEL_LEN}"
fi

if [[ "${#rows[@]}" -eq 0 ]]; then
  echo "No jobs selected. Enable at least one benchmark/model combination." >&2
  exit 1
fi

declare -a all_job_ids=()
for row in "${rows[@]}"; do
  IFS='|' read -r run_job model benchmark output_dir max_problems gpus cpus wall tp_size max_model_len figure_dir <<< "${row}"
  run_id="$(submit_run_job "${run_job}" "${model}" "${benchmark}" "${output_dir}" "${max_problems}" "${gpus}" "${cpus}" "${wall}" "${tp_size}" "${max_model_len}")"
  report_id="$(submit_report_job "${run_id}" "report_${run_job}" "${output_dir}" "${figure_dir}")"
  echo "${run_job}=${run_id}"
  echo "report_${run_job}=${report_id}"
  all_job_ids+=("${run_id}" "${report_id}")
done

job_csv="$(IFS=,; echo "${all_job_ids[*]}")"
if [[ "${DRY_RUN}" -eq 0 ]]; then
  submit_remote "squeue -j ${job_csv} -O jobid,state,reason,name,timeused,timeleft"
fi
