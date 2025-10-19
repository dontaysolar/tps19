#!/usr/bin/env python3
"""Vortex Indicator Bot - Trend direction and strength"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class VortexIndicatorBot:
    def __init__(self):
        self.name = "Vortex_Indicator"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 14
        self.metrics = {'signals': 0}
    
    def calculate_vortex(self, ohlcv: List) -> Dict:
        """Calculate Vortex Indicator"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Vortex Movement
        vm_plus = np.abs(highs[1:] - lows[:-1])
        vm_minus = np.abs(lows[1:] - highs[:-1])
        
        # True Range
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]), 
                                 abs(lows[1:] - closes[:-1])))
        
        # VI
        vi_plus = vm_plus[-self.period:].sum() / tr[-self.period:].sum() if tr[-self.period:].sum() > 0 else 1
        vi_minus = vm_minus[-self.period:].sum() / tr[-self.period:].sum() if tr[-self.period:].sum() > 0 else 1
        
        # Crossover signals
        if vi_plus > vi_minus and vi_plus > 1:
            signal, confidence = 'BUY', 0.75
            reason = "VI+ above VI- - uptrend"
        elif vi_minus > vi_plus and vi_minus > 1:
            signal, confidence = 'SELL', 0.75
            reason = "VI- above VI+ - downtrend"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "No clear trend"
        
        self.metrics['signals'] += 1
        
        return {
            'vi_plus': vi_plus,
            'vi_minus': vi_minus,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = VortexIndicatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
