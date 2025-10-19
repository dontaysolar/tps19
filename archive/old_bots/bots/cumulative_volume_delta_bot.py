#!/usr/bin/env python3
"""Cumulative Volume Delta (CVD) - Buy vs sell volume tracking"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class CumulativeVolumeDeltaBot:
    def __init__(self):
        self.name = "Cumulative_Volume_Delta"
        self.version = "1.0.0"
        self.enabled = True
        self.cumulative_delta = 0
        self.metrics = {'calculations': 0, 'divergences': 0}
    
    def calculate_cvd(self, ohlcv: List) -> Dict:
        """Calculate CVD from OHLCV data"""
        if len(ohlcv) < 2:
            return {'error': 'Insufficient data'}
        
        deltas = []
        
        for i, candle in enumerate(ohlcv):
            close_price = candle[4]
            volume = candle[5]
            
            if i > 0:
                prev_close = ohlcv[i-1][4]
                
                # Estimate buy/sell volume based on price movement
                if close_price > prev_close:
                    buy_volume = volume * 0.7  # Assume 70% buying
                    sell_volume = volume * 0.3
                elif close_price < prev_close:
                    buy_volume = volume * 0.3
                    sell_volume = volume * 0.7  # Assume 70% selling
                else:
                    buy_volume = volume * 0.5
                    sell_volume = volume * 0.5
                
                delta = buy_volume - sell_volume
                deltas.append(delta)
                self.cumulative_delta += delta
        
        current_delta = deltas[-1] if deltas else 0
        
        # Price divergence check
        price_trend = ohlcv[-1][4] - ohlcv[0][4]
        cvd_trend = sum(deltas[-20:]) if len(deltas) >= 20 else sum(deltas)
        
        # Divergence: price up but CVD down (bearish) or vice versa
        divergence = False
        if price_trend > 0 and cvd_trend < 0:
            divergence = True
            divergence_type = 'BEARISH'
            signal, confidence = 'SELL', 0.75
            self.metrics['divergences'] += 1
        elif price_trend < 0 and cvd_trend > 0:
            divergence = True
            divergence_type = 'BULLISH'
            signal, confidence = 'BUY', 0.75
            self.metrics['divergences'] += 1
        else:
            divergence_type = None
            if cvd_trend > 0:
                signal, confidence = 'BUY', 0.65
            elif cvd_trend < 0:
                signal, confidence = 'SELL', 0.65
            else:
                signal, confidence = 'HOLD', 0.50
        
        self.metrics['calculations'] += 1
        
        return {
            'current_delta': current_delta,
            'cumulative_delta': self.cumulative_delta,
            'recent_trend': cvd_trend,
            'divergence': divergence,
            'divergence_type': divergence_type,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'cumulative_delta': self.cumulative_delta, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = CumulativeVolumeDeltaBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
