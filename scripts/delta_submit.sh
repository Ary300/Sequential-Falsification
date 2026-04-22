#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delta_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <slurm-script-path> [extra sbatch args...]" >&2
  exit 1
fi

SLURM_SCRIPT="$1"
shift

REMOTE_CMD=$(
  cat <<EOF
cd ${DELTA_PROJECT_ROOT} && \
unset SBATCH_ACCOUNT SBATCH_PARTITION SBATCH_QOS && \
export SBATCH_ACCOUNT=${DELTA_ACCOUNT} && \
export SBATCH_PARTITION=${DELTA_PARTITION} && \
export SBATCH_QOS=${DELTA_QOS} && \
sbatch --parsable --account="\$SBATCH_ACCOUNT" --partition="\$SBATCH_PARTITION" --qos="\$SBATCH_QOS" "$SLURM_SCRIPT" "$@"
EOF
)

delta_ssh_base "$REMOTE_CMD"
