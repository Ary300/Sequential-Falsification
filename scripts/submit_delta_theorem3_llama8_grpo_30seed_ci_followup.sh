#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

DELTA_USER=${DELTA_USER:-adas17}
PROJECT_ROOT="${DELTA_PROJECT_ROOT:-/u/${DELTA_USER}/tts-falsification-git}"
RESULTS_ROOT="${U_RESULTS_ROOT:-/u/${DELTA_USER}/tts_results_staging}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-docs/generated/llama8_grpo_30seed_theorem3_ci}"
SEED_START="${SEED_START:-42}"
SEED_END="${SEED_END:-71}"
JOB_NAME="${JOB_NAME:-l8g_ci}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <seed_job_id> [<seed_job_id> ...]" >&2
  exit 1
fi

deps=$(IFS=:; echo "$*")

cmd=$(
  cat <<EOF
cd ${PROJECT_ROOT} && \
source /u/${DELTA_USER}/venvs/tts-delta/bin/activate && \
python3 scripts/build_theorem3_multiseed_ci.py \
  --glob '${RESULTS_ROOT}/results/e1_llama8b_grpo_s*/theorem3_eval/theorem3_report/theorem3_summary.json' \
  --label 'Llama-8B GRPO 30-seed theorem-3' \
  --output-prefix '${OUTPUT_PREFIX}'
EOF
)

if [[ "$(hostname 2>/dev/null || true)" == gh-login* || "$(pwd)" == /u/${DELTA_USER}/* ]]; then
  sbatch --parsable \
    --account="${DELTA_ACCOUNT}" \
    --partition="${DELTA_PARTITION}" \
    --qos="${DELTA_QOS}" \
    --gpus-per-node=1 \
    --cpus-per-task=2 \
    --mem=8G \
    --time=00:30:00 \
    --job-name="${JOB_NAME}" \
    --dependency="afterany:${deps}" \
    --output="${PROJECT_ROOT}/logs/${JOB_NAME}.%j.out" \
    --wrap "${cmd}"
else
  ssh ${DELTA_SSH_KEY:+-i "${DELTA_SSH_KEY}"} ${DELTA_SSH_OPTS} "${DELTA_LOGIN}" \
    "sbatch --parsable --account='${DELTA_ACCOUNT}' --partition='${DELTA_PARTITION}' --qos='${DELTA_QOS}' --gpus-per-node=1 --cpus-per-task=2 --mem=8G --time=00:30:00 --job-name='${JOB_NAME}' --dependency='afterany:${deps}' --output='${PROJECT_ROOT}/logs/${JOB_NAME}.%j.out' --wrap $(printf '%q' "${cmd}")"
fi
