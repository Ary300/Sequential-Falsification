#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

GPU_ACCOUNT="${GPU_ACCOUNT:-$DELTA_ACCOUNT}"
GPU_PARTITION="${GPU_PARTITION:-$DELTA_PARTITION}"
GPU_QOS="${GPU_QOS:-$DELTA_QOS}"
DELTA_LOCAL_MODE=0
DRY_RUN=0
SYNC_FIRST=0

ROWS_JSONL="${ROWS_JSONL:-/work/nvme/bgvi/${DELTA_USER}/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl,/work/nvme/bgvi/${DELTA_USER}/tts_results/theorem3_closedbook_control_r1_14b_v1/theorem3_generation_rows.jsonl}"
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_confidence_head_pilot_r1_14b_v1}"
MODEL_NAME="${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}"
MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS:-1200}"
MAX_VAL_ROWS="${MAX_VAL_ROWS:-200}"
MAX_EVAL_ROWS="${MAX_EVAL_ROWS:-500}"
TRAIN_BENCHMARKS="${TRAIN_BENCHMARKS:-wikicontradict,conflictbank}"
EVAL_BENCHMARK="${EVAL_BENCHMARK:-conflictbank}"
EVAL_CONDITION="${EVAL_CONDITION:-conflict_context}"
EVAL_COT_LENGTH="${EVAL_COT_LENGTH:-1024}"
MAX_LENGTH="${MAX_LENGTH:-1024}"
FEATURE_BATCH_SIZE="${FEATURE_BATCH_SIZE:-2}"
EPOCHS="${EPOCHS:-12}"
LR="${LR:-0.002}"
WEIGHT_DECAY="${WEIGHT_DECAY:-0.0001}"
SEED="${SEED:-42}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
WALL="${WALL:-08:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-t3_confhead}"

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
  --export=ALL,DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT},DELTA_VENV=${DELTA_VENV},DELTA_RESULTS_ROOT=/work/nvme/bgvi/${DELTA_USER}/tts_results,ROWS_JSONL=${ROWS_JSONL},OUTPUT_DIR=${OUTPUT_DIR},MODEL_NAME=${MODEL_NAME},MAX_TRAIN_ROWS=${MAX_TRAIN_ROWS},MAX_VAL_ROWS=${MAX_VAL_ROWS},MAX_EVAL_ROWS=${MAX_EVAL_ROWS},TRAIN_BENCHMARKS=${TRAIN_BENCHMARKS},EVAL_BENCHMARK=${EVAL_BENCHMARK},EVAL_CONDITION=${EVAL_CONDITION},EVAL_COT_LENGTH=${EVAL_COT_LENGTH},MAX_LENGTH=${MAX_LENGTH},FEATURE_BATCH_SIZE=${FEATURE_BATCH_SIZE},EPOCHS=${EPOCHS},LR=${LR},WEIGHT_DECAY=${WEIGHT_DECAY},SEED=${SEED},TORCH_DTYPE=${TORCH_DTYPE} \
  slurm/delta/theorem3_confidence_head_pilot_delta.sbatch
EOF
)

submit_remote "${cmd}"
