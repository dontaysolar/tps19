#!/usr/bin/env python3
"""
VWAP (Volume Weighted Average Price) Execution Bot
Executes trades at or better than VWAP
Includes VWAP bands for entry/exit optimization
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class VWAPExecutionBot:
    def __init__(self):
        self.name = "VWAP_Execution"
        self.version = "1.0.0"
        self.enabled = True
        
        self.metrics = {
            'trades_executed': 0,
            'beats_vwap': 0,
            'avg_slippage': 0
        }
    
    def calculate_vwap(self, ohlcv: List) -> Dict:
        """Calculate VWAP and bands"""
        if len(ohlcv) < 10:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        # Typical price
        typical_price = (highs + lows + closes) / 3
        
        # VWAP calculation
        cumulative_tp_volume = np.cumsum(typical_price * volumes)
        cumulative_volume = np.cumsum(volumes)
        
        vwap = cumulative_tp_volume / cumulative_volume
        
        # VWAP bands (standard deviation bands)
        vwap_std = self._calculate_vwap_std(typical_price, volumes, vwap)
        
        upper_band1 = vwap + vwap_std
        upper_band2 = vwap + (2 * vwap_std)
        lower_band1 = vwap - vwap_std
        lower_band2 = vwap - (2 * vwap_std)
        
        current_price = closes[-1]
        current_vwap = vwap[-1]
        
        # Determine price position
        distance_from_vwap = ((current_price - current_vwap) / current_vwap) * 100
        
        # Generate signal
        signal, confidence = self._generate_vwap_signal(
            current_price, current_vwap, upper_band1[-1], upper_band2[-1],
            lower_band1[-1], lower_band2[-1], closes
        )
        
        return {
            'vwap': current_vwap,
            'current_price': current_price,
            'upper_band1': upper_band1[-1],
            'upper_band2': upper_band2[-1],
            'lower_band1': lower_band1[-1],
            'lower_band2': lower_band2[-1],
            'distance_pct': distance_from_vwap,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(distance_from_vwap, signal),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_vwap_std(self, typical_price, volumes, vwap) -> np.ndarray:
        """Calculate VWAP standard deviation"""
        squared_diff = (typical_price - vwap) ** 2
        variance = np.cumsum(squared_diff * volumes) / np.cumsum(volumes)
        std = np.sqrt(variance)
        return std
    
    def _generate_vwap_signal(self, price, vwap, ub1, ub2, lb1, lb2, closes) -> tuple:
        """Generate signal from VWAP analysis"""
        
        # Price at lower band - potential buy
        if price <= lb2:
            return ('BUY', 0.90)
        elif price <= lb1:
            return ('BUY', 0.75)
        
        # Price at upper band - potential sell
        elif price >= ub2:
            return ('SELL', 0.90)
        elif price >= ub1:
            return ('SELL', 0.75)
        
        # Price mean reversion to VWAP
        elif price < vwap and closes[-1] > closes[-2]:
            return ('BUY', 0.65)
        elif price > vwap and closes[-1] < closes[-2]:
            return ('SELL', 0.65)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, distance, signal) -> str:
        """Get human-readable reason"""
        if abs(distance) < 0.5:
            return f"Price at VWAP ({distance:+.2f}%)"
        elif distance < -2:
            return f"Price {abs(distance):.1f}% below VWAP - oversold"
        elif distance > 2:
            return f"Price {distance:.1f}% above VWAP - overbought"
        return f"Price {distance:+.2f}% from VWAP"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = VWAPExecutionBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
