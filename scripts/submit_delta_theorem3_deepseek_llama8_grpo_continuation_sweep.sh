#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

DELTA_USER=${DELTA_USER:-adas17}
HDD_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/${DELTA_USER}/tts_results}
HDD_CACHE_ROOT=${HDD_CACHE_ROOT:-${HDD_RESULTS_ROOT}/runtime_cache}
U_RESULTS_ROOT=${U_RESULTS_ROOT:-/u/${DELTA_USER}/tts_results_staging}

submit_job() {
  local tag="$1"
  local beta="$2"
  local group_size="$3"
  local temperature="$4"
  local warmstart_epochs="$5"
  local objective_epochs="$6"
  local seed="$7"

  local output_dir="results/e1_deepseek_llama8_grpo_${tag}"
  local job_name="r1l8gc_${tag}"

  local -a env_args=(
    "OBJECTIVE=grpo"
    "MODEL_NAME=deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
    "OUTPUT_DIR=${output_dir}"
    "JOB_NAME=${job_name}"
    "WALL=14:00:00"
    "DELTA_RESULTS_ROOT=${HDD_RESULTS_ROOT}"
    "USE_NODE_LOCAL_STAGING=1"
    "SYNC_BACK_ROOT=${U_RESULTS_ROOT}"
    "HF_HOME=${HDD_CACHE_ROOT}/hf_cache"
    "XDG_CACHE_HOME=${HDD_CACHE_ROOT}/xdg_cache"
    "XDG_CONFIG_HOME=${HDD_CACHE_ROOT}/xdg_config"
    "MAX_SOURCE_ROWS=900"
    "MAX_TRAIN_ROWS=640"
    "MAX_VAL_ROWS=96"
    "MAX_EVAL_ROWS=96"
    "WARMSTART_EPOCHS=${warmstart_epochs}"
    "EPOCHS=${objective_epochs}"
    "BETA=${beta}"
    "GROUP_SIZE=${group_size}"
    "TEMPERATURE=${temperature}"
    "TOP_P=0.95"
    "SEED=${seed}"
    "SAVE_INTERMEDIATE_CHECKPOINTS=1"
    "VLLM_MAX_MODEL_LEN=4096"
    "RUN_THEOREM3_EVAL=1"
    "EVAL_WIKICONTRADICT_MAX=96"
    "EVAL_CONFLICTBANK_MAX=128"
    "EVAL_REQUEST_FORMAT=completion"
    "EVAL_PROMPT_PROTOCOL=deepseek_native"
  )

  if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    env "${env_args[@]}" bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
  else
    env "${env_args[@]}" bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh"
  fi
}

# The previous best native-matched pocket was beta=0.02, group=8, warmstart=2.
# Continue around that pocket before moving farther afield.
submit_job "nativeplus_b002g8w3" "0.02" "8" "0.7" "3" "1" "42"

# Same pocket, but one extra objective epoch in case the GRPO leg is simply
# undertrained relative to the DPO/SFT warmstart.
submit_job "nativeplus_b002g8w3e2" "0.02" "8" "0.7" "3" "2" "42"

# Slightly softer regularization while keeping the smaller group size fixed,
# to separate the effects of beta and group size from the larger-group rescue.
submit_job "nativeplus_b001g8w3" "0.01" "8" "0.7" "3" "1" "43"
