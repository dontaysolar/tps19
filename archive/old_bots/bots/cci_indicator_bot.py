#!/usr/bin/env python3
"""CCI (Commodity Channel Index) - Momentum indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class CCIIndicatorBot:
    def __init__(self):
        self.name = "CCI_Indicator"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 20
        self.constant = 0.015
        self.metrics = {'signals': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        recent = ohlcv[-self.period:]
        typical_prices = np.array([(c[2] + c[3] + c[4]) / 3 for c in recent])
        
        sma = typical_prices.mean()
        mean_deviation = np.mean(np.abs(typical_prices - sma))
        
        cci = (typical_prices[-1] - sma) / (self.constant * mean_deviation) if mean_deviation > 0 else 0
        
        if cci > 100:
            signal, confidence = 'SELL', 0.75
        elif cci < -100:
            signal, confidence = 'BUY', 0.75
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {'cci': cci, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = CCIIndicatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
