#!/usr/bin/env python3
"""Money Flow Index Bot - Volume-weighted momentum"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MoneyFlowIndexBot:
    def __init__(self):
        self.name = "Money_Flow_Index"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 14
        self.metrics = {'signals': 0}
    
    def calculate_mfi(self, ohlcv: List) -> Dict:
        """Calculate Money Flow Index"""
        if len(ohlcv) < self.period + 1:
            return {'error': 'Insufficient data'}
        
        # Calculate typical price
        typical_prices = [(c[2] + c[3] + c[4]) / 3 for c in ohlcv]
        volumes = [c[5] for c in ohlcv]
        
        # Money flow
        money_flow = [tp * vol for tp, vol in zip(typical_prices, volumes)]
        
        # Positive and negative money flow
        positive_flow = sum([money_flow[i] for i in range(1, len(money_flow)) 
                            if typical_prices[i] > typical_prices[i-1]])
        negative_flow = sum([money_flow[i] for i in range(1, len(money_flow)) 
                            if typical_prices[i] < typical_prices[i-1]])
        
        # MFI
        if negative_flow == 0:
            mfi = 100
        else:
            money_ratio = positive_flow / negative_flow
            mfi = 100 - (100 / (1 + money_ratio))
        
        if mfi < 20:
            signal, confidence = 'BUY', 0.80
        elif mfi > 80:
            signal, confidence = 'SELL', 0.80
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {
            'mfi': mfi,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MoneyFlowIndexBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
