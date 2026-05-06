#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH -J pilot_delta
#SBATCH -o logs/pilot_delta_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

cd /u/adas17/tts-falsification
nvidia-smi -L || true

python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --port 8000 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  > logs/vllm_pilot_${SLURM_JOB_ID}.log 2>&1 &
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

python src/evaluate.py \
  --benchmark humaneval_plus \
  --methods greedy,majority_vote,falsification,oracle \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --backend openai \
  --api-base http://127.0.0.1:8000/v1 \
  --n-candidates 16 \
  --n-falsification-rounds 2 \
  --temperature 0.7 \
  --seed 42 \
  --max-problems 8 \
  --output-dir results/pilot_delta
