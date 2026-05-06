#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <jobid[,jobid,...]>" >&2
  exit 1
fi

JOB_IDS="$1"
anvil_ssh_base "sacct -j ${JOB_IDS} --format=JobID,JobName,State,ExitCode,Elapsed"
