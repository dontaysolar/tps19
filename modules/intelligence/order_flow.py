#!/usr/bin/env python3
"""
Order Flow Analyzer - Detect smart money and liquidity
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class OrderFlowAnalyzer:
    """
    Analyze order book and trade flow to detect institutional activity
    """
    
    def __init__(self):
        # Store recent data
        self.recent_trades = deque(maxlen=1000)
        self.orderbook_history = deque(maxlen=100)
        
        # Thresholds
        self.whale_threshold_multiplier = 10  # 10x median = whale trade
        self.wall_threshold = 50000  # $50k+ order = wall
        
    def analyze_orderbook(self, orderbook: Dict) -> Dict:
        """
        Comprehensive order book analysis
        
        Args:
            orderbook: {'bids': [(price, size), ...], 'asks': [(price, size), ...]}
            
        Returns:
            Analysis dict with signals and metrics
        """
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            return {'error': 'Empty orderbook'}
        
        # Store for historical analysis
        self.orderbook_history.append({
            'timestamp': datetime.now(),
            'bids': bids[:20],  # Top 20 levels
            'asks': asks[:20]
        })
        
        # 1. Liquidity Imbalance
        imbalance = self._calculate_imbalance(bids, asks)
        
        # 2. Detect Walls (large orders)
        bid_walls = self._detect_walls(bids, 'bid')
        ask_walls = self._detect_walls(asks, 'ask')
        
        # 3. Support/Resistance from order clustering
        support_levels = self._find_order_clusters(bids)
        resistance_levels = self._find_order_clusters(asks)
        
        # 4. Spread Analysis
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        spread = best_ask - best_bid
        spread_pct = spread / best_bid
        
        # 5. Depth Analysis
        bid_depth = self._calculate_depth(bids, best_bid, depth_pct=0.01)  # 1% depth
        ask_depth = self._calculate_depth(asks, best_ask, depth_pct=0.01)
        
        # 6. Order book pressure
        pressure = self._calculate_pressure(bids, asks, best_bid, best_ask)
        
        # Generate trading signal
        signal = self._generate_orderbook_signal(
            imbalance, bid_walls, ask_walls, pressure
        )
        
        return {
            'imbalance': imbalance,
            'signal': signal['direction'],
            'confidence': signal['confidence'],
            'bid_walls': bid_walls,
            'ask_walls': ask_walls,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'spread': spread,
            'spread_pct': spread_pct,
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'pressure': pressure,
            'analysis': signal['reasoning']
        }
    
    def _calculate_imbalance(self, bids: List[Tuple], asks: List[Tuple], 
                            levels: int = 20) -> float:
        """
        Calculate order book imbalance
        
        Returns:
            Imbalance from -1 (sell pressure) to +1 (buy pressure)
        """
        bid_volume = sum([size for price, size in bids[:levels]])
        ask_volume = sum([size for price, size in asks[:levels]])
        
        total = bid_volume + ask_volume
        if total == 0:
            return 0
        
        return (bid_volume - ask_volume) / total
    
    def _detect_walls(self, orders: List[Tuple], side: str) -> List[Dict]:
        """Detect large orders (walls)"""
        if not orders:
            return []
        
        # Calculate median order size
        sizes = [size for price, size in orders[:50]]
        median_size = np.median(sizes)
        
        # Find walls (orders significantly larger than median)
        walls = []
        for price, size in orders[:20]:
            value = price * size
            if value > self.wall_threshold and size > median_size * 5:
                walls.append({
                    'price': price,
                    'size': size,
                    'value': value,
                    'side': side,
                    'strength': size / median_size
                })
        
        return walls
    
    def _find_order_clusters(self, orders: List[Tuple], 
                            cluster_threshold: float = 0.001) -> List[float]:
        """
        Find price levels with clustered orders (support/resistance)
        """
        if not orders:
            return []
        
        # Group orders by price level (within threshold)
        clusters = {}
        for price, size in orders[:100]:
            # Round to cluster threshold
            price_key = round(price / cluster_threshold) * cluster_threshold
            if price_key not in clusters:
                clusters[price_key] = 0
            clusters[price_key] += size
        
        # Find significant clusters (top 5)
        sorted_clusters = sorted(
            clusters.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [price for price, size in sorted_clusters]
    
    def _calculate_depth(self, orders: List[Tuple], 
                        reference_price: float,
                        depth_pct: float = 0.01) -> float:
        """
        Calculate order book depth within % of reference price
        """
        depth = 0
        for price, size in orders:
            if abs(price - reference_price) / reference_price <= depth_pct:
                depth += size
            else:
                break
        return depth
    
    def _calculate_pressure(self, bids: List[Tuple], asks: List[Tuple],
                           best_bid: float, best_ask: float) -> Dict:
        """
        Calculate buy/sell pressure at multiple levels
        """
        # Pressure within 0.5%
        bid_pressure_05 = sum([s for p, s in bids if p >= best_bid * 0.995])
        ask_pressure_05 = sum([s for p, s in asks if p <= best_ask * 1.005])
        
        # Pressure within 1%
        bid_pressure_1 = sum([s for p, s in bids if p >= best_bid * 0.99])
        ask_pressure_1 = sum([s for p, s in asks if p <= best_ask * 1.01])
        
        return {
            'bid_pressure_05': bid_pressure_05,
            'ask_pressure_05': ask_pressure_05,
            'bid_pressure_1': bid_pressure_1,
            'ask_pressure_1': ask_pressure_1,
            'ratio_05': bid_pressure_05 / (ask_pressure_05 + 1e-10),
            'ratio_1': bid_pressure_1 / (ask_pressure_1 + 1e-10)
        }
    
    def _generate_orderbook_signal(self, imbalance: float, 
                                   bid_walls: List, ask_walls: List,
                                   pressure: Dict) -> Dict:
        """Generate trading signal from orderbook analysis"""
        score = 0
        reasons = []
        
        # Imbalance signal
        if imbalance > 0.3:
            score += 2
            reasons.append(f"Strong bid imbalance ({imbalance:.2f})")
        elif imbalance < -0.3:
            score -= 2
            reasons.append(f"Strong ask imbalance ({imbalance:.2f})")
        
        # Wall signals
        if bid_walls and not ask_walls:
            score += 1
            reasons.append(f"{len(bid_walls)} bid wall(s) detected")
        elif ask_walls and not bid_walls:
            score -= 1
            reasons.append(f"{len(ask_walls)} ask wall(s) detected")
        
        # Pressure signals
        if pressure['ratio_05'] > 1.5:
            score += 1
            reasons.append("Strong buy pressure")
        elif pressure['ratio_05'] < 0.67:
            score -= 1
            reasons.append("Strong sell pressure")
        
        # Determine signal
        if score >= 2:
            direction = 'BUY'
            confidence = min(0.8, 0.5 + (score / 10))
        elif score <= -2:
            direction = 'SELL'
            confidence = min(0.8, 0.5 + (abs(score) / 10))
        else:
            direction = 'NEUTRAL'
            confidence = 0.5
        
        return {
            'direction': direction,
            'confidence': confidence,
            'reasoning': '; '.join(reasons) if reasons else 'No clear signal'
        }
    
    def analyze_trade_flow(self, trades: List[Dict]) -> Dict:
        """
        Analyze recent trades to detect patterns
        
        Args:
            trades: List of trade dicts with 'price', 'quantity', 'side', 'timestamp'
            
        Returns:
            Trade flow analysis
        """
        if not trades:
            return {'error': 'No trades to analyze'}
        
        # Add to history
        for trade in trades:
            self.recent_trades.append(trade)
        
        # Analyze recent trades (last 100)
        recent = list(self.recent_trades)[-100:]
        
        # 1. Buy/Sell volume
        buy_volume = sum([t['quantity'] for t in recent if t['side'] == 'buy'])
        sell_volume = sum([t['quantity'] for t in recent if t['side'] == 'sell'])
        total_volume = buy_volume + sell_volume
        
        buy_ratio = buy_volume / total_volume if total_volume > 0 else 0.5
        
        # 2. Large trade detection (whales)
        whale_activity = self._detect_whale_activity(recent)
        
        # 3. Trade velocity (trades per minute)
        if len(recent) > 1:
            time_span = (recent[-1]['timestamp'] - recent[0]['timestamp']).total_seconds() / 60
            velocity = len(recent) / time_span if time_span > 0 else 0
        else:
            velocity = 0
        
        # 4. Price impact
        prices = [t['price'] for t in recent]
        price_change = (prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0
        
        # 5. Aggressive trading detection
        aggressive_buys = len([t for t in recent if t['side'] == 'buy' and t.get('taker', True)])
        aggressive_sells = len([t for t in recent if t['side'] == 'sell' and t.get('taker', True)])
        
        return {
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'buy_ratio': buy_ratio,
            'whale_activity': whale_activity,
            'velocity': velocity,
            'price_change': price_change,
            'aggressive_buys': aggressive_buys,
            'aggressive_sells': aggressive_sells,
            'signal': 'BUY' if buy_ratio > 0.6 else 'SELL' if buy_ratio < 0.4 else 'NEUTRAL',
            'confidence': abs(buy_ratio - 0.5) * 2
        }
    
    def _detect_whale_activity(self, trades: List[Dict]) -> Dict:
        """Detect large trader activity"""
        if not trades:
            return {'detected': False}
        
        # Calculate median trade size
        sizes = [t['quantity'] for t in trades]
        median_size = np.median(sizes)
        
        # Find whale trades
        whale_threshold = median_size * self.whale_threshold_multiplier
        whale_trades = [t for t in trades if t['quantity'] > whale_threshold]
        
        if not whale_trades:
            return {'detected': False}
        
        # Analyze whale direction
        whale_buys = sum([t['quantity'] for t in whale_trades if t['side'] == 'buy'])
        whale_sells = sum([t['quantity'] for t in whale_trades if t['side'] == 'sell'])
        whale_total = whale_buys + whale_sells
        
        return {
            'detected': True,
            'count': len(whale_trades),
            'direction': 'BUY' if whale_buys > whale_sells else 'SELL',
            'buy_volume': whale_buys,
            'sell_volume': whale_sells,
            'total_volume': whale_total,
            'confidence': abs(whale_buys - whale_sells) / whale_total if whale_total > 0 else 0,
            'largest_trade': max(whale_trades, key=lambda x: x['quantity'])
        }


# Global instance
order_flow_analyzer = OrderFlowAnalyzer()
