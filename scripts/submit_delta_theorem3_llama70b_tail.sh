#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

resolve_hf_snapshot() {
  local repo_id="$1"
  local cache_root="${HF_HOME:-$HOME/.cache/huggingface}/hub/models--${repo_id//\//--}"
  local snapshot=""
  if [[ -f "${cache_root}/refs/main" ]]; then
    local rev
    rev="$(<"${cache_root}/refs/main")"
    if [[ -d "${cache_root}/snapshots/${rev}" ]]; then
      snapshot="${cache_root}/snapshots/${rev}"
    fi
  fi
  if [[ -z "${snapshot}" && -d "${cache_root}/snapshots" ]]; then
    snapshot="$(find "${cache_root}/snapshots" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)"
  fi
  if [[ -n "${snapshot}" ]]; then
    printf '%s\n' "${snapshot}"
  else
    printf '%s\n' "${repo_id}"
  fi
}

if [[ -z "${TAIL_COT_LENGTHS:-}" ]]; then
  TAIL_COT_LENGTHS="$(python3 - <<'PY'
values = [0, 128, 256, 512, 768] + list(range(924, 1025))
print(",".join(str(v) for v in sorted(set(values))))
PY
)"
fi

MODEL="${MODEL:-${TAIL_MODEL:-$(resolve_hf_snapshot "meta-llama/Llama-3.1-70B-Instruct")}}" \
OUTPUT_DIR="${OUTPUT_DIR:-${TAIL_OUTPUT_DIR:-results/theorem3_llama31_70b_tail_trajectory_v1}}" \
BENCHMARKS="${BENCHMARKS:-${TAIL_BENCHMARKS:-wikicontradict,conflictbank}}" \
CONDITIONS="${CONDITIONS:-${TAIL_CONDITIONS:-aligned_context,conflict_context}}" \
CONFLICTBANK_MAX="${CONFLICTBANK_MAX:-${TAIL_CONFLICTBANK_MAX:-48}}" \
WIKICONTRADICT_MAX="${WIKICONTRADICT_MAX:-${TAIL_WIKICONTRADICT_MAX:-48}}" \
TRIVIAQA_MAX="${TRIVIAQA_MAX:-${TAIL_TRIVIAQA_MAX:-0}}" \
CONFLICTBANK_SCREENING_POOL="${CONFLICTBANK_SCREENING_POOL:-${TAIL_CONFLICTBANK_SCREENING_POOL:-96}}" \
JOB_NAME="${JOB_NAME:-${TAIL_JOB_NAME:-l3170_tail}}" \
WALL="${WALL:-${TAIL_WALL:-24:00:00}}" \
GPUS="${GPUS:-${TAIL_GPUS:-4}}" \
CPUS="${CPUS:-${TAIL_CPUS:-32}}" \
TP_SIZE="${TP_SIZE:-${TAIL_TP_SIZE:-4}}" \
MAX_MODEL_LEN="${MAX_MODEL_LEN:-${TAIL_MAX_MODEL_LEN:-16384}}" \
BENCHMARK_MAXIMA="${BENCHMARK_MAXIMA:-${TAIL_BENCHMARK_MAXIMA:-conflictbank=48,wikicontradict=48}}" \
COT_LENGTHS="${COT_LENGTHS:-${TAIL_COT_LENGTHS}}" \
bash "${SCRIPT_DIR}/submit_delta_theorem3_real_generation.sh" "$@"
