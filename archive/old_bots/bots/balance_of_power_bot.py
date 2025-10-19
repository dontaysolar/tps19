#!/usr/bin/env python3
"""Balance of Power Bot - Buyer vs seller strength"""
from datetime import datetime
from typing import Dict, List

class BalanceOfPowerBot:
    def __init__(self):
        self.name = "Balance_Of_Power"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'signals': 0}
    
    def calculate_bop(self, ohlcv: List) -> Dict:
        """Calculate Balance of Power"""
        if not ohlcv:
            return {'error': 'No data'}
        
        candle = ohlcv[-1]
        open_price, high, low, close = candle[1], candle[2], candle[3], candle[4]
        
        # BOP = (Close - Open) / (High - Low)
        if high != low:
            bop = (close - open_price) / (high - low)
        else:
            bop = 0
        
        if bop > 0.5:
            signal, confidence = 'BUY', 0.75
            reason = "Strong buying pressure"
        elif bop < -0.5:
            signal, confidence = 'SELL', 0.75
            reason = "Strong selling pressure"
        elif bop > 0:
            signal, confidence = 'BUY', 0.60
            reason = "Buyers in control"
        else:
            signal, confidence = 'SELL', 0.60
            reason = "Sellers in control"
        
        self.metrics['signals'] += 1
        
        return {
            'bop': bop,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = BalanceOfPowerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
