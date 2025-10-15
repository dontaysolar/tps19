#!/bin/bash
# TPS19 Startup Script

echo "🚀 Starting TPS19 Trading System..."
cd /workspace

# Load environment variables if .env exists
if [ -f "tps19.env" ]; then
    export $(cat tps19.env | grep -v '^#' | xargs)
fi

# Start the system
python3 tps19_main.py
