#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/delta_env.sh"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 '<remote command>'" >&2
  exit 1
fi

delta_ssh_base "$1"
