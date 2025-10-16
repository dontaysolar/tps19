#!/bin/bash
# TPS19 APEX - Complete Installation Script

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   TPS19 APEX ORGANISM - COMPLETE INSTALLATION                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📦 Installing Python dependencies..."
echo ""

# Core dependencies (always install)
echo "${GREEN}[1/4]${NC} Core organism dependencies..."
pip3 install --user python-dotenv psutil requests

# Data & ML dependencies
echo ""
echo "${GREEN}[2/4]${NC} Data & ML dependencies (this may take a few minutes)..."
pip3 install --user pandas numpy scipy scikit-learn ta

# Exchange & API dependencies
echo ""
echo "${GREEN}[3/4]${NC} Exchange & API dependencies..."
pip3 install --user ccxt Flask Flask-CORS Flask-SocketIO python-socketio eventlet websockets

# Optional: Deep learning (large download)
echo ""
echo "${YELLOW}[4/4]${NC} Deep learning (optional - large download)..."
read -p "Install TensorFlow for deep learning? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    pip3 install --user tensorflow
    echo "✅ TensorFlow installed"
else
    echo "⏭️  Skipped TensorFlow (you can install later with: pip install tensorflow)"
fi

echo ""
echo "=" * 60
echo "✅ PYTHON INSTALLATION COMPLETE!"
echo "=" * 60

# Dashboard dependencies
echo ""
echo "📊 Installing dashboard dependencies..."
echo ""

if [ -d "dashboard" ]; then
    cd dashboard
    echo "${GREEN}Installing Node.js packages...${NC}"
    npm install
    
    echo ""
    echo "🔨 Building dashboard..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Dashboard build successful!"
    else
        echo ""
        echo "⚠️  Dashboard build failed (check errors above)"
    fi
    
    cd ..
else
    echo "⚠️  Dashboard directory not found - skipping"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              INSTALLATION COMPLETE! ✅                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🧪 Test the organism:"
echo "   python3 test_complete_system.py"
echo ""
echo "🚀 Run the organism:"
echo "   python3 tps19_apex.py"
echo ""
echo "📊 Run the dashboard:"
echo "   Terminal 1: python3 api_server.py"
echo "   Terminal 2: cd dashboard && npm run dev"
echo ""
echo "🎉 You're ready to trade!"
echo ""
