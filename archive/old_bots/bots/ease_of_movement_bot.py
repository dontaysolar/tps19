#!/usr/bin/env python3
"""Ease of Movement Bot - Price movement vs volume"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class EaseOfMovementBot:
    def __init__(self):
        self.name = "Ease_Of_Movement"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 14
        self.metrics = {'signals': 0}
    
    def calculate_eom(self, ohlcv: List) -> Dict:
        """Calculate Ease of Movement"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        highs = [c[2] for c in ohlcv]
        lows = [c[3] for c in ohlcv]
        volumes = [c[5] for c in ohlcv]
        
        # Distance moved
        distance_moved = [(highs[i] + lows[i]) / 2 - (highs[i-1] + lows[i-1]) / 2 
                         for i in range(1, len(ohlcv))]
        
        # Box ratio
        box_ratios = [(volumes[i] / 1000000) / (highs[i] - lows[i]) 
                     if (highs[i] - lows[i]) > 0 else 1 
                     for i in range(1, len(ohlcv))]
        
        # EMV
        emv_values = [distance_moved[i] / box_ratios[i] if box_ratios[i] != 0 else 0 
                     for i in range(len(distance_moved))]
        
        # Average EMV
        avg_emv = np.mean(emv_values[-self.period:]) if len(emv_values) >= self.period else 0
        
        if avg_emv > 0:
            signal, confidence = 'BUY', 0.70
            reason = "Positive ease of movement"
        elif avg_emv < 0:
            signal, confidence = 'SELL', 0.70
            reason = "Negative ease of movement"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Neutral movement"
        
        self.metrics['signals'] += 1
        
        return {
            'emv': avg_emv,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = EaseOfMovementBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
