#!/usr/bin/env python3
"""Volatility Breakout Bot - Trades volatility expansions"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class VolatilityBreakoutBot:
    def __init__(self):
        self.name = "Volatility_Breakout"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'breakouts': 0}
    
    def detect_breakout(self, ohlcv: List) -> Dict:
        """Detect volatility breakouts"""
        if len(ohlcv) < 30:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Historical volatility (20-day)
        returns = np.diff(np.log(closes[-20:]))
        hist_vol = np.std(returns) * np.sqrt(252)  # Annualized
        
        # Recent volatility (5-day)
        recent_returns = np.diff(np.log(closes[-5:]))
        recent_vol = np.std(recent_returns) * np.sqrt(252)
        
        # Volatility ratio
        vol_ratio = recent_vol / hist_vol if hist_vol > 0 else 1
        
        # Price movement
        price_change = (closes[-1] - closes[-5]) / closes[-5] if closes[-5] > 0 else 0
        
        # Volatility breakout
        if vol_ratio > 2 and abs(price_change) > 0.05:
            self.metrics['breakouts'] += 1
            
            if price_change > 0:
                signal, confidence = 'BUY', 0.85
                reason = "Volatility breakout upward"
            else:
                signal, confidence = 'SELL', 0.85
                reason = "Volatility breakout downward"
        
        elif vol_ratio > 1.5:
            signal, confidence = 'CAUTION', 0.70
            reason = "Volatility increasing"
        
        elif vol_ratio < 0.5:
            signal, confidence = 'HOLD', 0.60
            reason = "Volatility contraction - await breakout"
        
        else:
            signal, confidence = 'HOLD', 0.50
            reason = "Normal volatility"
        
        return {
            'historical_vol': hist_vol,
            'recent_vol': recent_vol,
            'vol_ratio': vol_ratio,
            'price_change_pct': price_change * 100,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = VolatilityBreakoutBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
