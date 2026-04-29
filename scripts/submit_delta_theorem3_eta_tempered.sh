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

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}"
ROWS_JSONL="${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-/work/nvme/bgvi/adas17/tts_results/theorem3_eta_tempered_r1_14b_conflictbank_conflict}"
BENCHMARK="${BENCHMARK:-conflictbank}"
CONDITION="${CONDITION:-conflict_context}"
COT_LENGTH="${COT_LENGTH:-1024}"
CALIBRATION_SIZE="${CALIBRATION_SIZE:-200}"
SEED="${SEED:-42}"
MAX_EXAMPLES="${MAX_EXAMPLES:-}"
BATCH_SIZE="${BATCH_SIZE:-4}"
ETA_GRID="${ETA_GRID:-0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
WALL="${WALL:-08:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-theorem3_eta}"
ETA_GRID_EXPORT="${ETA_GRID//,/:}"

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
  --export=ALL,DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT},DELTA_VENV=${DELTA_VENV},MODEL=${MODEL},ROWS_JSONL=${ROWS_JSONL},OUTPUT_PREFIX=${OUTPUT_PREFIX},BENCHMARK=${BENCHMARK},CONDITION=${CONDITION},COT_LENGTH=${COT_LENGTH},CALIBRATION_SIZE=${CALIBRATION_SIZE},SEED=${SEED},MAX_EXAMPLES=${MAX_EXAMPLES},BATCH_SIZE=${BATCH_SIZE},ETA_GRID=${ETA_GRID_EXPORT},TORCH_DTYPE=${TORCH_DTYPE} \
  slurm/delta/theorem3_eta_tempered_delta.sbatch
EOF
)

submit_remote "${cmd}"
