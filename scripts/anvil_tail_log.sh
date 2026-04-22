#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <log-path-relative-to-project-root>" >&2
  exit 1
fi

LOG_PATH="$1"
anvil_ssh_base "cd ${ANVIL_PROJECT_ROOT} && tail -n 120 ${LOG_PATH}"
