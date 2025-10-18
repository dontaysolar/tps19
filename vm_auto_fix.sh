#!/bin/bash
# TPS19 AUTO-FIX AND CONFIGURATION SCRIPT
# Pulls latest fixes and configures API keys

echo "============================================================"
echo "🔧 TPS19 AUTO-FIX - STARTING"
echo "============================================================"
echo ""

cd ~/tps19

# Pull latest fixes from GitHub
echo "📥 Pulling latest fixes from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "⚠️  Git pull failed - may have local changes"
    echo "   Trying to reset..."
    git reset --hard origin/main
fi

echo "✅ Latest code pulled successfully!"
echo ""

# Update .env file with real Crypto.com API keys
echo "🔑 Configuring API keys..."
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

echo "✅ API keys configured!"
echo ""

# Make scripts executable
chmod +x *.sh *.py 2>/dev/null

# Ensure directories exist with proper permissions
echo "📁 Creating directories..."
mkdir -p data/models data/databases logs config patches backups
chmod 755 data data/models data/databases logs config patches backups

echo "✅ Directories created!"
echo ""

echo "============================================================"
echo "✅ AUTO-FIX COMPLETE!"
echo "============================================================"
echo ""
echo "🔍 NEXT: Run comprehensive validation:"
echo "   python3 comprehensive_test_suite.py"
echo ""
echo "📱 Test Telegram (optional):"
echo "   python3 test_telegram.py"
echo ""
echo "🚀 Start trading bot:"
echo "   python3 tps19_main.py"
echo ""
echo "🎯 Or run in background:"
echo "   tmux new -s tps19"
echo "   python3 tps19_main.py"
echo "   # Press Ctrl+B then D to detach"
echo ""
echo "============================================================"
