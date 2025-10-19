#!/usr/bin/env python3
"""
Support & Resistance Level Detection Bot
Uses multiple methods: pivot points, horizontal levels, psychological levels
Identifies strong zones with volume confluence
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class SupportResistanceBot:
    def __init__(self):
        self.name = "Support_Resistance"
        self.version = "1.0.0"
        self.enabled = True
        
        self.min_touches = 2  # Minimum touches for valid level
        self.proximity_threshold = 0.005  # 0.5% proximity for level clustering
        
        self.metrics = {
            'levels_identified': 0,
            'support_breaks': 0,
            'resistance_breaks': 0,
            'bounces_detected': 0
        }
        
        # Store historical levels
        self.support_levels = []
        self.resistance_levels = []
    
    def identify_levels(self, ohlcv: List, lookback: int = 100) -> Dict:
        """
        Identify support and resistance levels
        
        Args:
            ohlcv: OHLCV candlestick data
            lookback: Number of candles to analyze
        
        Returns:
            Dict with levels, current signal, and confidence
        """
        if len(ohlcv) < lookback:
            return {'error': 'Insufficient data'}
        
        data = ohlcv[-lookback:]
        highs = np.array([c[2] for c in data])
        lows = np.array([c[3] for c in data])
        closes = np.array([c[4] for c in data])
        volumes = np.array([c[5] for c in data])
        
        current_price = closes[-1]
        
        # Method 1: Pivot Points
        pivot_levels = self._calculate_pivot_points(highs, lows, closes)
        
        # Method 2: Local extrema (swing highs/lows)
        swing_levels = self._find_swing_levels(highs, lows, closes)
        
        # Method 3: Psychological levels (round numbers)
        psychological_levels = self._find_psychological_levels(current_price)
        
        # Method 4: Volume-weighted levels
        volume_levels = self._find_volume_levels(closes, volumes)
        
        # Combine and cluster levels
        all_levels = (
            pivot_levels['support'] + pivot_levels['resistance'] +
            swing_levels['support'] + swing_levels['resistance'] +
            psychological_levels + volume_levels
        )
        
        # Cluster nearby levels
        support_clusters, resistance_clusters = self._cluster_levels(
            all_levels, current_price
        )
        
        # Rank levels by strength
        support_ranked = self._rank_levels(support_clusters, 'support', closes, volumes)
        resistance_ranked = self._rank_levels(resistance_clusters, 'resistance', closes, volumes)
        
        # Find nearest levels
        nearest_support = self._find_nearest_level(current_price, support_ranked, 'below')
        nearest_resistance = self._find_nearest_level(current_price, resistance_ranked, 'above')
        
        # Check for breakouts
        breakout_signal = self._check_breakout(
            current_price, closes, nearest_support, nearest_resistance
        )
        
        # Generate signal
        signal, confidence = self._generate_sr_signal(
            current_price, nearest_support, nearest_resistance, breakout_signal, closes
        )
        
        # Update storage
        self.support_levels = support_ranked[:5]  # Top 5
        self.resistance_levels = resistance_ranked[:5]
        self.metrics['levels_identified'] += 1
        
        return {
            'current_price': current_price,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'support_levels': support_ranked[:5],
            'resistance_levels': resistance_ranked[:5],
            'breakout_signal': breakout_signal,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(breakout_signal, nearest_support, nearest_resistance),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_pivot_points(self, highs, lows, closes) -> Dict:
        """Calculate classic pivot points"""
        h = highs[-1]
        l = lows[-1]
        c = closes[-2]  # Previous close
        
        pivot = (h + l + c) / 3
        
        support1 = (2 * pivot) - h
        support2 = pivot - (h - l)
        support3 = l - 2 * (h - pivot)
        
        resistance1 = (2 * pivot) - l
        resistance2 = pivot + (h - l)
        resistance3 = h + 2 * (pivot - l)
        
        return {
            'pivot': pivot,
            'support': [support1, support2, support3],
            'resistance': [resistance1, resistance2, resistance3]
        }
    
    def _find_swing_levels(self, highs, lows, closes) -> Dict:
        """Find swing high and swing low levels"""
        window = 5
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(closes) - window):
            # Swing low
            if lows[i] == np.min(lows[i-window:i+window+1]):
                support_levels.append(lows[i])
            
            # Swing high
            if highs[i] == np.max(highs[i-window:i+window+1]):
                resistance_levels.append(highs[i])
        
        return {
            'support': support_levels,
            'resistance': resistance_levels
        }
    
    def _find_psychological_levels(self, price: float) -> List[float]:
        """Find psychological round number levels near current price"""
        levels = []
        
        # Find order of magnitude
        magnitude = 10 ** int(np.log10(price))
        
        # Generate round numbers around current price
        for multiplier in [0.5, 1, 2, 5, 10, 20, 50]:
            level = magnitude * multiplier
            if abs(level - price) / price < 0.1:  # Within 10%
                levels.append(level)
        
        return levels
    
    def _find_volume_levels(self, closes, volumes) -> List[float]:
        """Find price levels with high volume concentration"""
        # Create price-volume profile
        price_bins = 20
        price_range = np.max(closes) - np.min(closes)
        bin_size = price_range / price_bins
        
        volume_profile = {}
        
        for i, price in enumerate(closes):
            bin_idx = int((price - np.min(closes)) / bin_size)
            if bin_idx not in volume_profile:
                volume_profile[bin_idx] = {'total_volume': 0, 'price_sum': 0, 'count': 0}
            
            volume_profile[bin_idx]['total_volume'] += volumes[i]
            volume_profile[bin_idx]['price_sum'] += price
            volume_profile[bin_idx]['count'] += 1
        
        # Find high volume nodes (HVN)
        avg_volume = np.mean([v['total_volume'] for v in volume_profile.values()])
        
        hvn_levels = []
        for bin_data in volume_profile.values():
            if bin_data['total_volume'] > avg_volume * 1.5:
                avg_price = bin_data['price_sum'] / bin_data['count']
                hvn_levels.append(avg_price)
        
        return hvn_levels
    
    def _cluster_levels(self, levels: List[float], current_price: float) -> Tuple[List, List]:
        """Cluster nearby levels and separate into support/resistance"""
        if not levels:
            return [], []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < self.proximity_threshold:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clusters.append(np.mean(current_cluster))
        
        # Separate into support (below) and resistance (above)
        support = [l for l in clusters if l < current_price]
        resistance = [l for l in clusters if l > current_price]
        
        return support, resistance
    
    def _rank_levels(self, levels: List[float], level_type: str, closes, volumes) -> List[Dict]:
        """Rank levels by strength (touches, volume, recency)"""
        ranked = []
        
        for level in levels:
            touches = 0
            total_volume = 0
            
            # Count touches and volume
            for i, price in enumerate(closes):
                if abs(price - level) / level < self.proximity_threshold:
                    touches += 1
                    total_volume += volumes[i]
            
            if touches >= self.min_touches:
                strength = touches * 40 + (total_volume / np.sum(volumes)) * 60
                
                ranked.append({
                    'price': level,
                    'touches': touches,
                    'strength': min(strength, 100),
                    'type': level_type
                })
        
        return sorted(ranked, key=lambda x: x['strength'], reverse=True)
    
    def _find_nearest_level(self, price: float, levels: List[Dict], direction: str) -> Optional[Dict]:
        """Find nearest level above or below current price"""
        if not levels:
            return None
        
        if direction == 'below':
            valid = [l for l in levels if l['price'] < price]
            return max(valid, key=lambda x: x['price']) if valid else None
        else:  # above
            valid = [l for l in levels if l['price'] > price]
            return min(valid, key=lambda x: x['price']) if valid else None
    
    def _check_breakout(self, price, closes, support, resistance) -> Optional[Dict]:
        """Check for support/resistance breakout"""
        if support and price < support['price'] * 0.995:
            if closes[-2] > support['price']:
                self.metrics['support_breaks'] += 1
                return {'type': 'SUPPORT_BREAK', 'level': support['price'], 'confidence': 0.80}
        
        if resistance and price > resistance['price'] * 1.005:
            if closes[-2] < resistance['price']:
                self.metrics['resistance_breaks'] += 1
                return {'type': 'RESISTANCE_BREAK', 'level': resistance['price'], 'confidence': 0.80}
        
        return None
    
    def _generate_sr_signal(self, price, support, resistance, breakout, closes) -> tuple:
        """Generate trading signal from S/R analysis"""
        
        # Breakout signals (strongest)
        if breakout:
            if breakout['type'] == 'RESISTANCE_BREAK':
                return ('BUY', 0.85)
            elif breakout['type'] == 'SUPPORT_BREAK':
                return ('SELL', 0.85)
        
        # Bounce from support
        if support:
            distance_to_support = (price - support['price']) / support['price']
            if 0 < distance_to_support < 0.01:  # Within 1%
                self.metrics['bounces_detected'] += 1
                return ('BUY', 0.75)
        
        # Rejection from resistance
        if resistance:
            distance_to_resistance = (resistance['price'] - price) / resistance['price']
            if 0 < distance_to_resistance < 0.01:
                return ('SELL', 0.70)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, breakout, support, resistance) -> str:
        """Get human-readable reason"""
        if breakout:
            return f"{breakout['type']} at {breakout['level']:.2f}"
        elif support:
            return f"Near support at {support['price']:.2f} (strength: {support['strength']:.0f})"
        elif resistance:
            return f"Near resistance at {resistance['price']:.2f} (strength: {resistance['strength']:.0f})"
        return "No significant S/R levels nearby"
    
    def get_status(self) -> Dict:
        """Return bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'active_support_levels': len(self.support_levels),
            'active_resistance_levels': len(self.resistance_levels),
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = SupportResistanceBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
