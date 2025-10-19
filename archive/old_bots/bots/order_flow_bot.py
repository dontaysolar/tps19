#!/usr/bin/env python3
"""
Order Flow Analysis Bot
Analyzes:
- Buy/Sell volume imbalance
- Cumulative Volume Delta (CVD)
- Order Block detection
- Liquidity zones
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

class OrderFlowBot:
    def __init__(self):
        self.name = "Order_Flow"
        self.version = "1.0.0"
        self.enabled = True
        
        self.imbalance_threshold = 0.65  # 65% buy or sell for imbalance
        
        self.metrics = {
            'buy_imbalances': 0,
            'sell_imbalances': 0,
            'order_blocks_found': 0,
            'liquidity_grabs': 0
        }
    
    def analyze_order_flow(self, ohlcv: List) -> Dict:
        """
        Analyze order flow patterns
        """
        if len(ohlcv) < 20:
            return {'error': 'Insufficient data'}
        
        opens = np.array([c[1] for c in ohlcv])
        closes = np.array([c[4] for c in ohlcv])
        highs = np.array([c[2] for c in ohlcv])
        lows = np.array([c[3] for c in ohlcv])
        volumes = np.array([c[5] for c in ohlcv])
        
        # Estimate buy/sell volume
        buy_volume, sell_volume = self._estimate_buy_sell_volume(opens, closes, highs, lows, volumes)
        
        # Calculate CVD
        cvd = self._calculate_cvd(buy_volume, sell_volume)
        
        # Detect order blocks
        order_blocks = self._detect_order_blocks(opens, closes, highs, lows, volumes)
        
        # Detect liquidity zones
        liquidity_zones = self._detect_liquidity_zones(highs, lows)
        
        # Generate signal
        signal, confidence = self._generate_orderflow_signal(
            buy_volume, sell_volume, cvd, order_blocks, liquidity_zones, closes[-1]
        )
        
        return {
            'buy_volume_pct': (buy_volume[-1] / (buy_volume[-1] + sell_volume[-1])) * 100,
            'sell_volume_pct': (sell_volume[-1] / (buy_volume[-1] + sell_volume[-1])) * 100,
            'cvd_current': cvd[-1],
            'cvd_trend': 'BULLISH' if cvd[-1] > cvd[-5] else 'BEARISH',
            'order_blocks': order_blocks,
            'liquidity_zones': liquidity_zones,
            'signal': signal,
            'confidence': confidence,
            'strength': confidence * 100,
            'reason': self._get_reason(buy_volume[-1], sell_volume[-1], cvd[-1], order_blocks),
            'timestamp': datetime.now().isoformat()
        }
    
    def _estimate_buy_sell_volume(self, opens, closes, highs, lows, volumes):
        """Estimate buy vs sell volume from candle characteristics"""
        buy_volume = np.zeros(len(volumes))
        sell_volume = np.zeros(len(volumes))
        
        for i in range(len(volumes)):
            close_position = (closes[i] - lows[i]) / (highs[i] - lows[i]) if highs[i] != lows[i] else 0.5
            
            # Estimate: higher close = more buying
            buy_volume[i] = volumes[i] * close_position
            sell_volume[i] = volumes[i] * (1 - close_position)
            
            # Adjust based on candle direction
            if closes[i] > opens[i]:  # Green candle
                buy_volume[i] *= 1.2
                sell_volume[i] *= 0.8
            else:  # Red candle
                buy_volume[i] *= 0.8
                sell_volume[i] *= 1.2
        
        return buy_volume, sell_volume
    
    def _calculate_cvd(self, buy_volume, sell_volume) -> np.ndarray:
        """Calculate Cumulative Volume Delta"""
        delta = buy_volume - sell_volume
        cvd = np.cumsum(delta)
        return cvd
    
    def _detect_order_blocks(self, opens, closes, highs, lows, volumes) -> List[Dict]:
        """
        Detect order blocks (institutional supply/demand zones)
        Order block = strong directional move with high volume
        """
        order_blocks = []
        
        for i in range(5, len(closes)):
            # Bullish order block: strong up move with volume
            if closes[i] > closes[i-1] * 1.02:  # 2% move
                if volumes[i] > np.mean(volumes[i-10:i]) * 1.5:
                    order_blocks.append({
                        'type': 'BULLISH',
                        'price': lows[i],  # Support zone
                        'strength': volumes[i] / np.mean(volumes[i-10:i]),
                        'index': i
                    })
                    self.metrics['order_blocks_found'] += 1
            
            # Bearish order block: strong down move with volume
            elif closes[i] < closes[i-1] * 0.98:
                if volumes[i] > np.mean(volumes[i-10:i]) * 1.5:
                    order_blocks.append({
                        'type': 'BEARISH',
                        'price': highs[i],  # Resistance zone
                        'strength': volumes[i] / np.mean(volumes[i-10:i]),
                        'index': i
                    })
                    self.metrics['order_blocks_found'] += 1
        
        return order_blocks[-5:]  # Return 5 most recent
    
    def _detect_liquidity_zones(self, highs, lows) -> List[Dict]:
        """Detect liquidity zones (areas where stop losses cluster)"""
        liquidity_zones = []
        
        # Recent swing highs/lows = liquidity zones
        for i in range(10, len(highs) - 10):
            # Swing high = liquidity above
            if highs[i] == np.max(highs[i-10:i+10]):
                liquidity_zones.append({
                    'type': 'HIGH',
                    'price': highs[i],
                    'index': i
                })
            
            # Swing low = liquidity below
            if lows[i] == np.min(lows[i-10:i+10]):
                liquidity_zones.append({
                    'type': 'LOW',
                    'price': lows[i],
                    'index': i
                })
        
        return liquidity_zones[-5:]
    
    def _generate_orderflow_signal(self, buy_vol, sell_vol, cvd, order_blocks, liq_zones, price) -> tuple:
        """Generate signal from order flow"""
        
        # Strong buy imbalance
        recent_buy_pct = buy_vol[-1] / (buy_vol[-1] + sell_vol[-1])
        if recent_buy_pct > self.imbalance_threshold:
            self.metrics['buy_imbalances'] += 1
            
            # CVD trending up = confirmation
            if cvd[-1] > cvd[-5]:
                return ('BUY', 0.85)
            return ('BUY', 0.70)
        
        # Strong sell imbalance
        if recent_buy_pct < (1 - self.imbalance_threshold):
            self.metrics['sell_imbalances'] += 1
            
            # CVD trending down = confirmation
            if cvd[-1] < cvd[-5]:
                return ('SELL', 0.85)
            return ('SELL', 0.70)
        
        # Check order block proximity
        for ob in order_blocks:
            if abs(price - ob['price']) / price < 0.01:
                if ob['type'] == 'BULLISH':
                    return ('BUY', 0.75)
                else:
                    return ('SELL', 0.75)
        
        return ('HOLD', 0.0)
    
    def _get_reason(self, buy_vol, sell_vol, cvd, order_blocks) -> str:
        """Get human-readable reason"""
        buy_pct = (buy_vol / (buy_vol + sell_vol)) * 100
        
        if buy_pct > 65:
            return f"Strong buy volume ({buy_pct:.0f}%), CVD: {cvd:.2f}"
        elif buy_pct < 35:
            return f"Strong sell volume ({100-buy_pct:.0f}%), CVD: {cvd:.2f}"
        elif order_blocks:
            ob = order_blocks[-1]
            return f"{ob['type']} order block at {ob['price']:.2f}"
        
        return "Balanced order flow"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = OrderFlowBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
