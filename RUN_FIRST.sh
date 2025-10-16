#!/bin/bash
# TPS19 APEX Organism - First Run Script

clear
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        TPS19 APEX ORGANISM - BRINGING TO LIFE 🧬              ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Test organism
echo "🧬 Testing organism systems..."
echo ""
python3 test_organism_simple.py

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ ORGANISM IS ALIVE AND READY!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Configure .env file with your settings"
echo "3. Run full system: python3 tps19_apex.py"
echo ""
echo "Documentation:"
echo "- Quick start: TPS19_APEX_QUICKSTART.md"
echo "- Complete index: INDEX.md"
echo "- Capabilities: CAPABILITIES.md"
echo ""
