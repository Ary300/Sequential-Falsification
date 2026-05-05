#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

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

GEMMA9_MODEL="${GEMMA9_MODEL:-$(resolve_hf_snapshot "google/gemma-2-9b-it")}"

submit_job() {
  local objective="$1"
  local output_dir="$2"
  local job_name="$3"
  local warmstart_epochs="$4"
  local epochs="$5"

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="${objective}" \
    MODEL_NAME="${GEMMA9_MODEL}" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="800" \
    MAX_TRAIN_ROWS="560" \
    MAX_VAL_ROWS="80" \
    MAX_EVAL_ROWS="80" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="${epochs}" \
    TEMPERATURE="0.8" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="generic" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="${objective}" \
    MODEL_NAME="${GEMMA9_MODEL}" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="800" \
    MAX_TRAIN_ROWS="560" \
    MAX_VAL_ROWS="80" \
    MAX_EVAL_ROWS="80" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="${epochs}" \
    TEMPERATURE="0.8" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="generic" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
}

# SFT-only matched control: same base, same source pool, no RL stage.
submit_job "dpo" "results/e1_gemma9_sft_control" "e1_g9_sft" "2" "0"

# DPO and GRPO matched pair on the same base and data budget.
submit_job "dpo" "results/e1_gemma9_dpo" "e1_g9_dpo" "1" "1"
submit_job "grpo" "results/e1_gemma9_grpo" "e1_g9_grpo" "1" "1"
