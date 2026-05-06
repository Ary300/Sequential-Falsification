#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

submit_pair() {
  local tag="$1"
  local objective="$2"
  local beta="$3"
  local group_size="$4"
  local temperature="$5"
  local warmstart_epochs="$6"
  local max_source="$7"
  local max_train="$8"
  local max_val="$9"
  local max_eval="${10}"

  local output_dir="results/e1_deepseek_llama8_${objective}_${tag}"
  local job_name
  if [[ "${objective}" == "dpo" ]]; then
    job_name="r1l8dn_${tag}"
  else
    job_name="r1l8gn_${tag}"
  fi

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="${objective}" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
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
    OBJECTIVE="${objective}" \
    MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    OUTPUT_DIR="${output_dir}" \
    JOB_NAME="${job_name}" \
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

# Pair A: slightly softer KL, larger group, extra warmstart, now with
# DeepSeek-native completion-mode theorem-3 eval.
submit_pair "native_b005g8w2" "dpo" "0.05" "8" "0.7" "2" "800" "560" "80" "80"
submit_pair "native_b005g8w2" "grpo" "0.05" "8" "0.7" "2" "800" "560" "80" "80"

# Pair B: even softer KL under the same matched data budget.
submit_pair "native_b002g8w2" "dpo" "0.02" "8" "0.7" "2" "800" "560" "80" "80"
submit_pair "native_b002g8w2" "grpo" "0.02" "8" "0.7" "2" "800" "560" "80" "80"
