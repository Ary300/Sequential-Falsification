#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

submit_job() {
  local objective="$1"
  local model_name="$2"
  local output_dir="$3"
  local job_name="$4"
  local wall="$5"
  local max_source="$6"
  local max_train="$7"
  local max_val="$8"
  local max_eval="$9"

  OBJECTIVE="${objective}" \
  MODEL_NAME="${model_name}" \
  OUTPUT_DIR="${output_dir}" \
  JOB_NAME="${job_name}" \
  WALL="${wall}" \
  MAX_SOURCE_ROWS="${max_source}" \
  MAX_TRAIN_ROWS="${max_train}" \
  MAX_VAL_ROWS="${max_val}" \
  MAX_EVAL_ROWS="${max_eval}" \
  RUN_THEOREM3_EVAL=1 \
  EVAL_WIKICONTRADICT_MAX=96 \
  EVAL_CONFLICTBANK_MAX=128 \
  bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
}

submit_job dpo "meta-llama/Llama-3.1-8B" "results/e1_llama8b_dpo" "e1_l8_dpo" "14:00:00" 900 640 96 96
submit_job grpo "meta-llama/Llama-3.1-8B" "results/e1_llama8b_grpo" "e1_l8_grpo" "14:00:00" 900 640 96 96
submit_job dpo "Qwen/Qwen2.5-14B" "results/e1_qwen14b_dpo" "e1_q14_dpo" "18:00:00" 1200 800 120 120
submit_job grpo "Qwen/Qwen2.5-14B" "results/e1_qwen14b_grpo" "e1_q14_grpo" "18:00:00" 1200 800 120 120
