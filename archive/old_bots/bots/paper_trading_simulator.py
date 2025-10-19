#!/usr/bin/env python3
"""
Paper Trading Simulator
Risk-free strategy testing with real market data
Validates strategies before live deployment
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class PaperTradingSimulator:
    def __init__(self):
        self.name = "Paper_Trading_Simulator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.starting_capital = 10000
        self.current_capital = self.starting_capital
        self.positions = {}
        self.trade_history = []
        
        self.metrics = {'total_trades': 0, 'win_rate': 0, 'total_pnl': 0}
    
    def execute_paper_trade(self, signal: str, symbol: str, price: float, size: float) -> Dict:
        """Execute trade in paper account"""
        if signal == 'BUY':
            cost = price * size
            if cost <= self.current_capital:
                self.current_capital -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + size
                
                trade = {
                    'type': 'BUY',
                    'symbol': symbol,
                    'price': price,
                    'size': size,
                    'cost': cost,
                    'timestamp': datetime.now().isoformat()
                }
                self.trade_history.append(trade)
                self.metrics['total_trades'] += 1
                
                return {'executed': True, 'trade': trade, 'remaining_capital': self.current_capital}
            else:
                return {'executed': False, 'reason': 'Insufficient capital'}
        
        elif signal == 'SELL':
            if symbol in self.positions and self.positions[symbol] >= size:
                proceeds = price * size
                self.current_capital += proceeds
                self.positions[symbol] -= size
                
                trade = {
                    'type': 'SELL',
                    'symbol': symbol,
                    'price': price,
                    'size': size,
                    'proceeds': proceeds,
                    'timestamp': datetime.now().isoformat()
                }
                self.trade_history.append(trade)
                self.metrics['total_trades'] += 1
                
                return {'executed': True, 'trade': trade, 'remaining_capital': self.current_capital}
            else:
                return {'executed': False, 'reason': 'Insufficient position'}
        
        return {'executed': False, 'reason': 'Invalid signal'}
    
    def get_account_value(self, current_prices: Dict[str, float]) -> Dict:
        """Calculate total account value"""
        position_value = sum([size * current_prices.get(symbol, 0) for symbol, size in self.positions.items()])
        total_value = self.current_capital + position_value
        
        return {
            'cash': self.current_capital,
            'positions_value': position_value,
            'total_value': total_value,
            'total_return': total_value - self.starting_capital,
            'total_return_pct': ((total_value - self.starting_capital) / self.starting_capital * 100) if self.starting_capital > 0 else 0,
            'positions': self.positions,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_summary(self) -> Dict:
        """Get performance metrics"""
        # Calculate win rate
        completed_trades = []
        buys = {}
        
        for trade in self.trade_history:
            if trade['type'] == 'BUY':
                if trade['symbol'] not in buys:
                    buys[trade['symbol']] = []
                buys[trade['symbol']].append(trade)
            elif trade['type'] == 'SELL' and trade['symbol'] in buys and buys[trade['symbol']]:
                buy_trade = buys[trade['symbol']].pop(0)
                pnl = (trade['price'] - buy_trade['price']) * trade['size']
                completed_trades.append({
                    'symbol': trade['symbol'],
                    'pnl': pnl,
                    'return_pct': (pnl / (buy_trade['price'] * trade['size']) * 100) if buy_trade['price'] > 0 else 0
                })
        
        if completed_trades:
            winning_trades = len([t for t in completed_trades if t['pnl'] > 0])
            total_pnl = sum([t['pnl'] for t in completed_trades])
            
            self.metrics['win_rate'] = winning_trades / len(completed_trades)
            self.metrics['total_pnl'] = total_pnl
        
        return {
            'total_trades': len(self.trade_history),
            'completed_trades': len(completed_trades),
            'win_rate': self.metrics['win_rate'],
            'total_pnl': self.metrics['total_pnl'],
            'timestamp': datetime.now().isoformat()
        }
    
    def reset(self):
        """Reset paper account"""
        self.current_capital = self.starting_capital
        self.positions.clear()
        self.trade_history.clear()
        self.metrics = {'total_trades': 0, 'win_rate': 0, 'total_pnl': 0}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'current_capital': self.current_capital, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    simulator = PaperTradingSimulator()
    print(f"✅ {simulator.name} v{simulator.version} initialized")
