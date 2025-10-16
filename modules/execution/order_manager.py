#!/usr/bin/env python3
"""Order Management System"""

from typing import Dict, List, Optional
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.database import get_db_connection

logger = get_logger(__name__)


class OrderManager:
    """
    Manages order lifecycle:
    - Validation
    - Execution
    - Monitoring
    - Exit management
    """
    
    def __init__(self):
        self.db_name = 'orders.db'
        self._init_database()
        self.active_orders = {}
        
    def _init_database(self):
        """Initialize orders database"""
        schema = """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL,
                order_type TEXT DEFAULT 'market',
                status TEXT DEFAULT 'pending',
                strategy TEXT,
                confidence REAL,
                stop_loss REAL,
                take_profit REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                filled_at DATETIME,
                metadata TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        """
        
        try:
            with get_db_connection(self.db_name) as conn:
                conn.executescript(schema)
            logger.info("Order manager database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
    
    def create_order(self, order_data: Dict) -> str:
        """
        Create and track new order
        
        Args:
            order_data: Order details
            
        Returns:
            Order ID
        """
        try:
            order_id = order_data.get('order_id', f"ORD_{int(datetime.now().timestamp())}")
            
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO orders (order_id, symbol, side, amount, price, 
                                      order_type, status, strategy, confidence,
                                      stop_loss, take_profit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    order_id,
                    order_data['symbol'],
                    order_data['side'],
                    order_data['amount'],
                    order_data.get('price'),
                    order_data.get('order_type', 'market'),
                    'pending',
                    order_data.get('strategy'),
                    order_data.get('confidence'),
                    order_data.get('stop_loss'),
                    order_data.get('take_profit')
                ))
            
            self.active_orders[order_id] = order_data
            logger.info(f"📋 Order created: {order_id}")
            
            return order_id
            
        except Exception as e:
            logger.error(f"Order creation error: {e}")
            return ""
    
    def update_order_status(self, order_id: str, status: str):
        """Update order status"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders 
                    SET status = ?, filled_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                """, (status, order_id))
            
            if order_id in self.active_orders:
                self.active_orders[order_id]['status'] = status
                
        except Exception as e:
            logger.error(f"Order update error: {e}")
    
    def get_active_orders(self) -> List[Dict]:
        """Get all active orders"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM orders 
                    WHERE status IN ('pending', 'open', 'partially_filled')
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Get orders error: {e}")
            return []


order_manager = OrderManager()
