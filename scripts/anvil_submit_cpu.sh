#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <slurm-script-path> [extra sbatch args...]" >&2
  exit 1
fi

SLURM_SCRIPT="$1"
shift

REMOTE_CMD=$(
  cat <<EOF
cd ${ANVIL_PROJECT_ROOT} && \
unset SBATCH_QOS SLURM_QOS && \
export SBATCH_ACCOUNT=bio260046 && \
export SBATCH_PARTITION=shared && \
sbatch --parsable --account="\$SBATCH_ACCOUNT" --partition="\$SBATCH_PARTITION" "$SLURM_SCRIPT" "$@"
EOF
)

anvil_ssh_base "$REMOTE_CMD"
