#!/usr/bin/env python3
"""
Liquidity Wave Bot
Minimizes price impact on large trades via order slicing
Part of APEX AI Trading System
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class LiquidityWaveBot:
    """Executes large orders with minimal price impact"""
    
    def __init__(self, exchange_config=None):
        self.name = "LiquidityWaveBot"
        self.version = "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        self.config = {
            'slice_threshold_usd': 100.0,  # Slice orders > $100
            'max_slice_pct': 10.0,          # Max 10% of order book depth
            'slice_interval_sec': 30,       # 30s between slices
            'max_slices': 10                # Max 10 slices per order
        }
        
        self.metrics = {
            'orders_sliced': 0,
            'total_slices': 0,
            'impact_reduced': 0.0
        }
    
    def analyze_order_book_depth(self, symbol: str, side: str) -> Dict:
        """Analyze order book depth for execution planning"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=50)
            
            # Get relevant side
            orders = orderbook['asks'] if side == 'buy' else orderbook['bids']
            
            # Calculate cumulative depth
            cumulative_depth = 0
            depth_levels = []
            
            for order in orders[:20]:
                price = order[0] if isinstance(order, (list, tuple)) else order
                volume = order[1] if isinstance(order, (list, tuple)) and len(order) > 1 else 0
                
                cumulative_depth += volume
                depth_levels.append({
                    'price': price,
                    'volume': volume,
                    'cumulative': cumulative_depth
                })
            
            # Calculate average depth at different percentiles
            total_depth = cumulative_depth
            
            # Calculate weighted average price safely
            total_volume = sum(d['volume'] for d in depth_levels)
            avg_price = sum(d['price'] * d['volume'] for d in depth_levels) / total_volume if total_volume > 0 else 0
            
            return {
                'symbol': symbol,
                'side': side,
                'total_depth': total_depth,
                'depth_levels': depth_levels,
                'avg_price': avg_price,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Order book analysis error: {e}")
            return {}
    
    def calculate_order_slices(self, symbol: str, amount: float, side: str) -> List[Dict]:
        """Calculate optimal order slicing strategy"""
        try:
            # Get order book depth
            depth = self.analyze_order_book_depth(symbol, side)
            
            if not depth:
                return []
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['ask'] if side == 'buy' else ticker['bid']
            
            order_value = amount * price
            
            # Check if slicing needed
            if order_value < self.config['slice_threshold_usd']:
                return [{
                    'slice': 1,
                    'amount': amount,
                    'delay': 0
                }]
            
            # Calculate max slice size based on order book depth
            total_depth = depth['total_depth']
            max_slice_amount = (total_depth * self.config['max_slice_pct'] / 100)
            
            # Determine number of slices
            num_slices = min(
                int(amount / max_slice_amount) + 1,
                self.config['max_slices']
            )
            
            # Calculate slice sizes
            base_slice = amount / num_slices
            slices = []
            
            for i in range(num_slices):
                slices.append({
                    'slice': i + 1,
                    'amount': base_slice,
                    'delay': i * self.config['slice_interval_sec']
                })
            
            self.metrics['orders_sliced'] += 1
            self.metrics['total_slices'] += num_slices
            
            return slices
            
        except Exception as e:
            print(f"❌ Order slicing error: {e}")
            return []
    
    def execute_sliced_order(self, symbol: str, amount: float, side: str) -> Dict:
        """Execute order with optimal slicing"""
        slices = self.calculate_order_slices(symbol, amount, side)
        
        if not slices:
            return {'success': False, 'error': 'Failed to calculate slices'}
        
        executed_slices = []
        total_filled = 0
        
        for slice_info in slices:
            # In production, would execute actual order here
            # For now, simulate
            executed_slices.append({
                'slice': slice_info['slice'],
                'amount': slice_info['amount'],
                'status': 'SIMULATED',
                'timestamp': datetime.now().isoformat()
            })
            
            total_filled += slice_info['amount']
            
            # Wait between slices (except last)
            if slice_info != slices[-1]:
                time.sleep(slice_info['delay'] / 1000)  # Convert to seconds
        
        return {
            'success': True,
            'symbol': symbol,
            'side': side,
            'total_amount': amount,
            'slices_executed': len(executed_slices),
            'total_filled': total_filled,
            'execution_details': executed_slices,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = LiquidityWaveBot()
    print("🌊 Liquidity Wave Bot - Test Mode\n")
    
    slices = bot.calculate_order_slices('BTC/USDT', 0.01, 'buy')
    print(f"Order slicing for 0.01 BTC:")
    print(f"  Total slices: {len(slices)}")
    for s in slices:
        print(f"  Slice {s['slice']}: {s['amount']:.6f} BTC (delay: {s['delay']}s)")
