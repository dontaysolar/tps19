#!/bin/bash
################################################################################
# APEX V3 - QUICK START GUIDE
# First-time setup and startup
################################################################################

echo "================================================================================"
echo "🚀 APEX V3 - QUICK START"
echo "================================================================================"
echo ""

# Check if .env is configured
if grep -q "YOUR_API_KEY_HERE" .env 2>/dev/null; then
    echo "⚠️  CREDENTIALS NOT CONFIGURED"
    echo ""
    echo "You need to update your .env file first:"
    echo ""
    echo "  1. Rotate your API keys (see USER_ACTION_REQUIRED.md)"
    echo "  2. Edit .env file:"
    echo "     nano .env"
    echo ""
    echo "  3. Replace these placeholders:"
    echo "     EXCHANGE_API_KEY=YOUR_API_KEY_HERE"
    echo "     EXCHANGE_API_SECRET=YOUR_API_SECRET_HERE"
    echo "     TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_TOKEN_HERE"
    echo ""
    echo "  4. Run this script again"
    echo ""
    exit 1
fi

echo "Step 1: Checking dependencies..."
echo ""

# Check if requirements are installed
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "✅ Dependencies OK"
echo ""

echo "Step 2: Running tests..."
echo ""

# Run tests
if python3 test_suite.py | tail -20; then
    echo ""
    echo "✅ Tests passed"
else
    echo ""
    echo "❌ Tests failed - check errors above"
    exit 1
fi

echo ""
echo "Step 3: Starting system..."
echo ""

# Start system
./start_system.sh
