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
  local objective="$2"
  local beta="$3"
  local group_size="$4"
  local temperature="$5"
  local warmstart_epochs="$6"
  local max_source="$7"
  local max_train="$8"
  local max_val="$9"
  local max_eval="${10}"
  local seed="${11}"

  local output_dir="results/e1_deepseek_llama8_${objective}_${tag}"
  local job_name
  if [[ "${objective}" == "dpo" ]]; then
    job_name="r1l8dr_${tag}"
  else
    job_name="r1l8gr_${tag}"
  fi

  local -a env_args=(
    "OBJECTIVE=${objective}"
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
    "MAX_SOURCE_ROWS=${max_source}"
    "MAX_TRAIN_ROWS=${max_train}"
    "MAX_VAL_ROWS=${max_val}"
    "MAX_EVAL_ROWS=${max_eval}"
    "WARMSTART_EPOCHS=${warmstart_epochs}"
    "EPOCHS=1"
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

# Pair 1: rerun the previously best native pocket, but with the intended
# warmstart now actually forwarded through the Delta submit wrapper.
submit_job "nativefix_b002g8w2" "dpo" "0.02" "8" "0.7" "2" "900" "640" "96" "96" "42"
submit_job "nativefix_b002g8w2" "grpo" "0.02" "8" "0.7" "2" "900" "640" "96" "96" "42"

# Pair 2: slightly softer GRPO/DPO regularization, larger groups, and one extra
# warmstart epoch to test whether the weak 8B story is mostly an undertrained
# small-budget artifact.
submit_job "nativerescue_b001g12w3" "dpo" "0.01" "12" "0.7" "3" "900" "640" "96" "96" "42"
submit_job "nativerescue_b001g12w3" "grpo" "0.01" "12" "0.7" "3" "900" "640" "96" "96" "42"

# Extra GRPO-only exploratory leg: slightly cooler sampling and a fresh seed to
# probe whether reward-variance quality, rather than only KL strength, is the
# main limiter for DeepSeek-8B.
submit_job "nativerescue_b001g16t06w3s43" "grpo" "0.01" "16" "0.6" "3" "900" "640" "96" "96" "43"
