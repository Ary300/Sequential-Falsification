#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRA_ARGS=("$@")

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <model_dir> [output_dir] [job_name]" >&2
  exit 1
fi

MODEL_DIR="$1"
OUTPUT_DIR="${2:-}"
JOB_NAME="${3:-r1l8_ckpteval}"

DELTA_USER=${DELTA_USER:-adas17}
HDD_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/hdd/bgvi/${DELTA_USER}/tts_results}
HDD_CACHE_ROOT=${HDD_CACHE_ROOT:-${HDD_RESULTS_ROOT}/runtime_cache}

if [[ -z "${OUTPUT_DIR}" ]]; then
  base_name="$(basename "${MODEL_DIR}")"
  parent_name="$(basename "$(dirname "${MODEL_DIR}")")"
  OUTPUT_DIR="results/${parent_name}/${base_name}_theorem3_eval_deepseek_native"
fi

if [[ ${#EXTRA_ARGS[@]} -gt 3 ]]; then
  EXTRA_PASSTHRU=("${EXTRA_ARGS[@]:3}")
else
  EXTRA_PASSTHRU=()
fi

env \
  DELTA_RESULTS_ROOT="${HDD_RESULTS_ROOT}" \
  HF_HOME="${HDD_CACHE_ROOT}/hf_cache" \
  XDG_CACHE_HOME="${HDD_CACHE_ROOT}/xdg_cache" \
  XDG_CONFIG_HOME="${HDD_CACHE_ROOT}/xdg_config" \
  MODEL="${MODEL_DIR}" \
  OUTPUT_DIR="${OUTPUT_DIR}" \
  BENCHMARKS="wikicontradict,conflictbank" \
  CONDITIONS="aligned_context,conflict_context" \
  WIKICONTRADICT_MAX="96" \
  CONFLICTBANK_MAX="128" \
  CONFLICTBANK_SCREENING_POOL="1200" \
  COT_LENGTHS="0,128,1024" \
  REQUEST_FORMAT="completion" \
  PROMPT_PROTOCOL="deepseek_native" \
  TEMPERATURE="0.6" \
  TOP_P="0.95" \
  TP_SIZE="1" \
  MAX_MODEL_LEN="12288" \
  WALL="06:00:00" \
  JOB_NAME="${JOB_NAME}" \
  bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "${EXTRA_PASSTHRU[@]}"
