#!/bin/bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/u/adas17/tts-falsification-git}
RESULTS_ROOT=${RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}
XDG_CACHE_HOME=${XDG_CACHE_HOME:-/work/nvme/bgvi/adas17/.cache}
XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-/work/nvme/bgvi/adas17/.config}
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}

DPO_MODEL=${DPO_MODEL:-${RESULTS_ROOT}/results/e1_deepseek_llama8_dpo/merged_model}
GRPO_MODEL=${GRPO_MODEL:-${RESULTS_ROOT}/results/e1_deepseek_llama8_grpo/merged_model}
ROWS_JSONL=${ROWS_JSONL:-${RESULTS_ROOT}/results/e1_deepseek_llama8_grpo/theorem3_eval_recovery_v1/theorem3_generation_rows.jsonl}
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
