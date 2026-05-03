#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}"
DATASETS="${DATASETS:-triviaqa_open,nq_open,asqa}"
MAX_EXAMPLES="${MAX_EXAMPLES:-32}"
SEARCH_LIMIT="${SEARCH_LIMIT:-6}"
TOP_K_CONTEXTS="${TOP_K_CONTEXTS:-3}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-96}"
BATCH_SIZE="${BATCH_SIZE:-4}"
TORCH_DTYPE="${TORCH_DTYPE:-bfloat16}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-docs/generated/paper2_freeform_eval}"
WALLTIME="${WALLTIME:-10:00:00}"
CPUS="${CPUS:-8}"
MEM="${MEM:-80G}"
GPUS="${GPUS:-1}"
JOB_NAME="${JOB_NAME:-p2free}"

REMOTE_CMD=$(
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
  --wrap='cd ${DELTA_PROJECT_ROOT} && mkdir -p logs docs/generated && export HF_TOKEN="${HF_TOKEN:-}" HUGGING_FACE_HUB_TOKEN="${HF_TOKEN:-}" && PYTHONPATH=src ${DELTA_VENV}/bin/python scripts/run_paper2_freeform_eval.py --model "${MODEL}" --datasets "${DATASETS}" --max-examples "${MAX_EXAMPLES}" --search-limit "${SEARCH_LIMIT}" --top-k-contexts "${TOP_K_CONTEXTS}" --max-new-tokens "${MAX_NEW_TOKENS}" --batch-size "${BATCH_SIZE}" --torch-dtype "${TORCH_DTYPE}" --output-prefix "${OUTPUT_PREFIX}"'
EOF
)

delta_ssh_base "$REMOTE_CMD"
