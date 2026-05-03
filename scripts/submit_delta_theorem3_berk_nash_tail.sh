#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "${TAIL_COT_LENGTHS:-}" ]]; then
  TAIL_COT_LENGTHS="$(python3 - <<'PY'
values = [0, 128, 256, 512, 768] + list(range(924, 1025))
print(",".join(str(v) for v in sorted(set(values))))
PY
)"
fi

MODEL="${TAIL_MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}" \
OUTPUT_DIR="${TAIL_OUTPUT_DIR:-results/theorem3_r1_14b_tail_trajectory_v1}" \
BENCHMARKS="${TAIL_BENCHMARKS:-wikicontradict,conflictbank}" \
CONDITIONS="${TAIL_CONDITIONS:-aligned_context,conflict_context}" \
CONFLICTBANK_MAX="${TAIL_CONFLICTBANK_MAX:-48}" \
WIKICONTRADICT_MAX="${TAIL_WIKICONTRADICT_MAX:-48}" \
TRIVIAQA_MAX="${TAIL_TRIVIAQA_MAX:-0}" \
CONFLICTBANK_SCREENING_POOL="${TAIL_CONFLICTBANK_SCREENING_POOL:-96}" \
JOB_NAME="${TAIL_JOB_NAME:-r1_14b_tail}" \
WALL="${TAIL_WALL:-18:00:00}" \
GPUS="${TAIL_GPUS:-1}" \
CPUS="${TAIL_CPUS:-16}" \
TP_SIZE="${TAIL_TP_SIZE:-1}" \
MAX_MODEL_LEN="${TAIL_MAX_MODEL_LEN:-16384}" \
BENCHMARK_MAXIMA="${TAIL_BENCHMARK_MAXIMA:-conflictbank=48,wikicontradict=48}" \
COT_LENGTHS="${TAIL_COT_LENGTHS}" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
