#!/usr/bin/env python3
"""Mass Index Bot - Trend reversal detector"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MassIndexBot:
    def __init__(self):
        self.name = "Mass_Index"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 25
        self.metrics = {'signals': 0, 'reversals': 0}
    
    def calculate_mass_index(self, ohlcv: List) -> Dict:
        """Calculate Mass Index"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        
        # Range
        ranges = highs - lows
        
        # EMA of range
        ema = ranges[-9:].mean() if len(ranges) >= 9 else ranges.mean()
        
        # EMA of EMA (simplified)
        ema_ema = ema * 0.9
        
        # Mass Index
        if ema_ema > 0:
            mass_index = sum([ema / ema_ema for _ in range(min(self.period, len(ranges)))])
        else:
            mass_index = self.period
        
        # Reversal bulge
        if mass_index > 27:
            self.metrics['reversals'] += 1
            signal, confidence = 'REVERSAL', 0.75
            reason = "Mass Index bulge - reversal likely"
        elif mass_index < 26.5:
            signal, confidence = 'HOLD', 0.50
            reason = "No reversal signal"
        else:
            signal, confidence = 'CAUTION', 0.60
            reason = "Approaching reversal zone"
        
        self.metrics['signals'] += 1
        
        return {
            'mass_index': mass_index,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MassIndexBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
