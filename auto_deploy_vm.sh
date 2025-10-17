#!/bin/bash
# TPS19 ONE-PASTE AUTOMATIC VM DEPLOYMENT
# Run this ON YOUR VM after connecting via SSH

set -e
trap 'echo "❌ Error on line $LINENO"' ERR

echo "============================================================"
echo "🚀 TPS19 AUTOMATIC VM SETUP & DEPLOYMENT"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✅${NC} $1"; }
log_step() { echo -e "${YELLOW}▶${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }

# Step 1: Update system
log_step "Step 1/8: Updating system..."
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -yqq
log_info "System updated"
echo ""

# Step 2: Install prerequisites
log_step "Step 2/8: Installing prerequisites..."
sudo apt-get install -y -qq git unzip python3-pip python3-dev build-essential curl
log_info "Prerequisites installed"
echo ""

# Step 3: Clone repository from GitHub
log_step "Step 3/8: Cloning TPS19 from GitHub..."
cd ~
if [ -d "tps19" ]; then
    log_info "TPS19 directory exists, removing old version..."
    rm -rf tps19
fi

git clone https://github.com/dontaysolar/tps19.git
cd tps19
log_info "Repository cloned"
echo ""

# Step 4: Upgrade pip
log_step "Step 4/8: Upgrading pip..."
python3 -m pip install --upgrade pip --quiet
log_info "pip upgraded"
echo ""

# Step 5: Install Python dependencies
log_step "Step 5/8: Installing Python dependencies (this may take 5-10 minutes)..."
log_info "Installing numpy, pandas, scikit-learn..."
pip3 install --quiet numpy>=1.24.0 pandas>=2.0.0 scikit-learn>=1.3.0

log_info "Installing TensorFlow (this is large, please wait)..."
pip3 install --quiet tensorflow>=2.13.0

log_info "Installing Redis and Google API libraries..."
pip3 install --quiet redis>=5.0.0
pip3 install --quiet google-auth>=2.22.0 google-auth-oauthlib>=1.0.0 google-api-python-client>=2.95.0

log_info "Installing utilities..."
pip3 install --quiet python-dotenv>=1.0.0 requests>=2.31.0

log_info "All Python dependencies installed"
echo ""

# Step 6: Create necessary directories
log_step "Step 6/8: Creating directories..."
mkdir -p ~/tps19/data/models
mkdir -p ~/tps19/data/databases
mkdir -p ~/tps19/logs
mkdir -p ~/tps19/config
chmod -R 755 ~/tps19
log_info "Directories created"
echo ""

# Step 7: Create configuration file
log_step "Step 7/8: Creating configuration file..."
cat > ~/tps19/.env << 'ENVEOF'
# TPS19 Configuration
# IMPORTANT: Edit this file and add your Crypto.com API keys!

# Exchange API Keys (REQUIRED - GET FROM CRYPTO.COM)
EXCHANGE_API_KEY=YOUR_CRYPTO_COM_API_KEY_HERE
EXCHANGE_API_SECRET=YOUR_CRYPTO_COM_SECRET_HERE

# Database
DATABASE_URL=sqlite:///data/tps19.db

# Trading Configuration
TPS19_ENV=production
MAX_POSITION_SIZE=1000
RISK_LEVEL=moderate
TRADING_ENABLED=true

# AI/ML Configuration
ENABLE_LSTM_PREDICTION=true
ENABLE_GAN_SIMULATION=false
ENABLE_SELF_LEARNING=true

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Optional: Telegram (if you want notifications)
# TELEGRAM_BOT_TOKEN=
# TELEGRAM_CHAT_ID=

# Optional: Google Sheets (if you want dashboard)
# GOOGLE_SHEETS_SPREADSHEET_ID=
ENVEOF

log_info "Configuration file created at ~/tps19/.env"
echo ""

# Step 8: Run validation
log_step "Step 8/8: Running validation tests..."
cd ~/tps19
python3 validate_phase1.py 2>&1 | tee validation_results.txt

echo ""
echo "============================================================"
log_info "🎉 INSTALLATION COMPLETE!"
echo "============================================================"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  EDIT YOUR API KEYS (REQUIRED!):"
echo "   nano ~/tps19/.env"
echo "   Replace YOUR_CRYPTO_COM_API_KEY_HERE with your actual key"
echo "   Press Ctrl+X, then Y, then Enter to save"
echo ""
echo "2️⃣  TEST THE BOT:"
echo "   cd ~/tps19"
echo "   python3 tps19_main.py test"
echo ""
echo "3️⃣  START TRADING:"
echo "   python3 tps19_main.py"
echo ""
echo "4️⃣  RUN IN BACKGROUND (keeps running even if you disconnect):"
echo "   sudo apt install -y tmux"
echo "   tmux new -s tps19"
echo "   python3 tps19_main.py"
echo "   # Press Ctrl+B then D to detach"
echo "   # Reconnect anytime with: tmux attach -t tps19"
echo ""
echo "5️⃣  AUTO-START ON REBOOT:"
echo "   sudo cp ~/tps19/services/tps19_main.service /etc/systemd/system/"
echo "   sudo systemctl enable tps19_main"
echo "   sudo systemctl start tps19_main"
echo ""
echo "============================================================"
echo "📊 Installation Summary:"
echo "   Location: ~/tps19"
echo "   Python: $(python3 --version)"
echo "   Status: ✅ Ready to configure and start"
echo "============================================================"
echo ""
