#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

OBJECTIVE=dpo \
MODEL_NAME="microsoft/Phi-3-mini-4k-instruct" \
OUTPUT_DIR="results/e1_phi3mini_sft_control" \
JOB_NAME="e1_p3_sft" \
WALL="12:00:00" \
MAX_SOURCE_ROWS=800 \
MAX_TRAIN_ROWS=560 \
MAX_VAL_ROWS=80 \
MAX_EVAL_ROWS=80 \
EPOCHS=0 \
WARMSTART_EPOCHS=2 \
TEMPERATURE=0.8 \
VLLM_MAX_MODEL_LEN=4096 \
RUN_THEOREM3_EVAL=1 \
EVAL_OUTPUT_DIR="results/e1_phi3mini_sft_control/theorem3_eval_full_v1" \
EVAL_WIKICONTRADICT_MAX=96 \
EVAL_CONFLICTBANK_MAX=128 \
bash "${SCRIPT_DIR}/submit_delta_theorem3_matched_objective_lora.sh" "${EXTRA_ARGS[@]}"
