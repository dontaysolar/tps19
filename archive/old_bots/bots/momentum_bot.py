#!/usr/bin/env python3
"""Momentum Bot - Rate of change indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MomentumBot:
    def __init__(self):
        self.name = "Momentum"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 10
        self.metrics = {'signals': 0}
    
    def calculate_momentum(self, ohlcv: List) -> Dict:
        """Calculate momentum"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Momentum = Current price - Price n periods ago
        momentum = closes[-1] - closes[-(self.period + 1)]
        momentum_pct = (momentum / closes[-(self.period + 1)]) * 100
        
        # ROC (Rate of Change)
        roc = ((closes[-1] - closes[-(self.period + 1)]) / closes[-(self.period + 1)]) * 100
        
        if momentum_pct > 5:
            signal, confidence = 'BUY', 0.75
            reason = f"Strong positive momentum: +{momentum_pct:.2f}%"
        elif momentum_pct < -5:
            signal, confidence = 'SELL', 0.75
            reason = f"Strong negative momentum: {momentum_pct:.2f}%"
        elif momentum_pct > 0:
            signal, confidence = 'BUY', 0.60
            reason = "Positive momentum"
        else:
            signal, confidence = 'SELL', 0.60
            reason = "Negative momentum"
        
        self.metrics['signals'] += 1
        
        return {
            'momentum': momentum,
            'momentum_pct': momentum_pct,
            'roc': roc,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'period': self.period, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MomentumBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
