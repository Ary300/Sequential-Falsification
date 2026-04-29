#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH -J theorem3_eta
#SBATCH -o logs/theorem3_eta_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}
ROWS_JSONL=${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl}
OUTPUT_PREFIX=${OUTPUT_PREFIX:-/work/nvme/bgvi/adas17/tts_results/theorem3_eta_tempered_r1_14b_conflictbank_conflict}
BENCHMARK=${BENCHMARK:-conflictbank}
CONDITION=${CONDITION:-conflict_context}
COT_LENGTH=${COT_LENGTH:-1024}
CALIBRATION_SIZE=${CALIBRATION_SIZE:-200}
SEED=${SEED:-42}
MAX_EXAMPLES=${MAX_EXAMPLES:-}
BATCH_SIZE=${BATCH_SIZE:-4}
ETA_GRID=${ETA_GRID:-0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}
DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

ARGS=(
  --rows-jsonl "${ROWS_JSONL}"
  --output-prefix "${OUTPUT_PREFIX}"
  --model "${MODEL}"
  --benchmark "${BENCHMARK}"
  --condition "${CONDITION}"
  --cot-length "${COT_LENGTH}"
  --calibration-size "${CALIBRATION_SIZE}"
  --seed "${SEED}"
  --batch-size "${BATCH_SIZE}"
  --eta-grid "${ETA_GRID}"
  --torch-dtype "${TORCH_DTYPE}"
)

if [[ -n "${MAX_EXAMPLES}" ]]; then
  ARGS+=(--max-examples "${MAX_EXAMPLES}")
fi

python scripts/run_theorem3_eta_tempered_decoding.py "${ARGS[@]}"
