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

echo "Submitting headline Delta reruns with stronger survivor tie-breaks..."

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=paperheadline \
  JOB_PREFIX=headline_ \
  N_CANDIDATES=64 \
  N_ROUNDS=4 \
  MAX_TIEBREAK_ROUNDS=8 \
  TEMPERATURE=0.8 \
  MAX_DIFFERENTIAL_PROBES=24 \
  CONSENSUS_MIN_FRACTION=0.70 \
  CONSENSUS_MIN_MARGIN=3 \
  CONSENSUS_MIN_VOTES=5 \
  ENABLE_7B=1 \
  ENABLE_14B=1 \
  ENABLE_32B=1 \
  RUN_HUMANEVAL=1 \
  RUN_MBPP=1 \
  RUN_LIVECODEBENCH=0 \
  RUN_MATH500=0 \
  DELTA_7B_WALL=24:00:00 \
  DELTA_14B_WALL=32:00:00 \
  DELTA_32B_WALL=48:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_paper_matrix.sh "${passthrough[@]}"
)

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=paperheadlineproxy \
  JOB_PREFIX=headline_ \
  N_CANDIDATES=64 \
  N_ROUNDS=4 \
  MAX_TIEBREAK_ROUNDS=8 \
  TEMPERATURE=0.8 \
  MAX_DIFFERENTIAL_PROBES=24 \
  CONSENSUS_MIN_FRACTION=0.70 \
  CONSENSUS_MIN_MARGIN=3 \
  CONSENSUS_MIN_VOTES=5 \
  ENABLE_7B=1 \
  ENABLE_14B=1 \
  ENABLE_32B=1 \
  RUN_HUMANEVAL=1 \
  RUN_MBPP=1 \
  RUN_LIVECODEBENCH=0 \
  RUN_MATH500=0 \
  DELTA_7B_WALL=24:00:00 \
  DELTA_14B_WALL=32:00:00 \
  DELTA_32B_WALL=48:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_proxy_matrix.sh "${passthrough[@]}"
)

(
  cd "${ROOT_DIR}"
  RESULT_PREFIX=paperheadlinegtf \
  JOB_PREFIX=headline_ \
  N_CANDIDATES=64 \
  N_ROUNDS=4 \
  MAX_TIEBREAK_ROUNDS=8 \
  TEMPERATURE=0.8 \
  MAX_DIFFERENTIAL_PROBES=24 \
  CONSENSUS_MIN_FRACTION=0.70 \
  CONSENSUS_MIN_MARGIN=3 \
  CONSENSUS_MIN_VOTES=5 \
  ENABLE_7B=1 \
  ENABLE_14B=1 \
  ENABLE_32B=1 \
  RUN_MBPP=1 \
  RUN_HUMANEVAL=1 \
  DELTA_7B_WALL=24:00:00 \
  DELTA_14B_WALL=32:00:00 \
  DELTA_32B_WALL=48:00:00 \
  DELTA_32B_MAX_MODEL_LEN=8192 \
  bash scripts/submit_delta_generated_filter_matrix.sh "${passthrough[@]}"
)
