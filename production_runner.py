#!/usr/bin/env python3
"""
PRODUCTION RUNNER - Autonomous Trading System
Runs continuously, monitors health, executes trades
"""
import os, sys, time, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, 'bots')

print("="*80)
print("🚀 APEX PRODUCTION RUNNER - STARTING")
print("="*80)

# Test imports
try:
    from god_bot import GODBot
    from king_bot import KINGBot
    from oracle_ai import OracleAI
    from crash_shield_bot import CrashShieldBot
    from conflict_resolver_bot import ConflictResolverBot
    print("✅ Core bots imported")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Initialize
god = GODBot()
king = KINGBot()
oracle = OracleAI()
crash = CrashShieldBot()
conflict = ConflictResolverBot()

print(f"✅ {god.name} initialized")
print(f"✅ {king.name} initialized - Profile: {king.active_profile}")
print(f"✅ {oracle.name} initialized")
print(f"✅ {crash.name} initialized")
print(f"✅ {conflict.name} initialized")

# Send Telegram notification
import requests
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                     json={'chat_id': chat_id, 'text': msg}, timeout=10)
    except: pass

send_telegram(f"""✅ APEX SYSTEM ONLINE

🛐 GOD BOT: Active
👑 KING BOT: {king.active_profile} mode
📡 Oracle AI: Ready
🛡️ Crash Shield: Armed
⚖️ Conflict Resolver: Ready

Trading pairs: BTC, ETH, SOL, ADA
Max position: $0.50
Status: MONITORING MARKETS

Will notify on first trade opportunity...""")

print("\n🔄 Starting trading cycle...")

# Trading cycle
cycle = 0
while True:
    cycle += 1
    print(f"\n{'='*80}")
    print(f"CYCLE #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    try:
        # 1. Check market conditions
        print("1️⃣ GOD BOT analyzing market...")
        market_state = god.analyze_market_state(['BTC/USDT', 'ETH/USDT'])
        print(f"   Market Regime: {market_state.get('regime', 'UNKNOWN')}")
        
        # 2. Check for crisis
        crisis = god.crisis_intervention()
        if crisis.get('intervention'):
            print(f"   🚨 CRISIS INTERVENTION: {crisis['action']}")
            send_telegram(f"🚨 CRISIS: {crisis['reason']}\nTrading HALTED")
            time.sleep(300)  # Wait 5 minutes
            continue
        
        # 3. Get Oracle prediction
        print("2️⃣ Oracle AI predicting...")
        prediction = oracle.predict_price_movement('BTC/USDT')
        if prediction:
            print(f"   BTC Direction: {prediction['direction']} ({prediction['confidence']*100:.0f}% confidence)")
        
        # 4. Check crash shield
        print("3️⃣ Crash Shield checking...")
        crash_check = crash.check_market_status()
        if crash_check.get('crash_detected'):
            print(f"   🛡️ CRASH DETECTED: Trading paused")
            send_telegram(f"🛡️ Market crash detected\n{crash_check['reason']}\nTrading paused")
            time.sleep(300)
            continue
        
        print("   ✅ No crash detected")
        
        # 5. Log cycle
        print(f"\n✅ Cycle #{cycle} complete - Next cycle in 60s")
        
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        send_telegram("🛑 APEX System shutting down")
        break
    except Exception as e:
        print(f"❌ Cycle error: {e}")
        send_telegram(f"⚠️ Error in cycle #{cycle}: {e}")
        time.sleep(60)

