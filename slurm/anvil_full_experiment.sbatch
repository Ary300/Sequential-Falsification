#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=48:00:00
#SBATCH -J anvil_full
#SBATCH -o logs/anvil_full_%j.out

set -euo pipefail

module purge
module load modtree/gpu
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

export HF_HOME=${HF_HOME:-/anvil/projects/x-bio260046/hf_cache}
MODEL=${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Qwen-7B}
BENCHMARKS=${BENCHMARKS:-humaneval_plus,mbpp_plus}
METHODS=${METHODS:-greedy,majority_vote,generated_test_filter,self_debug,falsification,oracle}
OUTPUT_DIR=${OUTPUT_DIR:-results/anvil_full}
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
PROBE_STRATEGY=${PROBE_STRATEGY:-adaptive_population}
ADAPTIVE_PROBE_SELECTION=${ADAPTIVE_PROBE_SELECTION:-true}
ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION:-true}
CONFIDENCE_MODE=${CONFIDENCE_MODE:-wealth}
DATA_ROOT=${DATA_ROOT:-data}

# Slurm export values may use colons to avoid comma splitting.
BENCHMARKS=${BENCHMARKS//:/,}
METHODS=${METHODS//:/,}
SEEDS=${SEEDS//:/,}

cd /anvil/projects/x-bio260046/tts-falsification
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

case "${ELIMINATE_ON_DETECTION,,}" in
  1|true|yes|on) EVAL_ARGS+=(--eliminate-on-detection) ;;
  0|false|no|off) EVAL_ARGS+=(--no-eliminate-on-detection) ;;
  *) echo "Invalid ELIMINATE_ON_DETECTION=${ELIMINATE_ON_DETECTION}" >&2; exit 1 ;;
esac

if [[ "${BACKEND}" == "openai" ]]; then
  "${PYTHON_BIN}" - <<'PY'
import importlib.util

if importlib.util.find_spec("vllm") is None:
    raise SystemExit("vllm is not installed in the active Anvil tts environment")
PY

  "${PYTHON_BIN}" -m vllm.entrypoints.openai.api_server \
    --model "${MODEL}" \
    --tensor-parallel-size "${TP_SIZE}" \
    --port 8000 \
    --max-model-len "${MAX_MODEL_LEN}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    > logs/vllm_anvil_${SLURM_JOB_ID}.log 2>&1 &
  VLLM_PID=$!
  trap 'kill ${VLLM_PID} >/dev/null 2>&1 || true' EXIT

  for _ in $(seq 1 60); do
    "${PYTHON_BIN}" - <<'PY' >/dev/null 2>&1 && break
from openai import OpenAI
client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="none")
client.models.list()
PY
    sleep 5
  done
  EVAL_ARGS+=(--api-base http://127.0.0.1:8000/v1)
else
  "${PYTHON_BIN}" - <<'PY'
import importlib.util

missing = [name for name in ("torch", "transformers") if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit(f"Missing required packages for backend=transformers: {missing}")
PY
fi

"${PYTHON_BIN}" src/evaluate.py "${EVAL_ARGS[@]}"
