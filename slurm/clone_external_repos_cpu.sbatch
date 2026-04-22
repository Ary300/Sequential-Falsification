#!/bin/bash
#SBATCH -A bio260046
#SBATCH --partition=shared
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH -J clone_external
#SBATCH -o logs/clone_external_%j.out

set -euo pipefail
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
