#!/usr/bin/env python3
"""Momentum Shift Detector - Early trend change detection"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MomentumShiftDetectorBot:
    def __init__(self):
        self.name = "Momentum_Shift_Detector"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'shifts_detected': 0}
    
    def detect_shift(self, ohlcv: List) -> Dict:
        """Detect momentum shifts"""
        if len(ohlcv) < 30:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Recent vs historical momentum
        recent_momentum = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0
        historical_momentum = (closes[-10] - closes[-20]) / closes[-20] if closes[-20] > 0 else 0
        
        # Momentum acceleration
        momentum_change = recent_momentum - historical_momentum
        
        # Rate of change acceleration
        roc_recent = np.diff(closes[-10:])
        roc_historical = np.diff(closes[-30:-10])
        
        acc_recent = np.mean(roc_recent)
        acc_historical = np.mean(roc_historical)
        
        # Detect shift
        shift_detected = False
        shift_type = None
        
        if recent_momentum > 0 and historical_momentum < 0 and momentum_change > 0.03:
            shift_detected = True
            shift_type = 'BULLISH_SHIFT'
            signal, confidence = 'BUY', 0.85
            reason = "Momentum shifting bullish"
            self.metrics['shifts_detected'] += 1
        
        elif recent_momentum < 0 and historical_momentum > 0 and momentum_change < -0.03:
            shift_detected = True
            shift_type = 'BEARISH_SHIFT'
            signal, confidence = 'SELL', 0.85
            reason = "Momentum shifting bearish"
            self.metrics['shifts_detected'] += 1
        
        elif acc_recent > 0 and acc_historical < 0:
            shift_detected = True
            shift_type = 'ACCELERATION_UP'
            signal, confidence = 'BUY', 0.75
            reason = "Accelerating upward"
        
        elif acc_recent < 0 and acc_historical > 0:
            shift_detected = True
            shift_type = 'DECELERATION'
            signal, confidence = 'SELL', 0.75
            reason = "Decelerating"
        
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "No momentum shift"
        
        return {
            'shift_detected': shift_detected,
            'shift_type': shift_type,
            'recent_momentum': recent_momentum,
            'historical_momentum': historical_momentum,
            'momentum_change': momentum_change,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MomentumShiftDetectorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
