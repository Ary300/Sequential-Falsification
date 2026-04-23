#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

GPU_ACCOUNT="${GPU_ACCOUNT:-$DELTA_ACCOUNT}"
GPU_PARTITION="${GPU_PARTITION:-$DELTA_PARTITION}"
GPU_QOS="${GPU_QOS:-$DELTA_QOS}"
SYNC_FIRST=0
DRY_RUN=0
DELTA_LOCAL_MODE=0

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}"
BENCHMARKS="${BENCHMARKS:-humaneval_plus:mbpp_plus}"
VERIFIERS="${VERIFIERS:-majority:public_test:sce_trace}"
OUTPUT_DIR="${OUTPUT_DIR:-results/capacity_pilot_delta}"
BACKEND="${BACKEND:-openai}"
SEED="${SEED:-42}"
N_CANDIDATES="${N_CANDIDATES:-16}"
MAX_PROBLEMS="${MAX_PROBLEMS:-32}"
TIMEOUT="${TIMEOUT:-10}"
TEMPERATURE="${TEMPERATURE:-0.7}"
MAX_TOKENS="${MAX_TOKENS:-512}"
TP_SIZE="${TP_SIZE:-1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
WALL="${WALL:-08:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-capacity_pilot}"

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
    echo "DRYRUN ${cmd}" >&2
  elif [[ "${DELTA_LOCAL_MODE}" -eq 1 ]]; then
    bash -lc "${cmd}"
  else
    delta_ssh_base "${cmd}"
  fi
}

cmd=$(
  cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
sbatch --parsable --account="${GPU_ACCOUNT}" --partition="${GPU_PARTITION}" --qos="${GPU_QOS}" \
  --gpus-per-node="${GPUS}" --cpus-per-task="${CPUS}" --time="${WALL}" --job-name="${JOB_NAME}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},MODEL=${MODEL},BENCHMARKS=${BENCHMARKS},VERIFIERS=${VERIFIERS},OUTPUT_DIR=${OUTPUT_DIR},BACKEND=${BACKEND},SEED=${SEED},N_CANDIDATES=${N_CANDIDATES},MAX_PROBLEMS=${MAX_PROBLEMS},TIMEOUT=${TIMEOUT},TEMPERATURE=${TEMPERATURE},MAX_TOKENS=${MAX_TOKENS},TP_SIZE=${TP_SIZE},MAX_MODEL_LEN=${MAX_MODEL_LEN} \
  slurm/delta/capacity_pilot_delta.sbatch
EOF
)

submit_remote "${cmd}"
