#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODEL="/work/nvme/bgvi/adas17/tts_results/results/e1_deepseek_llama8_dpo/merged_model" \
OUTPUT_DIR="results/e1_deepseek_llama8_dpo/theorem3_eval_recovery_v2" \
BENCHMARKS="wikicontradict,conflictbank" \
CONDITIONS="aligned_context,conflict_context" \
WIKICONTRADICT_MAX=96 \
CONFLICTBANK_MAX=128 \
CONFLICTBANK_SCREENING_POOL=1200 \
COT_LENGTHS="0,128,1024" \
TP_SIZE=1 \
MAX_MODEL_LEN=12288 \
GPU_MEMORY_UTILIZATION=0.90 \
WALL="06:00:00" \
JOB_NAME="r1l8_drev" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
