#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=2
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH -J test_vllm
#SBATCH -o logs/test_vllm_%j.out

module purge
module load modtree/gpu
module load conda
source activate tts
export HF_HOME=${HF_HOME:-$HOME/.cache/huggingface}

python -m vllm.entrypoints.openai.api_server \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --tensor-parallel-size 1 \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.90 \
  --port 8000 &
SERVER_PID=$!
sleep 60

python - <<'PY'
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
resp = client.completions.create(
    model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    prompt="def fibonacci(n):\n",
    max_tokens=128,
    temperature=0.7,
    n=8,
)
print("received", len(resp.choices), "choices")
PY

kill $SERVER_PID
