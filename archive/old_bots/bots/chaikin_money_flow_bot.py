#!/usr/bin/env python3
"""Chaikin Money Flow - Volume-weighted accumulation/distribution"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class ChaikinMoneyFlowBot:
    def __init__(self):
        self.name = "Chaikin_Money_Flow"
        self.version = "1.0.0"
        self.enabled = True
        self.period = 20
        self.metrics = {'signals': 0}
    
    def calculate(self, ohlcv: List) -> Dict:
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        recent = ohlcv[-self.period:]
        
        cmf_values = []
        for candle in recent:
            high, low, close, volume = candle[2], candle[3], candle[4], candle[5]
            
            # Money Flow Multiplier
            if high != low:
                mf_multiplier = ((close - low) - (high - close)) / (high - low)
            else:
                mf_multiplier = 0
            
            # Money Flow Volume
            mf_volume = mf_multiplier * volume
            cmf_values.append(mf_volume)
        
        cmf = sum(cmf_values) / sum([c[5] for c in recent]) if sum([c[5] for c in recent]) > 0 else 0
        
        if cmf > 0.15:
            signal, confidence = 'BUY', 0.75
        elif cmf < -0.15:
            signal, confidence = 'SELL', 0.75
        else:
            signal, confidence = 'HOLD', 0.50
        
        self.metrics['signals'] += 1
        
        return {'cmf': cmf, 'signal': signal, 'confidence': confidence, 'timestamp': datetime.now().isoformat()}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = ChaikinMoneyFlowBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
