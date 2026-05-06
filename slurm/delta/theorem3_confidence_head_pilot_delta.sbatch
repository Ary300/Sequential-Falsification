#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH -J t3_confhead
#SBATCH -o logs/t3_confhead_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification}
DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
ROWS_JSONL=${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/theorem3_real_generation_r1_14b_v3/theorem3_generation_rows.jsonl,/work/nvme/bgvi/adas17/tts_results/theorem3_closedbook_control_r1_14b_v1/theorem3_generation_rows.jsonl}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_confidence_head_pilot_r1_14b_v1}
MODEL_NAME=${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}
MAX_TRAIN_ROWS=${MAX_TRAIN_ROWS:-1200}
MAX_VAL_ROWS=${MAX_VAL_ROWS:-200}
MAX_EVAL_ROWS=${MAX_EVAL_ROWS:-500}
TRAIN_BENCHMARKS=${TRAIN_BENCHMARKS:-wikicontradict,conflictbank}
EVAL_BENCHMARK=${EVAL_BENCHMARK:-conflictbank}
EVAL_CONDITION=${EVAL_CONDITION:-conflict_context}
EVAL_COT_LENGTH=${EVAL_COT_LENGTH:-1024}
MAX_LENGTH=${MAX_LENGTH:-1024}
FEATURE_BATCH_SIZE=${FEATURE_BATCH_SIZE:-2}
EPOCHS=${EPOCHS:-12}
LR=${LR:-0.002}
WEIGHT_DECAY=${WEIGHT_DECAY:-0.0001}
SEED=${SEED:-42}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}

cd "${DELTA_PROJECT_ROOT}"
if [[ "${OUTPUT_DIR}" = /* ]]; then
  RUN_OUTPUT_DIR="${OUTPUT_DIR}"
else
  RUN_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${OUTPUT_DIR}"
fi
mkdir -p "${RUN_OUTPUT_DIR}"

python scripts/run_theorem3_confidence_head_pilot.py \
  --rows-jsonl "${ROWS_JSONL}" \
  --output-dir "${RUN_OUTPUT_DIR}" \
  --model-name "${MODEL_NAME}" \
  --max-train-rows "${MAX_TRAIN_ROWS}" \
  --max-val-rows "${MAX_VAL_ROWS}" \
  --max-eval-rows "${MAX_EVAL_ROWS}" \
  --train-benchmarks "${TRAIN_BENCHMARKS}" \
  --eval-benchmark "${EVAL_BENCHMARK}" \
  --eval-condition "${EVAL_CONDITION}" \
  --eval-cot-length "${EVAL_COT_LENGTH}" \
  --max-length "${MAX_LENGTH}" \
  --feature-batch-size "${FEATURE_BATCH_SIZE}" \
  --epochs "${EPOCHS}" \
  --lr "${LR}" \
  --weight-decay "${WEIGHT_DECAY}" \
  --seed "${SEED}" \
  --torch-dtype "${TORCH_DTYPE}"
