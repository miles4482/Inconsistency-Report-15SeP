#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! python3 -c "import openpyxl, pyxlsb" >/dev/null 2>&1; then
  echo "Installing Python dependencies..."
  python3 -m pip install -r "$ROOT/requirements.txt"
fi

python3 "$ROOT/scripts/compare_reference_parameters.py" "$@"
