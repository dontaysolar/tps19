#!/bin/bash
# Start Telegram Controller in background

cd ~/tps19

echo "🤖 Starting Telegram Controller..."

# Kill existing session if any
tmux kill-session -t telegram 2>/dev/null || true

# Start in tmux
tmux new-session -d -s telegram "cd ~/tps19 && python3 telegram_controller.py 2>&1 | tee logs/telegram_$(date +%Y%m%d_%H%M%S).log"

sleep 2

if tmux has-session -t telegram 2>/dev/null; then
    echo "✅ Telegram Controller started!"
    echo ""
    echo "📱 You can now send commands via Telegram!"
    echo ""
    echo "Try sending: 'help' to your bot"
    echo ""
    echo "📊 To view controller console:"
    echo "   tmux attach -t telegram"
    echo "   (Press Ctrl+B then D to detach)"
else
    echo "❌ Failed to start controller"
fi
