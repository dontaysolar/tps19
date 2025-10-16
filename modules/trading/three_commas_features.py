#!/usr/bin/env python3
"""
3Commas-Style Smart Trading Features
DCA, Grid Bots, Smart Trading, Trailing
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from modules.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DCAOrder:
    """DCA (Dollar Cost Averaging) order"""
    level: int
    price: float
    size: float
    deviation_pct: float
    filled: bool = False


@dataclass
class GridLevel:
    """Grid trading level"""
    price: float
    buy_size: float
    sell_size: float
    filled: bool = False


class SmartTrading:
    """
    3Commas-style smart trading features
    """
    
    def __init__(self):
        # DCA configuration
        self.dca_enabled = True
        self.max_dca_orders = 5
        self.dca_deviation = 0.02  # 2% between orders
        self.dca_volume_scale = 1.5  # Increase size each level
        
        # Grid configuration  
        self.grid_enabled = False
        self.grid_levels = 10
        self.grid_range_pct = 0.10  # 10% range
        
        # Smart trailing
        self.trailing_enabled = True
        self.trailing_deviation = 0.01  # 1% trailing
        
        # Safety orders
        self.max_safety_orders = 3
        
    def create_dca_strategy(self, entry_price: float, 
                           base_size: float) -> List[DCAOrder]:
        """
        Create DCA (Dollar Cost Averaging) orders
        
        Smart entry strategy - buy more as price drops
        """
        dca_orders = []
        
        for level in range(1, self.max_dca_orders + 1):
            deviation = self.dca_deviation * level
            order_price = entry_price * (1 - deviation)
            
            # Increase size at each level (martingale-style but controlled)
            order_size = base_size * (self.dca_volume_scale ** (level - 1))
            
            dca_orders.append(DCAOrder(
                level=level,
                price=order_price,
                size=order_size,
                deviation_pct=deviation
            ))
        
        logger.info(f"Created {len(dca_orders)} DCA orders")
        return dca_orders
    
    def create_grid_levels(self, current_price: float,
                          total_capital: float) -> List[GridLevel]:
        """
        Create grid trading levels
        
        Places buy and sell orders at regular intervals
        """
        grid_levels = []
        
        # Calculate price range
        upper_price = current_price * (1 + self.grid_range_pct)
        lower_price = current_price * (1 - self.grid_range_pct)
        
        # Calculate step size
        step = (upper_price - lower_price) / self.grid_levels
        
        # Size per level
        size_per_level = total_capital / (self.grid_levels * current_price)
        
        for i in range(self.grid_levels):
            level_price = lower_price + (step * i)
            
            grid_levels.append(GridLevel(
                price=level_price,
                buy_size=size_per_level,
                sell_size=size_per_level
            ))
        
        logger.info(f"Created {len(grid_levels)} grid levels")
        return grid_levels
    
    def calculate_smart_trailing(self, position: Dict, 
                                 current_price: float) -> Dict:
        """
        Smart trailing take profit
        
        Trails price up but locks in profit
        """
        entry_price = position['entry_price']
        max_price = position.get('max_price', entry_price)
        
        # Update max price if current is higher
        if current_price > max_price:
            max_price = current_price
        
        # Calculate trailing stop
        trailing_stop = max_price * (1 - self.trailing_deviation)
        
        # Ensure always in profit
        min_profit_price = entry_price * 1.01  # At least 1% profit
        trailing_stop = max(trailing_stop, min_profit_price)
        
        should_exit = current_price <= trailing_stop
        
        return {
            'trailing_stop': trailing_stop,
            'max_price': max_price,
            'should_exit': should_exit,
            'current_profit_pct': (current_price - entry_price) / entry_price,
            'locked_profit_pct': (trailing_stop - entry_price) / entry_price
        }
    
    def manage_safety_orders(self, position: Dict, 
                            current_price: float) -> Optional[Dict]:
        """
        Safety orders - add to position at better prices
        
        Similar to DCA but for existing positions
        """
        entry_price = position['entry_price']
        safety_orders_used = position.get('safety_orders_used', 0)
        
        if safety_orders_used >= self.max_safety_orders:
            return None
        
        # Calculate next safety order price
        deviation = 0.03 * (safety_orders_used + 1)  # 3%, 6%, 9%
        safety_price = entry_price * (1 - deviation)
        
        if current_price <= safety_price:
            # Trigger safety order
            base_size = position['size']
            safety_size = base_size * (1.5 ** safety_orders_used)  # Increasing size
            
            return {
                'action': 'ADD_TO_POSITION',
                'price': current_price,
                'size': safety_size,
                'level': safety_orders_used + 1,
                'average_entry': self._calculate_new_average(
                    entry_price, position['size'],
                    current_price, safety_size
                )
            }
        
        return None
    
    def _calculate_new_average(self, price1: float, size1: float,
                               price2: float, size2: float) -> float:
        """Calculate new average entry price after adding to position"""
        total_value = (price1 * size1) + (price2 * size2)
        total_size = size1 + size2
        return total_value / total_size if total_size > 0 else price1


# Global instance
smart_trading = SmartTrading()
