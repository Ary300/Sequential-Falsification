#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIG_PATH="${CONFIG_PATH:-src/configs/knowledge_arbitration_spotlight_extended.yaml}"
OUTPUT_ROOT="${OUTPUT_ROOT:-results/arbitration_spotlight_extended_manifest}"
DRY_RUN=0
SYNC_FIRST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="$2"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="$2"
      shift 2
      ;;
    --sync-first)
      SYNC_FIRST=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

cd "${ROOT_DIR}"

python3 scripts/build_arbitration_spotlight_manifest.py \
  --config "${CONFIG_PATH}" \
  --output-dir "${OUTPUT_ROOT}"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "DRYRUN only: extended empirical completion manifest built at ${OUTPUT_ROOT}."
  echo "No remote submission attempted."
  exit 0
fi

source "${ROOT_DIR}/scripts/delta_env.sh"

auth_detail=""
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "${DELTA_LOGIN}" "hostname" >/tmp/delta_empirical_completion_auth.out 2>/tmp/delta_empirical_completion_auth.err; then
  auth_detail="$(tr '\n' ' ' </tmp/delta_empirical_completion_auth.err | sed 's/  */ /g' | sed 's/^ //; s/ $//')"
  python3 scripts/build_extended_empirical_wave_ready.py \
    --manifest "${OUTPUT_ROOT}/manifest.json" \
    --delta-auth-state blocked \
    --delta-auth-detail "${auth_detail:-Delta login unavailable from this session.}" >/dev/null
  echo "Delta authentication is currently blocked."
  echo "${auth_detail:-Delta login unavailable from this session.}"
  echo "Manifest is still ready locally at ${OUTPUT_ROOT}."
  exit 2
fi

python3 scripts/build_extended_empirical_wave_ready.py \
  --manifest "${OUTPUT_ROOT}/manifest.json" \
  --delta-auth-state ready \
  --delta-auth-detail "BatchMode ssh probe to ${DELTA_LOGIN} succeeded." >/dev/null

echo "Delta authentication probe succeeded."
echo "Next step is to sync the repo to ${DELTA_LOGIN}:${DELTA_PROJECT_ROOT} and launch the extended sweep there."
if [[ "${SYNC_FIRST}" -eq 1 ]]; then
  echo "SYNC_FIRST requested, but this wrapper intentionally stops after validation so sync and submit stay explicit."
fi
