#!/usr/bin/env python3
"""
Supertrend Indicator Bot
Trend-following indicator using ATR
Popular for identifying trend direction
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class SupertrendIndicatorBot:
    def __init__(self):
        self.name = "Supertrend_Indicator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.period = 10
        self.multiplier = 3.0
        
        self.metrics = {'signals_generated': 0, 'trend_changes': 0}
    
    def calculate_supertrend(self, ohlcv: List) -> Dict:
        """Calculate Supertrend indicator"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate ATR
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]), 
                                 abs(lows[1:] - closes[:-1])))
        
        atr = np.zeros(len(closes))
        atr[self.period:] = [np.mean(tr[i-self.period:i]) for i in range(self.period, len(tr))]
        
        # Calculate basic bands
        hl_avg = (highs + lows) / 2
        upper_band = hl_avg + (self.multiplier * atr)
        lower_band = hl_avg - (self.multiplier * atr)
        
        # Determine trend
        supertrend = np.zeros(len(closes))
        trend = np.ones(len(closes))  # 1 = uptrend, -1 = downtrend
        
        for i in range(self.period, len(closes)):
            if closes[i] > upper_band[i-1]:
                trend[i] = 1
                supertrend[i] = lower_band[i]
            elif closes[i] < lower_band[i-1]:
                trend[i] = -1
                supertrend[i] = upper_band[i]
            else:
                trend[i] = trend[i-1]
                supertrend[i] = upper_band[i] if trend[i] == -1 else lower_band[i]
        
        current_trend = 'BULLISH' if trend[-1] == 1 else 'BEARISH'
        signal = 'BUY' if trend[-1] == 1 else 'SELL'
        
        # Detect trend change
        if len(trend) > 1 and trend[-1] != trend[-2]:
            self.metrics['trend_changes'] += 1
        
        self.metrics['signals_generated'] += 1
        
        return {
            'supertrend': supertrend[-1],
            'trend': current_trend,
            'signal': signal,
            'confidence': 0.75,
            'atr': atr[-1],
            'upper_band': upper_band[-1],
            'lower_band': lower_band[-1],
            'reason': f"Supertrend shows {current_trend} trend",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'period': self.period, 'multiplier': self.multiplier, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = SupertrendIndicatorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
