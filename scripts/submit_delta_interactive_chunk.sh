#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

ACCOUNT="${ACCOUNT:-$DELTA_ACCOUNT}"
PARTITION="${PARTITION:-ghx4-interactive}"
WALL="${WALL:-02:00:00}"
GPUS="${GPUS:-1}"
CPUS="${CPUS:-16}"

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}"
BENCHMARKS="${BENCHMARKS:-humaneval_plus}"
METHODS="${METHODS:-greedy:majority_vote:self_debug:falsification:oracle}"
OUTPUT_DIR="${OUTPUT_DIR:-results/delta_interactive_chunk}"
SEEDS="${SEEDS:-42}"
MAX_PROBLEMS="${MAX_PROBLEMS:-164}"
N_CANDIDATES="${N_CANDIDATES:-8}"
N_ROUNDS="${N_ROUNDS:-2}"
MAX_TIEBREAK_ROUNDS="${MAX_TIEBREAK_ROUNDS:-4}"
TEMPERATURE="${TEMPERATURE:-0.7}"
MAX_TOKENS="${MAX_TOKENS:-512}"
TP_SIZE="${TP_SIZE:-1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
BACKEND="${BACKEND:-openai}"
PROBE_STRATEGY="${PROBE_STRATEGY:-adaptive_population}"
ADAPTIVE_PROBE_SELECTION="${ADAPTIVE_PROBE_SELECTION:-true}"
ENFORCE_ROUND_FAMILY_DIVERSITY="${ENFORCE_ROUND_FAMILY_DIVERSITY:-true}"
ELIMINATE_ON_DETECTION="${ELIMINATE_ON_DETECTION:-true}"
CONFIDENCE_MODE="${CONFIDENCE_MODE:-wealth}"
DATA_ROOT="${DATA_ROOT:-data}"
JOB_NAME="${JOB_NAME:-delta_chunk}"
AFTERANY_DEPENDENCY="${AFTERANY_DEPENDENCY:-}"
SYNC_FIRST=0
DRY_RUN=0
DELTA_LOCAL_MODE=0

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
    local fake_id="dryrun_${RANDOM}_${RANDOM}"
    echo "DRYRUN[${fake_id}] ${cmd}" >&2
    echo "${fake_id}"
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
sbatch --parsable --account="${ACCOUNT}" --partition="${PARTITION}" \
  ${AFTERANY_DEPENDENCY:+--dependency="afterany:${AFTERANY_DEPENDENCY}"} \
  --gpus-per-node="${GPUS}" --cpus-per-task="${CPUS}" --time="${WALL}" --job-name="${JOB_NAME}" \
  --export=ALL,DELTA_VENV=${DELTA_VENV},BACKEND=${BACKEND},MODEL=${MODEL},BENCHMARKS=${BENCHMARKS},METHODS=${METHODS},OUTPUT_DIR=${OUTPUT_DIR},SEEDS=${SEEDS},MAX_PROBLEMS=${MAX_PROBLEMS},N_CANDIDATES=${N_CANDIDATES},N_ROUNDS=${N_ROUNDS},MAX_TIEBREAK_ROUNDS=${MAX_TIEBREAK_ROUNDS},TEMPERATURE=${TEMPERATURE},MAX_TOKENS=${MAX_TOKENS},TP_SIZE=${TP_SIZE},MAX_MODEL_LEN=${MAX_MODEL_LEN},PROBE_STRATEGY=${PROBE_STRATEGY},ADAPTIVE_PROBE_SELECTION=${ADAPTIVE_PROBE_SELECTION},ENFORCE_ROUND_FAMILY_DIVERSITY=${ENFORCE_ROUND_FAMILY_DIVERSITY},ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION},CONFIDENCE_MODE=${CONFIDENCE_MODE},DATA_ROOT=${DATA_ROOT} \
  slurm/delta/full_experiment_delta.sbatch
EOF
)

job_id="$(submit_remote "${cmd}")"
echo "${JOB_NAME}=${job_id}"
if [[ "${DRY_RUN}" -eq 0 ]]; then
  submit_remote "squeue -j ${job_id} -O jobid,state,reason,name,timeused,timeleft"
fi
