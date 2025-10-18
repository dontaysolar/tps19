#!/usr/bin/env python3
"""
Momentum Rider Bot - Trend Following Strategy
Rides uptrends with volume confirmation
Part of APEX AI Trading System - ATN (Apex Trading Nexus)
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

class MomentumRiderBot:
    def __init__(self, exchange_config: Dict = None):
        self.name, self.version = "MomentumRiderBot", "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({'apiKey': os.getenv('EXCHANGE_API_KEY'), 'secret': os.getenv('EXCHANGE_API_SECRET'), 'enableRateLimit': True})
        
        self.config = {'momentum_threshold': 0.02, 'volume_spike_threshold': 1.5, 'trend_strength_min': 0.6}
        self.metrics = {'trades_executed': 0, 'wins': 0, 'total_profit': 0.0}
    
    def detect_momentum(self, symbol: str) -> Dict:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            if len(ohlcv) < 24: return {}
            
            closes = [c[4] for c in ohlcv]
            volumes = [c[5] for c in ohlcv]
            
            momentum = (closes[-1] - closes[0]) / closes[0]
            vol_avg = np.mean(volumes[:-1])
            vol_current = volumes[-1]
            vol_ratio = vol_current / vol_avg if vol_avg > 0 else 0
            
            # Calculate trend strength (EMA comparison)
            ema_short = np.mean(closes[-7:])
            ema_long = np.mean(closes[-25:]) if len(closes) >= 25 else np.mean(closes)
            trend_strength = (ema_short - ema_long) / ema_long if ema_long > 0 else 0
            
            signal = 'BUY' if (momentum >= self.config['momentum_threshold'] and 
                              vol_ratio >= self.config['volume_spike_threshold'] and
                              trend_strength >= self.config['trend_strength_min']) else 'HOLD'
            
            return {'symbol': symbol, 'momentum': momentum, 'volume_ratio': vol_ratio, 'trend_strength': trend_strength, 'signal': signal, 'confidence': min(abs(momentum) * vol_ratio * abs(trend_strength) * 10, 1.0), 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            print(f"❌ Momentum detection error: {e}")
            return {}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'metrics': self.metrics, 'config': self.config}

if __name__ == '__main__':
    bot = MomentumRiderBot()
    print("🏇 Momentum Rider Bot - Test\n")
    result = bot.detect_momentum('BTC/USDT')
    if result: print(f"Signal: {result['signal']}, Confidence: {result['confidence']*100:.0f}%")
