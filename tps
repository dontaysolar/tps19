#!/bin/bash
source /opt/tps19/venv/bin/activate
clear
echo "==========================="
echo "     🧠 TPS19 LAUNCHER     "
echo "==========================="
echo "1. Start All Bots"
echo "2. Run Diagnostics"
echo "3. View Logs"
echo "4. Exit"
read -p "Select option: " opt

case $opt in
  1)
    echo "Launching all bots in screen..."
    screen -dmS tps python3 main.py
    ;;
  2)
    echo "🩺 Running diagnostics..."
    python3 diagnostics.py
    ;;
  3)
    echo "📜 Viewing logs..."
    tail -f logs/main.log
    ;;
  4)
    echo "Exiting TPS19"
    exit 0
    ;;
esac
