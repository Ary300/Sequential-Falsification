#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/anvil_env.sh"

CONFIG_PATH="${CONFIG_PATH:-src/configs/experiments.yaml}"
OUTPUT_ROOT="${OUTPUT_ROOT:-results/anvil_ablations}"
FIGURE_ROOT="${FIGURE_ROOT:-figures/anvil_ablations}"
GPU_ACCOUNT="${GPU_ACCOUNT:-$ANVIL_ACCOUNT}"
GPU_PARTITION="${GPU_PARTITION:-$ANVIL_PARTITION}"
CPU_ACCOUNT="${CPU_ACCOUNT:-bio260046}"
CPU_PARTITION="${CPU_PARTITION:-shared}"
BACKEND_OVERRIDE="${BACKEND_OVERRIDE:-transformers}"
SEEDS="${SEEDS:-42,43,44}"
DRY_RUN=0
LOCAL_PYTHON_BIN="${LOCAL_PYTHON_BIN:-python3}"
AFTEROK_DEPENDENCY="${AFTEROK_DEPENDENCY:-}"

declare -a EXPERIMENT_NAMES=()
declare -a EXPERIMENT_PREFIXES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="$2"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="$2"
      shift 2
      ;;
    --figure-root)
      FIGURE_ROOT="$2"
      shift 2
      ;;
    --backend-override)
      BACKEND_OVERRIDE="$2"
      shift 2
      ;;
    --seeds)
      SEEDS="$2"
      shift 2
      ;;
    --afterok)
      AFTEROK_DEPENDENCY="$2"
      shift 2
      ;;
    --experiment-name)
      EXPERIMENT_NAMES+=("$2")
      shift 2
      ;;
    --experiment-prefix)
      EXPERIMENT_PREFIXES+=("$2")
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ${#EXPERIMENT_NAMES[@]} -eq 0 && ${#EXPERIMENT_PREFIXES[@]} -eq 0 ]]; then
  EXPERIMENT_NAMES=(
    n_scaling_mbpp_7b
    round_ablation_mbpp_7b
    temperature_ablation_mbpp_7b
    compute_matched_mbpp_7b
  )
  EXPERIMENT_PREFIXES=(
    probe_family_ablation_
    component_ablation_
  )
fi

declare -a BASE_DEP_ARGS=()
if [[ -n "${AFTEROK_DEPENDENCY}" ]]; then
  BASE_DEP_ARGS=(--dependency="afterok:${AFTEROK_DEPENDENCY}")
fi

MANIFEST=$(
  cd "${ROOT_DIR}" && "${LOCAL_PYTHON_BIN}" - "${CONFIG_PATH}" "${EXPERIMENT_NAMES[*]-}" "${EXPERIMENT_PREFIXES[*]-}" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root / "src"))

from experiment_registry import filter_experiments, load_expanded_experiments

config_path = Path(sys.argv[1])
names = [item for item in sys.argv[2].split() if item]
prefixes = [item for item in sys.argv[3].split() if item]
experiments = filter_experiments(load_expanded_experiments(config_path), names=names, prefixes=prefixes)

for experiment in experiments:
    row = {
        "name": experiment["name"],
        "benchmarks": experiment.get("benchmarks", []),
        "methods": experiment.get("methods", []),
        "model": experiment.get("model", "mock-model"),
        "backend": experiment.get("backend", "mock"),
        "n_candidates": experiment.get("n_candidates", 4),
        "n_falsification_rounds": experiment.get("n_falsification_rounds", 2),
        "max_tiebreak_rounds": experiment.get("max_tiebreak_rounds", 4),
        "delta": experiment.get("delta", 0.05),
        "alpha": experiment.get("alpha", 0.05),
        "timeout": experiment.get("timeout", 10),
        "temperature": experiment.get("temperature", 0.7),
        "max_tokens": experiment.get("max_tokens", 512),
        "probe_strategy": experiment.get("probe_strategy", "adaptive_population"),
        "adaptive_probe_selection": experiment.get("adaptive_probe_selection", True),
        "eliminate_on_detection": experiment.get("eliminate_on_detection", True),
        "confidence_mode": experiment.get("confidence_mode", "wealth"),
        "max_differential_probes": experiment.get("max_differential_probes", 8),
        "consensus_min_fraction": experiment.get("consensus_min_fraction", 0.70),
        "consensus_min_margin": experiment.get("consensus_min_margin", 2),
        "consensus_min_votes": experiment.get("consensus_min_votes", 3),
        "max_problems": experiment.get("max_problems"),
        "data_root": experiment.get("data_root", "data"),
    }
    print(json.dumps(row))
PY
)

if [[ -z "${MANIFEST}" ]]; then
  echo "No experiments matched the requested selection." >&2
  exit 1
fi

slugify() {
  printf '%s' "$1" | LC_ALL=C sed 's|[/=,: ]|_|g; s|[^[:alnum:]_.-]||g' | cut -c1-80
}

resource_profile() {
  local model="$1"
  local max_problems="$2"
  local gpus=1
  local cpus=32
  local wall="10:00:00"
  local tp=1
  if [[ "$model" == *"32B"* ]]; then
    gpus=2
    cpus=48
    wall="24:00:00"
    tp=2
  elif [[ "$model" == *"14B"* || "$model" == *"16B"* ]]; then
    gpus=1
    cpus=32
    wall="16:00:00"
    tp=1
  elif [[ "$max_problems" =~ ^[0-9]+$ ]] && (( max_problems > 128 )); then
    wall="14:00:00"
  fi
  printf '%s\t%s\t%s\t%s\n' "$gpus" "$cpus" "$wall" "$tp"
}

submit_remote() {
  local cmd="$1"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    local fake_id="dryrun_${RANDOM}_${RANDOM}"
    echo "DRYRUN[${fake_id}] ${cmd}" >&2
    echo "${fake_id}"
  else
    anvil_ssh_base "$cmd"
  fi
}

while IFS= read -r row; do
  [[ -z "$row" ]] && continue
  parsed_fields="$("${LOCAL_PYTHON_BIN}" - "$row" <<'PY'
from __future__ import annotations

import json
import sys

row = json.loads(sys.argv[1])
fields = [
    row["name"],
    ",".join(row["benchmarks"]),
    ":".join(row["methods"]),
    row["model"],
    row["backend"],
    str(row["n_candidates"]),
    str(row["n_falsification_rounds"]),
    str(row["max_tiebreak_rounds"]),
    str(row["delta"]),
    str(row["alpha"]),
    str(row["timeout"]),
    str(row["temperature"]),
    str(row["max_tokens"]),
    row["probe_strategy"],
    "true" if row["adaptive_probe_selection"] else "false",
    "true" if row["eliminate_on_detection"] else "false",
    row["confidence_mode"],
    str(row["max_differential_probes"]),
    str(row["consensus_min_fraction"]),
    str(row["consensus_min_margin"]),
    str(row["consensus_min_votes"]),
    "" if row["max_problems"] is None else str(row["max_problems"]),
    row["data_root"],
]
print("\t".join(fields))
PY
)"
  IFS=$'\t' read -r exp_name benchmarks methods model backend n_candidates n_rounds max_tiebreak_rounds delta_param alpha timeout temperature max_tokens probe_strategy adaptive_probe_selection eliminate_on_detection confidence_mode max_differential_probes consensus_min_fraction consensus_min_margin consensus_min_votes max_problems data_root <<< "${parsed_fields}"
  benchmarks_export="${benchmarks//,/:}"

  read -r gpus cpus wall tp_size <<<"$(resource_profile "$model" "${max_problems:-0}")"
  exp_slug="$(slugify "$exp_name")"

  declare -a report_ids=()
  declare -a run_dirs=()
  IFS=',' read -ra seed_values <<< "$SEEDS"
  for seed in "${seed_values[@]}"; do
    seed="$(echo "$seed" | xargs)"
    [[ -z "$seed" ]] && continue
    run_dir="${OUTPUT_ROOT}/${exp_slug}_s${seed}"
    fig_dir="${FIGURE_ROOT}/${exp_slug}_s${seed}"
    job_name="$(slugify "${exp_slug}_s${seed}")"
    run_dirs+=("$run_dir")

    exp_cmd=$(
      cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${GPU_ACCOUNT}" --partition="${GPU_PARTITION}" \
  ${BASE_DEP_ARGS:+${BASE_DEP_ARGS[*]}} \
  --gpus-per-node="${gpus}" --cpus-per-task="${cpus}" --time="${wall}" --job-name="${job_name}" \
  --export=ALL,ANVIL_CONDA_ENV=${ANVIL_CONDA_ENV},BACKEND=${BACKEND_OVERRIDE},MODEL=${model},BENCHMARKS=${benchmarks_export},METHODS=${methods},OUTPUT_DIR=${run_dir},SEEDS=${seed},MAX_PROBLEMS=${max_problems},N_CANDIDATES=${n_candidates},N_ROUNDS=${n_rounds},MAX_TIEBREAK_ROUNDS=${max_tiebreak_rounds},DELTA_PARAM=${delta_param},ALPHA=${alpha},TIMEOUT=${timeout},TEMPERATURE=${temperature},MAX_TOKENS=${max_tokens},TP_SIZE=${tp_size},PROBE_STRATEGY=${probe_strategy},ADAPTIVE_PROBE_SELECTION=${adaptive_probe_selection},ELIMINATE_ON_DETECTION=${eliminate_on_detection},CONFIDENCE_MODE=${confidence_mode},MAX_DIFFERENTIAL_PROBES=${max_differential_probes},CONSENSUS_MIN_FRACTION=${consensus_min_fraction},CONSENSUS_MIN_MARGIN=${consensus_min_margin},CONSENSUS_MIN_VOTES=${consensus_min_votes},DATA_ROOT=${data_root} \
  slurm/anvil_full_experiment.sbatch
EOF
    )
    exp_id="$(submit_remote "$exp_cmd")"

    rep_cmd=$(
      cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${CPU_ACCOUNT}" --partition="${CPU_PARTITION}" \
  --dependency="afterany:${exp_id}" --job-name="${job_name}_rep" \
  --export=ALL,ANVIL_CONDA_ENV=${ANVIL_CONDA_ENV},RESULTS_FILE=${run_dir}/results.json,PROGRESS_DIR=${run_dir},OUTPUT_DIR=${fig_dir} \
  slurm/report_results_cpu.sbatch
EOF
    )
    rep_id="$(submit_remote "$rep_cmd")"
    report_ids+=("$rep_id")

    echo "queued ${exp_name} seed=${seed} exp=${exp_id} rep=${rep_id}"
  done

  dep_chain=$(IFS=:; echo "${report_ids[*]}")
  merge_dir="${OUTPUT_ROOT}/${exp_slug}_merged"
  merge_fig_dir="${FIGURE_ROOT}/${exp_slug}_merged"
  merge_output="${merge_dir}/results.json"
  merge_job_name="$(slugify "${exp_slug}_merge")"

  merge_wrap="cd ${ANVIL_PROJECT_ROOT} && module purge && module load conda && source activate ${ANVIL_CONDA_ENV} && python scripts/merge_seed_results.py"
  for run_dir in "${run_dirs[@]}"; do
    merge_wrap+=" --run-dir ${run_dir}"
  done
  merge_wrap+=" --output-file ${merge_output} && python src/report.py --results-file ${merge_output} --output-dir ${merge_fig_dir}"

  merge_cmd=$(
    cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
sbatch --parsable --account="${CPU_ACCOUNT}" --partition="${CPU_PARTITION}" \
  --dependency="afterany:${dep_chain}" --job-name="${merge_job_name}" \
  --output="logs/${merge_job_name}_%j.out" \
  --wrap='${merge_wrap}'
EOF
  )
  merge_id="$(submit_remote "$merge_cmd")"
  echo "queued ${exp_name} merge=${merge_id}"
done <<< "${MANIFEST}"
