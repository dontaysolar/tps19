#!/usr/bin/env python3
"""
Market Cipher Style Indicators - Advanced multi-layered analysis
Combines wave trend, momentum, and divergence detection
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MarketCipherIndicators:
    """
    Market Cipher-style multi-disciplinary technical analysis
    Combines multiple signal layers for high accuracy
    """
    
    def __init__(self):
        self.name = "Market Cipher"
        
    def analyze(self, df) -> Optional[Dict]:
        """
        Comprehensive Market Cipher analysis
        
        Returns signals based on:
        - Wave Trend
        - Money Flow  
        - Momentum
        - Divergences
        - Volume
        """
        if not HAS_PANDAS:
            logger.warning("Pandas required for Market Cipher indicators")
            return None
        
        if len(df) < 100:
            return None
        
        # Calculate all indicator layers
        wave_trend = self._calculate_wave_trend(df)
        money_flow = self._calculate_money_flow(df)
        momentum = self._calculate_momentum_wave(df)
        divergence = self._detect_divergences(df)
        volume_analysis = self._analyze_volume(df)
        
        # Combine all signals
        signal = self._fuse_cipher_signals(
            wave_trend, money_flow, momentum, divergence, volume_analysis, df
        )
        
        return signal
    
    def _calculate_wave_trend(self, df) -> Dict:
        """
        Calculate Wave Trend indicator (similar to Market Cipher)
        Based on weighted moving average with volume
        """
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # Calculate HLC3 (typical price)
        hlc3 = (high + low + close) / 3
        
        # Apply EMA with volume weighting
        esa = hlc3.ewm(span=10, adjust=False).mean()
        d = (hlc3 - esa).abs().ewm(span=10, adjust=False).mean()
        ci = (hlc3 - esa) / (0.015 * d)
        
        # Wave trend calculation
        wt1 = ci.ewm(span=21, adjust=False).mean()
        wt2 = wt1.ewm(span=4, adjust=False).mean()
        
        # Current values
        wt1_current = wt1.iloc[-1]
        wt2_current = wt2.iloc[-1]
        wt1_prev = wt1.iloc[-2]
        
        # Signal logic
        if wt1_current > wt2_current and wt1_prev <= wt2.iloc[-2]:
            signal = 'BUY'
            strength = min(abs(wt1_current), 100) / 100
        elif wt1_current < wt2_current and wt1_prev >= wt2.iloc[-2]:
            signal = 'SELL'
            strength = min(abs(wt1_current), 100) / 100
        else:
            signal = 'NEUTRAL'
            strength = 0.5
        
        return {
            'signal': signal,
            'wt1': wt1_current,
            'wt2': wt2_current,
            'strength': strength,
            'oversold': wt1_current < -60,
            'overbought': wt1_current > 60
        }
    
    def _calculate_money_flow(self, df) -> Dict:
        """
        Calculate Money Flow Index (MFI) - volume-weighted RSI
        """
        high = df['high']
        low = df['low']
        close = df['close']
        volume = df['volume']
        
        # Typical price
        typical_price = (high + low + close) / 3
        
        # Money flow
        money_flow = typical_price * volume
        
        # Positive and negative money flow
        delta = typical_price.diff()
        positive_flow = money_flow.where(delta > 0, 0).rolling(14).sum()
        negative_flow = money_flow.where(delta < 0, 0).rolling(14).sum()
        
        # MFI calculation
        money_ratio = positive_flow / (negative_flow + 1e-10)
        mfi = 100 - (100 / (1 + money_ratio))
        
        current_mfi = mfi.iloc[-1]
        
        # Signal logic
        if current_mfi < 20:
            signal = 'BUY'
            confidence = 0.8
        elif current_mfi > 80:
            signal = 'SELL'
            confidence = 0.8
        else:
            signal = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'signal': signal,
            'mfi': current_mfi,
            'confidence': confidence,
            'oversold': current_mfi < 20,
            'overbought': current_mfi > 80
        }
    
    def _calculate_momentum_wave(self, df) -> Dict:
        """
        Calculate momentum wave using multiple oscillators
        """
        close = df['close']
        
        # Stochastic RSI
        rsi = self._calculate_stoch_rsi(df)
        
        # Rate of change
        roc = ((close - close.shift(14)) / close.shift(14) * 100).iloc[-1]
        
        # Momentum
        momentum = (close - close.shift(10)).iloc[-1]
        
        # Combine
        if rsi > 80 and momentum > 0:
            signal = 'BUY'
            strength = 0.8
        elif rsi < 20 and momentum < 0:
            signal = 'SELL'
            strength = 0.8
        else:
            signal = 'NEUTRAL'
            strength = 0.5
        
        return {
            'signal': signal,
            'stoch_rsi': rsi,
            'roc': roc,
            'momentum': momentum,
            'strength': strength
        }
    
    def _calculate_stoch_rsi(self, df, period: int = 14) -> float:
        """Calculate Stochastic RSI"""
        close = df['close']
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = -delta.where(delta < 0, 0).rolling(period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # Stochastic of RSI
        rsi_min = rsi.rolling(period).min()
        rsi_max = rsi.rolling(period).max()
        stoch_rsi = ((rsi - rsi_min) / (rsi_max - rsi_min + 1e-10)) * 100
        
        return stoch_rsi.iloc[-1]
    
    def _detect_divergences(self, df) -> Dict:
        """
        Detect bullish/bearish divergences
        Price makes new low but indicator makes higher low = bullish divergence
        """
        close = df['close']
        
        # Calculate RSI for divergence detection
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain / (loss + 1e-10)))
        
        # Look for divergences in last 20 periods
        lookback = 20
        price_lows = close.iloc[-lookback:].rolling(5).min()
        rsi_lows = rsi.iloc[-lookback:].rolling(5).min()
        
        # Bullish divergence: price making lower lows, RSI making higher lows
        price_trend = price_lows.iloc[-1] < price_lows.iloc[-10]
        rsi_trend = rsi_lows.iloc[-1] > rsi_lows.iloc[-10]
        
        if price_trend and rsi_trend:
            return {
                'type': 'bullish_divergence',
                'signal': 'BUY',
                'confidence': 0.75,
                'detected': True
            }
        
        # Bearish divergence: price making higher highs, RSI making lower highs
        price_highs = close.iloc[-lookback:].rolling(5).max()
        rsi_highs = rsi.iloc[-lookback:].rolling(5).max()
        
        price_trend_up = price_highs.iloc[-1] > price_highs.iloc[-10]
        rsi_trend_down = rsi_highs.iloc[-1] < rsi_highs.iloc[-10]
        
        if price_trend_up and rsi_trend_down:
            return {
                'type': 'bearish_divergence',
                'signal': 'SELL',
                'confidence': 0.75,
                'detected': True
            }
        
        return {
            'type': 'none',
            'signal': 'NEUTRAL',
            'confidence': 0.5,
            'detected': False
        }
    
    def _analyze_volume(self, df) -> Dict:
        """Advanced volume analysis"""
        volume = df['volume']
        close = df['close']
        
        # Volume moving average
        vol_ma = volume.rolling(20).mean()
        
        # Current vs average
        current_vol = volume.iloc[-1]
        avg_vol = vol_ma.iloc[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        # Volume trend
        vol_increasing = volume.iloc[-5:].is_monotonic_increasing
        
        # Price-volume confirmation
        price_up = close.iloc[-1] > close.iloc[-2]
        volume_up = current_vol > volume.iloc[-2]
        
        confirmation = (price_up and volume_up) or (not price_up and not volume_up)
        
        return {
            'volume_ratio': vol_ratio,
            'increasing': vol_increasing,
            'confirmation': confirmation,
            'signal': 'STRONG' if vol_ratio > 1.5 and confirmation else 'WEAK'
        }
    
    def _fuse_cipher_signals(self, wave_trend: Dict, money_flow: Dict,
                            momentum: Dict, divergence: Dict,
                            volume: Dict, df) -> Optional[Dict]:
        """
        Fuse all Market Cipher signals for final decision
        
        Requires multiple confirmations for high accuracy
        """
        # Count bullish and bearish signals
        bullish_count = 0
        bearish_count = 0
        
        signals = [wave_trend, money_flow, momentum, divergence]
        
        for signal_data in signals:
            if signal_data['signal'] == 'BUY':
                bullish_count += 1
            elif signal_data['signal'] == 'SELL':
                bearish_count += 1
        
        # Require at least 3 confirmations for signal
        min_confirmations = 3
        
        latest_price = df['close'].iloc[-1]
        
        if bullish_count >= min_confirmations:
            # Calculate confidence based on agreement
            confidence = 0.6 + (bullish_count / len(signals)) * 0.3
            
            # Boost confidence if volume confirms
            if volume['signal'] == 'STRONG' and volume['confirmation']:
                confidence = min(0.95, confidence + 0.1)
            
            # Boost if divergence detected
            if divergence['detected'] and divergence['type'] == 'bullish_divergence':
                confidence = min(0.95, confidence + 0.15)
            
            return {
                'signal': 'BUY',
                'strategy': 'Market Cipher',
                'confidence': confidence,
                'price': latest_price,
                'confirmations': bullish_count,
                'wave_trend': wave_trend,
                'money_flow': money_flow,
                'momentum': momentum,
                'divergence': divergence,
                'volume': volume,
                'reasoning': f"{bullish_count} bullish confirmations with {confidence:.0%} confidence"
            }
        
        elif bearish_count >= min_confirmations:
            confidence = 0.6 + (bearish_count / len(signals)) * 0.3
            
            if volume['signal'] == 'STRONG' and volume['confirmation']:
                confidence = min(0.95, confidence + 0.1)
            
            if divergence['detected'] and divergence['type'] == 'bearish_divergence':
                confidence = min(0.95, confidence + 0.15)
            
            return {
                'signal': 'SELL',
                'strategy': 'Market Cipher',
                'confidence': confidence,
                'price': latest_price,
                'confirmations': bearish_count,
                'wave_trend': wave_trend,
                'money_flow': money_flow,
                'momentum': momentum,
                'divergence': divergence,
                'volume': volume,
                'reasoning': f"{bearish_count} bearish confirmations with {confidence:.0%} confidence"
            }
        
        return None  # Not enough confirmations


# Global instance
market_cipher_indicators = MarketCipherIndicators()
