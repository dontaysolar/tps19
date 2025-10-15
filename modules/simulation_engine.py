#!/usr/bin/env python3
"""TPS19 Simulation Engine - Paper trading functionality"""

import json
import sqlite3
import time
from datetime import datetime
import random
import os
from modules.utils.paths import db_path

class SimulationEngine:
    def __init__(self):
        self.db_path = db_path("simulation.db")
        self.balance = 10000.0  # Starting balance
        self.positions = {}
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

if __name__ == "__main__":
    sim = SimulationEngine()
    print("Simulation Engine initialized successfully")
