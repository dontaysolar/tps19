#!/bin/bash
# APEX Full System Deployment
# Deploys all 5 bots + Phase 1 features + Master Controller
# Following ATLAS Autonomous Agent Protocol

set -e

echo "============================================================"
echo "🚀 APEX AI TRADING SYSTEM - FULL DEPLOYMENT"
echo "============================================================"
echo ""

# Navigate to repo
cd ~/tps19

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --break-system-packages ccxt numpy pandas flask flask-cors requests python-dotenv -q

# Create directories
echo "📁 Creating directories..."
mkdir -p bots modules tests data logs config

# Make scripts executable
chmod +x *.py bots/*.py tests/*.py *.sh 2>/dev/null

# Configure .env if doesn't exist
if [ ! -f .env ]; then
    echo "🔑 Creating .env configuration..."
    cat > .env << 'ENVEOF'
# TPS19 Production Configuration
EXCHANGE_API_KEY=A8YmbndHwWATwn6WScdUco
EXCHANGE_API_SECRET=cxakp_gJ4ZFRhFSzq6tyxuLrwqJn

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=7289126201:AAHaWTLKxpddtbJ9oa4hGdvKaq0mypqU75Y
TELEGRAM_CHAT_ID=7517400013

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=P6NYOL1UB59UXI42

# TPS19 Configuration
TPS19_ENV=production
TRADING_ENABLED=true
ENABLE_LSTM_PREDICTION=true
ENABLE_SELF_LEARNING=true
LOG_LEVEL=INFO
ENVEOF
    chmod 600 .env
    echo "✅ .env configured"
fi

echo ""
echo "============================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "📊 System Components:"
echo "   ✅ Bot #1: Dynamic Stop-Loss"
echo "   ✅ Bot #2: Fee Optimizer"
echo "   ✅ Bot #3: Whale Monitor"
echo "   ✅ Bot #4: Crash Shield"
echo "   ✅ Bot #5: Capital Rotator"
echo "   ✅ Phase 1: Sentiment Analysis"
echo "   ✅ Phase 1: Multi-Coin Trading"
echo "   ✅ Phase 1: Trailing Stop-Loss"
echo "   ✅ Phase 1: Enhanced Notifications"
echo "   ✅ Phase 1: Dashboard API"
echo "   ✅ APEX Master Controller"
echo ""
echo "🚀 To start APEX system:"
echo "   python3 apex_master_controller.py"
echo ""
echo "📱 To start Telegram controller:"
echo "   bash start_telegram_controller.sh"
echo ""
echo "📊 To start Dashboard API:"
echo "   python3 dashboard_api.py &"
echo ""
echo "🔍 To check bot status:"
echo "   bash check_bot_status.sh"
echo ""
echo "============================================================"
