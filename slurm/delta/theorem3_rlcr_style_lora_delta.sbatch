#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --time=20:00:00
#SBATCH -J t3_rlcr14
#SBATCH -o logs/theorem3_rlcr_style_lora_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}

DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification-git}
ROWS_JSONL=${ROWS_JSONL:-/work/nvme/bgvi/adas17/tts_results/results/theorem3_tierA_r1_qwen14_seed42/theorem3_generation_rows.jsonl}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_rlcr_style_lora_r1_14b_conflict}
MODEL_NAME=${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Qwen-14B}
TRAIN_BENCHMARK=${TRAIN_BENCHMARK:-conflictbank}
TRAIN_CONDITION=${TRAIN_CONDITION:-conflict_context}
EVAL_BENCHMARK=${EVAL_BENCHMARK:-conflictbank}
EVAL_CONDITION=${EVAL_CONDITION:-conflict_context}
EVAL_COT_LENGTH=${EVAL_COT_LENGTH:-1024}
MAX_TRAIN_ROWS=${MAX_TRAIN_ROWS:-1200}
MAX_VAL_ROWS=${MAX_VAL_ROWS:-200}
MAX_EVAL_ROWS=${MAX_EVAL_ROWS:-500}
MAX_LENGTH=${MAX_LENGTH:-1024}
FEATURE_BATCH_SIZE=${FEATURE_BATCH_SIZE:-2}
WARMSTART_EPOCHS=${WARMSTART_EPOCHS:-1}
EPOCHS=${EPOCHS:-3}
LR=${LR:-0.00005}
HEAD_LR=${HEAD_LR:-0.0005}
WEIGHT_DECAY=${WEIGHT_DECAY:-0.0001}
ANSWER_LOSS_WEIGHT=${ANSWER_LOSS_WEIGHT:-1.0}
CONFIDENCE_LOSS_WEIGHT=${CONFIDENCE_LOSS_WEIGHT:-1.0}
LORA_RANK=${LORA_RANK:-8}
LORA_ALPHA=${LORA_ALPHA:-16}
LORA_DROPOUT=${LORA_DROPOUT:-0.05}
SEED=${SEED:-42}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}
DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
RUN_THEOREM3_EVAL=${RUN_THEOREM3_EVAL:-1}
EVAL_OUTPUT_DIR=${EVAL_OUTPUT_DIR:-}
EVAL_BENCHMARKS=${EVAL_BENCHMARKS:-wikicontradict,conflictbank}
EVAL_CONDITIONS=${EVAL_CONDITIONS:-aligned_context,conflict_context}
EVAL_COT_LENGTHS=${EVAL_COT_LENGTHS:-0,128,1024}
EVAL_WIKICONTRADICT_MAX=${EVAL_WIKICONTRADICT_MAX:-96}
EVAL_CONFLICTBANK_MAX=${EVAL_CONFLICTBANK_MAX:-128}
EVAL_TRIVIAQA_MAX=${EVAL_TRIVIAQA_MAX:-0}

cd "${DELTA_PROJECT_ROOT}"
nvidia-smi -L || true

if [[ "${OUTPUT_DIR}" = /* ]]; then
  RUN_OUTPUT_DIR="${OUTPUT_DIR}"
else
  RUN_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${OUTPUT_DIR}"
fi
mkdir -p "${RUN_OUTPUT_DIR}"

python scripts/run_theorem3_rlcr_style_lora.py \
  --rows-jsonl "${ROWS_JSONL}" \
  --output-dir "${RUN_OUTPUT_DIR}" \
  --model-name "${MODEL_NAME}" \
  --train-benchmark "${TRAIN_BENCHMARK}" \
  --train-condition "${TRAIN_CONDITION}" \
  --eval-benchmark "${EVAL_BENCHMARK}" \
  --eval-condition "${EVAL_CONDITION}" \
  --eval-cot-length "${EVAL_COT_LENGTH}" \
  --max-train-rows "${MAX_TRAIN_ROWS}" \
  --max-val-rows "${MAX_VAL_ROWS}" \
  --max-eval-rows "${MAX_EVAL_ROWS}" \
  --max-length "${MAX_LENGTH}" \
  --feature-batch-size "${FEATURE_BATCH_SIZE}" \
  --warmstart-epochs "${WARMSTART_EPOCHS}" \
  --epochs "${EPOCHS}" \
  --lr "${LR}" \
  --head-lr "${HEAD_LR}" \
  --weight-decay "${WEIGHT_DECAY}" \
  --answer-loss-weight "${ANSWER_LOSS_WEIGHT}" \
  --confidence-loss-weight "${CONFIDENCE_LOSS_WEIGHT}" \
  --lora-rank "${LORA_RANK}" \
  --lora-alpha "${LORA_ALPHA}" \
  --lora-dropout "${LORA_DROPOUT}" \
  --seed "${SEED}" \
  --torch-dtype "${TORCH_DTYPE}"

if [[ "${RUN_THEOREM3_EVAL}" == "1" ]]; then
  API_PORT=$((20000 + (${SLURM_JOB_ID:-0} % 20000)))
  MERGED_MODEL_DIR="${RUN_OUTPUT_DIR}/merged_model"
  if [[ -z "${EVAL_OUTPUT_DIR}" ]]; then
    RUN_EVAL_OUTPUT_DIR="${RUN_OUTPUT_DIR}/theorem3_eval"
  elif [[ "${EVAL_OUTPUT_DIR}" = /* ]]; then
    RUN_EVAL_OUTPUT_DIR="${EVAL_OUTPUT_DIR}"
  else
    RUN_EVAL_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${EVAL_OUTPUT_DIR}"
  fi
  mkdir -p "${RUN_EVAL_OUTPUT_DIR}"
  python -m vllm.entrypoints.openai.api_server \
    --model "${MERGED_MODEL_DIR}" \
    --generation-config vllm \
    --tensor-parallel-size 1 \
    --port "${API_PORT}" \
    --max-model-len 12288 \
    --gpu-memory-utilization 0.9 \
    > logs/vllm_rlcr_${SLURM_JOB_ID}.log 2>&1 &
  VLLM_PID=$!
  trap 'kill ${VLLM_PID} >/dev/null 2>&1 || true' EXIT

  for _ in $(seq 1 60); do
    python - <<'PY' >/dev/null 2>&1 && break
from openai import OpenAI
import os
client = OpenAI(base_url=f"http://127.0.0.1:{os.environ['API_PORT']}/v1", api_key="none")
client.models.list()
PY
    sleep 5
  done

  python scripts/run_theorem3_real_generation.py \
    --output-dir "${RUN_EVAL_OUTPUT_DIR}" \
    --backend openai \
    --model "${MERGED_MODEL_DIR}" \
    --api-base "http://127.0.0.1:${API_PORT}/v1" \
    --api-key none \
    --request-timeout 600 \
    --temperature 0.0 \
    --top-p 1.0 \
    --seed "${SEED}" \
    --benchmarks "${EVAL_BENCHMARKS}" \
    --conditions "${EVAL_CONDITIONS}" \
    --wikicontradict-max "${EVAL_WIKICONTRADICT_MAX}" \
    --conflictbank-max "${EVAL_CONFLICTBANK_MAX}" \
    --triviaqa-max "${EVAL_TRIVIAQA_MAX}" \
    --cot-lengths "${EVAL_COT_LENGTHS}"

  python scripts/report_theorem3_real_generation.py \
    --results-file "${RUN_EVAL_OUTPUT_DIR}/theorem3_real_generation_results.json" \
    --output-dir "${RUN_EVAL_OUTPUT_DIR}/theorem3_report"
fi
