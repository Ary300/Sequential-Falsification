#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=18:00:00
#SBATCH -J t3_matchobj
#SBATCH -o logs/theorem3_matched_objective_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
if [[ ! -f "${DELTA_VENV}/bin/activate" ]]; then
  for candidate in "/u/${USER}/venvs/tts-delta" "/u/${USER}/.venvs/tts-delta"; do
    if [[ -f "${candidate}/bin/activate" ]]; then
      DELTA_VENV="${candidate}"
      break
    fi
  done
fi
if [[ ! -f "${DELTA_VENV}/bin/activate" ]]; then
  echo "Delta venv not found: ${DELTA_VENV}" >&2
  exit 1
fi
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}
export XDG_CACHE_HOME=${XDG_CACHE_HOME:-/work/nvme/bgvi/adas17/.cache}
export XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-/work/nvme/bgvi/adas17/.config}
export VLLM_CACHE_ROOT=${VLLM_CACHE_ROOT:-${XDG_CACHE_HOME}/vllm}
export VLLM_CONFIG_ROOT=${VLLM_CONFIG_ROOT:-${XDG_CONFIG_HOME}/vllm}
export VLLM_NO_USAGE_STATS=${VLLM_NO_USAGE_STATS:-1}
export VLLM_DO_NOT_TRACK=${VLLM_DO_NOT_TRACK:-1}
export DO_NOT_TRACK=${DO_NOT_TRACK:-1}

DELTA_PROJECT_ROOT=${DELTA_PROJECT_ROOT:-/u/adas17/tts-falsification-git}
DELTA_RESULTS_ROOT=${DELTA_RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
OBJECTIVE=${OBJECTIVE:-dpo}
OUTPUT_DIR=${OUTPUT_DIR:-results/theorem3_matched_objective_qwen14_dpo}
MODEL_NAME=${MODEL_NAME:-Qwen/Qwen2.5-14B}
BENCHMARK=${BENCHMARK:-conflictbank}
MAX_SOURCE_ROWS=${MAX_SOURCE_ROWS:-1200}
MAX_TRAIN_ROWS=${MAX_TRAIN_ROWS:-800}
MAX_VAL_ROWS=${MAX_VAL_ROWS:-120}
MAX_EVAL_ROWS=${MAX_EVAL_ROWS:-120}
MAX_PROMPT_LENGTH=${MAX_PROMPT_LENGTH:-768}
MAX_ANSWER_LENGTH=${MAX_ANSWER_LENGTH:-24}
EPOCHS=${EPOCHS:-1}
LR=${LR:-0.00005}
WEIGHT_DECAY=${WEIGHT_DECAY:-0.0001}
BETA=${BETA:-0.1}
GROUP_SIZE=${GROUP_SIZE:-4}
TEMPERATURE=${TEMPERATURE:-0.8}
TOP_P=${TOP_P:-0.95}
LORA_RANK=${LORA_RANK:-8}
LORA_ALPHA=${LORA_ALPHA:-16}
LORA_DROPOUT=${LORA_DROPOUT:-0.05}
SEED=${SEED:-42}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}
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
mkdir -p "${HF_HOME}" "${XDG_CACHE_HOME}" "${XDG_CONFIG_HOME}" "${VLLM_CACHE_ROOT}" "${VLLM_CONFIG_ROOT}"

if [[ "${OUTPUT_DIR}" = /* ]]; then
  RUN_OUTPUT_DIR="${OUTPUT_DIR}"
else
  RUN_OUTPUT_DIR="${DELTA_RESULTS_ROOT%/}/${OUTPUT_DIR}"
fi
mkdir -p "${RUN_OUTPUT_DIR}"

python scripts/run_theorem3_matched_objective_lora.py \
  --objective "${OBJECTIVE}" \
  --model-name "${MODEL_NAME}" \
  --output-dir "${RUN_OUTPUT_DIR}" \
  --benchmark "${BENCHMARK}" \
  --max-source-rows "${MAX_SOURCE_ROWS}" \
  --max-train-rows "${MAX_TRAIN_ROWS}" \
  --max-val-rows "${MAX_VAL_ROWS}" \
  --max-eval-rows "${MAX_EVAL_ROWS}" \
  --max-prompt-length "${MAX_PROMPT_LENGTH}" \
  --max-answer-length "${MAX_ANSWER_LENGTH}" \
  --epochs "${EPOCHS}" \
  --lr "${LR}" \
  --weight-decay "${WEIGHT_DECAY}" \
  --beta "${BETA}" \
  --group-size "${GROUP_SIZE}" \
  --temperature "${TEMPERATURE}" \
  --top-p "${TOP_P}" \
  --lora-rank "${LORA_RANK}" \
  --lora-alpha "${LORA_ALPHA}" \
  --lora-dropout "${LORA_DROPOUT}" \
  --seed "${SEED}" \
  --torch-dtype "${TORCH_DTYPE}"

if [[ "${RUN_THEOREM3_EVAL}" == "1" ]]; then
  API_PORT=$((20000 + (${SLURM_JOB_ID:-0} % 20000)))
  export API_PORT
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
    > logs/vllm_matchobj_${SLURM_JOB_ID}.log 2>&1 &
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
