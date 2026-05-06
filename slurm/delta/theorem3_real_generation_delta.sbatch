#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH -J theorem3_real
#SBATCH -o logs/theorem3_real_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
if [[ ! -f "${DELTA_VENV}/bin/activate" ]]; then
  for candidate in "/u/${USER}/venvs/tts-delta" "/u/${USER}/.venvs/tts-delta"; do
    if [[ -f "${candidate}/bin/activate" ]]; then
      DELTA_VENV="${candidate}"
      break
    fi
  done
fi
if [[ ! -f "${DELTA_VENV}/bin/activate" ]]; then
  echo "Delta venv not found: ${DELTA_VENV}" >&2
  exit 1
fi
source "${DELTA_VENV}/bin/activate"

DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
DELTA_CACHE_ROOT=${DELTA_CACHE_ROOT:-${DELTA_RESULTS_ROOT%/}/runtime_cache}
export HF_HOME=${HF_HOME:-${DELTA_CACHE_ROOT}/hf_home}
export XDG_CACHE_HOME=${XDG_CACHE_HOME:-${DELTA_CACHE_ROOT}/xdg_cache}
export XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-${DELTA_CACHE_ROOT}/xdg_config}
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-${XDG_CACHE_HOME}/vllm}
export VLLM_CONFIG_ROOT=${VLLM_CONFIG_ROOT:-${XDG_CONFIG_HOME}/vllm}
export TORCHINDUCTOR_CACHE_DIR=${TORCHINDUCTOR_CACHE_DIR:-${XDG_CACHE_HOME}/torchinductor}
export TRITON_CACHE_DIR=${TRITON_CACHE_DIR:-${XDG_CACHE_HOME}/triton}
export VLLM_NO_USAGE_STATS=${VLLM_NO_USAGE_STATS:-1}
export VLLM_DO_NOT_TRACK=${VLLM_DO_NOT_TRACK:-1}
export DO_NOT_TRACK=${DO_NOT_TRACK:-1}
USE_NODE_LOCAL_STAGING=${USE_NODE_LOCAL_STAGING:-0}
SYNC_BACK_ROOT=${SYNC_BACK_ROOT:-${DELTA_RESULTS_ROOT}}
NODE_LOCAL_ROOT=${NODE_LOCAL_ROOT:-${TMPDIR:-/tmp}/${USER}/tts_stage_${SLURM_JOB_ID}}
NODE_LOCAL_CACHE_ROOT=${NODE_LOCAL_CACHE_ROOT:-${NODE_LOCAL_ROOT}/runtime_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
BACKEND=${BACKEND:-openai}
BENCHMARKS=${BENCHMARKS:-wikicontradict,conflictbank}
CONDITIONS=${CONDITIONS:-aligned_context,conflict_context}
REQUEST_TIMEOUT=${REQUEST_TIMEOUT:-600}
TEMPERATURE=${TEMPERATURE:-0.0}
TOP_P=${TOP_P:-1.0}
SEED=${SEED:-42}
REQUEST_FORMAT=${REQUEST_FORMAT:-chat}
PROMPT_PROTOCOL=${PROMPT_PROTOCOL:-generic}
API_PORT=${API_PORT:-$((20000 + (${SLURM_JOB_ID:-0} % 20000)))}
export API_PORT
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}
TP_SIZE=${TP_SIZE:-1}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_real_generation_r1_7b}
WIKICONTRADICT_MAX=${WIKICONTRADICT_MAX:-200}
CONFLICTBANK_MAX=${CONFLICTBANK_MAX:-500}
TRIVIAQA_MAX=${TRIVIAQA_MAX:-200}
COT_LENGTHS=${COT_LENGTHS:-0,128,1024}
BENCHMARK_MAXIMA=${BENCHMARK_MAXIMA:-}
DATASET_PATHS=${DATASET_PATHS:-}
MERGE_PEFT_ADAPTER_FROM=${MERGE_PEFT_ADAPTER_FROM:-}
CONFLICTBANK_SCREENING_POOL=${CONFLICTBANK_SCREENING_POOL:-1200}
AMBIGUITY_LOW=${AMBIGUITY_LOW:-0.2}
AMBIGUITY_HIGH=${AMBIGUITY_HIGH:-0.8}
DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification-git}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

if [[ "${OUTPUT_DIR}" = /* ]]; then
  PERSIST_OUTPUT_DIR="${OUTPUT_DIR}"
else
  PERSIST_OUTPUT_DIR="${SYNC_BACK_ROOT%/}/${OUTPUT_DIR}"
fi

if [[ "${USE_NODE_LOCAL_STAGING}" == "1" ]]; then
  export HF_HOME="${NODE_LOCAL_CACHE_ROOT}/hf_home"
  export XDG_CACHE_HOME="${NODE_LOCAL_CACHE_ROOT}/xdg_cache"
  export XDG_CONFIG_HOME="${NODE_LOCAL_CACHE_ROOT}/xdg_config"
  export VLLM_CACHE_ROOT="${XDG_CACHE_HOME}/vllm"
  export VLLM_CONFIG_ROOT="${XDG_CONFIG_HOME}/vllm"
  export TORCHINDUCTOR_CACHE_DIR="${XDG_CACHE_HOME}/torchinductor"
  export TRITON_CACHE_DIR="${XDG_CACHE_HOME}/triton"
  RUN_OUTPUT_DIR="${NODE_LOCAL_ROOT}/run_output"
else
  RUN_OUTPUT_DIR="${PERSIST_OUTPUT_DIR}"
fi

VLLM_PID=""
cleanup() {
  local rc=$?
  if [[ -n "${VLLM_PID}" ]]; then
    kill "${VLLM_PID}" >/dev/null 2>&1 || true
  fi
  if [[ "${USE_NODE_LOCAL_STAGING}" == "1" && -d "${RUN_OUTPUT_DIR}" ]]; then
    mkdir -p "${PERSIST_OUTPUT_DIR}"
    rsync -a "${RUN_OUTPUT_DIR}/" "${PERSIST_OUTPUT_DIR}/"
  fi
  exit "${rc}"
}
trap cleanup EXIT

mkdir -p "${HF_HOME}" "${XDG_CACHE_HOME}" "${XDG_CONFIG_HOME}" "${VLLM_CACHE_ROOT}" "${VLLM_CONFIG_ROOT}"
mkdir -p "${TORCHINDUCTOR_CACHE_DIR}" "${TRITON_CACHE_DIR}" "${RUN_OUTPUT_DIR}"

if [[ -n "${MERGE_PEFT_ADAPTER_FROM}" ]]; then
  MERGED_LOCAL_MODEL_DIR="${NODE_LOCAL_ROOT}/merged_peft_model"
  mkdir -p "${MERGED_LOCAL_MODEL_DIR}"
  python scripts/merge_peft_adapter.py \
    --base-model "${MODEL}" \
    --adapter-dir "${MERGE_PEFT_ADAPTER_FROM}" \
    --output-dir "${MERGED_LOCAL_MODEL_DIR}" \
    --torch-dtype "bfloat16"
  MODEL="${MERGED_LOCAL_MODEL_DIR}"
fi

ARGS=(
  --output-dir "${RUN_OUTPUT_DIR}" \
  --backend "${BACKEND}" \
  --benchmarks "${BENCHMARKS}" \
  --conditions "${CONDITIONS}" \
  --model "${MODEL}" \
  --request-timeout "${REQUEST_TIMEOUT}" \
  --temperature "${TEMPERATURE}" \
  --top-p "${TOP_P}" \
  --seed "${SEED}" \
  --request-format "${REQUEST_FORMAT}" \
  --prompt-protocol "${PROMPT_PROTOCOL}" \
  --wikicontradict-max "${WIKICONTRADICT_MAX}" \
  --conflictbank-max "${CONFLICTBANK_MAX}" \
  --triviaqa-max "${TRIVIAQA_MAX}" \
  --cot-lengths "${COT_LENGTHS}" \
  --benchmark-maxima "${BENCHMARK_MAXIMA}" \
  --dataset-paths "${DATASET_PATHS}" \
  --conflictbank-screening-pool "${CONFLICTBANK_SCREENING_POOL}" \
  --ambiguity-low "${AMBIGUITY_LOW}" \
  --ambiguity-high "${AMBIGUITY_HIGH}"
)

if [[ "${BACKEND}" == "openai" ]]; then
  python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --generation-config vllm \
    --tensor-parallel-size "${TP_SIZE}" \
    --port "${API_PORT}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    > logs/vllm_theorem3_${SLURM_JOB_ID}.log 2>&1 &
  VLLM_PID=$!

  for _ in $(seq 1 60); do
    python - <<'PY' >/dev/null 2>&1 && break
from openai import OpenAI
import os
client = OpenAI(base_url=f"http://127.0.0.1:{os.environ['API_PORT']}/v1", api_key="none")
client.models.list()
PY
    sleep 5
  done
  ARGS+=(--api-base "http://127.0.0.1:${API_PORT}/v1")
fi

python scripts/run_theorem3_real_generation.py "${ARGS[@]}"
python scripts/report_theorem3_real_generation.py \
  --results-file "${RUN_OUTPUT_DIR}/theorem3_real_generation_results.json" \
  --output-dir "${RUN_OUTPUT_DIR}/theorem3_report"

if [[ "${CONDITIONS}" == *"closed_book"* ]]; then
  python scripts/analyze_theorem3_controls.py \
    --rows-jsonl "${RUN_OUTPUT_DIR}/theorem3_generation_rows.jsonl" \
    --model "${MODEL}" \
    --output "${RUN_OUTPUT_DIR}/theorem3_control_analysis.json"
fi
