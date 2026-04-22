#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH -J bootstrap_tts
#SBATCH -o logs/bootstrap_%j.out

module purge
module load modtree/gpu
module load conda
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

if ! conda env list | awk '{print $1}' | grep -qx "tts"; then
  rm -rf "$(conda info --base)/envs/tts"
  conda create -n tts python=3.10 -y
fi

if [ ! -x "$(conda info --base)/envs/tts/bin/python" ]; then
  rm -rf "$(conda info --base)/envs/tts"
  conda create -n tts python=3.10 -y
fi

conda activate tts
PYTHON_BIN="$(conda info --base)/envs/tts/bin/python"
"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install "vllm>=0.19.0" "transformers>=4.45.0" "sglang>=0.4.0"
"${PYTHON_BIN}" -m pip install "evalplus>=0.3.1" "evalplus[vllm]" "lm-eval>=0.4.7"
"${PYTHON_BIN}" -m pip install "confseq>=0.0.11" "scipy>=1.11.0" "numpy>=1.24.0"
"${PYTHON_BIN}" -m pip install "RestrictedPython>=7.0"
"${PYTHON_BIN}" -m pip install "matplotlib>=3.8.0" "SciencePlots>=2.1.0" "seaborn>=0.13.0" "pandas>=2.1.0"
"${PYTHON_BIN}" -m pip install arxiv-latex-cleaner
