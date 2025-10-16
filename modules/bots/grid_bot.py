#!/usr/bin/env python3
"""
Grid Trading Bot - Automated grid trading
Based on 3Commas features and enhancement roadmap
"""

from typing import Dict, List, Optional
from datetime import datetime

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class GridTradingBot:
    """
    Automated grid trading bot
    
    Features:
    - Dynamic grid creation
    - Neutral grid (range-bound markets)
    - Long grid (uptrending markets)
    - Short grid (downtrending markets)
    - Automatic grid adjustment
    """
    
    def __init__(self, initial_capital: float = 1000):
        self.name = "Grid Trading Bot"
        self.initial_capital = initial_capital
        
        # Grid parameters
        self.grid_levels = 10
        self.grid_type = "neutral"  # neutral, long, short
        self.price_range_pct = 0.10  # 10% default range
        
        # Grid state
        self.grids = {}
        self.active_grids = []
        self.filled_orders = []
        
        # Performance
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0
        
        logger.info("📊 Grid Trading Bot initialized")
    
    def create_grid(self, symbol: str, current_price: float,
                   grid_type: str = "neutral") -> Dict:
        """
        Create grid trading setup
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            grid_type: neutral/long/short
            
        Returns:
            Grid configuration
        """
        self.grid_type = grid_type
        
        # Calculate grid range
        if grid_type == "neutral":
            upper_price = current_price * (1 + self.price_range_pct)
            lower_price = current_price * (1 - self.price_range_pct)
        elif grid_type == "long":
            # Bias towards upside
            upper_price = current_price * (1 + self.price_range_pct * 1.5)
            lower_price = current_price * (1 - self.price_range_pct * 0.5)
        elif grid_type == "short":
            # Bias towards downside
            upper_price = current_price * (1 + self.price_range_pct * 0.5)
            lower_price = current_price * (1 - self.price_range_pct * 1.5)
        else:
            raise ValueError(f"Invalid grid type: {grid_type}")
        
        # Calculate grid levels
        step = (upper_price - lower_price) / self.grid_levels
        grid_levels = []
        
        for i in range(self.grid_levels + 1):
            price = lower_price + (step * i)
            
            # Determine order type
            if price < current_price:
                order_type = "BUY"
            elif price > current_price:
                order_type = "SELL"
            else:
                order_type = "NEUTRAL"
            
            grid_levels.append({
                'level': i,
                'price': price,
                'order_type': order_type,
                'filled': False,
                'size': self._calculate_grid_size(i)
            })
        
        grid = {
            'symbol': symbol,
            'type': grid_type,
            'current_price': current_price,
            'upper_price': upper_price,
            'lower_price': lower_price,
            'levels': grid_levels,
            'created_at': datetime.now().isoformat(),
            'active': True
        }
        
        # Store grid
        grid_id = f"{symbol}_{grid_type}_{int(datetime.now().timestamp())}"
        self.grids[grid_id] = grid
        self.active_grids.append(grid_id)
        
        logger.info(f"📊 Grid created: {symbol} {grid_type} "
                   f"({len(grid_levels)} levels, {lower_price:.2f} - {upper_price:.2f})")
        
        return grid
    
    def _calculate_grid_size(self, level: int) -> float:
        """Calculate order size for grid level"""
        # Equal size per level
        return self.initial_capital / (self.grid_levels + 1)
    
    def process_price_update(self, symbol: str, current_price: float):
        """
        Process price update and execute grid orders
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
        """
        for grid_id in self.active_grids:
            grid = self.grids.get(grid_id)
            if not grid or grid['symbol'] != symbol:
                continue
            
            # Check each grid level
            for level in grid['levels']:
                if level['filled']:
                    continue
                
                # Check if price hit this level
                if self._price_hit_level(current_price, level['price']):
                    self._execute_grid_order(grid, level, current_price)
    
    def _price_hit_level(self, current_price: float, level_price: float) -> bool:
        """Check if price hit grid level"""
        tolerance = level_price * 0.002  # 0.2% tolerance
        return abs(current_price - level_price) < tolerance
    
    def _execute_grid_order(self, grid: Dict, level: Dict, 
                           execution_price: float):
        """Execute grid order"""
        try:
            order_type = level['order_type']
            size = level['size']
            
            logger.info(f"⚡ Grid order: {order_type} @ {execution_price:.2f}")
            
            # Mark level as filled
            level['filled'] = True
            level['executed_at'] = datetime.now().isoformat()
            level['execution_price'] = execution_price
            
            # Record trade
            self.filled_orders.append({
                'grid_id': grid.get('symbol'),
                'level': level['level'],
                'order_type': order_type,
                'price': execution_price,
                'size': size,
                'timestamp': datetime.now().isoformat()
            })
            
            self.total_trades += 1
            
            # Calculate profit if closing a position
            if order_type == "SELL":
                profit = self._calculate_profit(grid, level)
                if profit > 0:
                    self.winning_trades += 1
                    self.total_profit += profit
                    logger.info(f"💰 Grid profit: ${profit:.2f}")
            
        except Exception as e:
            logger.error(f"Grid order execution error: {e}")
    
    def _calculate_profit(self, grid: Dict, sell_level: Dict) -> float:
        """Calculate profit from grid trade"""
        # Find corresponding buy order
        buy_levels = [l for l in grid['levels'] 
                     if l['order_type'] == "BUY" and l['filled']]
        
        if not buy_levels:
            return 0
        
        # Use nearest buy level
        buy_level = min(buy_levels, 
                       key=lambda l: abs(l['price'] - sell_level['price']))
        
        buy_price = buy_level.get('execution_price', buy_level['price'])
        sell_price = sell_level.get('execution_price', sell_level['price'])
        size = sell_level['size']
        
        profit = (sell_price - buy_price) * size
        return profit
    
    def adjust_grid(self, grid_id: str, new_price_range: float):
        """
        Adjust grid range dynamically
        
        Args:
            grid_id: Grid identifier
            new_price_range: New price range percentage
        """
        if grid_id not in self.grids:
            logger.warning(f"Grid not found: {grid_id}")
            return
        
        grid = self.grids[grid_id]
        
        logger.info(f"📊 Adjusting grid range: {grid['price_range_pct']:.1%} → "
                   f"{new_price_range:.1%}")
        
        # Cancel unfilled orders
        for level in grid['levels']:
            if not level['filled']:
                level['cancelled'] = True
        
        # Recreate grid with new range
        symbol = grid['symbol']
        current_price = grid['current_price']
        grid_type = grid['type']
        
        self.price_range_pct = new_price_range
        new_grid = self.create_grid(symbol, current_price, grid_type)
        
        # Deactivate old grid
        grid['active'] = False
        if grid_id in self.active_grids:
            self.active_grids.remove(grid_id)
    
    def stop_grid(self, grid_id: str):
        """Stop grid trading for a symbol"""
        if grid_id in self.grids:
            self.grids[grid_id]['active'] = False
            if grid_id in self.active_grids:
                self.active_grids.remove(grid_id)
            
            logger.info(f"🛑 Grid stopped: {grid_id}")
    
    def get_grid_status(self, grid_id: str) -> Dict:
        """Get status of specific grid"""
        if grid_id not in self.grids:
            return {'error': 'Grid not found'}
        
        grid = self.grids[grid_id]
        
        filled_buy_orders = sum(1 for l in grid['levels'] 
                               if l['filled'] and l['order_type'] == "BUY")
        filled_sell_orders = sum(1 for l in grid['levels'] 
                                if l['filled'] and l['order_type'] == "SELL")
        
        return {
            'grid_id': grid_id,
            'symbol': grid['symbol'],
            'type': grid['type'],
            'active': grid['active'],
            'total_levels': len(grid['levels']),
            'filled_buy_orders': filled_buy_orders,
            'filled_sell_orders': filled_sell_orders,
            'price_range': [grid['lower_price'], grid['upper_price']],
            'created_at': grid['created_at']
        }
    
    def get_stats(self) -> Dict:
        """Get grid bot statistics"""
        win_rate = self.winning_trades / max(1, self.total_trades)
        
        return {
            'active_grids': len(self.active_grids),
            'total_grids_created': len(self.grids),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'total_profit': self.total_profit,
            'avg_profit_per_trade': self.total_profit / max(1, self.total_trades)
        }


# Global instance
grid_trading_bot = GridTradingBot()
