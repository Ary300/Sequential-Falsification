#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:30:00
#SBATCH -J test_vllm_delta
#SBATCH -o logs/test_vllm_delta_%j.out

module load python/anaconda3/2.10.0
source /u/adas17/venvs/tts-delta/bin/activate

nvidia-smi -L || true

python - <<'PY'
import importlib
import torch

print("cuda_available", torch.cuda.is_available())
print("cuda_device_count", torch.cuda.device_count())
mods = ["torch", "transformers", "evalplus", "matplotlib", "vllm"]
for m in mods:
    try:
        importlib.import_module(m)
        print(m, "OK")
    except Exception as exc:
        print(m, type(exc).__name__, exc)
PY
