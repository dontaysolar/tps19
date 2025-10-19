#!/usr/bin/env python3
"""ATR Bot - Average True Range volatility indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class AverageTrueRangeBot:
    def __init__(self):
        self.name = "Average_True_Range"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 14
        self.metrics = {'calculations': 0}
    
    def calculate_atr(self, ohlcv: List) -> Dict:
        """Calculate ATR"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # True Range
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]), 
                                 abs(lows[1:] - closes[:-1])))
        
        # ATR
        atr = tr[-self.period:].mean()
        atr_pct = (atr / closes[-1]) * 100
        
        # Volatility state
        if atr_pct > 5:
            volatility = 'HIGH'
        elif atr_pct > 2:
            volatility = 'MEDIUM'
        else:
            volatility = 'LOW'
        
        self.metrics['calculations'] += 1
        
        return {
            'atr': atr,
            'atr_pct': atr_pct,
            'volatility': volatility,
            'current_price': closes[-1],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'period': self.period, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = AverageTrueRangeBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
