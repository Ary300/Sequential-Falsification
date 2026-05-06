#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4-interactive
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH -J report_delta
#SBATCH -o logs/report_delta_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"

RESULTS_FILE=${RESULTS_FILE:-results/full_delta/results.json}
OUTPUT_DIR=${OUTPUT_DIR:-figures/full_delta}
PROGRESS_DIR=${PROGRESS_DIR:-$(dirname "${RESULTS_FILE}")}

cd /u/adas17/tts-falsification
if [ ! -s "${RESULTS_FILE}" ]; then
  mkdir -p "${PROGRESS_DIR}"
  RESULTS_FILE="${PROGRESS_DIR}/results_from_progress.json"
  python src/collect_progress.py \
    --progress-dir "${PROGRESS_DIR}" \
    --output-file "${RESULTS_FILE}"
fi

python src/report.py \
  --results-file "${RESULTS_FILE}" \
  --output-dir "${OUTPUT_DIR}"
