#!/bin/bash
# TPS19 Test Script

echo "🧪 Running TPS19 System Tests..."
cd /workspace

# Load environment variables if .env exists
if [ -f "tps19.env" ]; then
    export $(cat tps19.env | grep -v '^#' | xargs)
fi

# Run tests
python3 modules/testing/comprehensive_test_suite.py
