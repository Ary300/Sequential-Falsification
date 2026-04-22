#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/anvil_env.sh"

REMOTE_CMD=$(cat <<'EOF'
set -euo pipefail
cd "$ANVIL_PROJECT_ROOT"
mkdir -p external
cd external

clone_or_update() {
  local url="$1"
  local dir="$2"
  if [[ -d "$dir/.git" ]]; then
    git -C "$dir" fetch --all --prune
    git -C "$dir" pull --ff-only || true
  else
    git clone "$url" "$dir"
  fi
}

clone_or_update https://github.com/NovaSky-AI/SkyThought.git SkyThought
clone_or_update https://github.com/evalplus/evalplus.git evalplus
clone_or_update https://github.com/benediktstroebl/inference-scaling-limits.git inference-scaling-limits
clone_or_update https://github.com/LiveCodeBench/LiveCodeBench.git LiveCodeBench
clone_or_update https://github.com/microsoft/CodeT.git CodeT
clone_or_update https://github.com/openreasoner/openr.git openr
clone_or_update https://github.com/zhentingqi/rStar.git rStar
EOF
)

anvil_ssh_base "export ANVIL_PROJECT_ROOT='${ANVIL_PROJECT_ROOT}' && ${REMOTE_CMD}"
