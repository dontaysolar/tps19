#!/bin/bash
################################################################################
# TPS19 - UNIFIED LAUNCHER
# Starts trading system + web UI
################################################################################

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                    🚀 TPS19 LAUNCHER                             ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.8+ and try again."
    exit 1
fi

# Show options
echo "Choose how to run TPS19:"
echo ""
echo "1) Trading System Only (console)"
echo "2) Web Dashboard Only (Streamlit)"
echo "3) Both (System + Dashboard)"
echo "4) API Server Only"
echo ""
read -p "Select option [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting TPS19 Trading System..."
        echo ""
        python3 tps19_main.py
        ;;
    2)
        echo ""
        echo "🌐 Starting TPS19 Web Dashboard..."
        echo "   Dashboard will open in your browser"
        echo "   URL: http://localhost:8501"
        echo ""
        ~/.local/bin/streamlit run streamlit_dashboard.py
        ;;
    3)
        echo ""
        echo "🚀 Starting TPS19 Complete Platform..."
        echo ""
        echo "   API Server: http://localhost:8000"
        echo "   Dashboard: http://localhost:8501"
        echo ""
        
        # Start API in background
        python3 api_server.py &
        API_PID=$!
        echo "   ✅ API Server started (PID: $API_PID)"
        
        # Wait a moment for API to start
        sleep 2
        
        # Start dashboard
        echo "   ✅ Starting Dashboard..."
        ~/.local/bin/streamlit run streamlit_dashboard.py
        
        # Cleanup on exit
        kill $API_PID 2>/dev/null
        ;;
    4)
        echo ""
        echo "🔌 Starting API Server Only..."
        echo "   API: http://localhost:8000"
        echo ""
        python3 api_server.py
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac
