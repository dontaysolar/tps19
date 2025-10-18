#!/bin/bash
# Quick bot status checker

echo "============================================================"
echo "🤖 TPS19 BOT STATUS CHECK"
echo "============================================================"
echo ""

# Check if tmux session exists
if tmux has-session -t tps19 2>/dev/null; then
    echo "✅ Bot is RUNNING"
    echo ""
    echo "📊 Session Info:"
    tmux list-sessions | grep tps19
    echo ""
    echo "📄 Recent logs:"
    echo "---"
    tail -n 20 ~/tps19/logs/bot_*.log 2>/dev/null | tail -20 || echo "No logs found yet"
    echo "---"
    echo ""
    echo "💻 To view live bot console:"
    echo "   tmux attach -t tps19"
    echo "   (Press Ctrl+B then D to detach)"
    echo ""
else
    echo "❌ Bot is NOT running"
    echo ""
    echo "🔍 Checking deployment log:"
    if [ -f ~/tps19_autonomous_deploy.log ]; then
        echo "Last 20 lines of deployment log:"
        echo "---"
        tail -n 20 ~/tps19_autonomous_deploy.log
        echo "---"
    else
        echo "No deployment log found"
    fi
    echo ""
    echo "🚀 To start bot:"
    echo "   cd ~/tps19 && bash autonomous_deploy.sh"
fi

echo "============================================================"
