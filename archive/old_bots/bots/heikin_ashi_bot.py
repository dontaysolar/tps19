#!/usr/bin/env python3
"""Heikin Ashi Bot - Smoothed candlestick patterns"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class HeikinAshiBot:
    def __init__(self):
        self.name = "Heikin_Ashi"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'candles_processed': 0}
    
    def convert_to_heikin_ashi(self, ohlcv: List) -> Dict:
        """Convert regular candles to Heikin Ashi"""
        if len(ohlcv) < 2:
            return {'error': 'Insufficient data'}
        
        ha_candles = []
        
        for i, candle in enumerate(ohlcv):
            open_price, high, low, close = candle[1], candle[2], candle[3], candle[4]
            
            if i == 0:
                ha_close = (open_price + high + low + close) / 4
                ha_open = (open_price + close) / 2
            else:
                ha_close = (open_price + high + low + close) / 4
                ha_open = (ha_candles[-1]['open'] + ha_candles[-1]['close']) / 2
            
            ha_high = max(high, ha_open, ha_close)
            ha_low = min(low, ha_open, ha_close)
            
            ha_candles.append({
                'open': ha_open,
                'high': ha_high,
                'low': ha_low,
                'close': ha_close,
                'body_color': 'GREEN' if ha_close > ha_open else 'RED'
            })
            
            self.metrics['candles_processed'] += 1
        
        # Analyze trend
        recent = ha_candles[-5:] if len(ha_candles) >= 5 else ha_candles
        green_candles = sum([1 for c in recent if c['body_color'] == 'GREEN'])
        
        if green_candles >= 4:
            signal, confidence = 'BUY', 0.80
            reason = "Strong uptrend - consecutive green HA candles"
        elif green_candles <= 1:
            signal, confidence = 'SELL', 0.80
            reason = "Strong downtrend - consecutive red HA candles"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Mixed trend"
        
        return {
            'ha_candles': recent,
            'current_color': ha_candles[-1]['body_color'],
            'trend_strength': abs(green_candles - 2.5) / 2.5,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = HeikinAshiBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
