#!/usr/bin/env python3
"""Volume Analysis Bot - Volume-based signals"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class VolumeAnalysisBot:
    def __init__(self):
        self.name = "Volume_Analysis"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'analyses': 0}
    
    def analyze_volume(self, ohlcv: List) -> Dict:
        """Analyze volume patterns"""
        if len(ohlcv) < 20:
            return {'error': 'Insufficient data'}
        
        volumes = np.array([c[5] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Volume moving average
        vol_ma = volumes[-20:].mean()
        current_vol = volumes[-1]
        vol_ratio = current_vol / vol_ma if vol_ma > 0 else 1
        
        # Price change
        price_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] > 0 else 0
        
        # Volume trend
        vol_trend = (volumes[-5:].mean() - volumes[-20:-5].mean()) / volumes[-20:-5].mean() if volumes[-20:-5].mean() > 0 else 0
        
        # Climax volume (very high volume)
        is_climax = vol_ratio > 3
        
        # Generate signal
        if vol_ratio > 2 and price_change > 0.02:
            signal, confidence = 'BUY', 0.85
            reason = "High volume breakout"
        elif vol_ratio > 2 and price_change < -0.02:
            signal, confidence = 'SELL', 0.85
            reason = "High volume breakdown"
        elif is_climax:
            signal, confidence = 'REVERSAL', 0.75
            reason = "Climax volume - potential reversal"
        elif vol_trend > 0.5 and price_change > 0:
            signal, confidence = 'BUY', 0.70
            reason = "Rising volume with price"
        elif vol_ratio < 0.5:
            signal, confidence = 'HOLD', 0.60
            reason = "Low volume - avoid"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Normal volume"
        
        self.metrics['analyses'] += 1
        
        return {
            'current_volume': current_vol,
            'avg_volume': vol_ma,
            'volume_ratio': vol_ratio,
            'volume_trend': vol_trend,
            'is_climax': is_climax,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = VolumeAnalysisBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
