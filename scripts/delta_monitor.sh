#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delta_env.sh"

if [[ $# -eq 0 ]]; then
  delta_ssh_base "squeue -u ${DELTA_USER}"
  exit 0
fi

delta_ssh_base "squeue -j $1 -O jobid,state,reason,partition,account,qos,name,timeused,timeleft,nodelist"
