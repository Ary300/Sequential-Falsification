#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

rsync -av \
  --exclude '.git/' \
  --exclude '__pycache__/' \
  --exclude 'results/' \
  --exclude 'figures/' \
  --exclude 'logs/' \
  --exclude 'checkpoints/' \
  -e "ssh -i $ANVIL_SSH_KEY $ANVIL_SSH_OPTS" \
  "$ROOT_DIR/" \
  "${ANVIL_LOGIN}:${ANVIL_PROJECT_ROOT}/"
