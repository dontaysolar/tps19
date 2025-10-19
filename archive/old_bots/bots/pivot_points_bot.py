#!/usr/bin/env python3
"""Pivot Points Bot - Support/Resistance calculation"""
from datetime import datetime
from typing import Dict

class PivotPointsBot:
    def __init__(self):
        self.name = "Pivot_Points"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'calculations': 0}
    
    def calculate_pivot_points(self, high: float, low: float, close: float) -> Dict:
        """Calculate pivot points and support/resistance levels"""
        
        # Pivot Point
        pivot = (high + low + close) / 3
        
        # Resistance levels
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        # Support levels
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        self.metrics['calculations'] += 1
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_price_vs_pivots(self, current_price: float, pivots: Dict) -> Dict:
        """Analyze current price vs pivot levels"""
        pivot = pivots['pivot']
        
        if current_price < pivots['s3']:
            signal, confidence = 'BUY', 0.85
            reason = "Price below S3 - strong support"
        elif current_price < pivots['s2']:
            signal, confidence = 'BUY', 0.75
            reason = "Price near S2"
        elif current_price > pivots['r3']:
            signal, confidence = 'SELL', 0.85
            reason = "Price above R3 - strong resistance"
        elif current_price > pivots['r2']:
            signal, confidence = 'SELL', 0.75
            reason = "Price near R2"
        elif current_price > pivot:
            signal, confidence = 'BUY', 0.60
            reason = "Price above pivot - bullish"
        else:
            signal, confidence = 'SELL', 0.60
            reason = "Price below pivot - bearish"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'current_price': current_price,
            'pivots': pivots,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = PivotPointsBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
