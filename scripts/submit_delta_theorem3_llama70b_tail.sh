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

TAIL_MODEL="${TAIL_MODEL:-meta-llama/Llama-3.1-70B-Instruct}" \
TAIL_OUTPUT_DIR="${TAIL_OUTPUT_DIR:-results/theorem3_llama31_70b_tail_trajectory_v1}" \
TAIL_BENCHMARKS="${TAIL_BENCHMARKS:-wikicontradict,conflictbank}" \
TAIL_CONDITIONS="${TAIL_CONDITIONS:-aligned_context,conflict_context}" \
TAIL_CONFLICTBANK_MAX="${TAIL_CONFLICTBANK_MAX:-48}" \
TAIL_WIKICONTRADICT_MAX="${TAIL_WIKICONTRADICT_MAX:-48}" \
TAIL_TRIVIAQA_MAX="${TAIL_TRIVIAQA_MAX:-0}" \
TAIL_CONFLICTBANK_SCREENING_POOL="${TAIL_CONFLICTBANK_SCREENING_POOL:-96}" \
TAIL_JOB_NAME="${TAIL_JOB_NAME:-l3170_tail}" \
TAIL_WALL="${TAIL_WALL:-24:00:00}" \
TAIL_GPUS="${TAIL_GPUS:-4}" \
TAIL_CPUS="${TAIL_CPUS:-32}" \
TAIL_TP_SIZE="${TAIL_TP_SIZE:-4}" \
TAIL_MAX_MODEL_LEN="${TAIL_MAX_MODEL_LEN:-16384}" \
TAIL_BENCHMARK_MAXIMA="${TAIL_BENCHMARK_MAXIMA:-conflictbank=48,wikicontradict=48}" \
TAIL_COT_LENGTHS="${TAIL_COT_LENGTHS}" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
