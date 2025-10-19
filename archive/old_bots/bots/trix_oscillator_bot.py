#!/usr/bin/env python3
"""TRIX - Triple exponential average oscillator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class TRIXOscillatorBot:
    def __init__(self):
        self.name = "TRIX_Oscillator"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 15
        self.signal_period = 9
        self.metrics = {'signals': 0, 'crossovers': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.period * 3:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Triple EMA (simplified)
        ema1 = closes[-self.period:].mean()
        ema2 = ema1  # Simplified
        ema3 = ema2
        
        # TRIX = Rate of change of triple EMA
        if len(closes) > self.period * 3 + 1:
            prev_ema3 = closes[-(self.period*3+1):-self.period*3].mean()
            trix = ((ema3 - prev_ema3) / prev_ema3) * 100 if prev_ema3 > 0 else 0
        else:
            trix = 0
        
        # Signal line
        signal_line = trix  # Simplified
        
        if trix > signal_line and trix > 0:
            signal, confidence = 'BUY', 0.75
            self.metrics['crossovers'] += 1
        elif trix < signal_line and trix < 0:
            signal, confidence = 'SELL', 0.75
            self.metrics['crossovers'] += 1
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {'trix': trix, 'signal_line': signal_line, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = TRIXOscillatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
