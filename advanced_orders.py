#!/usr/bin/env python3
"""
ADVANCED ORDER TYPES
Limit, stop-loss, take-profit, trailing stops, OCO orders
"""

import ccxt
from datetime import datetime
from typing import Dict, Optional
import time

class AdvancedOrderManager:
    """Manage advanced order types"""
    
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        self.name = "Advanced_Orders"
        self.version = "1.0.0"
        
        # Track active orders
        self.active_orders = {}
        self.trailing_stops = {}
        
    def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Place limit order"""
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            
            self.active_orders[order['id']] = {
                'type': 'limit',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'status': 'open',
                'created': datetime.now().isoformat()
            }
            
            print(f"✅ Limit order placed: {side} {amount} {symbol} @ ${price}")
            return {
                'success': True,
                'order_id': order['id'],
                'order': order
            }
        
        except Exception as e:
            print(f"❌ Limit order failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def place_stop_loss(self, symbol: str, side: str, amount: float, stop_price: float, 
                        limit_price: Optional[float] = None) -> Dict:
        """Place stop-loss order"""
        try:
            # Stop-limit if limit price provided, else stop-market
            if limit_price:
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='stop_limit',
                    side=side,
                    amount=amount,
                    price=limit_price,
                    params={'stopPrice': stop_price}
                )
            else:
                order = self.exchange.create_order(
                    symbol=symbol,
                    type='stop_market',
                    side=side,
                    amount=amount,
                    params={'stopPrice': stop_price}
                )
            
            self.active_orders[order['id']] = {
                'type': 'stop_loss',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'stop_price': stop_price,
                'limit_price': limit_price,
                'status': 'open',
                'created': datetime.now().isoformat()
            }
            
            print(f"✅ Stop-loss placed: {side} {amount} {symbol} @ ${stop_price}")
            return {
                'success': True,
                'order_id': order['id'],
                'order': order
            }
        
        except Exception as e:
            print(f"❌ Stop-loss failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def place_take_profit(self, symbol: str, side: str, amount: float, take_profit_price: float) -> Dict:
        """Place take-profit order"""
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='take_profit_market',
                side=side,
                amount=amount,
                params={'stopPrice': take_profit_price}
            )
            
            self.active_orders[order['id']] = {
                'type': 'take_profit',
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': take_profit_price,
                'status': 'open',
                'created': datetime.now().isoformat()
            }
            
            print(f"✅ Take-profit placed: {side} {amount} {symbol} @ ${take_profit_price}")
            return {
                'success': True,
                'order_id': order['id'],
                'order': order
            }
        
        except Exception as e:
            print(f"❌ Take-profit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def place_oco_order(self, symbol: str, side: str, amount: float, 
                        stop_price: float, take_profit_price: float) -> Dict:
        """Place OCO (One-Cancels-Other) order"""
        try:
            # Place both stop-loss and take-profit
            # When one executes, cancel the other
            
            stop_order = self.place_stop_loss(symbol, side, amount, stop_price)
            if not stop_order['success']:
                return stop_order
            
            tp_order = self.place_take_profit(symbol, side, amount, take_profit_price)
            if not tp_order['success']:
                # Cancel stop order
                self.cancel_order(stop_order['order_id'])
                return tp_order
            
            # Link orders
            self.active_orders[stop_order['order_id']]['oco_pair'] = tp_order['order_id']
            self.active_orders[tp_order['order_id']]['oco_pair'] = stop_order['order_id']
            
            print(f"✅ OCO order placed: {symbol} SL=${stop_price} TP=${take_profit_price}")
            return {
                'success': True,
                'stop_order_id': stop_order['order_id'],
                'tp_order_id': tp_order['order_id']
            }
        
        except Exception as e:
            print(f"❌ OCO order failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_trailing_stop(self, symbol: str, side: str, amount: float, 
                           trail_percent: float, initial_price: float):
        """Start a trailing stop-loss"""
        trail_id = f"trail_{symbol}_{int(time.time())}"
        
        self.trailing_stops[trail_id] = {
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'trail_percent': trail_percent,
            'highest_price': initial_price if side == 'sell' else None,
            'lowest_price': initial_price if side == 'buy' else None,
            'stop_price': None,
            'active': True,
            'created': datetime.now().isoformat()
        }
        
        print(f"✅ Trailing stop started: {symbol} {trail_percent}% trail")
        return {'success': True, 'trail_id': trail_id}
    
    def update_trailing_stop(self, trail_id: str, current_price: float) -> Dict:
        """Update trailing stop based on current price"""
        if trail_id not in self.trailing_stops:
            return {'error': 'Trailing stop not found'}
        
        trail = self.trailing_stops[trail_id]
        if not trail['active']:
            return {'error': 'Trailing stop not active'}
        
        side = trail['side']
        trail_percent = trail['trail_percent']
        
        if side == 'sell':  # Long position
            # Update highest price
            if current_price > trail['highest_price']:
                trail['highest_price'] = current_price
                trail['stop_price'] = current_price * (1 - trail_percent / 100)
                print(f"🔼 Trail updated: {trail['symbol']} stop now ${trail['stop_price']:.2f}")
            
            # Check if stop hit
            if current_price <= trail['stop_price']:
                print(f"🛑 Trailing stop triggered: {trail['symbol']} @ ${current_price:.2f}")
                # Place market order
                self.exchange.create_market_order(trail['symbol'], side, trail['amount'])
                trail['active'] = False
                return {'triggered': True, 'price': current_price}
        
        else:  # Short position
            # Update lowest price
            if current_price < trail['lowest_price']:
                trail['lowest_price'] = current_price
                trail['stop_price'] = current_price * (1 + trail_percent / 100)
                print(f"🔽 Trail updated: {trail['symbol']} stop now ${trail['stop_price']:.2f}")
            
            # Check if stop hit
            if current_price >= trail['stop_price']:
                print(f"🛑 Trailing stop triggered: {trail['symbol']} @ ${current_price:.2f}")
                self.exchange.create_market_order(trail['symbol'], side, trail['amount'])
                trail['active'] = False
                return {'triggered': True, 'price': current_price}
        
        return {'updated': True, 'stop_price': trail['stop_price']}
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        try:
            if order_id in self.active_orders:
                order_info = self.active_orders[order_id]
                self.exchange.cancel_order(order_id, order_info['symbol'])
                
                # Cancel OCO pair if exists
                if 'oco_pair' in order_info:
                    pair_id = order_info['oco_pair']
                    if pair_id in self.active_orders:
                        self.exchange.cancel_order(pair_id, self.active_orders[pair_id]['symbol'])
                        del self.active_orders[pair_id]
                
                del self.active_orders[order_id]
                print(f"✅ Order cancelled: {order_id}")
                return {'success': True}
            else:
                return {'success': False, 'error': 'Order not found'}
        
        except Exception as e:
            print(f"❌ Cancel failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_active_orders(self) -> Dict:
        """Get all active orders"""
        return self.active_orders
    
    def get_active_trailing_stops(self) -> Dict:
        """Get all active trailing stops"""
        return {k: v for k, v in self.trailing_stops.items() if v['active']}


if __name__ == '__main__':
    # Test (dry run)
    print("Advanced Orders Module Loaded")
    print("Available order types:")
    print("  - Limit orders")
    print("  - Stop-loss orders")
    print("  - Take-profit orders")
    print("  - OCO (One-Cancels-Other)")
    print("  - Trailing stop-loss")
