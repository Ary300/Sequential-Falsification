#!/bin/bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/u/adas17/tts-falsification-git}
RESULTS_ROOT=${RESULTS_ROOT:-/work/hdd/bgvi/adas17/tts_results}
HF_HOME=${HF_HOME:-${RESULTS_ROOT}/runtime_cache/hf_cache}
XDG_CACHE_HOME=${XDG_CACHE_HOME:-${RESULTS_ROOT}/runtime_cache/xdg_cache}
XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-${RESULTS_ROOT}/runtime_cache/xdg_config}
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}

latest_dir() {
  local pattern="$1"
  find /work/hdd/bgvi/adas17/tts_results/results /work/nvme/bgvi/adas17/tts_results/results \
    -maxdepth 1 -type d -name "${pattern}" -print0 2>/dev/null \
    | xargs -0 stat -c '%Y %n' 2>/dev/null \
    | sort -nr \
    | head -n 1 \
    | cut -d' ' -f2-
}

latest_file() {
  local pattern="$1"
  find /work/hdd/bgvi/adas17/tts_results/results /work/nvme/bgvi/adas17/tts_results/results \
    -path "${pattern}" -type f -print0 2>/dev/null \
    | xargs -0 stat -c '%Y %n' 2>/dev/null \
    | sort -nr \
    | head -n 1 \
    | cut -d' ' -f2-
}

DEFAULT_DPO_DIR="$(latest_dir 'e1_deepseek_llama8_dpo*')"
DEFAULT_GRPO_DIR="$(latest_dir 'e1_deepseek_llama8_grpo*')"
DEFAULT_ROWS_JSONL="$(latest_file '*/e1_deepseek_llama8_grpo*/theorem3_eval*/theorem3_generation_rows.jsonl')"

DPO_MODEL=${DPO_MODEL:-${DEFAULT_DPO_DIR}/merged_model}
GRPO_MODEL=${GRPO_MODEL:-${DEFAULT_GRPO_DIR}/merged_model}
ROWS_JSONL=${ROWS_JSONL:-${DEFAULT_ROWS_JSONL}}
OUTPUT_DIR=${OUTPUT_DIR:-${RESULTS_ROOT}/results/deepseek_llama8_objective_mechanism_v1}
JOB_NAME=${JOB_NAME:-r1l8_mech}
WALL=${WALL:-04:00:00}
MAX_PROMPTS_PER_SPLIT=${MAX_PROMPTS_PER_SPLIT:-64}
MAX_NEW_TOKENS=${MAX_NEW_TOKENS:-192}
MAX_PROMPT_LENGTH=${MAX_PROMPT_LENGTH:-2048}
NUM_BOOTSTRAP=${NUM_BOOTSTRAP:-1000}
TORCH_DTYPE=${TORCH_DTYPE:-bfloat16}

cd "${PROJECT_ROOT}"
mkdir -p logs

sbatch <<EOF
#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=${WALL}
#SBATCH -J ${JOB_NAME}
#SBATCH -o logs/${JOB_NAME}_%j.out
set -euo pipefail
module load python/anaconda3/2.10.0
source "${DELTA_VENV}/bin/activate"
export HF_HOME="${HF_HOME}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME}"
cd "${PROJECT_ROOT}"
python scripts/run_llama_objective_mechanism_probe.py \
  --dpo-model "${DPO_MODEL}" \
  --grpo-model "${GRPO_MODEL}" \
  --rows-jsonl "${ROWS_JSONL}" \
  --output-dir "${OUTPUT_DIR}" \
  --benchmark conflictbank \
  --cot-length 1024 \
  --max-prompts-per-split "${MAX_PROMPTS_PER_SPLIT}" \
  --max-new-tokens "${MAX_NEW_TOKENS}" \
  --max-prompt-length "${MAX_PROMPT_LENGTH}" \
  --num-bootstrap "${NUM_BOOTSTRAP}" \
  --torch-dtype "${TORCH_DTYPE}"
EOF
