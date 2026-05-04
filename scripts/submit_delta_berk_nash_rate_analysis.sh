#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"
ROWS_JSONL="${ROWS_JSONL:-/work/nvme/bgvi/${DELTA_USER}/tts_results/results/theorem3_r1_14b_tail_trajectory_v1/theorem3_generation_rows.jsonl}"
MODEL_FILTER="${MODEL_FILTER:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}"
TAIL_WINDOW="${TAIL_WINDOW:-100}"
JSON_OUT="${JSON_OUT:-docs/generated/berk_nash_rate_empirical.json}"
MD_OUT="${MD_OUT:-docs/generated/berk_nash_rate_empirical.md}"
JOB_NAME="${JOB_NAME:-bn14b_ana}"
WALLTIME="${WALLTIME:-01:00:00}"
CPUS="${CPUS:-4}"
MEM="${MEM:-24G}"
GPUS="${GPUS:-1}"

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
  ${AFTEROK_DEPENDENCY:+--dependency="afterok:${AFTEROK_DEPENDENCY}"} \
  --gpus-per-node="${GPUS}" \
  --cpus-per-task="${CPUS}" \
  --mem="${MEM}" \
  --time="${WALLTIME}" \
  --job-name="${JOB_NAME}" \
  --output="logs/${JOB_NAME}.%j.out" \
  --wrap='cd ${DELTA_PROJECT_ROOT} && mkdir -p docs/generated logs && PYTHONPATH=src ${DELTA_VENV}/bin/python scripts/build_berk_nash_rate_empirical.py --rows-jsonl "${ROWS_JSONL}" --model "${MODEL_FILTER}" --tail-window "${TAIL_WINDOW}" --json-out "${JSON_OUT}" --md-out "${MD_OUT}"'
EOF
)

if hostname 2>/dev/null | grep -q "gh-login\\|dtai-login\\|gh0"; then
  bash -lc "$SBATCH_CMD"
else
  delta_ssh_base "$SBATCH_CMD"
fi
