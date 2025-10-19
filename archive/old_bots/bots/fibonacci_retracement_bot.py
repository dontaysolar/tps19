#!/usr/bin/env python3
"""
Fibonacci Retracement & Extension Bot
Identifies key Fibonacci levels for entry/exit
Includes: 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%, 161.8%, 261.8%
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class FibonacciRetracementBot:
    def __init__(self):
        self.name = "Fibonacci_Retracement"
        self.version = "1.0.0"
        self.enabled = True
        
        # Fibonacci ratios
        self.retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.extension_levels = [1.272, 1.618, 2.618, 3.618, 4.236]
        
        # Golden ratio
        self.golden_ratio = 0.618
        
        self.metrics = {
            'levels_calculated': 0,
            'bounces_detected': 0,
            'golden_zone_hits': 0,
            'extensions_hit': 0
        }
    
    def calculate_fibonacci_levels(self, ohlcv: List, lookback: int = 50) -> Dict:
        """
        Calculate Fibonacci retracement and extension levels
        
        Args:
            ohlcv: OHLCV data
            lookback: Period for swing high/low detection
        
        Returns:
            Dict with levels, signal, and confidence
        """
        if len(ohlcv) < lookback:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv[-lookback:]])
        lows = np.array([c[3] for c in ohlcv[-lookback:]])
        closes = np.array([c[4] for c in ohlcv[-lookback:]])
        
        # Find swing high and swing low
        swing_high = np.max(highs)
        swing_low = np.min(lows)
        current_price = closes[-1]
        
        # Determine trend
        trend = 'UPTREND' if current_price > (swing_high + swing_low) / 2 else 'DOWNTREND'
        
        # Calculate levels
        if trend == 'UPTREND':
            # Retracement levels (from swing high back to swing low)
            retracement_levels = self._calculate_retracement_levels(
                swing_high, swing_low, 'UPTREND'
            )
            extension_levels = self._calculate_extension_levels(
                swing_high, swing_low, 'UPTREND'
            )
        else:
            # Retracement levels (from swing low back to swing high)
            retracement_levels = self._calculate_retracement_levels(
                swing_low, swing_high, 'DOWNTREND'
            )
            extension_levels = self._calculate_extension_levels(
                swing_low, swing_high, 'DOWNTREND'
            )
        
        # Check current price position
        level_touched = self._check_level_touch(current_price, retracement_levels, extension_levels)
        
        # Generate signal
        signal, confidence = self._generate_fibonacci_signal(
            current_price, retracement_levels, extension_levels, trend, level_touched
        )
        
        # Update metrics
        self.metrics['levels_calculated'] += 1
        if level_touched:
            if level_touched['level'] in [0.618, 0.786]:
                self.metrics['golden_zone_hits'] += 1
            if level_touched['type'] == 'extension':
                self.metrics['extensions_hit'] += 1
            self.metrics['bounces_detected'] += 1
        
        return {
            'trend': trend,
            'swing_high': swing_high,
            'swing_low': swing_low,
            'current_price': current_price,
            'retracement_levels': retracement_levels,
            'extension_levels': extension_levels,
            'level_touched': level_touched,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(level_touched, trend),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_retracement_levels(self, high: float, low: float, trend: str) -> Dict:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        levels = {}
        
        if trend == 'UPTREND':
            # Retracing from high back toward low
            for ratio in self.retracement_levels:
                levels[ratio] = high - (diff * ratio)
        else:
            # Retracing from low back toward high
            for ratio in self.retracement_levels:
                levels[ratio] = low + (diff * ratio)
        
        return levels
    
    def _calculate_extension_levels(self, high: float, low: float, trend: str) -> Dict:
        """Calculate Fibonacci extension levels"""
        diff = high - low
        levels = {}
        
        if trend == 'UPTREND':
            # Extensions above swing high
            for ratio in self.extension_levels:
                levels[ratio] = high + (diff * (ratio - 1))
        else:
            # Extensions below swing low
            for ratio in self.extension_levels:
                levels[ratio] = low - (diff * (ratio - 1))
        
        return levels
    
    def _check_level_touch(self, price: float, retracement: Dict, extension: Dict) -> Optional[Dict]:
        """Check if price is touching a Fibonacci level"""
        tolerance = 0.003  # 0.3% tolerance
        
        # Check retracement levels
        for ratio, level in retracement.items():
            if abs(price - level) / level < tolerance:
                return {
                    'type': 'retracement',
                    'level': ratio,
                    'price': level,
                    'distance': abs(price - level) / level
                }
        
        # Check extension levels
        for ratio, level in extension.items():
            if abs(price - level) / level < tolerance:
                return {
                    'type': 'extension',
                    'level': ratio,
                    'price': level,
                    'distance': abs(price - level) / level
                }
        
        return None
    
    def _generate_fibonacci_signal(self, price: float, retracement: Dict, 
                                   extension: Dict, trend: str, level_touched: Optional[Dict]) -> tuple:
        """Generate trading signal from Fibonacci analysis"""
        
        if not level_touched:
            return ('HOLD', 0.0)
        
        level_type = level_touched['type']
        level_ratio = level_touched['level']
        
        # GOLDEN ZONE (0.618 - 0.786) - High probability reversal
        if level_type == 'retracement' and level_ratio in [0.618, 0.786]:
            if trend == 'UPTREND':
                return ('BUY', 0.85)  # Bounce from golden zone in uptrend
            else:
                return ('SELL', 0.85)  # Bounce from golden zone in downtrend
        
        # 50% LEVEL - Moderate probability reversal
        elif level_type == 'retracement' and level_ratio == 0.5:
            if trend == 'UPTREND':
                return ('BUY', 0.70)
            else:
                return ('SELL', 0.70)
        
        # 38.2% LEVEL - Weak reversal
        elif level_type == 'retracement' and level_ratio == 0.382:
            if trend == 'UPTREND':
                return ('BUY', 0.60)
            else:
                return ('SELL', 0.60)
        
        # EXTENSION LEVELS - Take profit zones
        elif level_type == 'extension':
            if trend == 'UPTREND':
                return ('SELL', 0.75)  # Take profit at extension
            else:
                return ('BUY', 0.75)  # Cover short at extension
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, level_touched: Optional[Dict], trend: str) -> str:
        """Get human-readable reason for signal"""
        if not level_touched:
            return "No Fibonacci level touched"
        
        level_type = level_touched['type']
        level_ratio = level_touched['level']
        
        if level_type == 'retracement':
            if level_ratio in [0.618, 0.786]:
                return f"Golden Zone {level_ratio:.1%} retracement in {trend} - high probability bounce"
            else:
                return f"Fibonacci {level_ratio:.1%} retracement level touched"
        else:
            return f"Fibonacci {level_ratio:.3f} extension reached - take profit zone"
    
    def get_status(self) -> Dict:
        """Return bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = FibonacciRetracementBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
    print(f"📊 Fibonacci levels: {bot.retracement_levels}")
