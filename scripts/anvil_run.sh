#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 '<remote command>'" >&2
  exit 1
fi

REMOTE_CMD="$1"
anvil_ssh_base "$REMOTE_CMD"
