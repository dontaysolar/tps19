#!/usr/bin/env python3
"""
Volatility Regime Detection Bot
Identifies market volatility states:
- LOW volatility (compression, breakout pending)
- NORMAL volatility (standard trading)
- HIGH volatility (expansion, risk management critical)
Uses ATR, Bollinger Band Width, Historical Volatility
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class VolatilityRegimeBot:
    def __init__(self):
        self.name = "Volatility_Regime"
        self.version = "1.0.0"
        self.enabled = True
        
        self.atr_period = 14
        self.bb_period = 20
        self.bb_std = 2
        
        self.metrics = {
            'low_vol_periods': 0,
            'high_vol_periods': 0,
            'breakouts_detected': 0
        }
    
    def analyze_volatility_regime(self, ohlcv: List) -> Dict:
        """Detect current volatility regime"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate volatility indicators
        atr = self._calculate_atr(highs, lows, closes)
        bb_width = self._calculate_bb_width(closes)
        hist_vol = self._calculate_historical_volatility(closes)
        
        # Determine regime
        regime = self._determine_regime(atr[-1], bb_width[-1], hist_vol)
        
        # Predict regime change
        regime_change = self._predict_regime_change(atr, bb_width)
        
        # Generate signal
        signal, confidence = self._generate_vol_signal(regime, regime_change, closes)
        
        return {
            'regime': regime,
            'atr': atr[-1],
            'bb_width': bb_width[-1],
            'historical_vol': hist_vol,
            'regime_change_predicted': regime_change,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(regime, regime_change),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_atr(self, highs, lows, closes) -> np.ndarray:
        """Calculate Average True Range"""
        tr = np.maximum(
            highs[1:] - lows[1:],
            np.maximum(
                abs(highs[1:] - closes[:-1]),
                abs(lows[1:] - closes[:-1])
            )
        )
        
        atr = []
        for i in range(len(tr)):
            if i < self.atr_period - 1:
                atr.append(np.nan)
            else:
                atr.append(np.mean(tr[i - self.atr_period + 1:i + 1]))
        
        return np.array(atr)
    
    def _calculate_bb_width(self, closes) -> np.ndarray:
        """Calculate Bollinger Band Width"""
        bb_width = []
        
        for i in range(len(closes)):
            if i < self.bb_period - 1:
                bb_width.append(np.nan)
            else:
                period_data = closes[i - self.bb_period + 1:i + 1]
                sma = np.mean(period_data)
                std = np.std(period_data)
                
                upper = sma + (self.bb_std * std)
                lower = sma - (self.bb_std * std)
                width = (upper - lower) / sma * 100
                
                bb_width.append(width)
        
        return np.array(bb_width)
    
    def _calculate_historical_volatility(self, closes, period=20) -> float:
        """Calculate historical volatility (annualized)"""
        if len(closes) < period:
            return 0
        
        returns = np.diff(np.log(closes[-period:]))
        vol = np.std(returns) * np.sqrt(365) * 100
        
        return vol
    
    def _determine_regime(self, atr, bb_width, hist_vol) -> str:
        """Determine current volatility regime"""
        # Normalize ATR
        # Low volatility: compressed, preparing for breakout
        # High volatility: expanded, trending or chaotic
        
        if bb_width < 2:  # Very tight Bollinger Bands
            self.metrics['low_vol_periods'] += 1
            return 'LOW_VOLATILITY'
        elif bb_width > 10:  # Very wide Bollinger Bands
            self.metrics['high_vol_periods'] += 1
            return 'HIGH_VOLATILITY'
        else:
            return 'NORMAL_VOLATILITY'
    
    def _predict_regime_change(self, atr, bb_width) -> Dict:
        """Predict upcoming regime change"""
        if len(atr) < 10:
            return {'change_expected': False}
        
        # Check for BB width compression (squeeze)
        current_bb = bb_width[-1]
        avg_bb = np.nanmean(bb_width[-20:])
        
        if current_bb < avg_bb * 0.5:
            # Squeeze detected - breakout imminent
            self.metrics['breakouts_detected'] += 1
            return {
                'change_expected': True,
                'type': 'BREAKOUT_IMMINENT',
                'probability': 0.80
            }
        
        # Check for volatility expansion
        atr_trend = atr[-1] / np.nanmean(atr[-10:]) if np.nanmean(atr[-10:]) > 0 else 1
        if atr_trend > 1.5:
            return {
                'change_expected': True,
                'type': 'VOLATILITY_EXPANDING',
                'probability': 0.70
            }
        
        return {'change_expected': False}
    
    def _generate_vol_signal(self, regime, regime_change, closes) -> tuple:
        """Generate signal from volatility analysis"""
        
        # Low volatility + breakout imminent = wait for direction
        if regime == 'LOW_VOLATILITY' and regime_change.get('change_expected'):
            return ('HOLD', 0.80)  # High confidence to wait
        
        # High volatility = reduce position size or stay out
        if regime == 'HIGH_VOLATILITY':
            return ('HOLD', 0.70)
        
        # Normal volatility = trade as usual
        if regime == 'NORMAL_VOLATILITY':
            # Use price action for direction
            if closes[-1] > closes[-5]:
                return ('BUY', 0.65)
            else:
                return ('SELL', 0.65)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, regime, regime_change) -> str:
        """Get human-readable reason"""
        if regime_change.get('change_expected'):
            return f"{regime} - {regime_change['type']} ({regime_change['probability']:.0%} probability)"
        
        return f"Market in {regime} state"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = VolatilityRegimeBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
