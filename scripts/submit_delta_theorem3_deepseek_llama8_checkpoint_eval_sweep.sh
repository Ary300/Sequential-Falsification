#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <result_dir> [job_prefix]" >&2
  exit 1
fi

RESULT_DIR="$1"
JOB_PREFIX="${2:-r1l8ck}"

if [[ ! -d "${RESULT_DIR}" ]]; then
  echo "Result directory not found: ${RESULT_DIR}" >&2
  exit 1
fi

CHECKPOINT_ROOT="${RESULT_DIR%/}/intermediate_checkpoints"
if [[ ! -d "${CHECKPOINT_ROOT}" ]]; then
  echo "No intermediate checkpoints found under: ${CHECKPOINT_ROOT}"
  exit 0
fi

shopt -s nullglob
checkpoint_dirs=("${CHECKPOINT_ROOT}"/*)
shopt -u nullglob

if [[ ${#checkpoint_dirs[@]} -eq 0 ]]; then
  echo "Checkpoint directory is empty: ${CHECKPOINT_ROOT}"
  exit 0
fi

submitted=0
for checkpoint_dir in "${checkpoint_dirs[@]}"; do
  [[ -d "${checkpoint_dir}" ]] || continue
  checkpoint_name="$(basename "${checkpoint_dir}")"
  output_dir="${RESULT_DIR%/}/theorem3_checkpoint_eval_deepseek_native/${checkpoint_name}"
  if [[ -f "${output_dir}/theorem3_summary.json" ]]; then
    echo "Skipping ${checkpoint_name}: theorem-3 checkpoint eval already complete"
    continue
  fi
  job_name="${JOB_PREFIX}_$(echo "${checkpoint_name}" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9_' '_')"
  bash "${SCRIPT_DIR}/submit_delta_theorem3_deepseek_llama8_checkpoint_eval.sh" \
    "${checkpoint_dir}" \
    "${output_dir}" \
    "${job_name}"
  submitted=$((submitted + 1))
done

if [[ "${submitted}" -eq 0 ]]; then
  echo "No new checkpoint eval jobs needed for ${CHECKPOINT_ROOT}"
  exit 0
fi

echo "Submitted ${submitted} checkpoint eval jobs from ${CHECKPOINT_ROOT}"
