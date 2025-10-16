#!/bin/bash
# TPS19 APEX Organism - Installation Script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       TPS19 APEX ORGANISM - INSTALLATION                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install --user pandas numpy ccxt ta python-dotenv requests

echo ""
echo "✅ Dependencies installed"
echo ""

# Verify organism modules
echo "🔍 Verifying organism modules..."

if [ -d "modules/organism" ]; then
    echo "✅ Organism modules found"
    ls -la modules/organism/
else
    echo "❌ Organism modules not found"
    exit 1
fi

echo ""

# Test organism
echo "🧬 Testing organism initialization..."
python3 test_organism_simple.py

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║             INSTALLATION COMPLETE ✅                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Configure .env file with your API keys"
echo "2. Run: python3 test_organism_live.py (requires pandas)"
echo "3. Run: python3 tps19_apex.py (full system)"
echo ""
