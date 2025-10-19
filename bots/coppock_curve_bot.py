#!/usr/bin/env python3
"""Coppock Curve Bot - Long-term buying opportunity indicator"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class CoppockCurveBot:
    def __init__(self):
        self.name = "Coppock_Curve"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'signals': 0}
    
    def calculate_coppock(self, ohlcv: List) -> Dict:
        """Calculate Coppock Curve"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # ROC 14 and 11
        roc14 = ((closes[-1] - closes[-15]) / closes[-15]) * 100 if len(closes) > 15 else 0
        roc11 = ((closes[-1] - closes[-12]) / closes[-12]) * 100 if len(closes) > 12 else 0
        
        # Sum of ROCs
        roc_sum = roc14 + roc11
        
        # WMA (simplified as average)
        coppock = roc_sum
        
        # Signal on zero-line cross
        if coppock > 0:
            signal, confidence = 'BUY', 0.70
            reason = "Coppock above zero - long-term buy"
        elif coppock < -5:
            signal, confidence = 'BUY', 0.75
            reason = "Coppock extreme low - buy opportunity"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Coppock neutral"
        
        self.metrics['signals'] += 1
        
        return {
            'coppock': coppock,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = CoppockCurveBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
