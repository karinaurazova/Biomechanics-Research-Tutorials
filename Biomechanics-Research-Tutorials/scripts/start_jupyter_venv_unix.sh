#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x ".venv/bin/python" ]]; then
  echo ".venv was not found. Run bash scripts/setup_venv_unix.sh first." >&2
  exit 1
fi
.venv/bin/python scripts/start_jupyter.py "$@"
