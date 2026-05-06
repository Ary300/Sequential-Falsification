#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=06:00:00
#SBATCH -J t3_tracesep
#SBATCH -o logs/theorem3_trace_separation_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}
ROWS_JSONL=${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl}
OUTPUT_PREFIX=${OUTPUT_PREFIX:-/work/nvme/bgvi/adas17/tts_results/theorem3_trace_separation_r1_14b_conflictbank_conflict}
BENCHMARK=${BENCHMARK:-conflictbank}
CONDITION=${CONDITION:-conflict_context}
COT_LENGTH=${COT_LENGTH:-1024}
MAX_EXAMPLES=${MAX_EXAMPLES:-100}
SEED=${SEED:-42}
BATCH_SIZE=${BATCH_SIZE:-1}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}
LONG_COT_STYLE=${LONG_COT_STYLE:-1024}
DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

python scripts/run_theorem3_trace_separation_check.py \
  --rows-jsonl "${ROWS_JSONL}" \
  --output-prefix "${OUTPUT_PREFIX}" \
  --model "${MODEL}" \
  --benchmark "${BENCHMARK}" \
  --condition "${CONDITION}" \
  --cot-length "${COT_LENGTH}" \
  --max-examples "${MAX_EXAMPLES}" \
  --seed "${SEED}" \
  --batch-size "${BATCH_SIZE}" \
  --torch-dtype "${TORCH_DTYPE}" \
  --long-cot-style "${LONG_COT_STYLE}"
