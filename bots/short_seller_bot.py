#!/usr/bin/env python3
"""
Short Seller Bot - Bear Market Trader
Profits from downturns
Part of APEX AI Trading System - ATN
"""

import os, sys, json
from datetime import datetime
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt, numpy as np
except ImportError:
    os.system("pip3 install --break-system-packages ccxt numpy -q")
    import ccxt, numpy as np

class ShortSellerBot:
    def __init__(self, exchange_config: Dict = None):
        self.name, self.version = "ShortSellerBot", "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({'apiKey': os.getenv('EXCHANGE_API_KEY'), 'secret': os.getenv('EXCHANGE_API_SECRET'), 'enableRateLimit': True})
        
        self.config = {'bear_threshold': -0.03, 'rsi_overbought': 70, 'volume_confirmation': 1.2}
        self.metrics = {'short_trades': 0, 'short_profit': 0.0}
    
    def detect_short_opportunity(self, symbol: str) -> Dict:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=50)
            if len(ohlcv) < 50: return {}
            
            closes = [c[4] for c in ohlcv]
            momentum = (closes[-1] - closes[-10]) / closes[-10]
            
            # Calculate RSI
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas[-14:]]
            losses = [-d if d < 0 else 0 for d in deltas[-14:]]
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi = 100 - (100 / (1 + rs))
            
            short_signal = momentum < self.config['bear_threshold'] and rsi > self.config['rsi_overbought']
            
            return {'symbol': symbol, 'short_opportunity': short_signal, 'momentum': momentum, 'rsi': rsi, 'signal': 'SHORT' if short_signal else 'HOLD', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            return {}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'metrics': self.metrics}

if __name__ == '__main__':
    bot = ShortSellerBot()
    print("📉 Short Seller Bot - Test\n")
    result = bot.detect_short_opportunity('BTC/USDT')
    if result: print(f"Short opportunity: {result['short_opportunity']}, RSI: {result.get('rsi', 0):.1f}")
