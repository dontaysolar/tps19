"""
SQLite Trade Store

Persists orders, trades, and positions for live/paper trading.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List


class TradeStore:
    def __init__(self, db_path: str = 'data/trading.db') -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                type TEXT,
                price REAL,
                amount REAL,
                cost REAL,
                status TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                symbol TEXT,
                side TEXT,
                price REAL,
                amount REAL,
                cost REAL,
                pnl REAL,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                side TEXT,
                entry_price REAL,
                amount REAL,
                created_at TEXT
            );
            """
        )
        conn.commit()
        conn.close()

    def record_order(self, order: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO orders (id, symbol, side, type, price, amount, cost, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order.get('id'),
                order.get('symbol'),
                order.get('side'),
                order.get('type', 'market'),
                float(order.get('price', 0) or 0),
                float(order.get('amount', 0) or 0),
                float(order.get('cost', 0) or 0),
                order.get('status', 'open'),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def list_orders(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, symbol, side, type, price, amount, cost, status, created_at
            FROM orders
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (int(limit),),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                'id': r[0],
                'symbol': r[1],
                'side': r[2],
                'type': r[3],
                'price': float(r[4]),
                'amount': float(r[5]),
                'cost': float(r[6]),
                'status': r[7],
                'created_at': r[8],
            }
            for r in rows
        ]

    def open_position(self, symbol: str, side: str, entry_price: float, amount: float) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO positions (symbol, side, entry_price, amount, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (symbol, side, float(entry_price), float(amount), datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    def close_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT symbol, side, entry_price, amount, created_at FROM positions WHERE symbol = ?", (symbol,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None
        cur.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
        conn.commit()
        conn.close()
        return {
            'symbol': row[0],
            'side': row[1],
            'entry_price': float(row[2]),
            'amount': float(row[3]),
            'created_at': row[4],
        }

    def list_positions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT symbol, side, entry_price, amount, created_at FROM positions")
        rows = cur.fetchall()
        conn.close()
        return [
            {
                'symbol': r[0],
                'side': r[1],
                'entry_price': float(r[2]),
                'amount': float(r[3]),
                'created_at': r[4],
            }
            for r in rows
        ]

    def record_trade(self, order_id: str, symbol: str, side: str, price: float, amount: float, cost: float, pnl: float) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO trades (order_id, symbol, side, price, amount, cost, pnl, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (order_id, symbol, side, float(price), float(amount), float(cost), float(pnl), datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
