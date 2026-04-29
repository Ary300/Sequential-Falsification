#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/delta_env.sh"

CONFIG_PATH="${CONFIG_PATH:-src/configs/knowledge_arbitration_spotlight_extended.yaml}"
OUTPUT_ROOT="${OUTPUT_ROOT:-results/delta_knowledge_arbitration_extended_wave}"
GPU_ACCOUNT="${GPU_ACCOUNT:-$DELTA_ACCOUNT}"
GPU_PARTITION="${GPU_PARTITION:-$DELTA_PARTITION}"
GPU_QOS="${GPU_QOS:-$DELTA_QOS}"
REMOTE_PYTHON_BIN="${REMOTE_PYTHON_BIN:-}"
LOCAL_PYTHON_BIN="${LOCAL_PYTHON_BIN:-python3}"
SYNC_FIRST=0
DRY_RUN=0

declare -a EXPERIMENT_NAMES=()
declare -a EXPERIMENT_PREFIXES=()

host_name="$(hostname 2>/dev/null || true)"
DELTA_LOCAL_MODE=0
if [[ "${host_name}" == gh-login* || "${host_name}" == dtai-login* || "${PWD}" == /u/${DELTA_USER}/* ]]; then
  DELTA_LOCAL_MODE=1
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="$2"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="$2"
      shift 2
      ;;
    --experiment-name)
      EXPERIMENT_NAMES+=("$2")
      shift 2
      ;;
    --experiment-prefix)
      EXPERIMENT_PREFIXES+=("$2")
      shift 2
      ;;
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

if [[ ${#EXPERIMENT_NAMES[@]} -eq 0 && ${#EXPERIMENT_PREFIXES[@]} -eq 0 ]]; then
  EXPERIMENT_PREFIXES=(
    arbitration_spotlight_extended_model_wave
    arbitration_spotlight_extended_t3_calibration_wave
    arbitration_spotlight_extended_api_slice
  )
fi

if [[ "${SYNC_FIRST}" -eq 1 && "${DELTA_LOCAL_MODE}" -eq 0 ]]; then
  rsync -az \
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

if [[ -z "${REMOTE_PYTHON_BIN}" ]]; then
  REMOTE_PYTHON_BIN='$(if [[ -x .venv-lm-deltaai/bin/python ]]; then echo .venv-lm-deltaai/bin/python; elif [[ -x "'"${DELTA_VENV}"'/bin/python" ]]; then echo "'"${DELTA_VENV}"'/bin/python"; else echo python3; fi)'
fi

MANIFEST="$(
  cd "${ROOT_DIR}" && "${LOCAL_PYTHON_BIN}" - "${CONFIG_PATH}" "${EXPERIMENT_NAMES[*]-}" "${EXPERIMENT_PREFIXES[*]-}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root / "src"))

from experiment_registry import filter_experiments, load_expanded_experiments

config_path = root / sys.argv[1]
names = [item for item in sys.argv[2].split() if item]
prefixes = [item for item in sys.argv[3].split() if item]
experiments = filter_experiments(load_expanded_experiments(config_path), names=names, prefixes=prefixes)
for experiment in experiments:
    print(json.dumps({
        "name": experiment["name"],
        "expanded_from": experiment.get("expanded_from", experiment["name"]),
    }))
PY
)"

if [[ -z "${MANIFEST}" ]]; then
  echo "No experiments matched the requested selection." >&2
  exit 1
fi

gpu_qos_arg=()
if [[ -n "${GPU_QOS}" ]]; then
  gpu_qos_arg+=(--qos="${GPU_QOS}")
fi

submit_remote() {
  local cmd="$1"
  if [[ "${DRY_RUN}" -eq 1 ]]; then
    echo "DRYRUN ${cmd}" >&2
    echo "dryrun_${RANDOM}_${RANDOM}"
  elif [[ "${DELTA_LOCAL_MODE}" -eq 1 ]]; then
    bash -lc "${cmd}"
  else
    delta_ssh_base "$cmd"
  fi
}

resource_profile() {
  local experiment_name="$1"
  if [[ "${experiment_name}" == arbitration_spotlight_extended_model_wave* ]]; then
    printf '%s\t%s\t%s\t%s\n' "08:00:00" "1" "8" "32G"
  elif [[ "${experiment_name}" == arbitration_spotlight_extended_t3_calibration_wave* ]]; then
    printf '%s\t%s\t%s\t%s\n' "06:00:00" "1" "8" "24G"
  else
    printf '%s\t%s\t%s\t%s\n' "03:00:00" "1" "4" "16G"
  fi
}

mkdir -p "${ROOT_DIR}/docs/generated"
submission_jsonl="${ROOT_DIR}/docs/generated/delta_extended_wave_submissions.jsonl"
touch "${submission_jsonl}"

while IFS= read -r row; do
  [[ -z "${row}" ]] && continue
  parsed="$("${LOCAL_PYTHON_BIN}" - "$row" <<'PY'
from __future__ import annotations

import json
import sys

row = json.loads(sys.argv[1])
print(f"{row['name']}\t{row['expanded_from']}")
PY
)"
  IFS=$'\t' read -r experiment_name expanded_from <<< "${parsed}"
  read -r wall gpus cpus mem <<< "$(resource_profile "${experiment_name}")"
  remote_output_dir="${DELTA_PROJECT_ROOT}/${OUTPUT_ROOT}/${experiment_name}"
  remote_logs_dir="${DELTA_PROJECT_ROOT}/logs/knowledge_arbitration_extended_wave"
  wrap_cmd="cd ${DELTA_PROJECT_ROOT} && mkdir -p ${remote_output_dir} ${remote_logs_dir} && PYTHONPATH=src ${REMOTE_PYTHON_BIN} scripts/run_expanded_arbitration_benchmarks.py --config ${CONFIG_PATH} --output-dir ${OUTPUT_ROOT} --experiment-name ${experiment_name}"
  sbatch_cmd="sbatch --parsable --account=\"${GPU_ACCOUNT}\" --partition=\"${GPU_PARTITION}\" ${gpu_qos_arg[*]-} --gpus-per-node=\"${gpus}\" --job-name=\"karb_${experiment_name:0:40}\" --output=\"${remote_logs_dir}/${experiment_name}.%j.out\" --time=\"${wall}\" --cpus-per-task=\"${cpus}\" --mem=\"${mem}\" --wrap='${wrap_cmd}'"
  job_id="$(submit_remote "${sbatch_cmd}")"
  printf '{"experiment_name":"%s","expanded_from":"%s","job_id":"%s","wall":"%s","gpus":"%s","cpus":"%s","mem":"%s"}\n' \
    "${experiment_name}" "${expanded_from}" "${job_id}" "${wall}" "${gpus}" "${cpus}" "${mem}" >> "${submission_jsonl}"
  echo "Submitted ${experiment_name} as ${job_id}"
done <<< "${MANIFEST}"

echo "Wrote submission manifest to ${submission_jsonl}"
