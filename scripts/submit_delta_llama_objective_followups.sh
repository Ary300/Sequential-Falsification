#!/bin/bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/u/adas17/tts-falsification-git}
RESULTS_ROOT=${RESULTS_ROOT:-/work/nvme/bgvi/adas17/tts_results}
HF_HOME=${HF_HOME:-/work/nvme/bgvi/adas17/hf_cache}
XDG_CACHE_HOME=${XDG_CACHE_HOME:-/work/nvme/bgvi/adas17/.cache}
XDG_CONFIG_HOME=${XDG_CONFIG_HOME:-/work/nvme/bgvi/adas17/.config}
DELTA_VENV=${DELTA_VENV:-/u/adas17/venvs/tts-delta}

cd "${PROJECT_ROOT}"
mkdir -p logs

sbatch <<'EOF'
#!/bin/bash
#SBATCH -A bgvi-dtai-gh
#SBATCH --partition=ghx4
#SBATCH --qos=bgvi-dtai-gh
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH -J l8_mech
#SBATCH -o logs/l8_mech_%j.out
set -euo pipefail
module load python/anaconda3/2.10.0
source "${DELTA_VENV}/bin/activate"
export HF_HOME="${HF_HOME}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME}"
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME}"
cd "${PROJECT_ROOT}"
python scripts/run_llama_objective_mechanism_probe.py \
  --dpo-model "${RESULTS_ROOT}/results/e1_llama8b_dpo/merged_model" \
  --grpo-model "${RESULTS_ROOT}/results/e1_llama8b_grpo/merged_model" \
  --rows-jsonl "${RESULTS_ROOT}/results/e1_llama8b_grpo/theorem3_eval_retry/theorem3_generation_rows.jsonl" \
  --output-dir "${RESULTS_ROOT}/results/llama8_objective_mechanism_v1" \
  --benchmark conflictbank \
  --cot-length 1024 \
  --max-prompts-per-split 64 \
  --max-new-tokens 192 \
  --max-prompt-length 2048 \
  --num-bootstrap 1000
EOF

sbatch \
  --export=ALL,DELTA_PROJECT_ROOT="${PROJECT_ROOT}",DELTA_RESULTS_ROOT="${RESULTS_ROOT}",HF_HOME="${HF_HOME}",XDG_CACHE_HOME="${XDG_CACHE_HOME}",XDG_CONFIG_HOME="${XDG_CONFIG_HOME}",HF_TOKEN="${HF_TOKEN:-}",HUGGING_FACE_HUB_TOKEN="${HF_TOKEN:-}",OBJECTIVE=dpo,MODEL_NAME=meta-llama/Llama-3.1-8B,OUTPUT_DIR=results/e1_llama8b_sft_control,BENCHMARK=conflictbank,MAX_SOURCE_ROWS=900,MAX_TRAIN_ROWS=640,MAX_VAL_ROWS=96,MAX_EVAL_ROWS=96,EPOCHS=0,WARMSTART_EPOCHS=2,RUN_THEOREM3_EVAL=1,EVAL_OUTPUT_DIR=results/e1_llama8b_sft_control/theorem3_eval_retry,EVAL_BENCHMARKS=wikicontradict,conflictbank,EVAL_CONDITIONS=aligned_context,conflict_context,EVAL_COT_LENGTHS=0,128,1024,EVAL_WIKICONTRADICT_MAX=96,EVAL_CONFLICTBANK_MAX=128,VLLM_MAX_MODEL_LEN=12288 \
  slurm/delta/theorem3_matched_objective_lora_delta.sbatch
