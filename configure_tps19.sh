#!/bin/bash
# TPS19 Configuration Script

echo "⚙️ TPS19 Configuration Helper"
echo "=============================="

# Check if .env exists
if [ ! -f "tps19.env" ]; then
    echo "Creating environment file from template..."
    cp tps19.env.template tps19.env
    echo "✅ Created tps19.env - please edit with your API keys"
else
    echo "✅ Environment file already exists"
fi

# Check configuration
echo ""
echo "Current configuration:"
echo "======================"
if [ -f "tps19_config.json" ]; then
    cat tps19_config.json | head -20
else
    echo "❌ Configuration file not found"
fi

echo ""
echo "To configure the system:"
echo "1. Edit tps19.env with your API keys"
echo "2. Run: ./test_tps19.sh to test the system"
echo "3. Run: ./start_tps19.sh to start trading"
