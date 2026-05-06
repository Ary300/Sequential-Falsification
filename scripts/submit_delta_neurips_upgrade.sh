#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SYNC_FIRST=0
DRY_RUN=0

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

declare -a passthrough=()
if [[ "${SYNC_FIRST}" -eq 1 ]]; then
  passthrough+=(--sync-first)
fi
if [[ "${DRY_RUN}" -eq 1 ]]; then
  passthrough+=(--dry-run)
fi

echo "Submitting stronger Delta reruns for the weakest reviewer-facing rows..."

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=paperproxystrong \
  JOB_PREFIX=strong_ \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  TEMPERATURE=0.7 \
  ENABLE_7B=1 \
  ENABLE_14B=1 \
  ENABLE_32B=1 \
  RUN_HUMANEVAL=1 \
  RUN_MBPP=1 \
  RUN_LIVECODEBENCH=0 \
  RUN_MATH500=0 \
  DELTA_7B_WALL=24:00:00 \
  DELTA_14B_WALL=24:00:00 \
  DELTA_32B_WALL=36:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_proxy_matrix.sh "${passthrough[@]}"
)

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=reviewerstrong \
  JOB_PREFIX=strong_ \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  TEMPERATURE=0.7 \
  ENABLE_7B=1 \
  ENABLE_14B=1 \
  ENABLE_32B=0 \
  RUN_MBPP=1 \
  RUN_HUMANEVAL=0 \
  DELTA_7B_WALL=20:00:00 \
  DELTA_14B_WALL=20:00:00 \
  bash scripts/submit_delta_generated_filter_matrix.sh "${passthrough[@]}"
)

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=reviewerstrong \
  JOB_PREFIX=strong_ \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  TEMPERATURE=0.7 \
  ENABLE_7B=1 \
  ENABLE_14B=0 \
  ENABLE_32B=1 \
  RUN_MBPP=0 \
  RUN_HUMANEVAL=1 \
  DELTA_7B_WALL=20:00:00 \
  DELTA_32B_WALL=36:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_generated_filter_matrix.sh "${passthrough[@]}"
)

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=paperplusstrong \
  JOB_PREFIX=strong_ \
  N_CANDIDATES=12 \
  N_ROUNDS=3 \
  TEMPERATURE=0.7 \
  ENABLE_7B=0 \
  ENABLE_14B=1 \
  ENABLE_32B=1 \
  RUN_HUMANEVAL=0 \
  RUN_MBPP=0 \
  RUN_LIVECODEBENCH=1 \
  RUN_MATH500=1 \
  DELTA_14B_WALL=24:00:00 \
  DELTA_32B_WALL=36:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_paper_matrix.sh "${passthrough[@]}"
)
