#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")
DELTA_USER=${DELTA_USER:-adas17}
HDD_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/${DELTA_USER}/tts_results}
HDD_CACHE_ROOT=${HDD_RESULTS_ROOT}/runtime_cache
U_RESULTS_ROOT=${U_RESULTS_ROOT:-/u/${DELTA_USER}/tts_results_staging}

submit_pair() {
  local tag="$1"
  local beta="$2"
  local group_size="$3"
  local temperature="$4"
  local warmstart_epochs="$5"
  local max_source="$6"
  local max_train="$7"
  local max_val="$8"
  local max_eval="$9"

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="dpo" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="results/e1_deepseek_llama8_dpo_${tag}" \
    JOB_NAME="r1l8d_${tag}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="${max_source}" \
    MAX_TRAIN_ROWS="${max_train}" \
    MAX_VAL_ROWS="${max_val}" \
    MAX_EVAL_ROWS="${max_eval}" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="${temperature}" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="dpo" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="results/e1_deepseek_llama8_dpo_${tag}" \
    JOB_NAME="r1l8d_${tag}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="${max_source}" \
    MAX_TRAIN_ROWS="${max_train}" \
    MAX_VAL_ROWS="${max_val}" \
    MAX_EVAL_ROWS="${max_eval}" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="${temperature}" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="grpo" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="results/e1_deepseek_llama8_grpo_${tag}" \
    JOB_NAME="r1l8g_${tag}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="${max_source}" \
    MAX_TRAIN_ROWS="${max_train}" \
    MAX_VAL_ROWS="${max_val}" \
    MAX_EVAL_ROWS="${max_eval}" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="${temperature}" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="grpo" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    USE_NODE_LOCAL_STAGING="1" \
    SYNC_BACK_ROOT="${U_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="results/e1_deepseek_llama8_grpo_${tag}" \
    JOB_NAME="r1l8g_${tag}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="${max_source}" \
    MAX_TRAIN_ROWS="${max_train}" \
    MAX_VAL_ROWS="${max_val}" \
    MAX_EVAL_ROWS="${max_eval}" \
    WARMSTART_EPOCHS="${warmstart_epochs}" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="${temperature}" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
}

# Pair A: slightly softer KL, larger GRPO group, extra warmstart.
submit_pair "b005g8w2" "0.05" "8" "0.7" "2" "800" "560" "80" "80"

# Pair B: even softer KL with the same matched data budget.
submit_pair "b002g8w2" "0.02" "8" "0.7" "2" "800" "560" "80" "80"
