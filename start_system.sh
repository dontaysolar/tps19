#!/bin/bash
################################################################################
# APEX V3 - SYSTEM STARTUP SCRIPT
# Verifies system and starts trading platform
################################################################################

set -e  # Exit on error

echo "================================================================================"
echo "🚀 APEX V3 - STARTING SYSTEM"
echo "================================================================================"
echo ""

# Change to workspace directory
cd /workspace

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 not found"
    echo "   Install Python 3.8+ and try again"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Run verification
echo "🔍 Running system verification..."
echo ""

if python3 verify_system.py; then
    echo ""
    echo "================================================================================"
    echo "✅ VERIFICATION PASSED - STARTING APEX V3"
    echo "================================================================================"
    echo ""
    echo "Mode: MONITORING (Trading disabled by default)"
    echo "Pairs: BTC/USDT, ETH/USDT, SOL/USDT"
    echo "Update Interval: 60 seconds"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    echo "================================================================================"
    echo ""
    
    # Start the system
    python3 apex_v3_integrated.py
else
    echo ""
    echo "================================================================================"
    echo "❌ VERIFICATION FAILED"
    echo "================================================================================"
    echo ""
    echo "Fix the issues above before starting the system."
    echo ""
    echo "Common fixes:"
    echo "  1. Update .env file with your credentials"
    echo "  2. Run: pip3 install -r requirements.txt"
    echo "  3. Check: USER_ACTION_REQUIRED.md"
    echo ""
    exit 1
fi
