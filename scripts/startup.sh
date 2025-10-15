#!/bin/bash
set -euo pipefail
# TPS System Startup Script

echo "🚀 Starting TPS System..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export TPS_HOME="${TPS_HOME:-$SCRIPT_DIR/..}"

# Check Python modules via dynamic path
python3 - <<'PY'
from modules.common.config import add_modules_to_sys_path
add_modules_to_sys_path()
import modules.trading_engine, modules.simulation_engine, modules.market_data, modules.risk_management, modules.ai_council
print('✅ All modules imported successfully')
PY

# Start core services (non-blocking)
python3 "$TPS_HOME/modules/trading_engine.py" &
python3 "$TPS_HOME/modules/simulation_engine.py" &
python3 "$TPS_HOME/modules/market_data.py" &

echo "✅ TPS System started successfully"
