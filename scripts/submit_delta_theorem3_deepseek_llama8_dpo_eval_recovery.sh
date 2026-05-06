#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DELTA_RESULTS_ROOT="${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/adas17/tts_results}"

latest_deepseek_dir() {
  local pattern="$1"
  find /work/hdd/bgvi/adas17/tts_results/results /work/nvme/bgvi/adas17/tts_results/results \
    -maxdepth 1 -type d -name "${pattern}" -print0 2>/dev/null \
    | xargs -0 stat -c '%Y %n' 2>/dev/null \
    | sort -nr \
    | head -n 1 \
    | cut -d' ' -f2-
}

DEFAULT_DPO_DIR="$(latest_deepseek_dir 'e1_deepseek_llama8_dpo*')"
MODEL="${MODEL:-${DEFAULT_DPO_DIR}/merged_model}" \
DELTA_RESULTS_ROOT="${DELTA_RESULTS_ROOT}" \
OUTPUT_DIR="${OUTPUT_DIR:-results/e1_deepseek_llama8_dpo/theorem3_eval_recovery_v2}" \
BENCHMARKS="wikicontradict,conflictbank" \
CONDITIONS="aligned_context,conflict_context" \
WIKICONTRADICT_MAX=96 \
CONFLICTBANK_MAX=128 \
CONFLICTBANK_SCREENING_POOL=1200 \
COT_LENGTHS="0,128,1024" \
REQUEST_FORMAT="completion" \
PROMPT_PROTOCOL="deepseek_native" \
TP_SIZE=1 \
MAX_MODEL_LEN=12288 \
GPU_MEMORY_UTILIZATION=0.90 \
WALL="${WALL:-06:00:00}" \
JOB_NAME="${JOB_NAME:-r1l8_drev}" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
