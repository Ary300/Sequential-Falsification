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

ROWS_JSONL="${ROWS_JSONL:-/work/nvme/bgvi/${DELTA_USER}/tts_results/results/theorem3_tierA_r1_qwen14_seed42/theorem3_generation_rows.jsonl}"
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_rlcr_style_lora_r1_14b_conflict}"
MODEL_NAME="${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}"
TRAIN_BENCHMARK="${TRAIN_BENCHMARK:-conflictbank}"
TRAIN_CONDITION="${TRAIN_CONDITION:-conflict_context}"
EVAL_BENCHMARK="${EVAL_BENCHMARK:-conflictbank}"
EVAL_CONDITION="${EVAL_CONDITION:-conflict_context}"
EVAL_COT_LENGTH="${EVAL_COT_LENGTH:-1024}"
MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS:-1200}"
MAX_VAL_ROWS="${MAX_VAL_ROWS:-200}"
MAX_EVAL_ROWS="${MAX_EVAL_ROWS:-500}"
MAX_LENGTH="${MAX_LENGTH:-1024}"
FEATURE_BATCH_SIZE="${FEATURE_BATCH_SIZE:-2}"
EPOCHS="${EPOCHS:-3}"
LR="${LR:-0.00005}"
HEAD_LR="${HEAD_LR:-0.0005}"
WEIGHT_DECAY="${WEIGHT_DECAY:-0.0001}"
LORA_RANK="${LORA_RANK:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"
LORA_DROPOUT="${LORA_DROPOUT:-0.05}"
SEED="${SEED:-42}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
WALL="${WALL:-20:00:00}"
GPUS="${GPUS:-4}"
CPUS="${CPUS:-32}"
JOB_NAME="${JOB_NAME:-t3_rlcr14}"

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

shell_quote() {
  printf "%q" "$1"
}

cmd=$(
  cat <<EOF
cd $(shell_quote "${DELTA_PROJECT_ROOT}") && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
export DELTA_PROJECT_ROOT=$(shell_quote "${DELTA_PROJECT_ROOT}") && \
export DELTA_VENV=$(shell_quote "${DELTA_VENV}") && \
export DELTA_RESULTS_ROOT=$(shell_quote "/work/nvme/bgvi/${DELTA_USER}/tts_results") && \
export ROWS_JSONL=$(shell_quote "${ROWS_JSONL}") && \
export OUTPUT_DIR=$(shell_quote "${OUTPUT_DIR}") && \
export MODEL_NAME=$(shell_quote "${MODEL_NAME}") && \
export TRAIN_BENCHMARK=$(shell_quote "${TRAIN_BENCHMARK}") && \
export TRAIN_CONDITION=$(shell_quote "${TRAIN_CONDITION}") && \
export EVAL_BENCHMARK=$(shell_quote "${EVAL_BENCHMARK}") && \
export EVAL_CONDITION=$(shell_quote "${EVAL_CONDITION}") && \
export EVAL_COT_LENGTH=$(shell_quote "${EVAL_COT_LENGTH}") && \
export MAX_TRAIN_ROWS=$(shell_quote "${MAX_TRAIN_ROWS}") && \
export MAX_VAL_ROWS=$(shell_quote "${MAX_VAL_ROWS}") && \
export MAX_EVAL_ROWS=$(shell_quote "${MAX_EVAL_ROWS}") && \
export MAX_LENGTH=$(shell_quote "${MAX_LENGTH}") && \
export FEATURE_BATCH_SIZE=$(shell_quote "${FEATURE_BATCH_SIZE}") && \
export EPOCHS=$(shell_quote "${EPOCHS}") && \
export LR=$(shell_quote "${LR}") && \
export HEAD_LR=$(shell_quote "${HEAD_LR}") && \
export WEIGHT_DECAY=$(shell_quote "${WEIGHT_DECAY}") && \
export LORA_RANK=$(shell_quote "${LORA_RANK}") && \
export LORA_ALPHA=$(shell_quote "${LORA_ALPHA}") && \
export LORA_DROPOUT=$(shell_quote "${LORA_DROPOUT}") && \
export SEED=$(shell_quote "${SEED}") && \
export TORCH_DTYPE=$(shell_quote "${TORCH_DTYPE}") && \
sbatch --parsable --account=$(shell_quote "${GPU_ACCOUNT}") --partition=$(shell_quote "${GPU_PARTITION}") --qos=$(shell_quote "${GPU_QOS}") \
  --gpus-per-node=$(shell_quote "${GPUS}") --cpus-per-task=$(shell_quote "${CPUS}") --time=$(shell_quote "${WALL}") --job-name=$(shell_quote "${JOB_NAME}") \
  --export=ALL slurm/delta/theorem3_rlcr_style_lora_delta.sbatch
EOF
)

submit_remote "${cmd}"
