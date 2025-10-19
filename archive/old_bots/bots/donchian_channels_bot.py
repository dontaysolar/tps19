#!/usr/bin/env python3
"""
Donchian Channels Bot
Breakout detection using price channels
Identifies new highs/lows for trend entry
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class DonchianChannelsBot:
    def __init__(self):
        self.name = "Donchian_Channels"
        self.version = "1.0.0"
        self.enabled = True
        
        self.period = 20
        self.metrics = {'breakouts_detected': 0, 'signals_generated': 0}
    
    def calculate_donchian(self, ohlcv: List) -> Dict:
        """Calculate Donchian Channels"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate channels
        upper_channel = np.max(highs[-self.period:])
        lower_channel = np.min(lows[-self.period:])
        middle_channel = (upper_channel + lower_channel) / 2
        
        current_price = closes[-1]
        
        # Channel width as volatility measure
        channel_width = upper_channel - lower_channel
        width_pct = (channel_width / middle_channel) * 100
        
        # Detect breakouts
        if current_price >= upper_channel:
            signal = 'BUY'
            confidence = 0.85
            reason = f"Breakout above upper channel ({upper_channel:.2f})"
            self.metrics['breakouts_detected'] += 1
        elif current_price <= lower_channel:
            signal = 'SELL'
            confidence = 0.85
            reason = f"Breakdown below lower channel ({lower_channel:.2f})"
            self.metrics['breakouts_detected'] += 1
        elif current_price > middle_channel:
            signal = 'BUY'
            confidence = 0.60
            reason = "Price above middle channel"
        elif current_price < middle_channel:
            signal = 'SELL'
            confidence = 0.60
            reason = "Price below middle channel"
        else:
            signal = 'HOLD'
            confidence = 0.50
            reason = "Price at middle channel"
        
        self.metrics['signals_generated'] += 1
        
        return {
            'upper_channel': upper_channel,
            'middle_channel': middle_channel,
            'lower_channel': lower_channel,
            'current_price': current_price,
            'channel_width_pct': width_pct,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'period': self.period, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = DonchianChannelsBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
