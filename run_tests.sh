#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export TPS_HOME="${TPS_HOME:-$SCRIPT_DIR}"
cd "$TPS_HOME"
python3 modules/testing/test_suite.py
