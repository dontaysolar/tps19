#!/usr/bin/env python3
"""
Grid Trading Strategy Bot
Places buy/sell orders at regular price intervals
Profits from market volatility and range-bound conditions
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class GridTradingBot:
    def __init__(self):
        self.name = "Grid_Trading"
        self.version = "1.0.0"
        self.enabled = True
        
        # Grid parameters
        self.grid_levels = 10
        self.grid_spacing_pct = 1.0  # 1% between levels
        self.grid_range = {'upper': None, 'lower': None}
        self.active_orders = []
        
        self.metrics = {
            'grids_created': 0,
            'trades_executed': 0,
            'profit_from_swings': 0.0
        }
    
    def create_grid(self, current_price: float, range_pct: float = 10) -> Dict:
        """
        Create price grid around current price
        
        Args:
            current_price: Current asset price
            range_pct: Total range as % of price (default 10%)
        """
        # Calculate grid boundaries
        half_range = range_pct / 2
        upper_bound = current_price * (1 + half_range / 100)
        lower_bound = current_price * (1 - half_range / 100)
        
        # Calculate grid levels
        price_range = upper_bound - lower_bound
        level_spacing = price_range / self.grid_levels
        
        grid_prices = []
        for i in range(self.grid_levels + 1):
            price = lower_bound + (i * level_spacing)
            grid_prices.append(price)
        
        # Create buy/sell orders at each level
        orders = []
        for i, price in enumerate(grid_prices):
            if price < current_price:
                # Place buy orders below current price
                orders.append({
                    'type': 'BUY',
                    'price': price,
                    'level': i,
                    'status': 'PENDING'
                })
            elif price > current_price:
                # Place sell orders above current price
                orders.append({
                    'type': 'SELL',
                    'price': price,
                    'level': i,
                    'status': 'PENDING'
                })
        
        self.active_orders = orders
        self.grid_range = {'upper': upper_bound, 'lower': lower_bound}
        self.metrics['grids_created'] += 1
        
        return {
            'grid_created': True,
            'levels': len(grid_prices),
            'upper_bound': upper_bound,
            'lower_bound': lower_bound,
            'spacing': level_spacing,
            'spacing_pct': (level_spacing / current_price) * 100,
            'buy_orders': len([o for o in orders if o['type'] == 'BUY']),
            'sell_orders': len([o for o in orders if o['type'] == 'SELL']),
            'orders': orders,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_grid_triggers(self, current_price: float) -> Dict:
        """
        Check if any grid orders should be triggered
        """
        triggered_orders = []
        
        for order in self.active_orders:
            if order['status'] != 'PENDING':
                continue
            
            if order['type'] == 'BUY' and current_price <= order['price']:
                order['status'] = 'TRIGGERED'
                order['executed_price'] = current_price
                triggered_orders.append(order)
                self.metrics['trades_executed'] += 1
                
            elif order['type'] == 'SELL' and current_price >= order['price']:
                order['status'] = 'TRIGGERED'
                order['executed_price'] = current_price
                triggered_orders.append(order)
                self.metrics['trades_executed'] += 1
        
        return {
            'triggered_count': len(triggered_orders),
            'triggered_orders': triggered_orders,
            'pending_orders': len([o for o in self.active_orders if o['status'] == 'PENDING']),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_grid_performance(self, initial_capital: float = 1000) -> Dict:
        """Calculate performance of grid strategy"""
        executed_orders = [o for o in self.active_orders if o['status'] == 'TRIGGERED']
        
        if not executed_orders:
            return {'no_trades': True}
        
        # Calculate profit from completed buy-sell cycles
        buy_orders = [o for o in executed_orders if o['type'] == 'BUY']
        sell_orders = [o for o in executed_orders if o['type'] == 'SELL']
        
        total_profit = 0
        completed_cycles = min(len(buy_orders), len(sell_orders))
        
        for i in range(completed_cycles):
            buy_price = buy_orders[i]['executed_price']
            sell_price = sell_orders[i]['executed_price']
            profit = sell_price - buy_price
            total_profit += profit
        
        profit_pct = (total_profit / initial_capital) * 100 if initial_capital > 0 else 0
        
        self.metrics['profit_from_swings'] = total_profit
        
        return {
            'total_profit': total_profit,
            'profit_pct': profit_pct,
            'completed_cycles': completed_cycles,
            'avg_profit_per_cycle': total_profit / completed_cycles if completed_cycles > 0 else 0,
            'total_trades': len(executed_orders),
            'timestamp': datetime.now().isoformat()
        }
    
    def adjust_grid(self, new_center_price: float) -> Dict:
        """Adjust grid center if price moves significantly"""
        if not self.grid_range['upper'] or not self.grid_range['lower']:
            return {'error': 'No active grid'}
        
        # Check if price is outside grid range
        if new_center_price > self.grid_range['upper'] or new_center_price < self.grid_range['lower']:
            # Recreate grid
            range_pct = ((self.grid_range['upper'] - self.grid_range['lower']) / new_center_price) * 100
            return self.create_grid(new_center_price, range_pct)
        
        return {'adjustment_needed': False}
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'grid_active': len(self.active_orders) > 0,
            'grid_levels': self.grid_levels,
            'grid_range': self.grid_range,
            'active_orders': len([o for o in self.active_orders if o['status'] == 'PENDING']),
            'executed_orders': len([o for o in self.active_orders if o['status'] == 'TRIGGERED']),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = GridTradingBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
    
    # Example
    grid = bot.create_grid(100, range_pct=10)
    print(f"📊 Grid created: {grid['levels']} levels, {grid['buy_orders']} buys, {grid['sell_orders']} sells")
