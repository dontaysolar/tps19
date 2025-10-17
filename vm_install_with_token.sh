#!/bin/bash
# TPS19 VM Installation Script - For Private Repository
# Usage: bash vm_install_with_token.sh YOUR_GITHUB_TOKEN

GITHUB_TOKEN="$1"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ ERROR: GitHub token required"
    echo ""
    echo "Usage: bash vm_install_with_token.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "Get token from: https://github.com/settings/tokens/new"
    echo "Need 'repo' permission"
    exit 1
fi

echo "============================================================"
echo "🚀 TPS19 INSTALLATION - STARTING"
echo "============================================================"
echo ""

cd ~

# Clean up any previous attempts
echo "🧹 Cleaning up previous installations..."
rm -rf tps19

# Clone using token
echo "📥 Cloning repository (private access)..."
git clone https://${GITHUB_TOKEN}@github.com/dontaysolar/tps19.git

if [ ! -d "tps19" ]; then
    echo "❌ ERROR: Failed to clone repository"
    echo "   Check your token has 'repo' permission"
    exit 1
fi

cd tps19

echo "✅ Repository cloned successfully!"
echo ""

# Install Python dependencies
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip -q

echo "⏳ Installing Python packages (10-12 minutes)..."
echo "   This includes TensorFlow - please be patient!"
echo ""

pip3 install -q numpy pandas scikit-learn
pip3 install -q tensorflow
pip3 install -q redis python-dotenv requests
pip3 install -q google-auth google-auth-oauthlib google-api-python-client
pip3 install -q python-telegram-bot

# Create directories
echo "📁 Creating directories..."
mkdir -p data/models data/databases logs config

# Make scripts executable
chmod +x *.sh *.py 2>/dev/null

# Create .env file
echo "📝 Creating configuration file..."
cat > .env << 'ENVEOF'
# TPS19 Production Configuration
EXCHANGE_API_KEY=YOUR_CRYPTO_COM_API_KEY
EXCHANGE_API_SECRET=YOUR_CRYPTO_COM_SECRET

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

echo ""
echo "============================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "============================================================"
echo ""
echo "📝 NEXT STEPS:"
echo ""
echo "1. Add your Crypto.com API keys:"
echo "   nano .env"
echo "   (Replace YOUR_CRYPTO_COM_API_KEY with real keys)"
echo "   (Press Ctrl+X, then Y, then Enter to save)"
echo ""
echo "2. Run comprehensive validation:"
echo "   python3 comprehensive_test_suite.py"
echo ""
echo "3. Test Telegram (you'll get a message!):"
echo "   python3 test_telegram.py"
echo ""
echo "4. Start trading bot:"
echo "   python3 tps19_main.py"
echo ""
echo "5. Run in background (keeps running):"
echo "   tmux new -s tps19"
echo "   python3 tps19_main.py"
echo "   # Press Ctrl+B then D to detach"
echo ""
echo "============================================================"
