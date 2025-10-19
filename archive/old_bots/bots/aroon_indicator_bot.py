#!/usr/bin/env python3
"""
Aroon Indicator Bot
Measures trend strength and direction
Identifies trend changes early
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class AroonIndicatorBot:
    def __init__(self):
        self.name = "Aroon_Indicator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.period = 25
        self.metrics = {'signals': 0, 'crossovers': 0}
    
    def calculate_aroon(self, ohlcv: List) -> Dict:
        """Calculate Aroon indicator"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv[-self.period:]])
        lows = np.array([c[3] for c in ohlcv[-self.period:]])
        
        # Find periods since highest high and lowest low
        periods_since_high = self.period - 1 - np.argmax(highs)
        periods_since_low = self.period - 1 - np.argmin(lows)
        
        # Calculate Aroon Up and Down
        aroon_up = ((self.period - periods_since_high) / self.period) * 100
        aroon_down = ((self.period - periods_since_low) / self.period) * 100
        
        # Aroon Oscillator
        aroon_oscillator = aroon_up - aroon_down
        
        # Generate signal
        if aroon_up > 70 and aroon_down < 30:
            signal = 'BUY'
            confidence = 0.80
            reason = "Strong uptrend - Aroon Up dominant"
        elif aroon_down > 70 and aroon_up < 30:
            signal = 'SELL'
            confidence = 0.80
            reason = "Strong downtrend - Aroon Down dominant"
        elif aroon_oscillator > 50:
            signal = 'BUY'
            confidence = 0.65
            reason = "Positive Aroon oscillator"
        elif aroon_oscillator < -50:
            signal = 'SELL'
            confidence = 0.65
            reason = "Negative Aroon oscillator"
        else:
            signal = 'HOLD'
            confidence = 0.50
            reason = "Weak trend indication"
        
        # Detect crossover
        if len(ohlcv) > self.period:
            prev_highs = np.array([c[2] for c in ohlcv[-self.period-1:-1]])
            prev_lows = np.array([c[3] for c in ohlcv[-self.period-1:-1]])
            
            prev_periods_high = self.period - 1 - np.argmax(prev_highs)
            prev_periods_low = self.period - 1 - np.argmin(prev_lows)
            
            prev_aroon_up = ((self.period - prev_periods_high) / self.period) * 100
            prev_aroon_down = ((self.period - prev_periods_low) / self.period) * 100
            
            if aroon_up > aroon_down and prev_aroon_up <= prev_aroon_down:
                self.metrics['crossovers'] += 1
        
        self.metrics['signals'] += 1
        
        return {
            'aroon_up': aroon_up,
            'aroon_down': aroon_down,
            'aroon_oscillator': aroon_oscillator,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'trend_strength': abs(aroon_oscillator),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'period': self.period, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = AroonIndicatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
