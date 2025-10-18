#!/bin/bash
# TPS19 System Startup Script

echo "🚀 Starting TPS19 System..."

# Check Python modules
python3 -c "import sys; sys.path.append('/opt/tps19/modules'); import trading_engine, simulation_engine, market_data, risk_management, ai_council; print('✅ All modules imported successfully')"

# Initialize databases
python3 /opt/tps19/modules/trading_engine.py &
python3 /opt/tps19/modules/simulation_engine.py &
python3 /opt/tps19/modules/market_data.py &

echo "✅ TPS19 System started successfully"
