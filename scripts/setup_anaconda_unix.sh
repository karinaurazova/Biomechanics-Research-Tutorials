#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if conda run -n biomechanics-tutorials python --version >/dev/null 2>&1; then
  conda env update --name biomechanics-tutorials --file environment.yml --prune
else
  conda env create --file environment.yml
fi
conda run -n biomechanics-tutorials python -m pip install -e ".[dev]"
conda run -n biomechanics-tutorials python -m ipykernel install \
  --user \
  --name biomechanics-tutorials \
  --display-name "Python (Biomechanics Research Tutorials)"
conda run -n biomechanics-tutorials python scripts/diagnose_environment.py

echo "Setup completed. Start Jupyter with:"
echo "conda run -n biomechanics-tutorials jupyter lab"
