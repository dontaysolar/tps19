#!/usr/bin/env python3
"""
PAPER TRADING MODE
Simulated trading with real market data
"""

from datetime import datetime
from typing import Dict, List
import json

class PaperTradingEngine:
    """Simulated trading engine"""
    
    def __init__(self, initial_balance: float = 10000.0):
        self.name = "Paper_Trading"
        self.version = "1.0.0"
        
        # Virtual account
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = {}
        self.orders = {}
        self.trade_history = []
        
        # Simulation settings
        self.maker_fee = 0.001  # 0.1%
        self.taker_fee = 0.001  # 0.1%
        self.slippage = 0.0005  # 0.05%
        
        self.next_order_id = 1
        
        print(f"🧪 Paper Trading Mode - Starting balance: ${initial_balance:,.2f}")
    
    def place_market_order(self, symbol: str, side: str, amount: float, current_price: float) -> Dict:
        """Simulate market order execution"""
        
        # Calculate slippage
        slippage_multiplier = 1 + self.slippage if side == 'buy' else 1 - self.slippage
        execution_price = current_price * slippage_multiplier
        
        # Calculate cost/proceeds
        notional = amount * execution_price
        fee = notional * self.taker_fee
        
        if side == 'buy':
            total_cost = notional + fee
            
            # Check balance
            if total_cost > self.balance:
                return {
                    'success': False,
                    'error': 'Insufficient balance',
                    'required': total_cost,
                    'available': self.balance
                }
            
            # Execute buy
            self.balance -= total_cost
            
            # Add to positions
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'amount': 0,
                    'avg_entry': 0,
                    'realized_pnl': 0
                }
            
            pos = self.positions[symbol]
            total_amount = pos['amount'] + amount
            pos['avg_entry'] = ((pos['amount'] * pos['avg_entry']) + (amount * execution_price)) / total_amount
            pos['amount'] = total_amount
        
        else:  # sell
            # Check position
            if symbol not in self.positions or self.positions[symbol]['amount'] < amount:
                return {
                    'success': False,
                    'error': 'Insufficient position',
                    'required': amount,
                    'available': self.positions.get(symbol, {}).get('amount', 0)
                }
            
            # Execute sell
            proceeds = notional - fee
            self.balance += proceeds
            
            # Update position
            pos = self.positions[symbol]
            realized_pnl = (execution_price - pos['avg_entry']) * amount - fee
            pos['realized_pnl'] += realized_pnl
            pos['amount'] -= amount
            
            if pos['amount'] == 0:
                del self.positions[symbol]
        
        # Record trade
        trade = {
            'order_id': self.next_order_id,
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': execution_price,
            'fee': fee,
            'balance_after': self.balance,
            'slippage': abs(execution_price - current_price) / current_price,
            'realized_pnl': realized_pnl if side == 'sell' else 0
        }
        
        self.trade_history.append(trade)
        self.next_order_id += 1
        
        print(f"🧪 PAPER: {side.upper()} {amount} {symbol} @ ${execution_price:.2f} (fee: ${fee:.2f})")
        
        return {
            'success': True,
            'order_id': trade['order_id'],
            'execution_price': execution_price,
            'fee': fee,
            'balance': self.balance
        }
    
    def place_limit_order(self, symbol: str, side: str, amount: float, limit_price: float) -> Dict:
        """Place simulated limit order"""
        order_id = self.next_order_id
        self.next_order_id += 1
        
        self.orders[order_id] = {
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'limit_price': limit_price,
            'status': 'open',
            'created': datetime.now().isoformat()
        }
        
        print(f"🧪 PAPER: Limit order placed - {side.upper()} {amount} {symbol} @ ${limit_price:.2f}")
        
        return {
            'success': True,
            'order_id': order_id,
            'status': 'open'
        }
    
    def check_limit_orders(self, symbol: str, current_price: float):
        """Check if any limit orders should execute"""
        executed = []
        
        for order_id, order in list(self.orders.items()):
            if order['symbol'] != symbol or order['status'] != 'open':
                continue
            
            should_execute = False
            
            if order['side'] == 'buy' and current_price <= order['limit_price']:
                should_execute = True
            elif order['side'] == 'sell' and current_price >= order['limit_price']:
                should_execute = True
            
            if should_execute:
                # Execute as market order at limit price
                result = self.place_market_order(
                    symbol, 
                    order['side'], 
                    order['amount'], 
                    order['limit_price']
                )
                
                if result['success']:
                    self.orders[order_id]['status'] = 'filled'
                    self.orders[order_id]['filled_at'] = datetime.now().isoformat()
                    executed.append(order_id)
                    print(f"🧪 PAPER: Limit order #{order_id} FILLED @ ${current_price:.2f}")
        
        return executed
    
    def calculate_unrealized_pnl(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate unrealized P&L for open positions"""
        unrealized_pnl = 0
        position_values = {}
        
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                current_price = current_prices[symbol]
                pnl = (current_price - pos['avg_entry']) * pos['amount']
                unrealized_pnl += pnl
                
                position_values[symbol] = {
                    'amount': pos['amount'],
                    'avg_entry': pos['avg_entry'],
                    'current_price': current_price,
                    'position_value': current_price * pos['amount'],
                    'unrealized_pnl': pnl,
                    'pnl_percent': (pnl / (pos['avg_entry'] * pos['amount'])) * 100
                }
        
        return {
            'total_unrealized_pnl': unrealized_pnl,
            'positions': position_values
        }
    
    def get_portfolio_stats(self, current_prices: Dict[str, float]) -> Dict:
        """Get complete portfolio statistics"""
        pnl_data = self.calculate_unrealized_pnl(current_prices)
        
        # Calculate total equity
        position_value = sum(p['position_value'] for p in pnl_data['positions'].values())
        total_equity = self.balance + position_value
        
        # Calculate returns
        total_pnl = total_equity - self.initial_balance
        total_return = (total_pnl / self.initial_balance) * 100
        
        # Trade statistics
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t.get('realized_pnl', 0) > 0)
        losing_trades = sum(1 for t in self.trade_history if t.get('realized_pnl', 0) < 0)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        realized_pnl = sum(pos['realized_pnl'] for pos in self.positions.values()) + \
                      sum(t.get('realized_pnl', 0) for t in self.trade_history if t['side'] == 'sell')
        
        return {
            'initial_balance': self.initial_balance,
            'cash_balance': self.balance,
            'position_value': position_value,
            'total_equity': total_equity,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': pnl_data['total_unrealized_pnl'],
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'open_positions': len(self.positions)
        }
    
    def get_trade_history(self) -> List[Dict]:
        """Get complete trade history"""
        return self.trade_history
    
    def reset(self, initial_balance: float = None):
        """Reset paper trading account"""
        if initial_balance:
            self.initial_balance = initial_balance
        
        self.balance = self.initial_balance
        self.positions = {}
        self.orders = {}
        self.trade_history = []
        self.next_order_id = 1
        
        print(f"🧪 Paper Trading Reset - Balance: ${self.initial_balance:,.2f}")


if __name__ == '__main__':
    # Test paper trading
    paper = PaperTradingEngine(initial_balance=10000)
    
    # Simulate some trades
    print("\n--- Simulating Trades ---")
    
    # Buy BTC
    result = paper.place_market_order('BTC/USDT', 'buy', 0.1, 50000)
    print(f"Balance after buy: ${paper.balance:.2f}")
    
    # Buy ETH
    paper.place_market_order('ETH/USDT', 'buy', 2.0, 3000)
    
    # Check portfolio
    current_prices = {'BTC/USDT': 52000, 'ETH/USDT': 3100}
    stats = paper.get_portfolio_stats(current_prices)
    
    print(f"\n--- Portfolio Stats ---")
    print(f"Total Equity: ${stats['total_equity']:.2f}")
    print(f"Total P&L: ${stats['total_pnl']:.2f} ({stats['total_return_pct']:.2f}%)")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    
    # Sell BTC
    paper.place_market_order('BTC/USDT', 'sell', 0.1, 52000)
    
    final_stats = paper.get_portfolio_stats(current_prices)
    print(f"\nFinal Equity: ${final_stats['total_equity']:.2f}")
