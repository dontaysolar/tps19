#!/usr%bin/env python3
"""Bollinger Band Squeeze - Volatility breakout detector"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class BollingerBandSqueezeBot:
    def __init__(self):
        self.name = "Bollinger_Band_Squeeze"
        self.version = "1.0.0"
        self.enabled = True
        
        self.period = 20
        self.std_dev = 2
        
        self.metrics = {'squeezes': 0, 'breakouts': 0}
    
    def calculate_bollinger_squeeze(self, ohlcv: List) -> Dict:
        """Calculate Bollinger Band squeeze"""
        if len(ohlcv) < self.period:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate Bollinger Bands
        sma = closes[-self.period:].mean()
        std = closes[-self.period:].std()
        
        upper_band = sma + (self.std_dev * std)
        lower_band = sma - (self.std_dev * std)
        band_width = upper_band - lower_band
        band_width_pct = (band_width / sma) * 100
        
        current_price = closes[-1]
        
        # Calculate squeeze (low volatility)
        # Compare current band width to historical
        if len(closes) >= 50:
            historical_widths = []
            for i in range(self.period, min(len(closes), 50)):
                hist_sma = closes[i-self.period:i].mean()
                hist_std = closes[i-self.period:i].std()
                hist_width = (2 * self.std_dev * hist_std / hist_sma) * 100
                historical_widths.append(hist_width)
            
            avg_historical_width = np.mean(historical_widths)
            
            is_squeeze = band_width_pct < avg_historical_width * 0.7
        else:
            is_squeeze = band_width_pct < 3  # Simple threshold
        
        if is_squeeze:
            self.metrics['squeezes'] += 1
            
            # Squeeze detected - prepare for breakout
            # Check direction indicators
            if current_price > sma:
                bias = 'BULLISH'
                signal = 'BUY_ON_BREAKOUT'
                confidence = 0.70
            elif current_price < sma:
                bias = 'BEARISH'
                signal = 'SELL_ON_BREAKOUT'
                confidence = 0.70
            else:
                bias = 'NEUTRAL'
                signal = 'WAIT'
                confidence = 0.50
            
            return {
                'squeeze_detected': True,
                'band_width_pct': band_width_pct,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'sma': sma,
                'current_price': current_price,
                'bias': bias,
                'signal': signal,
                'confidence': confidence,
                'reason': f"BB Squeeze - low volatility, {bias} bias",
                'timestamp': datetime.now().isoformat()
            }
        
        # Check for breakout
        if current_price > upper_band:
            self.metrics['breakouts'] += 1
            return {
                'squeeze_detected': False,
                'breakout': 'UPWARD',
                'signal': 'BUY',
                'confidence': 0.80,
                'reason': "Upward breakout from Bollinger Bands"
            }
        
        elif current_price < lower_band:
            self.metrics['breakouts'] += 1
            return {
                'squeeze_detected': False,
                'breakout': 'DOWNWARD',
                'signal': 'SELL',
                'confidence': 0.80,
                'reason': "Downward breakout from Bollinger Bands"
            }
        
        return {
            'squeeze_detected': False,
            'signal': 'HOLD',
            'band_width_pct': band_width_pct
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'period': self.period,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = BollingerBandSqueezeBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
