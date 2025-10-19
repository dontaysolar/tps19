#!/usr/bin/env python3
"""
TRADE PERSISTENCE MODULE
Ensures all trades and positions are saved to disk
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class TradeJournal:
    """JSON-based trade journal for quick implementation"""
    
    def __init__(self, filename='data/trades.jsonl'):
        self.filename = filename
        Path('data').mkdir(exist_ok=True)
        Path(filename).touch(exist_ok=True)
    
    def log_trade(self, trade_data: Dict):
        """Append trade to journal"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': f"{datetime.now().timestamp()}",
            **trade_data
        }
        
        with open(self.filename, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return entry['trade_id']
    
    def get_trades(self, symbol: Optional[str] = None, 
                   limit: Optional[int] = None) -> List[Dict]:
        """Load trades, optionally filtered"""
        if not Path(self.filename).exists():
            return []
        
        trades = []
        with open(self.filename, 'r') as f:
            for line in f:
                if line.strip():
                    trade = json.loads(line)
                    if symbol is None or trade.get('symbol') == symbol:
                        trades.append(trade)
        
        if limit:
            trades = trades[-limit:]
        
        return trades
    
    def get_summary(self) -> Dict:
        """Get trading summary statistics"""
        trades = self.get_trades()
        
        if not trades:
            return {
                'total_trades': 0,
                'realized_pnl': 0,
                'win_rate': 0
            }
        
        total_pnl = sum(t.get('pnl', 0) for t in trades if 'pnl' in t)
        winning_trades = sum(1 for t in trades if t.get('pnl', 0) > 0)
        total_with_pnl = sum(1 for t in trades if 'pnl' in t)
        
        return {
            'total_trades': len(trades),
            'realized_pnl': total_pnl,
            'win_rate': (winning_trades / total_with_pnl * 100) if total_with_pnl > 0 else 0,
            'avg_pnl': total_pnl / total_with_pnl if total_with_pnl > 0 else 0
        }


class PositionDatabase:
    """SQLite database for position tracking"""
    
    def __init__(self, db_path='data/positions.db'):
        self.db_path = db_path
        Path('data').mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Positions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                entry_time TEXT NOT NULL,
                last_update TEXT NOT NULL
            )
        ''')
        
        # Portfolio state table
        c.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_equity REAL NOT NULL,
                available_balance REAL NOT NULL,
                positions_value REAL NOT NULL,
                total_pnl REAL NOT NULL,
                last_update TEXT NOT NULL
            )
        ''')
        
        # Insert default portfolio state if not exists
        c.execute('''
            INSERT OR IGNORE INTO portfolio_state 
            (id, total_equity, available_balance, positions_value, total_pnl, last_update)
            VALUES (1, 10000.0, 10000.0, 0.0, 0.0, ?)
        ''', (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
    
    def save_position(self, position: Dict):
        """Save or update position"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO positions 
            (symbol, side, amount, entry_price, current_price, unrealized_pnl, entry_time, last_update)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            position['symbol'],
            position['side'],
            position['amount'],
            position['entry_price'],
            position.get('current_price', position['entry_price']),
            position.get('unrealized_pnl', 0),
            position.get('entry_time', datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position by symbol"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM positions WHERE symbol = ?', (symbol,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_positions(self) -> List[Dict]:
        """Get all open positions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM positions')
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def close_position(self, symbol: str):
        """Remove closed position"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM positions WHERE symbol = ?', (symbol,))
        conn.commit()
        conn.close()
    
    def update_portfolio(self, equity: float, available: float, 
                        positions_value: float, total_pnl: float):
        """Update portfolio state"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE portfolio_state 
            SET total_equity = ?, available_balance = ?, 
                positions_value = ?, total_pnl = ?, last_update = ?
            WHERE id = 1
        ''', (equity, available, positions_value, total_pnl, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM portfolio_state WHERE id = 1')
        row = c.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {
            'total_equity': 10000.0,
            'available_balance': 10000.0,
            'positions_value': 0.0,
            'total_pnl': 0.0
        }


class PersistenceManager:
    """Combined manager for all persistence needs"""
    
    def __init__(self):
        self.trade_journal = TradeJournal()
        self.position_db = PositionDatabase()
    
    def log_trade(self, trade_data: Dict) -> str:
        """Log a trade"""
        return self.trade_journal.log_trade(trade_data)
    
    def save_position(self, position: Dict):
        """Save position state"""
        self.position_db.save_position(position)
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position"""
        return self.position_db.get_position(symbol)
    
    def get_all_positions(self) -> List[Dict]:
        """Get all positions"""
        return self.position_db.get_all_positions()
    
    def close_position(self, symbol: str):
        """Close position"""
        self.position_db.close_position(symbol)
    
    def get_portfolio_state(self) -> Dict:
        """Get portfolio"""
        return self.position_db.get_portfolio_state()
    
    def update_portfolio(self, **kwargs):
        """Update portfolio"""
        state = self.get_portfolio_state()
        self.position_db.update_portfolio(
            equity=kwargs.get('total_equity', state['total_equity']),
            available=kwargs.get('available_balance', state['available_balance']),
            positions_value=kwargs.get('positions_value', state['positions_value']),
            total_pnl=kwargs.get('total_pnl', state['total_pnl'])
        )
    
    def get_trade_summary(self) -> Dict:
        """Get trade statistics"""
        return self.trade_journal.get_summary()


if __name__ == '__main__':
    # Test persistence
    pm = PersistenceManager()
    
    # Test trade logging
    trade_id = pm.log_trade({
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'amount': 0.001,
        'price': 50000,
        'value': 50
    })
    print(f"✅ Trade logged: {trade_id}")
    
    # Test position saving
    pm.save_position({
        'symbol': 'BTC/USDT',
        'side': 'long',
        'amount': 0.001,
        'entry_price': 50000
    })
    print(f"✅ Position saved")
    
    # Test retrieval
    pos = pm.get_position('BTC/USDT')
    print(f"✅ Position retrieved: {pos}")
    
    # Test portfolio
    state = pm.get_portfolio_state()
    print(f"✅ Portfolio state: {state}")
    
    print("\n✅ Persistence module working correctly")
