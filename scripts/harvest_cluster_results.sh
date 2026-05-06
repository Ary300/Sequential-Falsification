#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

source "${SCRIPT_DIR}/anvil_env.sh"
source "${SCRIPT_DIR}/delta_env.sh"

SKIP_ANVIL=0
SKIP_DELTA=0
SKIP_FINALIZE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-anvil)
      SKIP_ANVIL=1
      shift
      ;;
    --skip-delta)
      SKIP_DELTA=1
      shift
      ;;
    --skip-finalize)
      SKIP_FINALIZE=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

sync_subdir() {
  local label="$1"
  local ssh_target="$2"
  local ssh_cmd="$3"
  local remote_root="$4"
  local subdir="$5"

  local remote_path="${remote_root}/${subdir}"
  local local_path="${ROOT_DIR}/${subdir}"
  mkdir -p "${local_path}"

  echo "[${label}] syncing ${subdir}"
  if ! eval "${ssh_cmd} \"${ssh_target}\" \"test -d '${remote_path}'\" >/dev/null 2>&1"; then
    echo "[${label}] skip ${subdir}: remote path not reachable (${remote_path})" >&2
    return 1
  fi

  if ! eval "rsync -az --timeout=60 -e \"${ssh_cmd}\" \"${ssh_target}:${remote_path}/\" \"${local_path}/\""; then
    echo "[${label}] sync failed for ${subdir}" >&2
    return 1
  fi
}

sync_cluster() {
  local label="$1"
  local ssh_target="$2"
  local ssh_cmd="$3"
  local remote_root="$4"
  local any_success=0

  for subdir in results figures logs paper/generated; do
    if sync_subdir "${label}" "${ssh_target}" "${ssh_cmd}" "${remote_root}" "${subdir}"; then
      any_success=1
    fi
  done

  if [[ "${any_success}" -eq 1 ]]; then
    echo "[${label}] sync complete"
  else
    echo "[${label}] nothing synced" >&2
  fi
}

ANVIL_RSYNC_SSH="ssh -o ConnectTimeout=10 -i ${ANVIL_SSH_KEY} ${ANVIL_SSH_OPTS}"
DELTA_RSYNC_SSH="ssh -o ConnectTimeout=10"
if [[ -n "${DELTA_SSH_KEY}" ]]; then
  DELTA_RSYNC_SSH+=" -i ${DELTA_SSH_KEY}"
fi
if [[ -n "${DELTA_SSH_OPTS}" ]]; then
  DELTA_RSYNC_SSH+=" ${DELTA_SSH_OPTS}"
fi

if [[ "${SKIP_ANVIL}" -eq 0 ]]; then
  sync_cluster "anvil" "${ANVIL_LOGIN}" "${ANVIL_RSYNC_SSH}" "${ANVIL_PROJECT_ROOT}" || true
fi

if [[ "${SKIP_DELTA}" -eq 0 ]]; then
  sync_cluster "delta" "${DELTA_LOGIN}" "${DELTA_RSYNC_SSH}" "${DELTA_PROJECT_ROOT}" || true
fi

if [[ "${SKIP_FINALIZE}" -eq 0 ]]; then
  echo "[local] finalizing project artifacts"
  python3 "${SCRIPT_DIR}/finalize_project.py"
fi

