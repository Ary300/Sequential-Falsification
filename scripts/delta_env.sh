#!/bin/bash

export DELTA_USER="${DELTA_USER:-adas17}"
export DELTA_HOST="${DELTA_HOST:-dtai-login.delta.ncsa.illinois.edu}"
export DELTA_LOGIN="${DELTA_LOGIN:-${DELTA_USER}@${DELTA_HOST}}"
export DELTA_SSH_KEY="${DELTA_SSH_KEY:-}"
export DELTA_SSH_OPTS="${DELTA_SSH_OPTS:--o IdentitiesOnly=yes}"
export DELTA_PROJECT_ROOT="${DELTA_PROJECT_ROOT:-/u/${DELTA_USER}/tts-falsification-git}"
export DELTA_ACCOUNT="${DELTA_ACCOUNT:-bgvi-dtai-gh}"
export DELTA_PARTITION="${DELTA_PARTITION:-ghx4}"
export DELTA_QOS="${DELTA_QOS:-bgvi-dtai-gh}"
export DELTA_VENV="${DELTA_VENV:-/u/${DELTA_USER}/venvs/tts-delta}"

delta_ssh_base() {
  local -a ssh_args=(-n -T)
  if [[ -n "${DELTA_SSH_KEY}" ]]; then
    ssh_args+=(-i "${DELTA_SSH_KEY}")
  fi
  if [[ -n "${DELTA_SSH_OPTS}" ]]; then
    local -a extra_opts=()
    read -r -a extra_opts <<< "${DELTA_SSH_OPTS}"
    ssh_args+=("${extra_opts[@]}")
  fi
  ssh "${ssh_args[@]}" "$DELTA_LOGIN" "$@"
}
