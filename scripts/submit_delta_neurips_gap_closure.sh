#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SYNC_FIRST=0
DRY_RUN=0
RUN_BASELINES="${RUN_BASELINES:-1}"
RUN_COVERAGE="${RUN_COVERAGE:-1}"
RUN_ABLATIONS="${RUN_ABLATIONS:-1}"
AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"

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
    --skip-baselines)
      RUN_BASELINES=0
      shift
      ;;
    --skip-coverage)
      RUN_COVERAGE=0
      shift
      ;;
    --skip-ablations)
      RUN_ABLATIONS=0
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

run_from_root() {
  (
    cd "${ROOT_DIR}"
    "$@"
  )
}

echo "Submitting conservative NeurIPS gap-closure jobs..."
echo "This launcher intentionally writes to new result prefixes; it does not overwrite existing rows."

if [[ "${RUN_BASELINES}" == "1" ]]; then
  echo "1/3: Baseline/proxy gap closure for HumanEval+/MBPP+."
  run_from_root env \
    RESULT_PREFIX=paperneugap_proxy \
    JOB_PREFIX=neugap_ \
    AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY}" \
    N_CANDIDATES=16 \
    N_ROUNDS=4 \
    MAX_TIEBREAK_ROUNDS=6 \
    ENABLE_7B=1 \
    ENABLE_14B=1 \
    ENABLE_32B=1 \
    RUN_HUMANEVAL=1 \
    RUN_MBPP=1 \
    RUN_LIVECODEBENCH=0 \
    RUN_MATH500=0 \
    DELTA_7B_WALL=24:00:00 \
    DELTA_14B_WALL=28:00:00 \
    DELTA_32B_WALL=40:00:00 \
    DELTA_32B_MAX_MODEL_LEN=8192 \
    bash scripts/submit_delta_proxy_matrix.sh "${passthrough[@]}"

  echo "1/3b: Generated-test-filter gap closure for HumanEval+/MBPP+."
  run_from_root env \
    RESULT_PREFIX=paperneugap_gtf \
    JOB_PREFIX=neugap_ \
    AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY}" \
    N_CANDIDATES=16 \
    N_ROUNDS=4 \
    MAX_TIEBREAK_ROUNDS=6 \
    ENABLE_7B=1 \
    ENABLE_14B=1 \
    ENABLE_32B=1 \
    RUN_HUMANEVAL=1 \
    RUN_MBPP=1 \
    DELTA_7B_WALL=24:00:00 \
    DELTA_14B_WALL=28:00:00 \
    DELTA_32B_WALL=40:00:00 \
    DELTA_32B_MAX_MODEL_LEN=8192 \
    bash scripts/submit_delta_generated_filter_matrix.sh "${passthrough[@]}"
fi

if [[ "${RUN_COVERAGE}" == "1" ]]; then
  echo "2/3: Benchmark-coverage gap closure for LiveCodeBench/MATH."
  run_from_root env \
    RESULT_PREFIX=paperneugap \
    JOB_PREFIX=neugap_ \
    AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY}" \
    N_CANDIDATES=16 \
    N_ROUNDS=4 \
    MAX_TIEBREAK_ROUNDS=6 \
    ENABLE_7B=1 \
    ENABLE_14B=1 \
    ENABLE_32B=1 \
    RUN_HUMANEVAL=0 \
    RUN_MBPP=0 \
    RUN_LIVECODEBENCH=1 \
    RUN_MATH500=1 \
    LCB_MAX_PROBLEMS=400 \
    MATH_MAX_PROBLEMS=500 \
    DELTA_7B_WALL=24:00:00 \
    DELTA_14B_WALL=28:00:00 \
    DELTA_32B_WALL=40:00:00 \
    DELTA_32B_MAX_MODEL_LEN=8192 \
    bash scripts/submit_delta_paper_matrix.sh "${passthrough[@]}"
fi

if [[ "${RUN_ABLATIONS}" == "1" ]]; then
  echo "3/3: Core ablation pack on 7B MBPP+."
  run_from_root env \
    OUTPUT_ROOT=results/delta_neurips_ablations \
    FIGURE_ROOT=figures/delta_neurips_ablations \
    BACKEND_OVERRIDE=openai \
    AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY}" \
    SEEDS=42,43,44 \
    bash scripts/submit_delta_ablation_campaign.sh "${passthrough[@]}"
fi
