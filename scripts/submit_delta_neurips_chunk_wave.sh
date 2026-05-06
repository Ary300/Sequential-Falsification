#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

SYNC_FIRST=0
DRY_RUN=0
CHAIN_LENGTH="${CHAIN_LENGTH:-1}"
CHUNK_WALL="${CHUNK_WALL:-01:00:00}"
HE_7B_DEPENDENCY="${HE_7B_DEPENDENCY:-}"
HE_14B_DEPENDENCY="${HE_14B_DEPENDENCY:-}"
MBPP_7B_DEPENDENCY="${MBPP_7B_DEPENDENCY:-}"
MBPP_14B_DEPENDENCY="${MBPP_14B_DEPENDENCY:-}"

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

echo "Submitting NeurIPS-style interactive chunk boosts for the weakest rows..."

submit_chunk() {
  (
    cd "${ROOT_DIR}"
    env "$@" bash scripts/submit_delta_interactive_chunk.sh "${passthrough[@]}"
  )
}

submit_chained_chunks() {
  local chain_name="$1"
  local dependency="${2:-}"
  shift 2
  local idx
  for idx in $(seq 1 "${CHAIN_LENGTH}"); do
    local suffix="${chain_name}_c${idx}"
    local output
    output="$(
      (
        cd "${ROOT_DIR}"
        env JOB_NAME="${suffix}" AFTERANY_DEPENDENCY="${dependency}" "$@" \
          bash scripts/submit_delta_interactive_chunk.sh "${passthrough[@]}"
      )
    )"
    echo "${output}"
    dependency="$(printf '%s\n' "${output}" | awk -F= '/=/{print $2}' | tail -n1)"
  done
}
submit_chained_chunks spx_r1_7b_he_i2h \
  "${HE_7B_DEPENDENCY}" \
  PARTITION=ghx4-interactive \
  WALL="${CHUNK_WALL}" \
  MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  BENCHMARKS=humaneval_plus \
  METHODS=greedy:majority_vote:generated_test_filter:self_debug:code_t:s_star:falsification:oracle \
  OUTPUT_DIR=results/paperproxystrongi2h_r1_7b_humaneval_full \
  SEEDS=42 \
  MAX_PROBLEMS=164 \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  MAX_TIEBREAK_ROUNDS=6

submit_chained_chunks spx_qwen14b_he_i2h \
  "${HE_14B_DEPENDENCY}" \
  PARTITION=ghx4-interactive \
  WALL="${CHUNK_WALL}" \
  MODEL=Qwen/Qwen2.5-Coder-14B-Instruct \
  BENCHMARKS=humaneval_plus \
  METHODS=greedy:majority_vote:generated_test_filter:self_debug:code_t:s_star:falsification:oracle \
  OUTPUT_DIR=results/paperproxystrongi2h_qwen14b_humaneval_full \
  SEEDS=42 \
  MAX_PROBLEMS=164 \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  MAX_TIEBREAK_ROUNDS=6

submit_chained_chunks sgtf_r1_7b_mbpp_i2h \
  "${MBPP_7B_DEPENDENCY}" \
  PARTITION=ghx4-interactive \
  WALL="${CHUNK_WALL}" \
  MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  BENCHMARKS=mbpp_plus \
  METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle \
  OUTPUT_DIR=results/reviewerstrongi2h_r1_7b_mbpp_full \
  SEEDS=42 \
  MAX_PROBLEMS=378 \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  MAX_TIEBREAK_ROUNDS=6

submit_chained_chunks sgtf_qwen14b_mbpp_i2h \
  "${MBPP_14B_DEPENDENCY}" \
  PARTITION=ghx4-interactive \
  WALL="${CHUNK_WALL}" \
  MODEL=Qwen/Qwen2.5-Coder-14B-Instruct \
  BENCHMARKS=mbpp_plus \
  METHODS=greedy:majority_vote:generated_test_filter:self_debug:falsification:oracle \
  OUTPUT_DIR=results/reviewerstrongi2h_qwen14b_mbpp_full \
  SEEDS=42 \
  MAX_PROBLEMS=378 \
  N_CANDIDATES=16 \
  N_ROUNDS=3 \
  MAX_TIEBREAK_ROUNDS=6
