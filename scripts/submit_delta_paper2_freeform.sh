#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

PAPER2_MODEL="${PAPER2_MODEL:-/work/nvme/bgvi/adas17/hf_cache/hub/models--deepseek-ai--DeepSeek-R1-Distill-Llama-8B/snapshots/6a6f4aa4197940add57724a7707d069478df56b1}"
DATASETS="${DATASETS:-triviaqa_open,nq_open,asqa}"
MAX_EXAMPLES="${MAX_EXAMPLES:-32}"
SEARCH_LIMIT="${SEARCH_LIMIT:-6}"
TOP_K_CONTEXTS="${TOP_K_CONTEXTS:-3}"
INDIVIDUAL_CONTEXT_CANDIDATES="${INDIVIDUAL_CONTEXT_CANDIDATES:-0}"
DECODE_MODE="${DECODE_MODE:-candidate_rescore}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-96}"
BATCH_SIZE="${BATCH_SIZE:-4}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-docs/generated/paper2_freeform_eval}"
RETRIEVAL_CACHE_FILE="${RETRIEVAL_CACHE_FILE:-docs/generated/paper2_freeform_retrieval_cache.json}"
HF_DATASETS_ROOT="${HF_DATASETS_ROOT:-/work/hdd/bgvi/adas17/paper2_hf_home}"
WALLTIME="${WALLTIME:-10:00:00}"
CPUS="${CPUS:-8}"
MEM="${MEM:-80G}"
GPUS="${GPUS:-1}"
JOB_NAME="${JOB_NAME:-p2free}"

SBATCH_CMD=$(
  cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
export SBATCH_ACCOUNT=${DELTA_ACCOUNT} && \
export SBATCH_PARTITION=${DELTA_PARTITION} && \
export SBATCH_QOS=${DELTA_QOS} && \
sbatch --parsable \
  --account="\$SBATCH_ACCOUNT" \
  --partition="\$SBATCH_PARTITION" \
  --qos="\$SBATCH_QOS" \
  --gpus-per-node="${GPUS}" \
  --cpus-per-task="${CPUS}" \
  --mem="${MEM}" \
  --time="${WALLTIME}" \
  --job-name="${JOB_NAME}" \
  --output="logs/${JOB_NAME}.%j.out" \
  --wrap='cd ${DELTA_PROJECT_ROOT} && mkdir -p logs docs/generated "${HF_DATASETS_ROOT}/datasets" "${HF_DATASETS_ROOT}/hub" && export HF_TOKEN="${HF_TOKEN:-}" HUGGING_FACE_HUB_TOKEN="${HF_TOKEN:-}" HF_HOME="${HF_DATASETS_ROOT}" HF_DATASETS_CACHE="${HF_DATASETS_ROOT}/datasets" HUGGINGFACE_HUB_CACHE="${HF_DATASETS_ROOT}/hub" && PYTHONPATH=src ${DELTA_VENV}/bin/python scripts/run_paper2_freeform_eval.py --model "${PAPER2_MODEL}" --datasets "${DATASETS}" --max-examples "${MAX_EXAMPLES}" --search-limit "${SEARCH_LIMIT}" --top-k-contexts "${TOP_K_CONTEXTS}" --individual-context-candidates "${INDIVIDUAL_CONTEXT_CANDIDATES}" --decode-mode "${DECODE_MODE}" --max-new-tokens "${MAX_NEW_TOKENS}" --batch-size "${BATCH_SIZE}" --torch-dtype "${TORCH_DTYPE}" --cache-file "${RETRIEVAL_CACHE_FILE}" --output-prefix "${OUTPUT_PREFIX}"'
EOF
)

if hostname 2>/dev/null | grep -q "gh-login\\|dtai-login\\|gh0"; then
  bash -lc "$SBATCH_CMD"
else
  delta_ssh_base "$SBATCH_CMD"
fi
