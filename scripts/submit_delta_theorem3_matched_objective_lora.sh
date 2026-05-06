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

OBJECTIVE="${OBJECTIVE:-dpo}"
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_matched_objective_qwen14_dpo}"
DELTA_RESULTS_ROOT="${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/${DELTA_USER}/tts_results}"
MODEL_NAME="${MODEL_NAME:-Qwen/Qwen2.5-14B}"
BENCHMARK="${BENCHMARK:-conflictbank}"
MAX_SOURCE_ROWS="${MAX_SOURCE_ROWS:-1200}"
MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS:-800}"
MAX_VAL_ROWS="${MAX_VAL_ROWS:-120}"
MAX_EVAL_ROWS="${MAX_EVAL_ROWS:-120}"
MAX_PROMPT_LENGTH="${MAX_PROMPT_LENGTH:-768}"
MAX_ANSWER_LENGTH="${MAX_ANSWER_LENGTH:-24}"
EPOCHS="${EPOCHS:-1}"
WARMSTART_EPOCHS="${WARMSTART_EPOCHS:-1}"
LR="${LR:-0.00005}"
WEIGHT_DECAY="${WEIGHT_DECAY:-0.0001}"
BETA="${BETA:-0.1}"
GROUP_SIZE="${GROUP_SIZE:-4}"
TEMPERATURE="${TEMPERATURE:-0.8}"
TOP_P="${TOP_P:-0.95}"
LORA_RANK="${LORA_RANK:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"
LORA_DROPOUT="${LORA_DROPOUT:-0.05}"
SEED="${SEED:-42}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
HF_HOME="${HF_HOME:-}"
XDG_CACHE_HOME="${XDG_CACHE_HOME:-}"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-}"
SAVE_INTERMEDIATE_CHECKPOINTS="${SAVE_INTERMEDIATE_CHECKPOINTS:-0}"
RUN_THEOREM3_EVAL="${RUN_THEOREM3_EVAL:-1}"
EVAL_OUTPUT_DIR="${EVAL_OUTPUT_DIR:-}"
EVAL_BENCHMARKS="${EVAL_BENCHMARKS:-wikicontradict,conflictbank}"
EVAL_CONDITIONS="${EVAL_CONDITIONS:-aligned_context,conflict_context}"
EVAL_COT_LENGTHS="${EVAL_COT_LENGTHS:-0,128,1024}"
EVAL_WIKICONTRADICT_MAX="${EVAL_WIKICONTRADICT_MAX:-96}"
EVAL_CONFLICTBANK_MAX="${EVAL_CONFLICTBANK_MAX:-128}"
EVAL_TRIVIAQA_MAX="${EVAL_TRIVIAQA_MAX:-0}"
EVAL_REQUEST_FORMAT="${EVAL_REQUEST_FORMAT:-chat}"
EVAL_PROMPT_PROTOCOL="${EVAL_PROMPT_PROTOCOL:-generic}"
WALL="${WALL:-18:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"
JOB_NAME="${JOB_NAME:-t3_matchobj}"

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
export OBJECTIVE=$(shell_quote "${OBJECTIVE}") && \
export OUTPUT_DIR=$(shell_quote "${OUTPUT_DIR}") && \
export MODEL_NAME=$(shell_quote "${MODEL_NAME}") && \
export BENCHMARK=$(shell_quote "${BENCHMARK}") && \
export MAX_SOURCE_ROWS=$(shell_quote "${MAX_SOURCE_ROWS}") && \
export MAX_TRAIN_ROWS=$(shell_quote "${MAX_TRAIN_ROWS}") && \
export MAX_VAL_ROWS=$(shell_quote "${MAX_VAL_ROWS}") && \
export MAX_EVAL_ROWS=$(shell_quote "${MAX_EVAL_ROWS}") && \
export MAX_PROMPT_LENGTH=$(shell_quote "${MAX_PROMPT_LENGTH}") && \
export MAX_ANSWER_LENGTH=$(shell_quote "${MAX_ANSWER_LENGTH}") && \
export EPOCHS=$(shell_quote "${EPOCHS}") && \
export WARMSTART_EPOCHS=$(shell_quote "${WARMSTART_EPOCHS}") && \
export LR=$(shell_quote "${LR}") && \
export WEIGHT_DECAY=$(shell_quote "${WEIGHT_DECAY}") && \
export BETA=$(shell_quote "${BETA}") && \
export GROUP_SIZE=$(shell_quote "${GROUP_SIZE}") && \
export TEMPERATURE=$(shell_quote "${TEMPERATURE}") && \
export TOP_P=$(shell_quote "${TOP_P}") && \
export LORA_RANK=$(shell_quote "${LORA_RANK}") && \
export LORA_ALPHA=$(shell_quote "${LORA_ALPHA}") && \
export LORA_DROPOUT=$(shell_quote "${LORA_DROPOUT}") && \
export SEED=$(shell_quote "${SEED}") && \
export TORCH_DTYPE=$(shell_quote "${TORCH_DTYPE}") && \
export HF_HOME=$(shell_quote "${HF_HOME}") && \
export XDG_CACHE_HOME=$(shell_quote "${XDG_CACHE_HOME}") && \
export XDG_CONFIG_HOME=$(shell_quote "${XDG_CONFIG_HOME}") && \
export SAVE_INTERMEDIATE_CHECKPOINTS=$(shell_quote "${SAVE_INTERMEDIATE_CHECKPOINTS}") && \
export RUN_THEOREM3_EVAL=$(shell_quote "${RUN_THEOREM3_EVAL}") && \
export EVAL_OUTPUT_DIR=$(shell_quote "${EVAL_OUTPUT_DIR}") && \
export EVAL_BENCHMARKS=$(shell_quote "${EVAL_BENCHMARKS}") && \
export EVAL_CONDITIONS=$(shell_quote "${EVAL_CONDITIONS}") && \
export EVAL_COT_LENGTHS=$(shell_quote "${EVAL_COT_LENGTHS}") && \
export EVAL_WIKICONTRADICT_MAX=$(shell_quote "${EVAL_WIKICONTRADICT_MAX}") && \
export EVAL_CONFLICTBANK_MAX=$(shell_quote "${EVAL_CONFLICTBANK_MAX}") && \
export EVAL_TRIVIAQA_MAX=$(shell_quote "${EVAL_TRIVIAQA_MAX}") && \
export EVAL_REQUEST_FORMAT=$(shell_quote "${EVAL_REQUEST_FORMAT}") && \
export EVAL_PROMPT_PROTOCOL=$(shell_quote "${EVAL_PROMPT_PROTOCOL}") && \
sbatch --parsable --account=$(shell_quote "${GPU_ACCOUNT}") --partition=$(shell_quote "${GPU_PARTITION}") --qos=$(shell_quote "${GPU_QOS}") \
  --gpus-per-node=$(shell_quote "${GPUS}") --cpus-per-task=$(shell_quote "${CPUS}") --time=$(shell_quote "${WALL}") --job-name=$(shell_quote "${JOB_NAME}") \
  --export=ALL slurm/delta/theorem3_matched_objective_lora_delta.sbatch
EOF
)

submit_remote "${cmd}"
