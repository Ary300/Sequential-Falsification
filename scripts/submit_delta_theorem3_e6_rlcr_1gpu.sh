#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GPUS=1 \
CPUS=16 \
WALL=18:00:00 \
FEATURE_BATCH_SIZE=1 \
MAX_TRAIN_ROWS=1200 \
MAX_VAL_ROWS=200 \
MAX_EVAL_ROWS=500 \
JOB_NAME=t3_rlcr1g \
OUTPUT_DIR=results/theorem3_rlcr_style_lora_r1_14b_conflict_1gpu \
bash "${SCRIPT_DIR}/submit_delta_theorem3_rlcr_style_lora.sh" "$@"
