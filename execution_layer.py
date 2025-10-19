#!/usr/bin/env python3
"""
EXECUTION LAYER
All execution methods consolidated
"""

import time
from datetime import datetime
from typing import Dict
import ccxt

class ExecutionLayer:
    """Smart order execution with multiple algorithms"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.name = "Execution_Layer"
        self.version = "1.0.0"
        self.exchange = exchange
        
        self.metrics = {'orders': 0, 'fills': 0, 'slippage_total': 0}
        
    def execute_trade(self, symbol: str, signal: Dict, risk: Dict) -> Dict:
        """Execute trade with optimal method"""
        
        # Select execution method based on conditions
        method = self.select_execution_method(symbol, signal, risk)
        
        if method == 'MARKET':
            return self.execute_market_order(symbol, signal, risk)
        elif method == 'VWAP':
            return self.execute_vwap(symbol, signal, risk)
        elif method == 'TWAP':
            return self.execute_twap(symbol, signal, risk)
        elif method == 'ICEBERG':
            return self.execute_iceberg(symbol, signal, risk)
        else:
            return self.execute_market_order(symbol, signal, risk)
    
    def select_execution_method(self, symbol: str, signal: Dict, risk: Dict) -> str:
        """Select best execution method"""
        position_size = risk.get('position_size', 0)
        confidence = signal.get('confidence', 0)
        
        # Small positions: market order
        if position_size < 0.05:
            return 'MARKET'
        
        # High confidence + large size: VWAP
        elif confidence > 0.80 and position_size > 0.08:
            return 'VWAP'
        
        # Medium size: TWAP
        elif position_size > 0.05:
            return 'TWAP'
        
        # Default
        else:
            return 'MARKET'
    
    def execute_market_order(self, symbol: str, signal: Dict, risk: Dict) -> Dict:
        """Execute immediate market order"""
        try:
            side = 'buy' if signal.get('signal') == 'BUY' else 'sell'
            position_size_pct = risk.get('position_size', 0.10)
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            # Calculate amount (simplified - would use actual balance)
            capital = 10000  # Placeholder
            position_value = capital * position_size_pct
            amount = position_value / price
            
            # Round amount
            amount = round(amount, 8)
            
            # Check minimum
            markets = self.exchange.load_markets()
            min_amount = markets[symbol]['limits']['amount']['min'] or 0.00001
            
            if amount < min_amount:
                return {
                    'success': False,
                    'reason': f'Amount {amount} below minimum {min_amount}'
                }
            
            # Execute (commented out for safety)
            # order = self.exchange.create_market_order(symbol, side, amount)
            
            self.metrics['orders'] += 1
            
            return {
                'success': True,
                'method': 'MARKET',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'value': position_value,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_vwap(self, symbol: str, signal: Dict, risk: Dict) -> Dict:
        """Execute using VWAP algorithm"""
        # VWAP: Volume-Weighted Average Price
        # Splits order to match volume profile
        
        try:
            side = 'buy' if signal.get('signal') == 'BUY' else 'sell'
            total_amount = risk.get('position_size', 0.10) * 10000 / self.exchange.fetch_ticker(symbol)['last']
            
            # Typical VWAP: split into 5-10 orders over time
            n_orders = 5
            amount_per_order = total_amount / n_orders
            
            orders_executed = []
            
            for i in range(n_orders):
                # In production: would check volume profile and adjust timing
                time.sleep(30)  # 30 seconds between orders
                
                # Execute slice (commented out)
                # order = self.exchange.create_market_order(symbol, side, amount_per_order)
                # orders_executed.append(order)
                
                orders_executed.append({
                    'slice': i + 1,
                    'amount': amount_per_order,
                    'status': 'SIMULATED'
                })
            
            return {
                'success': True,
                'method': 'VWAP',
                'symbol': symbol,
                'side': side,
                'total_amount': total_amount,
                'slices': n_orders,
                'orders': orders_executed,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_twap(self, symbol: str, signal: Dict, risk: Dict) -> Dict:
        """Execute using TWAP algorithm"""
        # TWAP: Time-Weighted Average Price
        # Equal-sized orders at regular intervals
        
        try:
            side = 'buy' if signal.get('signal') == 'BUY' else 'sell'
            total_amount = risk.get('position_size', 0.10) * 10000 / self.exchange.fetch_ticker(symbol)['last']
            
            # Split into equal slices over time
            n_slices = 4
            amount_per_slice = total_amount / n_slices
            interval_seconds = 60  # 1 minute between slices
            
            return {
                'success': True,
                'method': 'TWAP',
                'symbol': symbol,
                'side': side,
                'total_amount': total_amount,
                'slices': n_slices,
                'interval_seconds': interval_seconds,
                'amount_per_slice': amount_per_slice,
                'status': 'PLANNED',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_iceberg(self, symbol: str, signal: Dict, risk: Dict) -> Dict:
        """Execute using iceberg orders"""
        # Iceberg: Show small portion, hide rest
        
        try:
            side = 'buy' if signal.get('signal') == 'BUY' else 'sell'
            total_amount = risk.get('position_size', 0.10) * 10000 / self.exchange.fetch_ticker(symbol)['last']
            
            # Show only 20% at a time
            visible_amount = total_amount * 0.20
            hidden_amount = total_amount * 0.80
            
            return {
                'success': True,
                'method': 'ICEBERG',
                'symbol': symbol,
                'side': side,
                'total_amount': total_amount,
                'visible_amount': visible_amount,
                'hidden_amount': hidden_amount,
                'status': 'PLANNED',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    print("✅ Execution Layer v1.0 initialized")
