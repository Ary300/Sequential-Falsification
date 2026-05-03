#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${COT_LENGTHS:-}" ]]; then
  COT_LENGTHS="$(python3 - <<'PY'
values = [0, 128, 256, 512, 768] + list(range(924, 1025))
print(",".join(str(v) for v in sorted(set(values))))
PY
)"
fi

MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}" \
OUTPUT_DIR="${OUTPUT_DIR:-results/theorem3_r1_14b_tail_trajectory_v1}" \
BENCHMARKS="${BENCHMARKS:-wikicontradict,conflictbank}" \
CONDITIONS="${CONDITIONS:-aligned_context,conflict_context}" \
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-48}" \
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-48}" \
TRIVIAQA_MAX="${TRIVIAQA_MAX:-0}" \
CONFLICTBANK_SCREENING_POOL="${CONFLICTBANK_SCREENING_POOL:-96}" \
JOB_NAME="${JOB_NAME:-r1_14b_tail}" \
WALL="${WALL:-18:00:00}" \
GPUS="${GPUS:-1}" \
CPUS="${CPUS:-16}" \
TP_SIZE="${TP_SIZE:-1}" \
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}" \
BENCHMARK_MAXIMA="${BENCHMARK_MAXIMA:-conflictbank=48,wikicontradict=48}" \
COT_LENGTHS="${COT_LENGTHS}" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
