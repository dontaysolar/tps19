#!/usr/bin/env python3
"""Mean Reversion Bot - Trades back to mean"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class MeanReversionBot:
    def __init__(self):
        self.name = "Mean_Reversion"
        self.version = "1.0.0"
        self.enabled = True
        self.lookback = 20
        self.std_threshold = 2
        self.metrics = {'trades': 0}
    
    def analyze_reversion(self, ohlcv: List) -> Dict:
        """Detect mean reversion opportunities"""
        if len(ohlcv) < self.lookback:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv[-self.lookback:]])
        
        mean = closes.mean()
        std = closes.std()
        current = closes[-1]
        
        # Z-score
        z_score = (current - mean) / std if std > 0 else 0
        
        # Distance from mean
        distance_pct = ((current - mean) / mean) * 100
        
        # Mean reversion signal
        if z_score < -self.std_threshold:
            signal, confidence = 'BUY', 0.80
            reason = f"Price {abs(z_score):.1f} std below mean"
            target = mean
            self.metrics['trades'] += 1
        
        elif z_score > self.std_threshold:
            signal, confidence = 'SELL', 0.80
            reason = f"Price {z_score:.1f} std above mean"
            target = mean
            self.metrics['trades'] += 1
        
        elif z_score < -1:
            signal, confidence = 'BUY', 0.65
            reason = "Price below mean"
            target = mean
        
        elif z_score > 1:
            signal, confidence = 'SELL', 0.65
            reason = "Price above mean"
            target = mean
        
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Price near mean"
            target = mean
        
        return {
            'mean': mean,
            'std': std,
            'z_score': z_score,
            'distance_pct': distance_pct,
            'target_price': target,
            'current_price': current,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'lookback': self.lookback, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = MeanReversionBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
