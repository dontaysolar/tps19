#!/usr/bin/env python3
"""Relative Vigor Index Bot - Measures trend strength"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class RelativeVigorIndexBot:
    def __init__(self):
        self.name = "Relative_Vigor_Index"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 10
        self.metrics = {'signals': 0}
    
    def calculate_rvi(self, ohlcv: List) -> Dict:
        """Calculate RVI"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        opens = np.array([c[1] for c in ohlcv[-self.period:]])
        closes = np.array([c[4] for c in ohlcv[-self.period:]])
        highs = np.array([c[2] for c in ohlcv[-self.period:]])
        lows = np.array([c[3] for c in ohlcv[-self.period:]])
        
        # Numerator and denominator
        numerator = (closes - opens).mean()
        denominator = (highs - lows).mean()
        
        rvi = numerator / denominator if denominator != 0 else 0
        
        # Signal line (simplified)
        signal_line = rvi * 0.9
        
        if rvi > signal_line and rvi > 0:
            signal, confidence = 'BUY', 0.70
        elif rvi < signal_line and rvi < 0:
            signal, confidence = 'SELL', 0.70
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {
            'rvi': rvi,
            'signal_line': signal_line,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = RelativeVigorIndexBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
