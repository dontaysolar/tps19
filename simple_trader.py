#!/usr/bin/env python3
import ccxt, os, time, requests
from dotenv import load_dotenv
from datetime import datetime

# Load env from .env without overriding already-set variables
load_dotenv(override=False)

exchange = ccxt.cryptocom({
    'apiKey': os.environ['EXCHANGE_API_KEY'],
    'secret': os.environ['EXCHANGE_API_SECRET']
})

def send_telegram(msg):
    requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
                 json={'chat_id': os.environ['TELEGRAM_CHAT_ID'], 'text': msg}, timeout=5)

send_telegram(f"🚀 SIMPLE TRADER ONLINE\n\nTime: {datetime.now()}\nMonitoring BTC/USDT\nWill trade when conditions are right...")

cycle = 0
while True:
    cycle += 1
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        change = ticker.get('percentage', 0)
        
        print(f"Cycle {cycle}: BTC ${price:.2f} ({change:+.2f}%)")
        
        if cycle % 10 == 0:
            send_telegram(f"💓 Still monitoring...\nCycle: {cycle}\nBTC: ${price:.2f}")
        
        time.sleep(30)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
