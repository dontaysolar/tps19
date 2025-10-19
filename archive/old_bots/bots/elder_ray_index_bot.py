#!/usr/bin/env python3
"""Elder Ray Index - Bull/Bear power indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class ElderRayIndexBot:
    def __init__(self):
        self.name = "Elder_Ray_Index"
        self.version = "1.0.0"
        self.enabled = True
        self.ema_period = 13
        self.metrics = {'signals': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.ema_period:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        
        # EMA
        ema = closes[-self.ema_period:].mean()  # Simplified
        
        # Bull Power = High - EMA
        bull_power = highs[-1] - ema
        
        # Bear Power = Low - EMA
        bear_power = lows[-1] - ema
        
        # Generate signal
        if bull_power > 0 and bear_power > 0:
            signal, confidence = 'BUY', 0.80
        elif bull_power < 0 and bear_power < 0:
            signal, confidence = 'SELL', 0.80
        elif bull_power > 0 and bear_power < bear_power:
            signal, confidence = 'BUY', 0.65
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {'bull_power': bull_power, 'bear_power': bear_power, 'ema': ema, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = ElderRayIndexBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
