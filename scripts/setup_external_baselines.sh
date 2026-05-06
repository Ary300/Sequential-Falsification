#!/bin/bash
set -euo pipefail

BASELINE_ROOT="${BASELINE_ROOT:-external/baselines}"
mkdir -p "${BASELINE_ROOT}"

clone_or_update() {
  local name="$1"
  local url="$2"
  local target="${BASELINE_ROOT}/${name}"
  if [[ -d "${target}/.git" ]]; then
    echo "Updating ${name}..."
    git -C "${target}" pull --ff-only
  else
    echo "Cloning ${name}..."
    git clone "${url}" "${target}"
  fi
}

clone_or_update SkyThought https://github.com/NovaSky-AI/SkyThought.git
clone_or_update CodeT https://github.com/microsoft/CodeT.git
clone_or_update ThinkPRM https://github.com/mukhal/thinkprm.git
clone_or_update AceCoder https://github.com/TIGER-AI-Lab/AceCoder.git
clone_or_update OpenR https://github.com/openreasoner/openr.git

cat <<EOF

External baseline repos are staged under ${BASELINE_ROOT}.

Next integration steps:
1. Pin commits after a successful environment solve on Delta/Anvil.
2. Add adapter scripts that convert this repo's candidate JSON into each tool's expected input format.
3. Report these as external baselines only after the original code path runs end-to-end.
EOF
