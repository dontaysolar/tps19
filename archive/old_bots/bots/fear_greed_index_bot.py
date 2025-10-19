#!/usr/bin/env python3
"""Fear & Greed Index Bot - Market sentiment gauge"""
import numpy as np
from datetime import datetime
from typing import Dict

class FearGreedIndexBot:
    def __init__(self):
        self.name = "Fear_Greed_Index"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'readings': 0}
    
    def calculate_index(self, market_data: Dict) -> Dict:
        """Calculate Fear & Greed Index (0-100)"""
        score = 50  # Neutral
        
        # Volatility component (25%)
        volatility = market_data.get('volatility', 0.02)
        if volatility < 0.02:
            score += 6.25  # Low vol = greed
        elif volatility > 0.05:
            score -= 6.25  # High vol = fear
        
        # Market momentum (25%)
        momentum = market_data.get('momentum', 0)
        score += momentum * 12.5
        
        # Market volume (25%)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        if volume_ratio > 1.2:
            score += 6.25
        elif volume_ratio < 0.8:
            score -= 6.25
        
        # Price strength (25%)
        price_change = market_data.get('price_change_pct', 0)
        score += price_change * 2.5
        
        score = max(0, min(100, score))
        
        # Categorize
        if score < 20:
            category, signal = 'EXTREME_FEAR', 'BUY'
            confidence = 0.85
        elif score < 45:
            category, signal = 'FEAR', 'BUY'
            confidence = 0.70
        elif score < 55:
            category, signal = 'NEUTRAL', 'HOLD'
            confidence = 0.50
        elif score < 75:
            category, signal = 'GREED', 'SELL'
            confidence = 0.70
        else:
            category, signal = 'EXTREME_GREED', 'SELL'
            confidence = 0.85
        
        self.metrics['readings'] += 1
        
        return {
            'index': score,
            'category': category,
            'signal': signal,
            'confidence': confidence,
            'components': {
                'volatility': volatility,
                'momentum': momentum,
                'volume': volume_ratio,
                'price_strength': price_change
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = FearGreedIndexBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
