#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONFIG_PATH="${CONFIG_PATH:-src/configs/knowledge_arbitration_spotlight.yaml}"
OUTPUT_ROOT="${OUTPUT_ROOT:-results/arbitration_spotlight_manifest}"
LOCAL_PYTHON_BIN="${LOCAL_PYTHON_BIN:-python3}"
DRY_RUN=0

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
"${LOCAL_PYTHON_BIN}" scripts/build_arbitration_spotlight_manifest.py \
  --config "${CONFIG_PATH}" \
  --output-dir "${OUTPUT_ROOT}"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "DRYRUN only: spotlight manifest generated locally at ${OUTPUT_ROOT}."
fi
