#!/usr/bin/env python3
"""Price Channel Bot - High/low breakout detector"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class PriceChannelBot:
    def __init__(self):
        self.name = "Price_Channel"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 20
        self.metrics = {'signals': 0}
    
    def calculate_price_channel(self, ohlcv: List) -> Dict:
        """Calculate price channel"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv[-self.period:]])
        lows = np.array([c[3] for c in ohlcv[-self.period:]])
        current_price = ohlcv[-1][4]
        
        upper_channel = highs.max()
        lower_channel = lows.min()
        mid_channel = (upper_channel + lower_channel) / 2
        
        if current_price >= upper_channel:
            signal, confidence = 'BUY', 0.80
            reason = "Breakout above channel"
        elif current_price <= lower_channel:
            signal, confidence = 'SELL', 0.80
            reason = "Breakdown below channel"
        elif current_price > mid_channel:
            signal, confidence = 'BUY', 0.60
            reason = "Above mid-channel"
        else:
            signal, confidence = 'SELL', 0.60
            reason = "Below mid-channel"
        
        self.metrics['signals'] += 1
        
        return {
            'upper_channel': upper_channel,
            'mid_channel': mid_channel,
            'lower_channel': lower_channel,
            'current_price': current_price,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = PriceChannelBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
