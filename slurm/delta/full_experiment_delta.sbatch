#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH -J full_delta
#SBATCH -o logs/full_delta_%j.out

set -euo pipefail

module load python/anaconda3/2.10.0
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}
source "${DELTA_VENV}/bin/activate"
export HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}
MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
BENCHMARKS=${BENCHMARKS:-humaneval_plus,mbpp_plus,livecodebench_v6,math500}
METHODS=${METHODS:-greedy,majority_vote,self_debug,falsification,oracle}
OUTPUT_DIR=${OUTPUT_DIR:-results/full_delta}
SEEDS=${SEEDS:-42,43,44}
MAX_PROBLEMS=${MAX_PROBLEMS:-16}
N_CANDIDATES=${N_CANDIDATES:-8}
N_ROUNDS=${N_ROUNDS:-2}
MAX_TIEBREAK_ROUNDS=${MAX_TIEBREAK_ROUNDS:-4}
DELTA_PARAM=${DELTA_PARAM:-0.05}
ALPHA=${ALPHA:-0.05}
TIMEOUT=${TIMEOUT:-10}
TEMPERATURE=${TEMPERATURE:-0.7}
MAX_TOKENS=${MAX_TOKENS:-512}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-16384}
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION:-0.90}
TP_SIZE=${TP_SIZE:-1}
PROBLEM_OFFSET=${PROBLEM_OFFSET:-0}
BACKEND=${BACKEND:-openai}
API_PORT=${API_PORT:-$((20000 + (${SLURM_JOB_ID:-0} % 20000)))}
PROBE_STRATEGY=${PROBE_STRATEGY:-adaptive_population}
ADAPTIVE_PROBE_SELECTION=${ADAPTIVE_PROBE_SELECTION:-true}
ENFORCE_ROUND_FAMILY_DIVERSITY=${ENFORCE_ROUND_FAMILY_DIVERSITY:-true}
ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION:-true}
CONFIDENCE_MODE=${CONFIDENCE_MODE:-wealth}
MAX_DIFFERENTIAL_PROBES=${MAX_DIFFERENTIAL_PROBES:-8}
CONSENSUS_MIN_FRACTION=${CONSENSUS_MIN_FRACTION:-0.70}
CONSENSUS_MIN_MARGIN=${CONSENSUS_MIN_MARGIN:-2}
CONSENSUS_MIN_VOTES=${CONSENSUS_MIN_VOTES:-3}
DATA_ROOT=${DATA_ROOT:-data}

# Slurm's --export option uses commas as separators, so callers can pass
# colon-delimited lists (for example SEEDS=42:43:44) and we normalize here.
BENCHMARKS=${BENCHMARKS//:/,}
METHODS=${METHODS//:/,}
SEEDS=${SEEDS//:/,}

cd /u/adas17/tts-falsification
nvidia-smi -L || true

EVAL_ARGS=(
  --benchmarks "${BENCHMARKS}" \
  --methods "${METHODS}" \
  --model "${MODEL}" \
  --backend "${BACKEND}" \
  --n-candidates "${N_CANDIDATES}" \
  --n-falsification-rounds "${N_ROUNDS}" \
  --max-tiebreak-rounds "${MAX_TIEBREAK_ROUNDS}" \
  --delta "${DELTA_PARAM}" \
  --alpha "${ALPHA}" \
  --timeout "${TIMEOUT}" \
  --temperature "${TEMPERATURE}" \
  --max-tokens "${MAX_TOKENS}" \
  --probe-strategy "${PROBE_STRATEGY}" \
  --confidence-mode "${CONFIDENCE_MODE}" \
  --max-differential-probes "${MAX_DIFFERENTIAL_PROBES}" \
  --consensus-min-fraction "${CONSENSUS_MIN_FRACTION}" \
  --consensus-min-margin "${CONSENSUS_MIN_MARGIN}" \
  --consensus-min-votes "${CONSENSUS_MIN_VOTES}" \
  --seeds "${SEEDS}" \
  --max-problems "${MAX_PROBLEMS}" \
  --problem-offset "${PROBLEM_OFFSET}" \
  --tp-size "${TP_SIZE}" \
  --data-root "${DATA_ROOT}" \
  --output-dir "${OUTPUT_DIR}" \
  --resume
)

case "${ADAPTIVE_PROBE_SELECTION,,}" in
  1|true|yes|on) EVAL_ARGS+=(--adaptive-probe-selection) ;;
  0|false|no|off) EVAL_ARGS+=(--no-adaptive-probe-selection) ;;
  *) echo "Invalid ADAPTIVE_PROBE_SELECTION=${ADAPTIVE_PROBE_SELECTION}" >&2; exit 1 ;;
esac

case "${ENFORCE_ROUND_FAMILY_DIVERSITY,,}" in
  1|true|yes|on) EVAL_ARGS+=(--enforce-round-family-diversity) ;;
  0|false|no|off) EVAL_ARGS+=(--no-enforce-round-family-diversity) ;;
  *) echo "Invalid ENFORCE_ROUND_FAMILY_DIVERSITY=${ENFORCE_ROUND_FAMILY_DIVERSITY}" >&2; exit 1 ;;
esac

case "${ELIMINATE_ON_DETECTION,,}" in
  1|true|yes|on) EVAL_ARGS+=(--eliminate-on-detection) ;;
  0|false|no|off) EVAL_ARGS+=(--no-eliminate-on-detection) ;;
  *) echo "Invalid ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION}" >&2; exit 1 ;;
esac

if [[ "${BACKEND}" == "openai" ]]; then
  python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size "${TP_SIZE}" \
    --port "${API_PORT}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    > logs/vllm_full_${SLURM_JOB_ID}.log 2>&1 &
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
  EVAL_ARGS+=(--api-base "http://127.0.0.1:${API_PORT}/v1")
else
  python - <<'PY'
import importlib.util

missing = [name for name in ("torch", "transformers") if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit(f"Missing required packages for backend=transformers: {missing}")
PY
fi

python src/evaluate.py "${EVAL_ARGS[@]}"
