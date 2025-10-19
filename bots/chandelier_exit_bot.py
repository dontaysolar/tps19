#!/usr/bin/env python3
"""Chandelier Exit - Trailing stop based on ATR"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class ChandelierExitBot:
    def __init__(self):
        self.name = "Chandelier_Exit"
        self.version = "1.0.0"
        self.enabled = True
        self.atr_period = 22
        self.multiplier = 3.0
        self.metrics = {'stops_calculated': 0}
    
    def calculate_exit_level(self, ohlcv: List, position_type: str = 'LONG') -> Dict:
        """Calculate chandelier exit level"""
        if len(ohlcv) < self.atr_period + 1:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # ATR
        tr = np.maximum(highs[1:] - lows[1:], np.maximum(abs(highs[1:] - closes[:-1]), abs(lows[1:] - closes[:-1])))
        atr = tr[-self.atr_period:].mean()
        
        # Chandelier Exit
        if position_type == 'LONG':
            highest_high = highs[-self.atr_period:].max()
            exit_level = highest_high - (self.multiplier * atr)
            signal = 'SELL' if closes[-1] < exit_level else 'HOLD'
        else:  # SHORT
            lowest_low = lows[-self.atr_period:].min()
            exit_level = lowest_low + (self.multiplier * atr)
            signal = 'BUY' if closes[-1] > exit_level else 'HOLD'
        
        self.metrics['stops_calculated'] += 1
        
        return {
            'exit_level': exit_level,
            'current_price': closes[-1],
            'atr': atr,
            'distance_to_exit': abs(closes[-1] - exit_level),
            'distance_pct': abs(closes[-1] - exit_level) / closes[-1] * 100,
            'signal': signal,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'atr_period': self.atr_period, 'multiplier': self.multiplier, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = ChandelierExitBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
