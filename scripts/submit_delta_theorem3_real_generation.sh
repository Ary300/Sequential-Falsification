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
BENCHMARKS="${BENCHMARKS:-wikicontradict,conflictbank}"
CONDITIONS="${CONDITIONS:-aligned_context,conflict_context}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-600}"
TEMPERATURE="${TEMPERATURE:-0.0}"
TOP_P="${TOP_P:-1.0}"
SEED="${SEED:-42}"
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-200}"
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-500}"
TRIVIAQA_MAX="${TRIVIAQA_MAX:-200}"
COT_LENGTHS="${COT_LENGTHS:-0,128,1024}"
BENCHMARK_MAXIMA="${BENCHMARK_MAXIMA:-}"
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
export MODEL=$(shell_quote "${MODEL}") && \
export BACKEND=$(shell_quote "${BACKEND}") && \
export BENCHMARKS=$(shell_quote "${BENCHMARKS}") && \
export CONDITIONS=$(shell_quote "${CONDITIONS}") && \
export REQUEST_TIMEOUT=$(shell_quote "${REQUEST_TIMEOUT}") && \
export TEMPERATURE=$(shell_quote "${TEMPERATURE}") && \
export TOP_P=$(shell_quote "${TOP_P}") && \
export SEED=$(shell_quote "${SEED}") && \
export WIKICONTRADICT_MAX=$(shell_quote "${WIKICONTRADICT_MAX}") && \
export CONFLICTBANK_MAX=$(shell_quote "${CONFLICTBANK_MAX}") && \
export TRIVIAQA_MAX=$(shell_quote "${TRIVIAQA_MAX}") && \
export COT_LENGTHS=$(shell_quote "${COT_LENGTHS}") && \
export BENCHMARK_MAXIMA=$(shell_quote "${BENCHMARK_MAXIMA}") && \
export CONFLICTBANK_SCREENING_POOL=$(shell_quote "${CONFLICTBANK_SCREENING_POOL}") && \
export AMBIGUITY_LOW=$(shell_quote "${AMBIGUITY_LOW}") && \
export AMBIGUITY_HIGH=$(shell_quote "${AMBIGUITY_HIGH}") && \
export TP_SIZE=$(shell_quote "${TP_SIZE}") && \
export MAX_MODEL_LEN=$(shell_quote "${MAX_MODEL_LEN}") && \
sbatch --parsable --account=$(shell_quote "${GPU_ACCOUNT}") --partition=$(shell_quote "${GPU_PARTITION}") --qos=$(shell_quote "${GPU_QOS}") \
  --gpus-per-node=$(shell_quote "${GPUS}") --cpus-per-task=$(shell_quote "${CPUS}") --time=$(shell_quote "${WALL}") --job-name=$(shell_quote "${JOB_NAME}") \
  --export=ALL slurm/delta/theorem3_real_generation_delta.sbatch
EOF
)

submit_remote "${cmd}"
