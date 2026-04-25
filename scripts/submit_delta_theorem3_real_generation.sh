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

OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_real_generation_r1_7b}"
DELTA_RESULTS_ROOT="${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/${DELTA_USER}/tts_results}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}"
BACKEND="${BACKEND:-openai}"
CONDITIONS="${CONDITIONS:-aligned_context,conflict_context}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-600}"
TEMPERATURE="${TEMPERATURE:-0.0}"
TOP_P="${TOP_P:-1.0}"
SEED="${SEED:-42}"
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-200}"
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-500}"
CONFLICTBANK_SCREENING_POOL="${CONFLICTBANK_SCREENING_POOL:-1200}"
AMBIGUITY_LOW="${AMBIGUITY_LOW:-0.2}"
AMBIGUITY_HIGH="${AMBIGUITY_HIGH:-0.8}"
TP_SIZE="${TP_SIZE:-1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
WALL="${WALL:-08:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-theorem3_real}"

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
  --export=ALL,DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT},DELTA_VENV=${DELTA_VENV},DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT},OUTPUT_DIR=${OUTPUT_DIR},MODEL=${MODEL},BACKEND=${BACKEND},CONDITIONS=${CONDITIONS},REQUEST_TIMEOUT=${REQUEST_TIMEOUT},TEMPERATURE=${TEMPERATURE},TOP_P=${TOP_P},SEED=${SEED},WIKICONTRADICT_MAX=${WIKICONTRADICT_MAX},CONFLICTBANK_MAX=${CONFLICTBANK_MAX},CONFLICTBANK_SCREENING_POOL=${CONFLICTBANK_SCREENING_POOL},AMBIGUITY_LOW=${AMBIGUITY_LOW},AMBIGUITY_HIGH=${AMBIGUITY_HIGH},TP_SIZE=${TP_SIZE},MAX_MODEL_LEN=${MAX_MODEL_LEN} \
  slurm/delta/theorem3_real_generation_delta.sbatch
EOF
)

submit_remote "${cmd}"
