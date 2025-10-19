#!/usr/bin/env python3
"""
MARKET ANALYSIS LAYER
All technical indicators, patterns, and analysis consolidated
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class MarketAnalysisLayer:
    """Comprehensive market analysis - all features integrated"""
    
    def __init__(self):
        self.name = "Market_Analysis_Layer"
        self.version = "1.0.0"
        
    def analyze_comprehensive(self, ohlcv: List) -> Dict:
        """Run complete market analysis"""
        if len(ohlcv) < 50:
            return {'error': 'Insufficient data'}
        
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        return {
            'trend': self.analyze_trend(closes, highs, lows),
            'momentum': self.analyze_momentum(closes),
            'volatility': self.analyze_volatility(closes, highs, lows),
            'volume': self.analyze_volume(volumes, closes),
            'support_resistance': self.find_key_levels(highs, lows, closes),
            'patterns': self.detect_patterns(ohlcv),
            'price_action': self.analyze_price_action(ohlcv),
            'market_structure': self.analyze_market_structure(ohlcv),
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_trend(self, closes, highs, lows) -> Dict:
        """Consolidated trend analysis"""
        current = closes[-1]
        
        # Moving averages
        sma_20 = closes[-20:].mean()
        sma_50 = closes[-50:].mean() if len(closes) >= 50 else sma_20
        sma_200 = closes[-200:].mean() if len(closes) >= 200 else sma_50
        ema_12 = closes[-12:].mean()  # Simplified
        ema_26 = closes[-26:].mean() if len(closes) >= 26 else ema_12
        
        # Trend direction
        if sma_20 > sma_50 > sma_200:
            trend_strength = 'STRONG_UPTREND'
            trend_score = 0.9
        elif sma_20 > sma_50:
            trend_strength = 'UPTREND'
            trend_score = 0.7
        elif sma_20 < sma_50 < sma_200:
            trend_strength = 'STRONG_DOWNTREND'
            trend_score = -0.9
        elif sma_20 < sma_50:
            trend_strength = 'DOWNTREND'
            trend_score = -0.7
        else:
            trend_strength = 'SIDEWAYS'
            trend_score = 0.0
        
        # ADX (simplified)
        high_diff = np.diff(highs)
        low_diff = -np.diff(lows)
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        adx = abs(plus_dm[-14:].mean() - minus_dm[-14:].mean()) * 10  # Simplified
        
        return {
            'direction': trend_strength,
            'score': trend_score,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'adx': min(adx, 100),
            'current_vs_sma20': (current - sma_20) / sma_20 * 100
        }
    
    def analyze_momentum(self, closes) -> Dict:
        """Consolidated momentum indicators"""
        # RSI
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = gains[-14:].mean()
        avg_loss = losses[-14:].mean()
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = closes[-12:].mean()
        ema_26 = closes[-26:].mean() if len(closes) >= 26 else ema_12
        macd = ema_12 - ema_26
        macd_signal = macd * 0.9  # Simplified signal line
        
        # ROC
        roc = ((closes[-1] - closes[-10]) / closes[-10] * 100) if len(closes) > 10 else 0
        
        # Stochastic
        low_14 = closes[-14:].min()
        high_14 = closes[-14:].max()
        stochastic = ((closes[-1] - low_14) / (high_14 - low_14) * 100) if (high_14 - low_14) > 0 else 50
        
        # CCI (simplified)
        typical_prices = closes[-20:]
        sma = typical_prices.mean()
        mean_deviation = np.mean(np.abs(typical_prices - sma))
        cci = (closes[-1] - sma) / (0.015 * mean_deviation) if mean_deviation > 0 else 0
        
        return {
            'rsi': rsi,
            'rsi_signal': 'OVERSOLD' if rsi < 30 else 'OVERBOUGHT' if rsi > 70 else 'NEUTRAL',
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd - macd_signal,
            'roc': roc,
            'stochastic': stochastic,
            'cci': cci,
            'momentum_score': (rsi - 50) / 50  # Normalized -1 to 1
        }
    
    def analyze_volatility(self, closes, highs, lows) -> Dict:
        """Consolidated volatility indicators"""
        # ATR
        tr = np.maximum(highs[1:] - lows[1:], 
                       np.maximum(abs(highs[1:] - closes[:-1]), 
                                 abs(lows[1:] - closes[:-1])))
        atr = tr[-14:].mean() if len(tr) >= 14 else tr.mean()
        atr_pct = (atr / closes[-1]) * 100
        
        # Bollinger Bands
        sma = closes[-20:].mean()
        std = closes[-20:].std()
        bb_upper = sma + 2 * std
        bb_lower = sma - 2 * std
        bb_middle = sma
        bb_width = ((bb_upper - bb_lower) / bb_middle) * 100
        
        # Current position in BB
        bb_position = (closes[-1] - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        # Keltner Channels
        keltner_upper = sma + 2 * atr
        keltner_lower = sma - 2 * atr
        
        # Historical volatility
        returns = np.diff(np.log(closes[-20:]))
        hist_vol = np.std(returns) * np.sqrt(252) * 100  # Annualized
        
        # Volatility regime
        if atr_pct > 5:
            regime = 'HIGH'
        elif atr_pct > 2:
            regime = 'MEDIUM'
        else:
            regime = 'LOW'
        
        return {
            'atr': atr,
            'atr_pct': atr_pct,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_width': bb_width,
            'bb_position': bb_position,
            'keltner_upper': keltner_upper,
            'keltner_lower': keltner_lower,
            'historical_vol': hist_vol,
            'regime': regime,
            'squeeze': bb_width < 3  # Low volatility squeeze
        }
    
    def analyze_volume(self, volumes, closes) -> Dict:
        """Consolidated volume analysis"""
        avg_vol = volumes[-20:].mean()
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        
        # Volume trend
        vol_sma_short = volumes[-5:].mean()
        vol_sma_long = volumes[-20:].mean()
        vol_trend = 'INCREASING' if vol_sma_short > vol_sma_long else 'DECREASING'
        
        # On Balance Volume (simplified)
        obv = 0
        for i in range(1, len(volumes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        
        # MFI (Money Flow Index)
        typical_prices = closes[-14:]
        money_flow = typical_prices * volumes[-14:]
        positive_flow = sum([money_flow[i] for i in range(1, len(money_flow)) if typical_prices[i] > typical_prices[i-1]])
        negative_flow = sum([money_flow[i] for i in range(1, len(money_flow)) if typical_prices[i] < typical_prices[i-1]])
        mfi = 100 - (100 / (1 + positive_flow / (negative_flow + 1e-10)))
        
        return {
            'current': current_vol,
            'average': avg_vol,
            'ratio': vol_ratio,
            'trend': vol_trend,
            'obv': obv,
            'mfi': mfi,
            'climax': vol_ratio > 3,
            'signal': 'HIGH' if vol_ratio > 2 else 'NORMAL' if vol_ratio > 0.8 else 'LOW'
        }
    
    def find_key_levels(self, highs, lows, closes) -> Dict:
        """Support/Resistance + Pivot Points"""
        current = closes[-1]
        
        # Recent high/low
        resistance = highs[-20:].max() if len(highs) >= 20 else highs.max()
        support = lows[-20:].min() if len(lows) >= 20 else lows.min()
        
        # Pivot points
        high = highs[-1]
        low = lows[-1]
        close = closes[-1]
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        
        # Fibonacci levels (from swing high to low)
        swing_high = highs[-50:].max() if len(highs) >= 50 else high
        swing_low = lows[-50:].min() if len(lows) >= 50 else low
        diff = swing_high - swing_low
        
        fib_236 = swing_high - 0.236 * diff
        fib_382 = swing_high - 0.382 * diff
        fib_50 = swing_high - 0.50 * diff
        fib_618 = swing_high - 0.618 * diff
        
        return {
            'resistance': resistance,
            'support': support,
            'pivot': pivot,
            'r1': r1, 'r2': r2,
            's1': s1, 's2': s2,
            'fib_236': fib_236,
            'fib_382': fib_382,
            'fib_50': fib_50,
            'fib_618': fib_618,
            'current': current,
            'near_resistance': abs(current - resistance) / current < 0.01,
            'near_support': abs(current - support) / current < 0.01
        }
    
    def detect_patterns(self, ohlcv: List) -> Dict:
        """Pattern detection"""
        if len(ohlcv) < 3:
            return {}
        
        patterns = []
        
        # Candlestick patterns
        last = ohlcv[-1]
        o, h, l, c = last[1], last[2], last[3], last[4]
        body = abs(c - o)
        total_range = h - l
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        
        if body < total_range * 0.1:
            patterns.append('DOJI')
        if lower_wick > body * 2 and c > o:
            patterns.append('HAMMER')
        if upper_wick > body * 2:
            patterns.append('SHOOTING_STAR')
        
        return {
            'candlestick': patterns,
            'chart_patterns': [],  # Could add head & shoulders, etc
            'count': len(patterns)
        }
    
    def analyze_price_action(self, ohlcv: List) -> Dict:
        """Price action analysis"""
        if len(ohlcv) < 10:
            return {}
        
        recent = ohlcv[-10:]
        highs = [c[2] for c in recent]
        lows = [c[3] for c in recent]
        
        # Higher highs, higher lows
        hh = all(highs[i] >= highs[i-1] for i in range(1, len(highs)))
        hl = all(lows[i] >= lows[i-1] for i in range(1, len(lows)))
        ll = all(lows[i] <= lows[i-1] for i in range(1, len(lows)))
        lh = all(highs[i] <= highs[i-1] for i in range(1, len(highs)))
        
        if hh and hl:
            structure = 'STRONG_UPTREND'
        elif ll and lh:
            structure = 'STRONG_DOWNTREND'
        elif hh:
            structure = 'UPTREND'
        elif ll:
            structure = 'DOWNTREND'
        else:
            structure = 'CONSOLIDATION'
        
        return {
            'structure': structure,
            'higher_highs': hh,
            'higher_lows': hl,
            'lower_lows': ll,
            'lower_highs': lh
        }
    
    def analyze_market_structure(self, ohlcv: List) -> Dict:
        """Market structure analysis"""
        closes = np.array([c[4] for c in ohlcv])
        
        # Linear regression for trend
        x = np.arange(len(closes))
        slope, intercept = np.polyfit(x, closes, 1)
        slope_pct = (slope / closes[0]) * 100
        
        # R-squared (trendiness)
        y_pred = slope * x + intercept
        ss_res = np.sum((closes - y_pred) ** 2)
        ss_tot = np.sum((closes - np.mean(closes)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'slope': slope_pct,
            'r_squared': r_squared,
            'trending': r_squared > 0.7,
            'trend_strength': r_squared
        }

if __name__ == '__main__':
    layer = MarketAnalysisLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
