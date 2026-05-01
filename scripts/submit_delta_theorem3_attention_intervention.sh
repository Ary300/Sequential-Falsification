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

OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_attention_intervention_r1_14b_conflict}"
DELTA_RESULTS_ROOT="${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/${DELTA_USER}/tts_results}"
ROWS_JSONL="${ROWS_JSONL:-/work/nvme/bgvi/${DELTA_USER}/tts_results/results/theorem3_tierA_r1_qwen14_seed42/theorem3_generation_rows.jsonl}"
MODEL_NAME="${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}"
BENCHMARK="${BENCHMARK:-conflictbank}"
CONDITION="${CONDITION:-conflict_context}"
COT_LENGTHS="${COT_LENGTHS:-0,128,1024}"
MAX_ROWS_PER_COT="${MAX_ROWS_PER_COT:-100}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-96}"
MAX_LENGTH="${MAX_LENGTH:-4096}"
SEED="${SEED:-42}"
WALL="${WALL:-12:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-t3_attnint}"

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
export DELTA_RESULTS_ROOT=$(shell_quote "${DELTA_RESULTS_ROOT}") && \
export OUTPUT_DIR=$(shell_quote "${OUTPUT_DIR}") && \
export ROWS_JSONL=$(shell_quote "${ROWS_JSONL}") && \
export MODEL_NAME=$(shell_quote "${MODEL_NAME}") && \
export BENCHMARK=$(shell_quote "${BENCHMARK}") && \
export CONDITION=$(shell_quote "${CONDITION}") && \
export COT_LENGTHS=$(shell_quote "${COT_LENGTHS}") && \
export MAX_ROWS_PER_COT=$(shell_quote "${MAX_ROWS_PER_COT}") && \
export MAX_NEW_TOKENS=$(shell_quote "${MAX_NEW_TOKENS}") && \
export MAX_LENGTH=$(shell_quote "${MAX_LENGTH}") && \
export SEED=$(shell_quote "${SEED}") && \
sbatch --parsable --account=$(shell_quote "${GPU_ACCOUNT}") --partition=$(shell_quote "${GPU_PARTITION}") --qos=$(shell_quote "${GPU_QOS}") \
  --gpus-per-node=$(shell_quote "${GPUS}") --cpus-per-task=$(shell_quote "${CPUS}") --time=$(shell_quote "${WALL}") --job-name=$(shell_quote "${JOB_NAME}") \
  --export=ALL slurm/delta/theorem3_attention_intervention_delta.sbatch
EOF
)

submit_remote "${cmd}"
