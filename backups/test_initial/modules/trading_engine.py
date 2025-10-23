#!/usr/bin/env python3
"""Trading Engine Module - Core Trading Logic"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

class TradingEngine:
    """Main Trading Engine for TPS19 System"""
    
    def __init__(self, db_path: str = None):
        """Initialize Trading Engine"""
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'data', 'databases', 'trading.db')
        
        self.db_path = db_path
        self.exchange = 'crypto.com'
        self.active = False
        
        self._init_database()
        
    def _init_database(self):
        """Initialize trading database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                exchange TEXT DEFAULT 'crypto.com',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Trading Engine database init failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get trading engine status"""
        return {
            'active': self.active,
            'exchange': self.exchange,
            'db_path': self.db_path
        }
    
    def execute_trade(self, symbol: str, action: str, price: float, amount: float) -> bool:
        """Execute a trade"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            trade_id = f"trade_{int(datetime.now().timestamp() * 1000)}"
            
            cursor.execute("""INSERT INTO trades 
                (trade_id, symbol, action, price, amount, status, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (trade_id, symbol, action, price, amount, 'executed', self.exchange))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            return False
    
    def test_functionality(self) -> bool:
        """Test trading engine functionality"""
        try:
            # Test database connection
            conn = sqlite3.connect(self.db_path)
            conn.close()
            
            # Test trade execution
            result = self.execute_trade('BTC_USDT', 'buy', 45000.0, 0.01)
            
            return result
            
        except Exception as e:
            print(f"❌ Trading Engine test failed: {e}")
            return False
