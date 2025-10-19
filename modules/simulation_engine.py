#!/usr/bin/env python3
"""TPS19 Simulation Engine - Paper trading functionality"""

import json
import sqlite3
import time
import os
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional

class SimulationEngine:
    def __init__(self, initial_balance: float = 10000.0):
        workspace = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(workspace, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "simulation.db")
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = {}
        self.trades_history = []
        self.init_database()
        
    def init_database(self):
        """Initialize simulation database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sim_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                pnl REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sim_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                balance REAL NOT NULL,
                total_pnl REAL DEFAULT 0.0,
                trades_count INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def simulate_trade(self, pair, side, amount, price=None):
        """Simulate a trade execution"""
        if price is None:
            # Simulate market price with some randomness
            price = 50000 + random.uniform(-1000, 1000)
            
        # Calculate trade value
        trade_value = amount * price
        
        # Simulate trade execution
        if side.lower() == 'buy':
            if self.balance >= trade_value:
                self.balance -= trade_value
                self.positions[pair] = self.positions.get(pair, 0) + amount
                status = "executed"
            else:
                status = "insufficient_balance"
        else:  # sell
            if self.positions.get(pair, 0) >= amount:
                self.balance += trade_value
                self.positions[pair] = self.positions.get(pair, 0) - amount
                status = "executed"
            else:
                status = "insufficient_position"
                
        # Log trade
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sim_trades (pair, side, amount, price)
            VALUES (?, ?, ?, ?)
        ''', (pair, side, amount, price))
        
        conn.commit()
        conn.close()
        
        return {
            "status": status,
            "trade_id": cursor.lastrowid,
            "price": price,
            "balance": self.balance
        }
        
    def get_portfolio(self):
        """Get current portfolio status"""
        return {
            "balance": self.balance,
            "positions": self.positions,
            "total_value": self.balance + sum(pos * 50000 for pos in self.positions.values())
        }
        
    def get_performance(self):
        """Get performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM sim_trades')
        total_trades = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(pnl) FROM sim_trades WHERE pnl != 0')
        avg_pnl = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_trades": total_trades,
            "avg_pnl": avg_pnl,
            "current_balance": self.balance,
            "roi": ((self.balance - 10000) / 10000) * 100
        }

    def run_backtest(self, strategy, historical_data: List[Dict], 
                    initial_balance: float = 10000.0) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            strategy: Trading strategy function
            historical_data: List of price/time data points
            initial_balance: Starting balance
            
        Returns:
            Dict with backtest results
        """
        self.balance = initial_balance
        self.positions = {}
        trades = []
        
        for data_point in historical_data:
            # Strategy generates signals
            signal = strategy(data_point, self.positions, self.balance)
            
            if signal and signal['action'] != 'hold':
                result = self.simulate_trade(
                    signal['pair'],
                    signal['action'],
                    signal['amount'],
                    data_point.get('price')
                )
                trades.append(result)
                
        # Calculate metrics
        total_return = ((self.balance - initial_balance) / initial_balance) * 100
        num_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        
        return {
            "initial_balance": initial_balance,
            "final_balance": self.balance,
            "total_return": round(total_return, 2),
            "total_trades": num_trades,
            "winning_trades": winning_trades,
            "win_rate": round((winning_trades / num_trades * 100) if num_trades > 0 else 0, 2),
            "max_drawdown": self._calculate_max_drawdown(trades)
        }
        
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0
            
        peak = self.initial_balance
        max_dd = 0.0
        current_balance = self.initial_balance
        
        for trade in trades:
            current_balance += trade.get('pnl', 0)
            if current_balance > peak:
                peak = current_balance
            dd = (peak - current_balance) / peak
            if dd > max_dd:
                max_dd = dd
                
        return round(max_dd * 100, 2)


if __name__ == "__main__":
    sim = SimulationEngine()
    print("✅ Simulation Engine initialized successfully")
    
    # Test backtest
    def simple_strategy(data, positions, balance):
        # Simple buy low, sell high strategy
        if data['price'] < 49000 and not positions:
            return {'action': 'buy', 'pair': 'BTC/USDT', 'amount': 0.01}
        elif data['price'] > 51000 and positions:
            return {'action': 'sell', 'pair': 'BTC/USDT', 'amount': 0.01}
        return {'action': 'hold'}
        
    # Generate mock historical data
    historical_data = [
        {'price': 48000 + (i * 100), 'timestamp': datetime.now()}
        for i in range(100)
    ]
    
    result = sim.run_backtest(simple_strategy, historical_data)
    print(f"Backtest results: {result}")
