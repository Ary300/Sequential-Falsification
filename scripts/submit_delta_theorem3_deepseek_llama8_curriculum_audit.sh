#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")
DELTA_USER=${DELTA_USER:-adas17}
HDD_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/${DELTA_USER}/tts_results}
HDD_CACHE_ROOT=${HDD_RESULTS_ROOT}/runtime_cache

submit_job() {
  local objective="$1"
  local output_dir="$2"
  local job_name="$3"
  local beta="$4"
  local group_size="$5"

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="${objective}" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="800" \
    MAX_TRAIN_ROWS="560" \
    MAX_VAL_ROWS="80" \
    MAX_EVAL_ROWS="80" \
    WARMSTART_EPOCHS="2" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="0.7" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    SAVE_INTERMEDIATE_CHECKPOINTS="1" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="${objective}" \
    DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
    HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
    XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
    XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
    WALL="12:00:00" \
    MAX_SOURCE_ROWS="800" \
    MAX_TRAIN_ROWS="560" \
    MAX_VAL_ROWS="80" \
    MAX_EVAL_ROWS="80" \
    WARMSTART_EPOCHS="2" \
    EPOCHS="1" \
    BETA="${beta}" \
    GROUP_SIZE="${group_size}" \
    TEMPERATURE="0.7" \
    TOP_P="0.95" \
    VLLM_MAX_MODEL_LEN="4096" \
    SAVE_INTERMEDIATE_CHECKPOINTS="1" \
    RUN_THEOREM3_EVAL="1" \
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    EVAL_REQUEST_FORMAT="completion" \
    EVAL_PROMPT_PROTOCOL="deepseek_native" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
}

# Curriculum-audit pair: save adapters after each warmstart/objective epoch so
# the failure diagnosis can compare intermediate checkpoints instead of only the
# final merged models.
submit_job "dpo" "results/e1_deepseek_llama8_dpo_curriculum_audit" "r1l8_dcurr" "0.05" "8"
submit_job "grpo" "results/e1_deepseek_llama8_grpo_curriculum_audit" "r1l8_gcurr" "0.05" "8"
