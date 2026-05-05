#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

SEED_START="${SEED_START:-42}"
SEED_END="${SEED_END:-71}"
MAX_SOURCE_ROWS="${MAX_SOURCE_ROWS:-900}"
MAX_TRAIN_ROWS="${MAX_TRAIN_ROWS:-640}"
MAX_VAL_ROWS="${MAX_VAL_ROWS:-96}"
MAX_EVAL_ROWS="${MAX_EVAL_ROWS:-96}"

resolve_hf_snapshot() {
  local repo_id="$1"
  local cache_root="${HF_HOME:-$HOME/.cache/huggingface}/hub/models--${repo_id//\//--}"
  local snapshot=""
  if [[ -f "${cache_root}/refs/main" ]]; then
    local rev
    rev="$(<"${cache_root}/refs/main")"
    if [[ -d "${cache_root}/snapshots/${rev}" ]]; then
      snapshot="${cache_root}/snapshots/${rev}"
    fi
  fi
  if [[ -z "${snapshot}" && -d "${cache_root}/snapshots" ]]; then
    snapshot="$(find "${cache_root}/snapshots" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
  fi
  if [[ -n "${snapshot}" ]]; then
    printf '%s\n' "${snapshot}"
  else
    printf '%s\n' "${repo_id}"
  fi
}

LLAMA8_MODEL="${LLAMA8_MODEL:-$(resolve_hf_snapshot "meta-llama/Llama-3.1-8B")}"

for seed in $(seq "${SEED_START}" "${SEED_END}"); do
  echo "Submitting Llama-8B GRPO seed ${seed}" >&2
  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="grpo" \
    MODEL_NAME="${LLAMA8_MODEL}" \
    OUTPUT_DIR="results/e1_llama8b_grpo_s${seed}" \
    JOB_NAME="l8g_s${seed}" \
    WALL="14:00:00" \
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
    WALL="14:00:00" \
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
