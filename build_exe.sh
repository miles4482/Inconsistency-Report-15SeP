#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt" pyinstaller
"$ROOT/.venv/bin/python" -m PyInstaller --noconfirm --clean "$ROOT/ParameterAudit.spec"
echo "Built folder: $ROOT/dist/ParameterAudit"
