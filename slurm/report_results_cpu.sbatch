#!/bin/bash
#SBATCH -A bio260046
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH -J report_cpu
#SBATCH -o logs/report_cpu_%j.out

set -euo pipefail

module purge
module load conda
ANVIL_RUNTIME_ROOT=${ANVIL_RUNTIME_ROOT:-${CLUSTER_SCRATCH:-/anvil/scratch/${USER}}/tts-runtime}
ANVIL_HOME=${ANVIL_HOME:-${ANVIL_RUNTIME_ROOT}/home}
ANVIL_CONDA_ENV=${ANVIL_CONDA_ENV:-${ANVIL_RUNTIME_ROOT}/conda-envs/tts}
mkdir -p "${ANVIL_HOME}"
export HOME="${ANVIL_HOME}"
export PYTHONNOUSERSITE=1
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "${ANVIL_CONDA_ENV}"
PYTHON_BIN="${ANVIL_CONDA_ENV}/bin/python"

RESULTS_FILE=${RESULTS_FILE:-results/anvil_full/results.json}
OUTPUT_DIR=${OUTPUT_DIR:-figures/anvil_full}
PROGRESS_DIR=${PROGRESS_DIR:-$(dirname "${RESULTS_FILE}")}

cd /anvil/projects/x-bio260046/tts-falsification
if [ ! -s "${RESULTS_FILE}" ]; then
  mkdir -p "${PROGRESS_DIR}"
  RESULTS_FILE="${PROGRESS_DIR}/results_from_progress.json"
  "${PYTHON_BIN}" src/collect_progress.py \
    --progress-dir "${PROGRESS_DIR}" \
    --output-file "${RESULTS_FILE}"
fi

"${PYTHON_BIN}" src/report.py \
  --results-file "${RESULTS_FILE}" \
  --output-dir "${OUTPUT_DIR}"
