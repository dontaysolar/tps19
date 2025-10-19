#!/bin/bash
################################################################################
# TPS19 - QUICK START (INTEGRATED SYSTEM)
# Starts everything you need in one command
################################################################################

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                    🚀 TPS19 QUICK START 🚀                                   ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down all services..."
    kill $API_PID 2>/dev/null
    kill $DASHBOARD_PID 2>/dev/null
    kill $TPS19_PID 2>/dev/null
    echo "✅ Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install Python 3.8+ and try again."
    exit 1
fi

# Check Node (for web dashboard)
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Web dashboard will not be available."
    echo "   Install Node.js 18+ to use the web UI."
    WEB_AVAILABLE=false
else
    WEB_AVAILABLE=true
fi

echo "Select what to run:"
echo ""
echo "1) TPS19 Trading System Only (Paper Mode)"
echo "2) TPS19 + API Server"
echo "3) TPS19 + API Server + Web Dashboard (Full Stack)"
echo "4) Web Dashboard Only (requires API server running)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🧪 Starting TPS19 in Paper Trading Mode..."
        echo ""
        python3 tps19_integrated.py paper
        ;;
    
    2)
        echo ""
        echo "🚀 Starting TPS19 + API Server..."
        echo ""
        
        # Start API server in background
        python3 api_server.py &
        API_PID=$!
        echo "✅ API Server started (PID: $API_PID)"
        echo "   API: http://localhost:8000"
        
        # Wait for API to start
        sleep 2
        
        # Start TPS19
        echo ""
        echo "✅ Starting TPS19..."
        python3 tps19_integrated.py paper
        
        # Cleanup on exit
        kill $API_PID 2>/dev/null
        ;;
    
    3)
        if [ "$WEB_AVAILABLE" = false ]; then
            echo ""
            echo "❌ Node.js not available. Cannot start web dashboard."
            echo "   Install Node.js 18+ and try again."
            exit 1
        fi
        
        echo ""
        echo "🚀 Starting Full Stack (TPS19 + API + Web Dashboard)..."
        echo ""
        
        # Check if node_modules exists
        if [ ! -d "web-dashboard/node_modules" ]; then
            echo "📦 Installing web dashboard dependencies..."
            cd web-dashboard
            npm install
            cd ..
        fi
        
        # Start API server in background
        python3 api_server.py &
        API_PID=$!
        echo "✅ API Server started (PID: $API_PID)"
        echo "   API: http://localhost:8000"
        
        # Wait for API
        sleep 3
        
        # Start web dashboard in background
        cd web-dashboard
        npm run dev &
        DASHBOARD_PID=$!
        cd ..
        echo "✅ Web Dashboard started (PID: $DASHBOARD_PID)"
        echo "   Dashboard: http://localhost:3000"
        
        # Wait for dashboard
        sleep 5
        
        # Start TPS19
        echo ""
        echo "✅ Starting TPS19..."
        echo "   Open http://localhost:3000 in your browser"
        echo ""
        python3 tps19_integrated.py paper
        
        # Cleanup on exit
        kill $API_PID 2>/dev/null
        kill $DASHBOARD_PID 2>/dev/null
        ;;
    
    4)
        if [ "$WEB_AVAILABLE" = false ]; then
            echo ""
            echo "❌ Node.js not available. Cannot start web dashboard."
            exit 1
        fi
        
        echo ""
        echo "🌐 Starting Web Dashboard Only..."
        echo "   Make sure API server is running on port 8000"
        echo ""
        
        # Check if node_modules exists
        if [ ! -d "web-dashboard/node_modules" ]; then
            echo "📦 Installing web dashboard dependencies..."
            cd web-dashboard
            npm install
            cd ..
        fi
        
        cd web-dashboard
        npm run dev
        ;;
    
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
