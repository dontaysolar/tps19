#!/usr/bin/env python3
"""Market Profile - TPO analysis, value area, point of control"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MarketProfileBot:
    def __init__(self):
        self.name = "Market_Profile"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'profiles_generated': 0}
    
    def generate_profile(self, ohlcv: List, price_increment: float = 1.0) -> Dict:
        """Generate market profile from price data"""
        if len(ohlcv) < 10:
            return {'error': 'Insufficient data'}
        
        # Extract price ranges
        all_prices = []
        for candle in ohlcv:
            all_prices.extend([candle[2], candle[3], candle[4]])  # high, low, close
        
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        # Create TPO (Time Price Opportunity) map
        price_levels = np.arange(min_price, max_price + price_increment, price_increment)
        tpo_count = {level: 0 for level in price_levels}
        
        for candle in ohlcv:
            low, high = candle[3], candle[2]
            for level in price_levels:
                if low <= level <= high:
                    tpo_count[level] += 1
        
        # Find POC (Point of Control) - most traded price
        poc_price = max(tpo_count, key=tpo_count.get)
        poc_volume = tpo_count[poc_price]
        
        # Calculate Value Area (70% of volume)
        sorted_levels = sorted(tpo_count.items(), key=lambda x: x[1], reverse=True)
        total_tpo = sum(tpo_count.values())
        target_tpo = total_tpo * 0.70
        
        accumulated = 0
        value_area_prices = []
        for price, count in sorted_levels:
            accumulated += count
            value_area_prices.append(price)
            if accumulated >= target_tpo:
                break
        
        vah = max(value_area_prices)  # Value Area High
        val = min(value_area_prices)  # Value Area Low
        
        current_price = ohlcv[-1][4]
        
        # Generate signal
        if current_price < val:
            signal, confidence = 'BUY', 0.75
            reason = "Price below value area - potential reversion"
        elif current_price > vah:
            signal, confidence = 'SELL', 0.75
            reason = "Price above value area - potential reversion"
        elif abs(current_price - poc_price) < price_increment * 2:
            signal, confidence = 'HOLD', 0.80
            reason = "Price near POC - balanced market"
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Price in value area"
        
        self.metrics['profiles_generated'] += 1
        
        return {
            'poc': poc_price,
            'vah': vah,
            'val': val,
            'value_area_width': vah - val,
            'current_price': current_price,
            'position_in_range': (current_price - val) / (vah - val) if (vah - val) > 0 else 0.5,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MarketProfileBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
