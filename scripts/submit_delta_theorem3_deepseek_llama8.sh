#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}" \
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_deepseek_r1_llama8_real_v1}" \
BENCHMARKS="${BENCHMARKS:-wikicontradict,conflictbank}" \
CONDITIONS="${CONDITIONS:-aligned_context,conflict_context}" \
COT_LENGTHS="${COT_LENGTHS:-0,128,1024}" \
REQUEST_FORMAT="${REQUEST_FORMAT:-completion}" \
TEMPERATURE="${TEMPERATURE:-0.0}" \
TOP_P="${TOP_P:-1.0}" \
TP_SIZE="${TP_SIZE:-1}" \
GPUS="${GPUS:-1}" \
CPUS="${CPUS:-16}" \
WALL="${WALL:-10:00:00}" \
MAX_MODEL_LEN="${MAX_MODEL_LEN:-8192}" \
JOB_NAME="${JOB_NAME:-r1l8t3}" \
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-128}" \
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-96}" \
TRIVIAQA_MAX="${TRIVIAQA_MAX:-0}" \
CONFLICTBANK_SCREENING_POOL="${CONFLICTBANK_SCREENING_POOL:-1200}" \
"${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
