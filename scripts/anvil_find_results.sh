#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

anvil_ssh_base "cd ${ANVIL_PROJECT_ROOT} && find results -maxdepth 4 -name results.json | sort"
