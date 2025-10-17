#!/usr/bin/env python3
"""Test Telegram Bot Connection and Send Test Message"""

import requests
import json
import os
from datetime import datetime

def test_telegram_bot():
    """Test Telegram bot and send test message"""
    
    print("="*70)
    print("📱 TELEGRAM BOT CONNECTION TEST")
    print("="*70)
    print()
    
    # Load credentials from .env
    bot_token = "7289126201:AAHaWTLKxpddtbJ9oa4hGdvKaq0mypqU75Y"
    chat_id = "7517400013"
    
    print(f"🔑 Bot Token: {bot_token[:20]}...")
    print(f"💬 Chat ID: {chat_id}")
    print()
    
    # Test 1: Get bot info
    print("Test 1: Checking bot authentication...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"  ✅ Bot authenticated successfully!")
                print(f"     Bot Name: {bot_info.get('first_name')}")
                print(f"     Bot Username: @{bot_info.get('username')}")
                print(f"     Bot ID: {bot_info.get('id')}")
            else:
                print(f"  ❌ Bot authentication failed: {data}")
                return False
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print()
    
    # Test 2: Send test message
    print("Test 2: Sending test message...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = f"""🤖 TPS19 Bot Test Message

✅ Bot Successfully Connected!

🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 System: TPS19 Trading Bot
📊 Status: Testing Phase

This confirms your Telegram bot is working correctly.
You will receive trading notifications here.

🚀 Ready to start trading!
"""
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print(f"  ✅ Test message sent successfully!")
                print(f"     Message ID: {data['result'].get('message_id')}")
                print(f"     📱 Check your Telegram app!")
            else:
                print(f"  ❌ Failed to send: {data}")
                return False
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print()
    print("="*70)
    print("✅ TELEGRAM TEST COMPLETE - CHECK YOUR PHONE!")
    print("="*70)
    print()
    
    return True

if __name__ == '__main__':
    success = test_telegram_bot()
    sys.exit(0 if success else 1)
