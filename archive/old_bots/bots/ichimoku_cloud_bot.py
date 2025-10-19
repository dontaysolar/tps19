#!/usr/bin/env python3
"""
Ichimoku Cloud Bot
Complete Ichimoku Kinko Hyo system with all 5 components:
- Tenkan-sen (Conversion Line)
- Kijun-sen (Base Line)
- Senkou Span A (Leading Span A)
- Senkou Span B (Leading Span B)
- Chikou Span (Lagging Span)
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class IchimokuCloudBot:
    def __init__(self):
        self.name = "Ichimoku_Cloud"
        self.version = "1.0.0"
        self.enabled = True
        
        # Ichimoku periods
        self.tenkan_period = 9   # Conversion Line
        self.kijun_period = 26   # Base Line
        self.senkou_b_period = 52  # Leading Span B
        self.displacement = 26    # Cloud displacement
        
        self.metrics = {
            'bullish_signals': 0,
            'bearish_signals': 0,
            'cloud_breakouts': 0,
            'tk_crosses': 0
        }
    
    def calculate_ichimoku(self, ohlcv: List) -> Dict:
        """
        Calculate all Ichimoku components and generate signals
        
        Returns:
            All Ichimoku lines, cloud status, and trading signal
        """
        if len(ohlcv) < 52:
            return {'error': 'Insufficient data (need 52+ candles)'}
        
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        
        # Calculate all Ichimoku components
        tenkan_sen = self._calculate_tenkan_sen(highs, lows)
        kijun_sen = self._calculate_kijun_sen(highs, lows)
        senkou_span_a = self._calculate_senkou_span_a(tenkan_sen, kijun_sen)
        senkou_span_b = self._calculate_senkou_span_b(highs, lows)
        chikou_span = self._calculate_chikou_span(closes)
        
        # Current values
        current_price = closes[-1]
        current_tenkan = tenkan_sen[-1]
        current_kijun = kijun_sen[-1]
        current_chikou = chikou_span[-self.displacement]  # Chikou is displaced backward
        
        # Cloud values (at current price location)
        cloud_top = max(senkou_span_a[-1], senkou_span_b[-1])
        cloud_bottom = min(senkou_span_a[-1], senkou_span_b[-1])
        cloud_color = 'BULLISH' if senkou_span_a[-1] > senkou_span_b[-1] else 'BEARISH'
        
        # Future cloud (26 periods ahead)
        future_cloud_top = max(senkou_span_a[-27], senkou_span_b[-27]) if len(senkou_span_a) >= 27 else None
        future_cloud_bottom = min(senkou_span_a[-27], senkou_span_b[-27]) if len(senkou_span_a) >= 27 else None
        
        # Determine price position relative to cloud
        if current_price > cloud_top:
            price_vs_cloud = 'ABOVE'
        elif current_price < cloud_bottom:
            price_vs_cloud = 'BELOW'
        else:
            price_vs_cloud = 'INSIDE'
        
        # Generate signal using all components
        signal, confidence = self._generate_ichimoku_signal(
            current_price, current_tenkan, current_kijun, current_chikou,
            cloud_top, cloud_bottom, cloud_color, price_vs_cloud,
            tenkan_sen, kijun_sen, closes
        )
        
        return {
            'tenkan_sen': current_tenkan,
            'kijun_sen': current_kijun,
            'senkou_span_a': senkou_span_a[-1],
            'senkou_span_b': senkou_span_b[-1],
            'chikou_span': current_chikou,
            'cloud_top': cloud_top,
            'cloud_bottom': cloud_bottom,
            'cloud_color': cloud_color,
            'price_vs_cloud': price_vs_cloud,
            'current_price': current_price,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(signal, price_vs_cloud, cloud_color, current_tenkan, current_kijun),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_tenkan_sen(self, highs, lows) -> np.ndarray:
        """Conversion Line: (9-period high + 9-period low) / 2"""
        tenkan = []
        for i in range(len(highs)):
            if i < self.tenkan_period - 1:
                tenkan.append(np.nan)
            else:
                period_high = np.max(highs[i - self.tenkan_period + 1:i + 1])
                period_low = np.min(lows[i - self.tenkan_period + 1:i + 1])
                tenkan.append((period_high + period_low) / 2)
        return np.array(tenkan)
    
    def _calculate_kijun_sen(self, highs, lows) -> np.ndarray:
        """Base Line: (26-period high + 26-period low) / 2"""
        kijun = []
        for i in range(len(highs)):
            if i < self.kijun_period - 1:
                kijun.append(np.nan)
            else:
                period_high = np.max(highs[i - self.kijun_period + 1:i + 1])
                period_low = np.min(lows[i - self.kijun_period + 1:i + 1])
                kijun.append((period_high + period_low) / 2)
        return np.array(kijun)
    
    def _calculate_senkou_span_a(self, tenkan, kijun) -> np.ndarray:
        """Leading Span A: (Tenkan + Kijun) / 2, displaced 26 periods forward"""
        senkou_a = (tenkan + kijun) / 2
        # Displacement handled in interpretation
        return senkou_a
    
    def _calculate_senkou_span_b(self, highs, lows) -> np.ndarray:
        """Leading Span B: (52-period high + 52-period low) / 2, displaced 26 forward"""
        senkou_b = []
        for i in range(len(highs)):
            if i < self.senkou_b_period - 1:
                senkou_b.append(np.nan)
            else:
                period_high = np.max(highs[i - self.senkou_b_period + 1:i + 1])
                period_low = np.min(lows[i - self.senkou_b_period + 1:i + 1])
                senkou_b.append((period_high + period_low) / 2)
        return np.array(senkou_b)
    
    def _calculate_chikou_span(self, closes) -> np.ndarray:
        """Lagging Span: Current close displaced 26 periods backward"""
        # Simply return closes (displacement applied in interpretation)
        return closes
    
    def _generate_ichimoku_signal(self, price, tenkan, kijun, chikou,
                                  cloud_top, cloud_bottom, cloud_color,
                                  price_vs_cloud, tenkan_history, kijun_history,
                                  closes) -> tuple:
        """
        Generate signal using multiple Ichimoku conditions
        
        Strong bullish signals (5/5 confirmations):
        1. Price above cloud
        2. Tenkan above Kijun
        3. Chikou above price (26 bars ago)
        4. Bullish cloud (Span A > Span B)
        5. TK cross occurred recently
        """
        confirmations = 0
        signal_strength = 0
        
        # Confirmation 1: Price vs Cloud
        if price_vs_cloud == 'ABOVE':
            confirmations += 1
            signal_strength += 20
        elif price_vs_cloud == 'BELOW':
            confirmations -= 1
            signal_strength -= 20
        
        # Confirmation 2: Tenkan vs Kijun
        if tenkan > kijun:
            confirmations += 1
            signal_strength += 20
        else:
            confirmations -= 1
            signal_strength -= 20
        
        # Confirmation 3: Chikou Span vs Price
        if len(closes) >= self.displacement and chikou > closes[-self.displacement]:
            confirmations += 1
            signal_strength += 15
        
        # Confirmation 4: Cloud Color
        if cloud_color == 'BULLISH':
            confirmations += 1
            signal_strength += 15
        else:
            confirmations -= 1
            signal_strength -= 15
        
        # Confirmation 5: Recent TK Cross
        tk_cross = self._check_tk_cross(tenkan_history, kijun_history)
        if tk_cross == 'BULLISH':
            confirmations += 1
            signal_strength += 30
            self.metrics['tk_crosses'] += 1
        elif tk_cross == 'BEARISH':
            confirmations -= 1
            signal_strength -= 30
        
        # Cloud breakout detection
        if self._check_cloud_breakout(price, closes, cloud_top, cloud_bottom):
            signal_strength += 20
            self.metrics['cloud_breakouts'] += 1
        
        # Generate final signal
        if confirmations >= 4:
            self.metrics['bullish_signals'] += 1
            return ('BUY', min(0.9, signal_strength / 100))
        elif confirmations <= -4:
            self.metrics['bearish_signals'] += 1
            return ('SELL', min(0.9, abs(signal_strength) / 100))
        elif confirmations >= 2:
            return ('BUY', min(0.7, signal_strength / 100))
        elif confirmations <= -2:
            return ('SELL', min(0.7, abs(signal_strength) / 100))
        
        return ('HOLD', 0.0)
    
    def _check_tk_cross(self, tenkan, kijun) -> Optional[str]:
        """Check for Tenkan-Kijun cross in last 3 periods"""
        if len(tenkan) < 3:
            return None
        
        # Bullish cross: Tenkan crosses above Kijun
        if tenkan[-1] > kijun[-1] and tenkan[-2] <= kijun[-2]:
            return 'BULLISH'
        
        # Bearish cross: Tenkan crosses below Kijun
        if tenkan[-1] < kijun[-1] and tenkan[-2] >= kijun[-2]:
            return 'BEARISH'
        
        return None
    
    def _check_cloud_breakout(self, price, closes, cloud_top, cloud_bottom) -> bool:
        """Check if price just broke through cloud"""
        if len(closes) < 2:
            return False
        
        prev_price = closes[-2]
        
        # Breakout above cloud
        if price > cloud_top and prev_price <= cloud_top:
            return True
        
        # Breakout below cloud
        if price < cloud_bottom and prev_price >= cloud_bottom:
            return True
        
        return False
    
    def _get_reason(self, signal, price_vs_cloud, cloud_color, tenkan, kijun) -> str:
        """Get human-readable reason"""
        if signal == 'BUY':
            reasons = []
            if price_vs_cloud == 'ABOVE':
                reasons.append("price above cloud")
            if tenkan > kijun:
                reasons.append("TK bullish")
            if cloud_color == 'BULLISH':
                reasons.append("bullish cloud")
            
            return f"Ichimoku BUY: {', '.join(reasons)}"
        
        elif signal == 'SELL':
            reasons = []
            if price_vs_cloud == 'BELOW':
                reasons.append("price below cloud")
            if tenkan < kijun:
                reasons.append("TK bearish")
            if cloud_color == 'BEARISH':
                reasons.append("bearish cloud")
            
            return f"Ichimoku SELL: {', '.join(reasons)}"
        
        return f"Ichimoku neutral - price {price_vs_cloud} cloud"
    
    def get_status(self) -> Dict:
        """Return bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = IchimokuCloudBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
