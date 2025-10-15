#!/usr/bin/env python3
"""TPS19 Risk Management - Position sizing and risk controls"""

import json
import sqlite3
from datetime import datetime

class RiskManager:
    def __init__(self):
        self.db_path = "/workspace/data/databases/risk.db"
        self.max_position_size = 0.1  # 10% max position size
        self.max_daily_loss = 0.05    # 5% max daily loss
        self.init_database()
        
    def init_database(self):
        """Initialize risk management database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_value REAL NOT NULL,
                daily_pnl REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                var_95 REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                limit_type TEXT NOT NULL,
                limit_value REAL NOT NULL,
                current_value REAL DEFAULT 0.0,
                status TEXT DEFAULT 'ok',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def calculate_position_size(self, portfolio_value, risk_per_trade=0.02):
        """Calculate optimal position size"""
        max_risk_amount = portfolio_value * risk_per_trade
        max_position_value = portfolio_value * self.max_position_size
        
        return min(max_risk_amount, max_position_value)
        
    def check_risk_limits(self, portfolio_value, daily_pnl):
        """Check if risk limits are exceeded"""
        risks = []
        
        # Check daily loss limit
        daily_loss_pct = abs(daily_pnl) / portfolio_value if portfolio_value > 0 else 0
        if daily_loss_pct > self.max_daily_loss:
            risks.append({
                "type": "daily_loss_limit",
                "current": daily_loss_pct,
                "limit": self.max_daily_loss,
                "severity": "high"
            })
            
        # Check position concentration
        # This would check individual position sizes in a real implementation
        
        return risks
        
    def calculate_var(self, returns, confidence=0.95):
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
            
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        
        return sorted_returns[index] if index < len(sorted_returns) else 0.0
        
    def update_risk_metrics(self, portfolio_value, daily_pnl):
        """Update risk metrics in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO risk_metrics (portfolio_value, daily_pnl)
            VALUES (?, ?)
        ''', (portfolio_value, daily_pnl))
        
        conn.commit()
        conn.close()
        
    def get_risk_report(self):
        """Generate risk report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(daily_pnl), MIN(daily_pnl), MAX(daily_pnl)
            FROM risk_metrics
            WHERE date(timestamp) = date('now')
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "avg_daily_pnl": result[0] or 0,
            "min_daily_pnl": result[1] or 0,
            "max_daily_pnl": result[2] or 0,
            "risk_status": "normal"
        }

if __name__ == "__main__":
    risk = RiskManager()
    print("Risk Management initialized successfully")
