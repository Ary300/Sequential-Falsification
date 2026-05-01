#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-70B}" \
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_paper2_r1_llama70_real}" \
BENCHMARKS="${BENCHMARKS:-wikicontradict,conflictbank}" \
CONDITIONS="${CONDITIONS:-conflict_context}" \
COT_LENGTHS="${COT_LENGTHS:-0,128,1024}" \
TP_SIZE="${TP_SIZE:-4}" \
GPUS="${GPUS:-4}" \
CPUS="${CPUS:-32}" \
WALL="${WALL:-20:00:00}" \
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}" \
JOB_NAME="${JOB_NAME:-p2_r1l70}" \
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-200}" \
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-200}" \
TRIVIAQA_MAX="${TRIVIAQA_MAX:-0}" \
"${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
