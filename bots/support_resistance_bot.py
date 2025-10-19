#!/usr/bin/env python3
"""Support/Resistance Bot - Key price levels"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class SupportResistanceBot:
    def __init__(self):
        self.name = "Support_Resistance"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'levels_found': 0}
    
    def find_levels(self, ohlcv: List, tolerance: float = 0.02) -> Dict:
        """Find support and resistance levels"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Find local maxima (resistance)
        resistance_levels = []
        for i in range(10, len(highs) - 10):
            if highs[i] == highs[i-10:i+10].max():
                resistance_levels.append(highs[i])
        
        # Find local minima (support)
        support_levels = []
        for i in range(10, len(lows) - 10):
            if lows[i] == lows[i-10:i+10].min():
                support_levels.append(lows[i])
        
        # Cluster nearby levels
        resistance = self._cluster_levels(resistance_levels, tolerance)
        support = self._cluster_levels(support_levels, tolerance)
        
        current_price = closes[-1]
        
        # Find nearest levels
        nearest_resistance = min([r for r in resistance if r > current_price], default=None)
        nearest_support = max([s for s in support if s < current_price], default=None)
        
        # Generate signal
        if nearest_support and abs(current_price - nearest_support) / current_price < 0.01:
            signal, confidence = 'BUY', 0.80
            reason = "Near support level"
        elif nearest_resistance and abs(current_price - nearest_resistance) / current_price < 0.01:
            signal, confidence = 'SELL', 0.80
            reason = "Near resistance level"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Between levels"
        
        self.metrics['levels_found'] += len(resistance) + len(support)
        
        return {
            'support_levels': support[:5],
            'resistance_levels': resistance[:5],
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'current_price': current_price,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def _cluster_levels(self, levels: List, tolerance: float) -> List:
        """Cluster nearby price levels"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < tolerance:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clustered.append(np.mean(current_cluster))
        return clustered
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = SupportResistanceBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
