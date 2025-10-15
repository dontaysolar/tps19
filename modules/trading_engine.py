#!/usr/bin/env python3
"""TPS19 Trading Engine - Crypto.com Integration"""

import json
import sqlite3
import time
from datetime import datetime
import os

class TradingEngine:
    def __init__(self):
        self.db_path = "/workspace/data/databases/trading.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.exchange = "crypto.com"
        self.mode = "simulation"  # Start in simulation mode
        self.balance = 10000.0
        self.positions = {}
        self.init_database()
        
    def init_database(self):
        """Initialize trading database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price REAL NOT NULL,
                    fee REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'pending',
                    exchange TEXT DEFAULT 'crypto.com',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    amount REAL NOT NULL,
                    avg_price REAL NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Trading Engine database initialized")
            
        except Exception as e:
            print(f"❌ Trading Engine database error: {e}")
            
    def execute_trade(self, symbol, side, amount, price=None):
        """Execute a trade (simulation mode)"""
        try:
            if not price:
                price = 50000.0  # Mock price for simulation
                
            trade_value = amount * price
            fee = trade_value * 0.001  # 0.1% fee
            
            if side.lower() == 'buy':
                if self.balance >= trade_value + fee:
                    self.balance -= (trade_value + fee)
                    self.positions[symbol] = self.positions.get(symbol, 0) + amount
                    status = "executed"
                else:
                    status = "insufficient_balance"
            else:  # sell
                if self.positions.get(symbol, 0) >= amount:
                    self.balance += (trade_value - fee)
                    self.positions[symbol] = self.positions.get(symbol, 0) - amount
                    status = "executed"
                else:
                    status = "insufficient_position"
                    
            # Log trade
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (symbol, side, amount, price, fee, status, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, side, amount, price, fee, status, self.exchange))
            
            conn.commit()
            trade_id = cursor.lastrowid
            conn.close()
            
            return {
                "trade_id": trade_id,
                "status": status,
                "price": price,
                "fee": fee,
                "balance": self.balance
            }
            
        except Exception as e:
            print(f"❌ Trade execution error: {e}")
            return {"status": "error", "error": str(e)}
            
    def get_portfolio(self):
        """Get current portfolio"""
        return {
            "balance": self.balance,
            "positions": self.positions,
            "mode": self.mode,
            "exchange": self.exchange
        }
        
    def get_trade_history(self, limit=50):
        """Get trade history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            trades = cursor.fetchall()
            conn.close()
            
            return trades
            
        except Exception as e:
            print(f"❌ Trade history error: {e}")
            return []

if __name__ == "__main__":
    engine = TradingEngine()
    print("✅ Trading Engine initialized successfully")