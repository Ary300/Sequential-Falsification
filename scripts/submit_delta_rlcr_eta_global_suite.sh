#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

ROWS_JSONL_DEFAULT="/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/theorem3_eval_full_v3/theorem3_generation_rows.jsonl"
MODEL_DEFAULT="/work/nvme/bgvi/adas17/tts_results/results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu_v2a/merged_model"
OUTPUT_ROOT_DEFAULT="/work/nvme/bgvi/adas17/tts_results/results/rlcr_eta_global_v1"

submit_cell() {
  local benchmark="$1"
  local condition="$2"
  local cot_length="$3"
  local output_prefix="${OUTPUT_ROOT_DEFAULT}/${benchmark}_${condition}_cot${cot_length}"
  local job_name="reta_${benchmark:0:2}_${condition:0:2}_${cot_length}"

  MODEL="${MODEL:-$MODEL_DEFAULT}" \
  ROWS_JSONL="${ROWS_JSONL:-$ROWS_JSONL_DEFAULT}" \
  OUTPUT_PREFIX="${output_prefix}" \
  BENCHMARK="${benchmark}" \
  CONDITION="${condition}" \
  COT_LENGTH="${cot_length}" \
  CALIBRATION_SIZE="${CALIBRATION_SIZE:-64}" \
  BATCH_SIZE="${BATCH_SIZE:-4}" \
  JOB_NAME="${job_name}" \
  WALL="${WALL:-04:00:00}" \
  bash "${SCRIPT_DIR}/submit_delta_theorem3_eta_tempered.sh" "${EXTRA_ARGS[@]}"
}

for benchmark in conflictbank wikicontradict; do
  for condition in aligned_context conflict_context; do
    for cot_length in 0 128 1024; do
      submit_cell "${benchmark}" "${condition}" "${cot_length}"
    done
    sleep 1
  done
done
