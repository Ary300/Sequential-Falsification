#!/bin/bash

export ANVIL_SSH_KEY="${ANVIL_SSH_KEY:-$HOME/.ssh/anvil_ed25519}"
export ANVIL_SSH_OPTS="${ANVIL_SSH_OPTS:--o IdentitiesOnly=yes}"
export ANVIL_USER="${ANVIL_USER:-x-adas17}"
export ANVIL_HOST="${ANVIL_HOST:-anvil.rcac.purdue.edu}"
export ANVIL_LOGIN="${ANVIL_LOGIN:-${ANVIL_USER}@${ANVIL_HOST}}"
export ANVIL_PROJECT_ROOT="${ANVIL_PROJECT_ROOT:-/anvil/projects/x-bio260046/tts-falsification}"
export ANVIL_RUNTIME_ROOT="${ANVIL_RUNTIME_ROOT:-/anvil/scratch/${ANVIL_USER}/tts-runtime}"
export ANVIL_HOME="${ANVIL_HOME:-${ANVIL_RUNTIME_ROOT}/home}"
export ANVIL_CONDA_ENV="${ANVIL_CONDA_ENV:-${ANVIL_RUNTIME_ROOT}/conda-envs/tts}"
export ANVIL_CONDA_PKGS="${ANVIL_CONDA_PKGS:-${ANVIL_RUNTIME_ROOT}/.conda/pkgs}"
export ANVIL_PIP_CACHE="${ANVIL_PIP_CACHE:-${ANVIL_RUNTIME_ROOT}/.cache/pip}"
export ANVIL_ACCOUNT="${ANVIL_ACCOUNT:-bio260046-gpu}"
export ANVIL_PARTITION="${ANVIL_PARTITION:-gpu}"

anvil_ssh_base() {
  ssh -n -T -i "$ANVIL_SSH_KEY" $ANVIL_SSH_OPTS "$ANVIL_LOGIN" "$@"
}
