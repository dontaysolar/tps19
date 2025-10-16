#!/usr/bin/env python3
"""
Market Making Bot - Provide liquidity and earn spreads
New implementation from enhancement roadmap
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MarketMakingBot:
    """
    Automated market making bot
    
    Features:
    - Dual-sided order placement (bid and ask)
    - Dynamic spread adjustment
    - Inventory management
    - Risk-neutral positioning
    - Spread capture strategy
    """
    
    def __init__(self, initial_capital: float = 5000):
        self.name = "Market Making Bot"
        self.initial_capital = initial_capital
        
        # Market making parameters
        self.target_spread = 0.002  # 0.2% spread
        self.min_spread = 0.001  # 0.1% minimum
        self.max_spread = 0.005  # 0.5% maximum
        self.order_size_pct = 0.02  # 2% of capital per order
        
        # Inventory management
        self.max_inventory_deviation = 0.20  # 20% max skew
        self.target_inventory = 0.50  # 50% in base, 50% in quote
        
        # Active orders
        self.bid_orders = []
        self.ask_orders = []
        
        # Performance
        self.total_fills = 0
        self.spread_captured = 0
        self.inventory_pnl = 0
        
        logger.info("🏪 Market Making Bot initialized")
    
    def calculate_quotes(self, market_data: Dict, 
                        current_inventory: Dict) -> Dict:
        """
        Calculate bid and ask quotes
        
        Args:
            market_data: Current market state
            current_inventory: Current inventory position
            
        Returns:
            Bid and ask quote levels
        """
        try:
            mid_price = market_data.get('mid_price', market_data.get('price', 0))
            volatility = market_data.get('volatility', 0.02)
            volume = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume)
            
            # Adjust spread based on volatility
            spread = self._calculate_dynamic_spread(volatility, volume / avg_volume if avg_volume > 0 else 1)
            
            # Adjust for inventory skew
            inventory_skew = self._calculate_inventory_skew(current_inventory)
            bid_adjustment, ask_adjustment = self._get_inventory_adjustments(inventory_skew)
            
            # Calculate quotes
            bid_price = mid_price * (1 - spread/2 + bid_adjustment)
            ask_price = mid_price * (1 + spread/2 + ask_adjustment)
            
            # Calculate sizes
            bid_size = self._calculate_order_size(current_inventory, 'BID')
            ask_size = self._calculate_order_size(current_inventory, 'ASK')
            
            quotes = {
                'mid_price': mid_price,
                'spread': spread,
                'bid': {
                    'price': bid_price,
                    'size': bid_size,
                    'adjustment': bid_adjustment
                },
                'ask': {
                    'price': ask_price,
                    'size': ask_size,
                    'adjustment': ask_adjustment
                },
                'inventory_skew': inventory_skew,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.debug(f"🏪 Quotes: Bid {bid_price:.2f} | Ask {ask_price:.2f} "
                        f"(Spread: {spread:.3%})")
            
            return quotes
            
        except Exception as e:
            logger.error(f"Quote calculation error: {e}")
            return {}
    
    def _calculate_dynamic_spread(self, volatility: float, 
                                  volume_ratio: float) -> float:
        """Calculate spread based on market conditions"""
        # Base spread from volatility
        base_spread = self.target_spread
        
        # Widen spread in high volatility
        if volatility > 0.03:
            vol_multiplier = 1 + (volatility - 0.03) / 0.03
            base_spread *= vol_multiplier
        
        # Tighten spread in high volume
        if volume_ratio > 1.5:
            volume_multiplier = 0.9
            base_spread *= volume_multiplier
        
        # Ensure within bounds
        spread = max(self.min_spread, min(self.max_spread, base_spread))
        
        return spread
    
    def _calculate_inventory_skew(self, inventory: Dict) -> float:
        """
        Calculate inventory skew
        
        Returns:
            Skew from -1 (all quote) to +1 (all base)
        """
        base_value = inventory.get('base_value', 0)
        quote_value = inventory.get('quote_value', 0)
        total_value = base_value + quote_value
        
        if total_value == 0:
            return 0
        
        # Calculate current allocation
        base_pct = base_value / total_value
        
        # Calculate skew relative to target
        skew = (base_pct - self.target_inventory) / 0.5
        
        return max(-1, min(1, skew))
    
    def _get_inventory_adjustments(self, skew: float) -> Tuple[float, float]:
        """
        Get price adjustments to manage inventory
        
        Args:
            skew: Inventory skew (-1 to +1)
            
        Returns:
            (bid_adjustment, ask_adjustment)
        """
        # If too much base (skew > 0), encourage selling
        if skew > 0:
            bid_adjustment = -skew * 0.001  # Lower bid (discourage buying more)
            ask_adjustment = -skew * 0.001  # Lower ask (encourage selling)
        # If too much quote (skew < 0), encourage buying
        else:
            bid_adjustment = abs(skew) * 0.001  # Raise bid (encourage buying)
            ask_adjustment = abs(skew) * 0.001  # Raise ask (discourage selling)
        
        return bid_adjustment, ask_adjustment
    
    def _calculate_order_size(self, inventory: Dict, side: str) -> float:
        """Calculate order size based on inventory"""
        base_size = self.initial_capital * self.order_size_pct
        
        skew = self._calculate_inventory_skew(inventory)
        
        # Adjust size based on inventory
        if side == 'BID' and skew > self.max_inventory_deviation:
            # Already have too much base, reduce buy size
            base_size *= (1 - skew)
        elif side == 'ASK' and skew < -self.max_inventory_deviation:
            # Don't have enough base, reduce sell size
            base_size *= (1 + skew)
        
        return max(0, base_size)
    
    def place_market_making_orders(self, quotes: Dict) -> Dict:
        """
        Place bid and ask orders
        
        Args:
            quotes: Quote prices and sizes
            
        Returns:
            Order placement result
        """
        try:
            bid_order = {
                'id': f"mm_bid_{int(datetime.now().timestamp())}",
                'side': 'BID',
                'price': quotes['bid']['price'],
                'size': quotes['bid']['size'],
                'placed_at': datetime.now(),
                'filled': False
            }
            
            ask_order = {
                'id': f"mm_ask_{int(datetime.now().timestamp())}",
                'side': 'ASK',
                'price': quotes['ask']['price'],
                'size': quotes['ask']['size'],
                'placed_at': datetime.now(),
                'filled': False
            }
            
            self.bid_orders.append(bid_order)
            self.ask_orders.append(ask_order)
            
            logger.info(f"🏪 MM orders placed: "
                       f"Bid ${quotes['bid']['price']:.2f} | "
                       f"Ask ${quotes['ask']['price']:.2f}")
            
            return {
                'bid_order': bid_order,
                'ask_order': ask_order,
                'spread': quotes['spread'],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_order_fill(self, order_id: str, fill_price: float):
        """
        Handle order fill
        
        Args:
            order_id: Order identifier
            fill_price: Fill price
        """
        # Find order
        order = None
        for order_list in [self.bid_orders, self.ask_orders]:
            for o in order_list:
                if o['id'] == order_id:
                    order = o
                    break
        
        if not order:
            logger.warning(f"Order not found: {order_id}")
            return
        
        # Mark as filled
        order['filled'] = True
        order['fill_price'] = fill_price
        order['filled_at'] = datetime.now()
        
        self.total_fills += 1
        
        # Calculate spread captured (if both sides filled)
        self._calculate_spread_capture()
        
        logger.info(f"🏪 Order filled: {order['side']} @ ${fill_price:.2f}")
    
    def _calculate_spread_capture(self):
        """Calculate spread captured from matched orders"""
        filled_bids = [o for o in self.bid_orders if o.get('filled')]
        filled_asks = [o for o in self.ask_orders if o.get('filled')]
        
        # Match filled orders (simplified)
        for bid in filled_bids[-5:]:  # Last 5
            for ask in filled_asks[-5:]:
                if not bid.get('matched') and not ask.get('matched'):
                    # Calculate spread capture
                    spread = ask.get('fill_price', 0) - bid.get('fill_price', 0)
                    spread_pct = spread / bid.get('fill_price', 1)
                    
                    self.spread_captured += spread_pct
                    
                    bid['matched'] = True
                    ask['matched'] = True
                    
                    logger.info(f"💰 Spread captured: {spread_pct:.3%}")
                    break
    
    def get_stats(self) -> Dict:
        """Get market making bot statistics"""
        active_bids = sum(1 for o in self.bid_orders if not o.get('filled'))
        active_asks = sum(1 for o in self.ask_orders if not o.get('filled'))
        
        return {
            'active_bid_orders': active_bids,
            'active_ask_orders': active_asks,
            'total_fills': self.total_fills,
            'spread_captured': self.spread_captured,
            'inventory_pnl': self.inventory_pnl,
            'target_spread': self.target_spread,
            'avg_spread_per_fill': self.spread_captured / max(1, self.total_fills / 2)
        }


# Global instance
market_making_bot = MarketMakingBot()
