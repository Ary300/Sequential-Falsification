#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delta_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <log-path-relative-to-project-root>" >&2
  exit 1
fi

delta_ssh_base "cd ${DELTA_PROJECT_ROOT} && tail -n 120 $1"
