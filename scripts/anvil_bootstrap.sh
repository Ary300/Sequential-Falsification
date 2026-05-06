#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

REMOTE_CMD=$(cat <<'EOF'
set -euo pipefail
mkdir -p "$ANVIL_PROJECT_ROOT"/{data,models,results,logs,figures,paper,checkpoints}
module purge
module load modtree/gpu
module load conda
mkdir -p "$ANVIL_HOME" "$(dirname "$ANVIL_CONDA_ENV")" "$ANVIL_CONDA_PKGS" "$ANVIL_PIP_CACHE"
export HOME="$ANVIL_HOME"
export CONDA_PKGS_DIRS="$ANVIL_CONDA_PKGS"
export PIP_CACHE_DIR="$ANVIL_PIP_CACHE"
export PYTHONNOUSERSITE=1
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"
if [ ! -d "$ANVIL_CONDA_ENV" ]; then
  rm -rf "$ANVIL_CONDA_ENV"
  conda create -p "$ANVIL_CONDA_ENV" python=3.10 -y
fi

if [ ! -x "$ANVIL_CONDA_ENV/bin/python" ]; then
  rm -rf "$ANVIL_CONDA_ENV"
  conda create -p "$ANVIL_CONDA_ENV" python=3.10 -y
fi

conda activate "$ANVIL_CONDA_ENV"
export PYTHON_BIN="$ANVIL_CONDA_ENV/bin/python"
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install "torch>=2.4,<2.6" --index-url https://download.pytorch.org/whl/cu121
"$PYTHON_BIN" -m pip install "transformers>=4.45.0" "accelerate>=1.0.0" "sglang>=0.4.0"
"$PYTHON_BIN" -m pip install "evalplus>=0.3.1" "lm-eval>=0.4.7" openai
"$PYTHON_BIN" -m pip install "confseq>=0.0.11" "scipy>=1.11.0" "numpy>=1.24.0"
"$PYTHON_BIN" -m pip install "RestrictedPython>=7.0"
"$PYTHON_BIN" -m pip install "matplotlib>=3.8.0" "SciencePlots>=2.1.0" "seaborn>=0.13.0" "pandas>=2.1.0"
"$PYTHON_BIN" -m pip install arxiv-latex-cleaner
EOF
)

anvil_ssh_base "export ANVIL_PROJECT_ROOT='${ANVIL_PROJECT_ROOT}' ANVIL_HOME='${ANVIL_HOME}' ANVIL_CONDA_ENV='${ANVIL_CONDA_ENV}' ANVIL_CONDA_PKGS='${ANVIL_CONDA_PKGS}' ANVIL_PIP_CACHE='${ANVIL_PIP_CACHE}' && ${REMOTE_CMD}"
