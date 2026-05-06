#!/bin/bash
#SBATCH -A bio260046-gpu
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --time=24:00:00
#SBATCH -J ablation
#SBATCH -o logs/ablation_%j.out

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

CONFIG_PATH=${CONFIG_PATH:-src/configs/experiments.yaml}
OUTPUT_ROOT=${OUTPUT_ROOT:-results/ablations}
BACKEND_OVERRIDE=${BACKEND_OVERRIDE:-transformers}
API_BASE_OVERRIDE=${API_BASE_OVERRIDE:-}
MODEL_OVERRIDE=${MODEL_OVERRIDE:-}
SEED_OVERRIDE=${SEED_OVERRIDE:-}
MAX_PROBLEMS_OVERRIDE=${MAX_PROBLEMS_OVERRIDE:-}
EXPERIMENT_NAMES=${EXPERIMENT_NAMES:-n_scaling_mbpp_7b,round_ablation_mbpp_7b,temperature_ablation_mbpp_7b,compute_matched_mbpp_7b}
EXPERIMENT_PREFIXES=${EXPERIMENT_PREFIXES:-probe_family_ablation_,component_ablation_}

cd /anvil/projects/x-bio260046/tts-falsification

ARGS=(--config "${CONFIG_PATH}" --output-root "${OUTPUT_ROOT}" --backend-override "${BACKEND_OVERRIDE}")
if [[ -n "${API_BASE_OVERRIDE}" ]]; then
  ARGS+=(--api-base-override "${API_BASE_OVERRIDE}")
fi
if [[ -n "${MODEL_OVERRIDE}" ]]; then
  ARGS+=(--model-override "${MODEL_OVERRIDE}")
fi
if [[ -n "${SEED_OVERRIDE}" ]]; then
  ARGS+=(--seed-override "${SEED_OVERRIDE}")
fi
if [[ -n "${MAX_PROBLEMS_OVERRIDE}" ]]; then
  ARGS+=(--max-problems-override "${MAX_PROBLEMS_OVERRIDE}")
fi

IFS=',' read -ra EXP_NAME_ARRAY <<< "${EXPERIMENT_NAMES}"
for name in "${EXP_NAME_ARRAY[@]}"; do
  name=$(echo "${name}" | xargs)
  if [[ -n "${name}" ]]; then
    ARGS+=(--experiment-name "${name}")
  fi
done

IFS=',' read -ra EXP_PREFIX_ARRAY <<< "${EXPERIMENT_PREFIXES}"
for prefix in "${EXP_PREFIX_ARRAY[@]}"; do
  prefix=$(echo "${prefix}" | xargs)
  if [[ -n "${prefix}" ]]; then
    ARGS+=(--experiment-prefix "${prefix}")
  fi
done

"${PYTHON_BIN}" src/run_full_pipeline.py "${ARGS[@]}"
