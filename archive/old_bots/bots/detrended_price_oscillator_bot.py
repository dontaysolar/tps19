#!/usr/bin/env python3
"""Detrended Price Oscillator - Removes trend to show cycles"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class DetrendedPriceOscillatorBot:
    def __init__(self):
        self.name = "Detrended_Price_Oscillator"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 20
        self.metrics = {'signals': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.period + 10:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # SMA displaced
        displacement = self.period // 2 + 1
        sma = np.array([closes[i-self.period:i].mean() for i in range(self.period, len(closes))])
        
        # DPO = Price - Displaced SMA
        dpo = closes[self.period:] - np.roll(sma, displacement)[:len(closes)-self.period]
        
        current_dpo = dpo[-1] if len(dpo) > 0 else 0
        
        if current_dpo > 0:
            signal, confidence = 'BUY', 0.65
        elif current_dpo < 0:
            signal, confidence = 'SELL', 0.65
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        return {'dpo': current_dpo, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = DetrendedPriceOscillatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
