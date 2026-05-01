#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH -J t3_attnint
#SBATCH -o logs/theorem3_attention_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification}
DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_attention_intervention_r1_14b_conflict}
ROWS_JSONL=${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/results/theorem3_tierA_r1_qwen14_seed42/theorem3_generation_rows.jsonl}
MODEL_NAME=${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}
BENCHMARK=${BENCHMARK:-conflictbank}
CONDITION=${CONDITION:-conflict_context}
COT_LENGTHS=${COT_LENGTHS:-0,128,1024}
MAX_ROWS_PER_COT=${MAX_ROWS_PER_COT:-100}
MAX_NEW_TOKENS=${MAX_NEW_TOKENS:-96}
MAX_LENGTH=${MAX_LENGTH:-4096}
SEED=${SEED:-42}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

if [[ "${OUTPUT_DIR}" = /* ]]; then
  RUN_OUTPUT_DIR="${OUTPUT_DIR}"
else
  RUN_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${OUTPUT_DIR}"
fi
mkdir -p "${RUN_OUTPUT_DIR}"

python scripts/run_theorem3_attention_intervention.py \
  --rows-jsonl "${ROWS_JSONL}" \
  --output-dir "${RUN_OUTPUT_DIR}" \
  --model-name "${MODEL_NAME}" \
  --benchmark "${BENCHMARK}" \
  --condition "${CONDITION}" \
  --cot-lengths "${COT_LENGTHS}" \
  --max-rows-per-cot "${MAX_ROWS_PER_COT}" \
  --max-new-tokens "${MAX_NEW_TOKENS}" \
  --max-length "${MAX_LENGTH}" \
  --seed "${SEED}"
