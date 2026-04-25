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
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
BACKEND=${BACKEND:-openai}
REQUEST_TIMEOUT=${REQUEST_TIMEOUT:-600}
TEMPERATURE=${TEMPERATURE:-0.0}
TOP_P=${TOP_P:-1.0}
SEED=${SEED:-42}
API_PORT=${API_PORT:-$((20000 + (${SLURM_JOB_ID:-0} % 20000)))}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}
TP_SIZE=${TP_SIZE:-1}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_real_generation_r1_7b}
DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
WIKICONTRADICT_MAX=${WIKICONTRADICT_MAX:-200}
CONFLICTBANK_MAX=${CONFLICTBANK_MAX:-500}
CONFLICTBANK_SCREENING_POOL=${CONFLICTBANK_SCREENING_POOL:-1200}
AMBIGUITY_LOW=${AMBIGUITY_LOW:-0.2}
AMBIGUITY_HIGH=${AMBIGUITY_HIGH:-0.8}
DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

if [[ "${OUTPUT_DIR}" = /* ]]; then
  RUN_OUTPUT_DIR="${OUTPUT_DIR}"
else
  RUN_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${OUTPUT_DIR}"
fi
mkdir -p "${RUN_OUTPUT_DIR}"

ARGS=(
  --output-dir "${RUN_OUTPUT_DIR}" \
  --backend "${BACKEND}" \
  --model "${MODEL}" \
  --request-timeout "${REQUEST_TIMEOUT}" \
  --temperature "${TEMPERATURE}" \
  --top-p "${TOP_P}" \
  --seed "${SEED}" \
  --wikicontradict-max "${WIKICONTRADICT_MAX}" \
  --conflictbank-max "${CONFLICTBANK_MAX}" \
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
  trap 'kill ${VLLM_PID} >/dev/null 2>&1 || true' EXIT

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
