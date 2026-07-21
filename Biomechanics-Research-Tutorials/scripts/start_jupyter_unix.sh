#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v conda >/dev/null 2>&1; then
  echo "conda was not found. Run the .venv setup or initialize conda first." >&2
  exit 1
fi
conda run -n biomechanics-tutorials jupyter lab "$@"
