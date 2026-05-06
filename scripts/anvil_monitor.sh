#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

if [[ $# -eq 0 ]]; then
  anvil_ssh_base "squeue -u ${ANVIL_USER}"
  exit 0
fi

JOB_IDS="$1"
anvil_ssh_base "squeue -j ${JOB_IDS} -O jobid,state,reason,partition,account,name,timeused,timeleft,nodelist"
