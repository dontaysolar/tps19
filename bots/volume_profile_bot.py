#!/usr/bin/env python3
"""
Volume Profile Bot
Analyzes price-volume distribution to find:
- Point of Control (POC) - highest volume price level
- Value Area High/Low (VAH/VAL) - 70% volume concentration
- High Volume Nodes (HVN) and Low Volume Nodes (LVN)
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

class VolumeProfileBot:
    def __init__(self):
        self.name = "Volume_Profile"
        self.version = "1.0.0"
        self.enabled = True
        
        self.value_area_percentage = 0.70  # 70% of volume
        self.num_bins = 24  # Price bins for profile
        
        self.metrics = {
            'poc_touches': 0,
            'value_area_trades': 0,
            'lvn_breakouts': 0
        }
    
    def analyze_volume_profile(self, ohlcv: List) -> Dict:
        """
        Build volume profile and identify key levels
        """
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        
        # Build volume profile
        profile = self._build_volume_profile(closes, highs, lows, volumes)
        
        # Find POC (Point of Control)
        poc_price, poc_volume = self._find_poc(profile)
        
        # Find Value Area High/Low
        vah, val = self._find_value_area(profile)
        
        # Find HVN and LVN
        hvn_levels = self._find_hvn(profile)
        lvn_levels = self._find_lvn(profile)
        
        # Generate signal
        current_price = closes[-1]
        signal, confidence = self._generate_volume_signal(
            current_price, poc_price, vah, val, hvn_levels, lvn_levels, closes
        )
        
        return {
            'current_price': current_price,
            'poc': poc_price,
            'vah': vah,
            'val': val,
            'hvn_levels': hvn_levels[:3],
            'lvn_levels': lvn_levels[:3],
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(current_price, poc_price, vah, val),
            'timestamp': datetime.now().isoformat()
        }
    
    def _build_volume_profile(self, closes, highs, lows, volumes) -> Dict:
        """Build price-volume distribution"""
        price_min = np.min(lows)
        price_max = np.max(highs)
        bin_size = (price_max - price_min) / self.num_bins
        
        profile = {}
        
        for i in range(len(closes)):
            # Distribute volume across price range
            bar_high = highs[i]
            bar_low = lows[i]
            bar_volume = volumes[i]
            
            # Find which bins this bar touches
            for price in np.linspace(bar_low, bar_high, 5):
                bin_idx = int((price - price_min) / bin_size)
                if bin_idx not in profile:
                    profile[bin_idx] = {'total_volume': 0, 'price_sum': 0, 'count': 0}
                
                profile[bin_idx]['total_volume'] += bar_volume / 5
                profile[bin_idx]['price_sum'] += price
                profile[bin_idx]['count'] += 1
        
        # Calculate average price for each bin
        for bin_data in profile.values():
            bin_data['avg_price'] = bin_data['price_sum'] / bin_data['count']
        
        return profile
    
    def _find_poc(self, profile: Dict) -> Tuple[float, float]:
        """Find Point of Control (highest volume price level)"""
        max_volume = 0
        poc_price = 0
        
        for bin_data in profile.values():
            if bin_data['total_volume'] > max_volume:
                max_volume = bin_data['total_volume']
                poc_price = bin_data['avg_price']
        
        return poc_price, max_volume
    
    def _find_value_area(self, profile: Dict) -> Tuple[float, float]:
        """Find Value Area High and Low (70% volume concentration)"""
        # Sort bins by volume
        sorted_bins = sorted(profile.items(), key=lambda x: x[1]['total_volume'], reverse=True)
        
        total_volume = sum(b[1]['total_volume'] for b in sorted_bins)
        target_volume = total_volume * self.value_area_percentage
        
        # Accumulate bins until we reach 70% volume
        accumulated_volume = 0
        value_area_bins = []
        
        for bin_idx, bin_data in sorted_bins:
            value_area_bins.append(bin_data['avg_price'])
            accumulated_volume += bin_data['total_volume']
            if accumulated_volume >= target_volume:
                break
        
        vah = max(value_area_bins)
        val = min(value_area_bins)
        
        return vah, val
    
    def _find_hvn(self, profile: Dict) -> List[float]:
        """Find High Volume Nodes"""
        avg_volume = np.mean([b['total_volume'] for b in profile.values()])
        
        hvn = []
        for bin_data in profile.values():
            if bin_data['total_volume'] > avg_volume * 1.5:
                hvn.append(bin_data['avg_price'])
        
        return sorted(hvn)
    
    def _find_lvn(self, profile: Dict) -> List[float]:
        """Find Low Volume Nodes (gaps in profile)"""
        avg_volume = np.mean([b['total_volume'] for b in profile.values()])
        
        lvn = []
        for bin_data in profile.values():
            if bin_data['total_volume'] < avg_volume * 0.3:
                lvn.append(bin_data['avg_price'])
        
        return sorted(lvn)
    
    def _generate_volume_signal(self, price, poc, vah, val, hvn, lvn, closes) -> tuple:
        """Generate signal from volume profile analysis"""
        
        # Price at POC - high probability of reversal or consolidation
        if abs(price - poc) / poc < 0.01:
            self.metrics['poc_touches'] += 1
            return ('HOLD', 0.70)
        
        # Price in Value Area - balanced, look for direction
        if val < price < vah:
            self.metrics['value_area_trades'] += 1
            # Check trend direction
            if closes[-1] > closes[-5]:
                return ('BUY', 0.65)
            else:
                return ('SELL', 0.65)
        
        # Price at LVN - potential for quick move through gap
        for lvn_level in lvn:
            if abs(price - lvn_level) / price < 0.01:
                self.metrics['lvn_breakouts'] += 1
                # Breakout through low volume = continuation
                if price > poc:
                    return ('BUY', 0.80)
                else:
                    return ('SELL', 0.80)
        
        # Price above Value Area High - strong bullish
        if price > vah * 1.01:
            return ('BUY', 0.75)
        
        # Price below Value Area Low - strong bearish
        if price < val * 0.99:
            return ('SELL', 0.75)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, price, poc, vah, val) -> str:
        """Get human-readable reason"""
        if abs(price - poc) / poc < 0.01:
            return f"Price at POC ({poc:.2f}) - high volume support/resistance"
        elif price > vah:
            return f"Price above Value Area High ({vah:.2f}) - strong position"
        elif price < val:
            return f"Price below Value Area Low ({val:.2f}) - weak position"
        elif val < price < vah:
            return f"Price in Value Area ({val:.2f}-{vah:.2f}) - balanced"
        return "Volume profile analysis"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = VolumeProfileBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
