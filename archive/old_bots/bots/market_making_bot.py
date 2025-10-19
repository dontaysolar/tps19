#!/usr/bin/env python3
"""
Market Making Strategy Bot
Provides liquidity by placing bid/ask orders
Profits from spread while managing inventory risk
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class MarketMakingBot:
    def __init__(self):
        self.name = "Market_Making"
        self.version = "1.0.0"
        self.enabled = True
        
        # Market making parameters
        self.min_spread_bps = 10  # 10 basis points minimum
        self.max_inventory = 10.0  # Max position size
        self.quote_size = 1.0  # Size per quote
        self.inventory_skew_factor = 0.5
        
        self.current_inventory = 0.0
        self.active_quotes = {'bids': [], 'asks': []}
        
        self.metrics = {
            'quotes_posted': 0,
            'trades_filled': 0,
            'spread_captured': 0.0,
            'inventory_turns': 0
        }
    
    def calculate_fair_value(self, ohlcv: List) -> float:
        """Calculate fair value using recent prices"""
        if len(ohlcv) < 10:
            return ohlcv[-1][4] if ohlcv else 0
        
        # Use VWAP of recent trades
        recent = ohlcv[-10:]
        total_volume = sum([c[5] for c in recent])
        vwap = sum([c[4] * c[5] for c in recent]) / total_volume if total_volume > 0 else recent[-1][4]
        
        return vwap
    
    def calculate_optimal_spread(self, volatility: float, volume: float) -> float:
        """Calculate optimal bid-ask spread"""
        # Base spread
        spread_bps = self.min_spread_bps
        
        # Widen spread in high volatility
        if volatility > 0.03:  # 3% volatility
            spread_bps *= 2
        elif volatility > 0.02:
            spread_bps *= 1.5
        
        # Tighten spread in high volume
        if volume > 1000000:
            spread_bps *= 0.8
        
        return spread_bps / 10000  # Convert bps to decimal
    
    def generate_quotes(self, fair_value: float, spread: float) -> Dict:
        """
        Generate bid/ask quotes around fair value
        Adjust for current inventory
        """
        # Inventory skew - adjust quotes based on position
        inventory_ratio = self.current_inventory / self.max_inventory if self.max_inventory > 0 else 0
        skew = inventory_ratio * self.inventory_skew_factor
        
        # Apply skew: if long, lower both bid/ask to encourage selling
        adjusted_mid = fair_value * (1 - skew)
        
        # Calculate bid/ask
        half_spread = spread / 2
        bid_price = adjusted_mid * (1 - half_spread)
        ask_price = adjusted_mid * (1 + half_spread)
        
        # Create quotes
        bid_quote = {
            'type': 'BID',
            'price': bid_price,
            'size': self.quote_size,
            'status': 'ACTIVE'
        }
        
        ask_quote = {
            'type': 'ASK',
            'price': ask_price,
            'size': self.quote_size,
            'status': 'ACTIVE'
        }
        
        self.active_quotes = {
            'bids': [bid_quote],
            'asks': [ask_quote]
        }
        
        self.metrics['quotes_posted'] += 2
        
        return {
            'bid_price': bid_price,
            'ask_price': ask_price,
            'mid_price': adjusted_mid,
            'spread': ask_price - bid_price,
            'spread_bps': ((ask_price - bid_price) / adjusted_mid) * 10000,
            'inventory_skew': skew,
            'quotes': self.active_quotes,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_fills(self, current_price: float, bid_ask: Dict) -> Dict:
        """
        Check if quotes were filled
        
        Args:
            current_price: Current market price
            bid_ask: {'bid': price, 'ask': price} - best market quotes
        """
        fills = []
        
        # Check if our bid was hit
        for bid_quote in self.active_quotes['bids']:
            if bid_quote['status'] == 'ACTIVE':
                if current_price <= bid_quote['price'] or bid_ask.get('ask', float('inf')) <= bid_quote['price']:
                    # Bid filled - we bought
                    self.current_inventory += bid_quote['size']
                    bid_quote['status'] = 'FILLED'
                    fills.append({
                        'side': 'BUY',
                        'price': bid_quote['price'],
                        'size': bid_quote['size']
                    })
                    self.metrics['trades_filled'] += 1
        
        # Check if our ask was lifted
        for ask_quote in self.active_quotes['asks']:
            if ask_quote['status'] == 'ACTIVE':
                if current_price >= ask_quote['price'] or bid_ask.get('bid', 0) >= ask_quote['price']:
                    # Ask filled - we sold
                    self.current_inventory -= ask_quote['size']
                    ask_quote['status'] = 'FILLED'
                    fills.append({
                        'side': 'SELL',
                        'price': ask_quote['price'],
                        'size': ask_quote['size']
                    })
                    self.metrics['trades_filled'] += 1
        
        # Calculate spread captured
        if len(fills) >= 2:
            buy_fills = [f for f in fills if f['side'] == 'BUY']
            sell_fills = [f for f in fills if f['side'] == 'SELL']
            
            if buy_fills and sell_fills:
                avg_buy = np.mean([f['price'] for f in buy_fills])
                avg_sell = np.mean([f['price'] for f in sell_fills])
                spread_captured = (avg_sell - avg_buy) * self.quote_size
                self.metrics['spread_captured'] += spread_captured
        
        return {
            'fills': fills,
            'fills_count': len(fills),
            'current_inventory': self.current_inventory,
            'inventory_pct': (self.current_inventory / self.max_inventory) * 100 if self.max_inventory > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def manage_inventory_risk(self) -> Dict:
        """Assess and manage inventory risk"""
        inventory_ratio = abs(self.current_inventory) / self.max_inventory if self.max_inventory > 0 else 0
        
        if inventory_ratio > 0.8:
            risk_level = 'HIGH'
            action = 'REDUCE' if self.current_inventory > 0 else 'COVER'
        elif inventory_ratio > 0.5:
            risk_level = 'MEDIUM'
            action = 'MONITOR'
        else:
            risk_level = 'LOW'
            action = 'CONTINUE'
        
        return {
            'inventory': self.current_inventory,
            'max_inventory': self.max_inventory,
            'utilization_pct': inventory_ratio * 100,
            'risk_level': risk_level,
            'recommended_action': action,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'current_inventory': self.current_inventory,
            'inventory_risk': self.manage_inventory_risk()['risk_level'],
            'active_bids': len([q for q in self.active_quotes['bids'] if q['status'] == 'ACTIVE']),
            'active_asks': len([q for q in self.active_quotes['asks'] if q['status'] == 'ACTIVE']),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = MarketMakingBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
