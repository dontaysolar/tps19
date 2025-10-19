#!/usr/bin/env python3
"""
Stochastic RSI Bot
Enhanced momentum oscillator
RSI applied to RSI for better sensitivity
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class StochasticRSIBot:
    def __init__(self):
        self.name = "Stochastic_RSI"
        self.version = "1.0.0"
        self.enabled = True
        
        self.rsi_period = 14
        self.stoch_period = 14
        
        self.metrics = {'signals': 0, 'overbought': 0, 'oversold': 0}
    
    def calculate_rsi(self, closes: np.ndarray) -> np.ndarray:
        """Calculate RSI"""
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.convolve(gains, np.ones(self.rsi_period)/self.rsi_period, mode='valid')
        avg_loss = np.convolve(losses, np.ones(self.rsi_period)/self.rsi_period, mode='valid')
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_stochastic_rsi(self, ohlcv: List) -> Dict:
        """Calculate Stochastic RSI"""
        if len(ohlcv) < self.rsi_period + self.stoch_period:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate RSI
        rsi = self.calculate_rsi(closes)
        
        if len(rsi) < self.stoch_period:
            return {'error': 'Insufficient RSI data'}
        
        # Apply Stochastic to RSI
        stoch_rsi = []
        for i in range(self.stoch_period - 1, len(rsi)):
            period_rsi = rsi[i - self.stoch_period + 1:i + 1]
            rsi_min = period_rsi.min()
            rsi_max = period_rsi.max()
            
            if rsi_max - rsi_min > 0:
                stoch = (rsi[i] - rsi_min) / (rsi_max - rsi_min) * 100
            else:
                stoch = 50
            
            stoch_rsi.append(stoch)
        
        current_stoch_rsi = stoch_rsi[-1]
        
        # Generate signal
        if current_stoch_rsi < 20:
            signal = 'BUY'
            confidence = 0.80
            reason = f"StochRSI oversold ({current_stoch_rsi:.1f})"
            self.metrics['oversold'] += 1
        elif current_stoch_rsi > 80:
            signal = 'SELL'
            confidence = 0.80
            reason = f"StochRSI overbought ({current_stoch_rsi:.1f})"
            self.metrics['overbought'] += 1
        else:
            signal = 'HOLD'
            confidence = 0.50
            reason = f"StochRSI neutral ({current_stoch_rsi:.1f})"
        
        self.metrics['signals'] += 1
        
        return {
            'stoch_rsi': current_stoch_rsi,
            'rsi': rsi[-1],
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = StochasticRSIBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
