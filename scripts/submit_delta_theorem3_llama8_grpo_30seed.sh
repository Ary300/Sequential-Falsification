#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")
DELTA_USER=${DELTA_USER:-adas17}
HDD_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/${DELTA_USER}/tts_results}
U_RESULTS_ROOT=${U_RESULTS_ROOT:-/u/${DELTA_USER}/tts_results_staging}

SEED_START="${SEED_START:-42}"
SEED_END="${SEED_END:-71}"
MAX_SOURCE_ROWS="${MAX_SOURCE_ROWS:-900}"
MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS:-640}"
MAX_VAL_ROWS="${MAX_VAL_ROWS:-96}"
MAX_EVAL_ROWS="${MAX_EVAL_ROWS:-96}"

resolve_hf_snapshot() {
  local repo_id="$1"
  local repo_cache="models--${repo_id//\//--}"
  local -a roots=()
  [[ -n "${HF_HOME:-}" ]] && roots+=("${HF_HOME}/hub")
  roots+=(
    "/work/nvme/bgvi/${DELTA_USER}/hf_cache/hub"
    "/work/hdd/bgvi/${DELTA_USER}/tts_results/runtime_cache/hf_cache/hub"
    "/u/${DELTA_USER}/.cache/huggingface/hub"
  )

  local root cache_root snapshot rev
  for root in "${roots[@]}"; do
    cache_root="${root}/${repo_cache}"
    if [[ -f "${cache_root}/refs/main" ]]; then
      rev="$(<"${cache_root}/refs/main")"
      if [[ -d "${cache_root}/snapshots/${rev}" ]]; then
        printf '%s\n' "${cache_root}/snapshots/${rev}"
        return 0
      fi
    fi
    if [[ -d "${cache_root}/snapshots" ]]; then
      snapshot="$(find "${cache_root}/snapshots" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
      if [[ -n "${snapshot}" ]]; then
        printf '%s\n' "${snapshot}"
        return 0
      fi
    fi
  done

  printf '%s\n' "${repo_id}"
}

LLAMA8_MODEL="${LLAMA8_MODEL:-$(resolve_hf_snapshot "meta-llama/Llama-3.1-8B")}"

for seed in $(seq "${SEED_START}" "${SEED_END}"); do
  echo "Submitting Llama-8B GRPO seed ${seed}" >&2
  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="grpo" \
    MODEL_NAME="${LLAMA8_MODEL}" \
    OUTPUT_DIR="results/e1_llama8b_grpo_s${seed}" \
    JOB_NAME="l8g_s${seed}" \
    WALL="${WALL:-04:00:00}" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    MAX_SOURCE_ROWS="${MAX_SOURCE_ROWS}" \
    MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS}" \
    MAX_VAL_ROWS="${MAX_VAL_ROWS}" \
    MAX_EVAL_ROWS="${MAX_EVAL_ROWS}" \
    WARMSTART_EPOCHS="1" \
    EPOCHS="1" \
    BETA="0.1" \
    GROUP_SIZE="4" \
    TEMPERATURE="0.8" \
    TOP_P="0.95" \
    SEED="${seed}" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="grpo" \
    MODEL_NAME="${LLAMA8_MODEL}" \
    OUTPUT_DIR="results/e1_llama8b_grpo_s${seed}" \
    JOB_NAME="l8g_s${seed}" \
    WALL="${WALL:-04:00:00}" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    MAX_SOURCE_ROWS="${MAX_SOURCE_ROWS}" \
    MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS}" \
    MAX_VAL_ROWS="${MAX_VAL_ROWS}" \
    MAX_EVAL_ROWS="${MAX_EVAL_ROWS}" \
    WARMSTART_EPOCHS="1" \
    EPOCHS="1" \
    BETA="0.1" \
    GROUP_SIZE="4" \
    TEMPERATURE="0.8" \
    TOP_P="0.95" \
    SEED="${seed}" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
done
