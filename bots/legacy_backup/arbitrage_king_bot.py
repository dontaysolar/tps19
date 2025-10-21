#!/usr/bin/env python3
"""
Arbitrage King Bot - Cross-Market Arbitrage
Exploits price differences
Part of APEX AI Trading System - ATN
"""

import os, sys, json
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class ArbitrageKingBot:
    def __init__(self, exchange_config=None):
        self.name, self.version = "ArbitrageKingBot", "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({'apiKey': os.getenv('EXCHANGE_API_KEY'), 'secret': os.getenv('EXCHANGE_API_SECRET'), 'enableRateLimit': True})
        
        self.config = {'min_spread_pct': 0.5, 'max_execution_time_sec': 10}
        self.metrics = {'arb_opportunities': 0, 'arb_profit': 0.0}
    
    def detect_arbitrage(self, symbol: str) -> Dict:
        try:
            orderbook = self.exchange.fetch_order_book(symbol)
            
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else 0
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else 0
            
            spread_pct = ((best_ask - best_bid) / best_bid) * 100 if best_bid > 0 else 0
            
            opportunity = spread_pct >= self.config['min_spread_pct']
            
            return {'symbol': symbol, 'opportunity': opportunity, 'spread_pct': spread_pct, 'bid': best_bid, 'ask': best_ask, 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            print(f"❌ Arb detection error: {e}")
            return {}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'metrics': self.metrics}

if __name__ == '__main__':
    bot = ArbitrageKingBot()
    print("💎 Arbitrage King Bot - Test\n")
    result = bot.detect_arbitrage('BTC/USDT')
    if result: print(f"Opportunity: {result['opportunity']}, Spread: {result.get('spread_pct', 0):.2f}%")
