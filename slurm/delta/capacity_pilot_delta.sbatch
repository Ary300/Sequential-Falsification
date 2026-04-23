#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH -J capacity_delta
#SBATCH -o logs/capacity_delta_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
BENCHMARKS=${BENCHMARKS:-humaneval_plus,mbpp_plus}
VERIFIERS=${VERIFIERS:-majority,public_test,sce_trace}
OUTPUT_DIR=${OUTPUT_DIR:-results/capacity_pilot_delta}
BACKEND=${BACKEND:-openai}
SEED=${SEED:-42}
N_CANDIDATES=${N_CANDIDATES:-16}
MAX_PROBLEMS=${MAX_PROBLEMS:-32}
TIMEOUT=${TIMEOUT:-10}
TEMPERATURE=${TEMPERATURE:-0.7}
MAX_TOKENS=${MAX_TOKENS:-512}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}
TP_SIZE=${TP_SIZE:-1}
API_PORT=${API_PORT:-$((20000 + (${SLURM_JOB_ID:-0} % 20000)))}
DATA_ROOT=${DATA_ROOT:-data}

BENCHMARKS=${BENCHMARKS//:/,}
VERIFIERS=${VERIFIERS//:/,}

cd /u/adas17/tts-falsification
nvidia-smi -L || true

ARGS=(
  --benchmarks "${BENCHMARKS}" \
  --verifiers "${VERIFIERS}" \
  --backend "${BACKEND}" \
  --model "${MODEL}" \
  --seed "${SEED}" \
  --n-candidates "${N_CANDIDATES}" \
  --max-problems "${MAX_PROBLEMS}" \
  --timeout "${TIMEOUT}" \
  --temperature "${TEMPERATURE}" \
  --max-tokens "${MAX_TOKENS}" \
  --data-root "${DATA_ROOT}" \
  --output-dir "${OUTPUT_DIR}"
)

if [[ "${BACKEND}" == "openai" ]]; then
  python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size "${TP_SIZE}" \
    --port "${API_PORT}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    > logs/vllm_capacity_${SLURM_JOB_ID}.log 2>&1 &
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

python scripts/estimate_capacity.py "${ARGS[@]}"
