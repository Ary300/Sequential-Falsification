#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=96
#SBATCH --time=48:00:00
#SBATCH -J full_exp
#SBATCH -o logs/full_%j.out

set -euo pipefail

module purge
module load modtree/gpu
module load conda
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate tts
PYTHON_BIN="$(conda info --base)/envs/tts/bin/python"
export HF_HOME=${HF_HOME:-$HOME/.cache/huggingface}

"${PYTHON_BIN}" src/run_full_pipeline.py \
  --config src/configs/experiments.yaml \
  --output-root results/full
