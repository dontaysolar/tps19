#!/usr/bin/env python3
"""Williams %R - Momentum oscillator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class WilliamsRBot:
    def __init__(self):
        self.name = "Williams_R"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 14
        self.metrics = {'signals': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv[-self.period:]])
        lows = np.array([c[3] for c in ohlcv[-self.period:]])
        close = ohlcv[-1][4]
        
        highest_high = highs.max()
        lowest_low = lows.min()
        
        williams_r = ((highest_high - close) / (highest_high - lowest_low)) * -100 if (highest_high - lowest_low) > 0 else -50
        
        if williams_r < -80:
            signal, confidence = 'BUY', 0.75
        elif williams_r > -20:
            signal, confidence = 'SELL', 0.75
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {'williams_r': williams_r, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = WilliamsRBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
