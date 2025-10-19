#!/usr/bin/env python3
"""Awesome Oscillator Bot - Momentum indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class AwesomeOscillatorBot:
    def __init__(self):
        self.name = "Awesome_Oscillator"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'signals': 0}
    
    def calculate_ao(self, ohlcv: List) -> Dict:
        """Calculate Awesome Oscillator"""
        if len(ohlcv) < 34:
            return {'error': 'Insufficient data'}
        
        median_prices = np.array([(c[2] + c[3]) / 2 for c in ohlcv])
        
        # 5-period and 34-period SMAs
        sma5 = median_prices[-5:].mean()
        sma34 = median_prices[-34:].mean()
        
        ao = sma5 - sma34
        
        # Check previous value for signal
        if len(median_prices) > 34:
            prev_sma5 = median_prices[-6:-1].mean()
            prev_sma34 = median_prices[-35:-1].mean()
            prev_ao = prev_sma5 - prev_sma34
            
            if ao > 0 and prev_ao <= 0:
                signal, confidence = 'BUY', 0.75
                reason = "AO crossed zero line upward"
            elif ao < 0 and prev_ao >= 0:
                signal, confidence = 'SELL', 0.75
                reason = "AO crossed zero line downward"
            elif ao > prev_ao:
                signal, confidence = 'BUY', 0.60
                reason = "AO increasing"
            else:
                signal, confidence = 'SELL', 0.60
                reason = "AO decreasing"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Insufficient history"
        
        self.metrics['signals'] += 1
        
        return {
            'ao': ao,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = AwesomeOscillatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
