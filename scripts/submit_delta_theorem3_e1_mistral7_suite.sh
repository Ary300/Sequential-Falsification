#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

submit_job() {
  local objective="$1"
  local output_dir="$2"
  local job_name="$3"
  local warmstart_epochs="$4"
  local epochs="$5"

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    OBJECTIVE="${objective}" \
    MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3" \
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
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    OBJECTIVE="${objective}" \
    MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3" \
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
    EVAL_WIKICONTRADICT_MAX="96" \
    EVAL_CONFLICTBANK_MAX="128" \
    bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
}

# SFT-only matched control: same base, same source pool, no RL stage.
submit_job "dpo" "results/e1_mistral7_sft_control" "e1_m7_sft" "2" "0"

# DPO and GRPO matched pair on the same base and data budget.
submit_job "dpo" "results/e1_mistral7_dpo" "e1_m7_dpo" "1" "1"
submit_job "grpo" "results/e1_mistral7_grpo" "e1_m7_grpo" "1" "1"
