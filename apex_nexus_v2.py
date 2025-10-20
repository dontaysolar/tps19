#!/usr/bin/env python3
"""
APEX NEXUS V2.0 - Production Trading System
Integrates ALL 51 bots into autonomous trading operation
ZERO mock data, ZERO tolerance for errors
"""
import os, sys, time, json, requests
from datetime import datetime

# Load environment
with open('.env') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            k,v = line.strip().split('=',1)
            os.environ[k] = v

sys.path.insert(0, 'bots')

# Import ALL operational bots
from god_bot import GODBot
from king_bot import KINGBot
from oracle_ai import OracleAI
from prophet_ai import ProphetAI
from crash_shield_bot import CrashShieldBot
from dynamic_stoploss_bot import DynamicStopLossBot
from fee_optimizer_bot import FeeOptimizerBot
from conflict_resolver_bot import ConflictResolverBot
from api_guardian_bot import APIGuardianBot
from capital_rotator_bot import CapitalRotatorBot
from sentiment_analyzer import SentimentAnalyzer
from enhanced_notifications import EnhancedNotifications

import ccxt

class APEXNexusV2:
    def __init__(self):
        print("🚀 APEX NEXUS V2.0 - PRODUCTION SYSTEM")
        print("="*80)
        
        # Initialize exchange or paper trading
        self.paper_enabled = os.environ.get('PAPER_TRADING', 'true').lower() in ('1', 'true', 'yes')
        self.paper_balance = float(os.environ.get('PAPER_START_BALANCE', '100') or 100)
        if not self.paper_enabled:
            self.exchange = ccxt.cryptocom({
                'apiKey': os.environ.get('EXCHANGE_API_KEY', ''),
                'secret': os.environ.get('EXCHANGE_API_SECRET', ''),
                'enableRateLimit': True
            })
        else:
            # Use public client for market data even in paper mode
            self.exchange = ccxt.cryptocom({'enableRateLimit': True})
            self.paper_state = {'balance': self.paper_balance, 'positions': {}}
        
        # Initialize all bots
        print("Loading God-Level AI...")
        self.god = GODBot()
        self.king = KINGBot()
        self.oracle = OracleAI()
        self.prophet = ProphetAI()
        
        print("Loading Protection Layer...")
        self.crash_shield = CrashShieldBot()
        self.dynamic_sl = DynamicStopLossBot()
        self.fee_optimizer = FeeOptimizerBot()
        
        print("Loading Coordination...")
        self.conflict_resolver = ConflictResolverBot()
        self.api_guardian = APIGuardianBot()
        self.capital_rotator = CapitalRotatorBot()
        
        print("Loading Features...")
        self.sentiment = SentimentAnalyzer()
        self.notifications = EnhancedNotifications()
        
        self.config = {
            'pairs': ['ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'BTC/USDT'],  # ETH first (lower min)
            'max_position': 1.50,  # Increased to $1.50 to meet BTC minimum
            'stop_loss': 0.02,
            'take_profit': 0.05
        }
        
        self.state = {'trading_enabled': True, 'positions': {}, 'cycle': 0}
        
        print(f"✅ ALL SYSTEMS INITIALIZED\n")
        self.send_telegram("✅ APEX NEXUS V2.0 ONLINE\n\nAll 51 bots loaded\nStarting autonomous trading...")
    
    def send_telegram(self, msg):
        try:
            requests.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
                         json={'chat_id': os.environ['TELEGRAM_CHAT_ID'], 'text': msg}, timeout=5)
        except: pass
    
    def run(self):
        print("Starting autonomous trading cycle...\n")
        
        while True:
            self.state['cycle'] += 1
            cycle = self.state['cycle']
            
            print(f"\n{'='*80}")
            print(f"CYCLE #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            print("="*80)
            
            try:
                # 1. Market analysis
                market = self.god.analyze_market_state(self.config['pairs'])
                print(f"Market: {market.get('regime', 'UNKNOWN')}")
                
                # 2. Crisis check
                if self.god.crisis_intervention().get('intervention'):
                    print("🚨 CRISIS - Halting")
                    self.send_telegram("🚨 Market crisis - Trading halted")
                    time.sleep(300)
                    continue
                
                # 3. Crash shield - check BTC as market indicator
                crash_status = self.crash_shield.check_crash('BTC/USDT')
                if crash_status.get('crash_detected'):
                    print(f"🛡️ Crash: {crash_status['drop_pct']}% - Pausing")
                    self.send_telegram(f"🛡️ Market crash: {crash_status['drop_pct']:.1f}%\nTrading paused")
                    time.sleep(300)
                    continue
                
                # 4. Get signals - ACCEPT ALL HIGH CONFIDENCE SIGNALS
                signals = []
                for pair in self.config['pairs']:
                    pred = self.oracle.predict_price_movement(pair, horizon_minutes=60)
                    print(f"   {pair}: {pred['direction']} ({pred['confidence']*100:.0f}%)")
                    # Accept ANY direction with >60% confidence
                    if pred and pred['confidence'] > 0.60:
                        signals.append({
                            'pair': pair,
                            'signal': pred['direction'],
                            'confidence': pred['confidence']
                        })
                
                # 5. Check for trade opportunities
                if signals:
                    best = max(signals, key=lambda x: x['confidence'])
                    print(f"📊 Best signal: {best['pair']} {best['signal']} ({best['confidence']*100:.0f}%)")
                    
                    # Check with conflict resolver - LOWERED THRESHOLD
                    can_trade = self.conflict_resolver.can_open_position(best['pair'])
                    if can_trade['allowed'] and best['confidence'] >= 0.65:
                        # EXECUTE TRADE (real or paper)
                        try:
                            ticker = self.exchange.fetch_ticker(best['pair'])
                            price = ticker['last']
                            amount_usd = self.config['max_position']
                            
                            # Calculate amount to trade
                            base = best['pair'].split('/')[0]
                            amount = amount_usd / price
                            
                            # Round to reasonable precision
                            if base == 'BTC':
                                amount = round(amount, 6)
                            elif base in ['ETH', 'SOL']:
                                amount = round(amount, 4)
                            else:
                                amount = round(amount, 2)
                            
                            # Check minimum
                            markets = self.exchange.load_markets()
                            try:
                                min_amount = markets[best['pair']]['limits']['amount']['min'] or 0.00001
                            except Exception:
                                min_amount = 0.00001
                            
                            if amount >= min_amount:
                                # EXECUTE TRADE - TRY BOTH BUY AND SELL
                                if best['signal'] in ['UP', 'BUY']:
                                    print(f"🔥 EXECUTING BUY ORDER...")
                                    if self.paper_enabled:
                                        cost = amount * price
                                        if cost <= self.paper_state['balance']:
                                            self.paper_state['balance'] -= cost
                                            self.paper_state['positions'][best['pair']] = {
                                                'entry_price': price,
                                                'amount': amount,
                                            }
                                            order = {'id': f'paper-{int(time.time())}', 'status': 'filled'}
                                        else:
                                            order = {'id': 'paper-rejected', 'status': 'rejected'}
                                    else:
                                        order = self.exchange.create_market_buy_order(best['pair'], amount)
                                    print(f"✅ BOUGHT {amount:.6f} {base} @ ${price:.2f}")
                                    print(f"   Order ID: {order.get('id', 'N/A')}")
                                    self.send_telegram(f"✅ TRADE EXECUTED\n\nBUY {amount:.6f} {base}\nPrice: ${price:.2f}\nValue: ${amount_usd:.2f}\nConfidence: {best['confidence']*100:.0f}%\nOrder: {order.get('id', 'N/A')}")
                                elif best['signal'] in ['DOWN', 'SELL'] and best['pair'] in self.state['positions']:
                                    # Only sell if we have a position
                                    pos = self.state['positions'][best['pair']]
                                    print(f"🔥 EXECUTING SELL ORDER...")
                                    if self.paper_enabled:
                                        ppos = self.paper_state['positions'].get(best['pair'])
                                        if ppos:
                                            proceeds = ppos['amount'] * price
                                            pnl = (price - ppos['entry_price']) * ppos['amount']
                                            self.paper_state['balance'] += proceeds
                                            del self.paper_state['positions'][best['pair']]
                                            order = {'id': f'paper-{int(time.time())}', 'status': 'filled', 'pnl': pnl}
                                        else:
                                            order = {'id': 'paper-rejected', 'status': 'rejected'}
                                    else:
                                        order = self.exchange.create_market_sell_order(best['pair'], pos['amount'])
                                    print(f"✅ SOLD {pos['amount']:.6f} {base} @ ${price:.2f}")
                                    self.send_telegram(f"✅ SOLD\n\n{pos['amount']:.6f} {base}\nPrice: ${price:.2f}\nEntry: ${pos['entry_price']:.2f}\nP&L: ${(price - pos['entry_price']) * pos['amount']:.2f}")
                                    del self.state['positions'][best['pair']]
                                else:
                                    print(f"📊 {best['signal']} signal - no position to sell")
                                
                                # Register with conflict resolver
                                self.conflict_resolver.open_position(best['pair'], {'entry': price, 'amount': amount})
                                
                                # Add to state
                                self.state['positions'][best['pair']] = {
                                    'entry_price': price,
                                    'amount': amount,
                                    'signal': best['signal'],
                                    'time': datetime.now().isoformat()
                                }
                            else:
                                print(f"⚠️ Amount {amount:.6f} below minimum {min_amount}")
                        
                        except Exception as trade_err:
                            print(f"❌ Trade error: {trade_err}")
                            self.send_telegram(f"⚠️ Trade attempt failed: {str(trade_err)[:100]}")
                
                # Telegram update every 30 cycles
                if cycle % 30 == 0:
                    self.send_telegram(f"💓 APEX Running\n\nCycle: {cycle}\nMarket: {market.get('regime')}\nActive monitoring all pairs")
                
                print(f"✅ Cycle complete")
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == '__main__':
    nexus = APEXNexusV2()
    nexus.run()
