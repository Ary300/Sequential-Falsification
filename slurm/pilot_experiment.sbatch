#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=2
#SBATCH --cpus-per-task=48
#SBATCH --time=06:00:00
#SBATCH -J pilot_exp
#SBATCH -o logs/pilot_%j.out

set -euo pipefail

module purge
module load modtree/gpu
module load conda
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate tts
PYTHON_BIN="$(conda info --base)/envs/tts/bin/python"
export HF_HOME=${HF_HOME:-$HOME/.cache/huggingface}

"${PYTHON_BIN}" src/evaluate.py \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
  --benchmark humaneval_plus \
  --n-candidates 16 \
  --n-falsification-rounds 2 \
  --temperature 0.7 \
  --methods greedy,majority_vote,self_debug,falsification,oracle \
  --backend openai \
  --seed 42 \
  --tp-size 1 \
  --output-dir results/pilot
