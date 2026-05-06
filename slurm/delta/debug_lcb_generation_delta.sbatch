#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH -J debug_lcb_generation
#SBATCH -o logs/debug_lcb_generation_%j.out

module load python/anaconda3/2.10.0
source /u/adas17/venvs/tts-delta/bin/activate
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
OUTPUT_FILE=${OUTPUT_FILE:-results/livecodebench_debug/debug_${SLURM_JOB_ID}.json}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}

cd /u/adas17/tts-falsification
export PYTHONPATH=/u/adas17/tts-falsification:${PYTHONPATH:-}
nvidia-smi -L || true

python -m vllm.entrypoints.openai.api_server \
  --model "${MODEL}" \
  --port 8000 \
  --max-model-len "${MAX_MODEL_LEN}" \
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
  > logs/vllm_debug_lcb_${SLURM_JOB_ID}.log 2>&1 &
VLLM_PID=$!
trap 'kill ${VLLM_PID} >/dev/null 2>&1 || true' EXIT

for _ in $(seq 1 60); do
  python - <<'PY' >/dev/null 2>&1 && break
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="none")
client.models.list()
PY
  sleep 5
done

python scripts/debug_lcb_generation.py \
  --api-base http://127.0.0.1:8000/v1 \
  --model "${MODEL}" \
  --output-file "${OUTPUT_FILE}"
