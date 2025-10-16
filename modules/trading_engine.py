#!/usr/bin/env python3
"""TPS19 Trading Engine - Order Execution and Management"""

import json
import sqlite3
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from modules.utils.config import config
from modules.utils.logger import get_logger
from modules.utils.database import get_db_connection

logger = get_logger(__name__)


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    FAILED = "failed"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class TradingEngine:
    """Core trading engine for order execution and management"""
    
    def __init__(self):
        self.db_name = 'trading.db'
        self.exchange = config.exchange
        self.is_simulation = config.is_simulation
        self.lock = threading.Lock()
        
        # Position tracking
        self.positions = {}
        
        # Initialize database
        self._init_database()
        self._load_positions()
        
        logger.info(f"Trading Engine initialized - Mode: {'SIMULATION' if self.is_simulation else 'LIVE'}")
    
    def _init_database(self):
        """Initialize trading database"""
        schema = """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT DEFAULT 'market',
                amount REAL NOT NULL,
                price REAL NOT NULL,
                filled_amount REAL DEFAULT 0.0,
                average_price REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                exchange TEXT NOT NULL,
                commission REAL DEFAULT 0.0,
                pnl REAL DEFAULT 0.0,
                metadata TEXT
            );
            
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                pair TEXT NOT NULL,
                amount REAL DEFAULT 0.0,
                avg_entry_price REAL DEFAULT 0.0,
                current_price REAL DEFAULT 0.0,
                unrealized_pnl REAL DEFAULT 0.0,
                realized_pnl REAL DEFAULT 0.0,
                exchange TEXT NOT NULL,
                opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                exchange TEXT NOT NULL,
                metadata TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
            CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
            CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
        """
        
        try:
            with get_db_connection(self.db_name) as conn:
                conn.executescript(schema)
            logger.info("Trading database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize trading database: {e}")
    
    def _load_positions(self):
        """Load existing positions from database"""
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM positions WHERE exchange = ?", (self.exchange,))
                rows = cursor.fetchall()
                
                for row in rows:
                    self.positions[row['symbol']] = {
                        'amount': row['amount'],
                        'avg_entry_price': row['avg_entry_price'],
                        'current_price': row['current_price'],
                        'unrealized_pnl': row['unrealized_pnl'],
                        'realized_pnl': row['realized_pnl']
                    }
                
                logger.info(f"Loaded {len(self.positions)} positions from database")
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
    
    def place_order(self, symbol: str, side: OrderSide, amount: float, 
                   order_type: OrderType = OrderType.MARKET, 
                   price: Optional[float] = None,
                   metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Place a trading order
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USD')
            side: Order side (BUY or SELL)
            amount: Order amount
            order_type: Type of order (MARKET, LIMIT, etc.)
            price: Order price (required for LIMIT orders)
            metadata: Additional order metadata
            
        Returns:
            Order result dictionary
        """
        with self.lock:
            try:
                # Validate order
                if amount <= 0:
                    return self._error_response("Invalid amount: must be positive")
                
                if order_type == OrderType.LIMIT and price is None:
                    return self._error_response("Price required for limit orders")
                
                # In simulation mode, execute immediately
                if self.is_simulation:
                    return self._simulate_order(symbol, side, amount, order_type, price, metadata)
                else:
                    # TODO: Implement live exchange API integration
                    return self._execute_live_order(symbol, side, amount, order_type, price, metadata)
                    
            except Exception as e:
                logger.error(f"Order placement failed: {e}")
                return self._error_response(str(e))
    
    def _simulate_order(self, symbol: str, side: OrderSide, amount: float,
                       order_type: OrderType, price: Optional[float],
                       metadata: Optional[Dict]) -> Dict[str, Any]:
        """Simulate order execution in simulation mode
        
        Args:
            symbol: Trading symbol
            side: Order side
            amount: Order amount
            order_type: Order type
            price: Order price
            metadata: Additional metadata
            
        Returns:
            Simulated order result
        """
        try:
            # Use provided price or simulate market price
            execution_price = price if price else self._get_market_price(symbol)
            
            # Calculate commission (0.1% default)
            commission_rate = config.get('trading.simulation.commission', 0.001)
            commission = amount * execution_price * commission_rate
            
            # Store trade
            trade_id = self._store_trade(
                symbol=symbol,
                side=side.value,
                amount=amount,
                price=execution_price,
                order_type=order_type.value,
                status=OrderStatus.FILLED.value,
                commission=commission,
                metadata=metadata
            )
            
            # Update position
            self._update_position(symbol, side, amount, execution_price)
            
            result = {
                'status': 'success',
                'trade_id': trade_id,
                'symbol': symbol,
                'side': side.value,
                'amount': amount,
                'price': execution_price,
                'commission': commission,
                'total_cost': amount * execution_price + commission,
                'timestamp': datetime.now().isoformat(),
                'mode': 'simulation'
            }
            
            logger.info(f"Simulated {side.value} order: {amount} {symbol} @ ${execution_price:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Simulation order failed: {e}")
            return self._error_response(str(e))
    
    def _execute_live_order(self, symbol: str, side: OrderSide, amount: float,
                           order_type: OrderType, price: Optional[float],
                           metadata: Optional[Dict]) -> Dict[str, Any]:
        """Execute order on live exchange
        
        NOTE: This is a placeholder for live trading implementation
        
        Args:
            symbol: Trading symbol
            side: Order side
            amount: Order amount
            order_type: Order type
            price: Order price
            metadata: Additional metadata
            
        Returns:
            Order result
        """
        logger.warning("Live trading not yet implemented - use simulation mode")
        return self._error_response("Live trading not implemented")
    
    def _get_market_price(self, symbol: str) -> float:
        """Get current market price for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Current market price
        """
        # TODO: Integrate with market data module
        # For now, return a simulated price
        base_prices = {
            'BTC/USD': 50000.0,
            'ETH/USD': 3000.0,
            'BTC_USDT': 50000.0,
            'ETH_USDT': 3000.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        # Add small random variation (+/- 1%)
        import random
        variation = random.uniform(-0.01, 0.01)
        return base_price * (1 + variation)
    
    def _store_trade(self, symbol: str, side: str, amount: float, price: float,
                    order_type: str, status: str, commission: float = 0.0,
                    metadata: Optional[Dict] = None) -> int:
        """Store trade in database
        
        Args:
            symbol: Trading symbol
            side: Order side
            amount: Trade amount
            price: Execution price
            order_type: Order type
            status: Trade status
            commission: Trade commission
            metadata: Additional metadata
            
        Returns:
            Trade ID
        """
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trades (symbol, pair, side, order_type, amount, price, 
                                      filled_amount, average_price, status, exchange, 
                                      commission, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, symbol, side, order_type, amount, price, amount, price,
                     status, self.exchange, commission, json.dumps(metadata or {})))
                
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to store trade: {e}")
            return -1
    
    def _update_position(self, symbol: str, side: OrderSide, amount: float, price: float):
        """Update position after trade
        
        Args:
            symbol: Trading symbol
            side: Trade side
            amount: Trade amount
            price: Trade price
        """
        try:
            current_position = self.positions.get(symbol, {
                'amount': 0.0,
                'avg_entry_price': 0.0,
                'current_price': price,
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0
            })
            
            if side == OrderSide.BUY:
                # Add to position
                total_cost = (current_position['amount'] * current_position['avg_entry_price'] + 
                            amount * price)
                new_amount = current_position['amount'] + amount
                new_avg_price = total_cost / new_amount if new_amount > 0 else 0.0
                
                current_position['amount'] = new_amount
                current_position['avg_entry_price'] = new_avg_price
                
            else:  # SELL
                # Reduce position and calculate realized P&L
                sell_amount = min(amount, current_position['amount'])
                realized_pnl = sell_amount * (price - current_position['avg_entry_price'])
                
                current_position['amount'] -= sell_amount
                current_position['realized_pnl'] += realized_pnl
                
                # If position is closed, reset avg entry price
                if current_position['amount'] <= 0.001:  # Close enough to zero
                    current_position['amount'] = 0.0
                    current_position['avg_entry_price'] = 0.0
            
            current_position['current_price'] = price
            self.positions[symbol] = current_position
            
            # Update database
            self._save_position(symbol, current_position)
            
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
    
    def _save_position(self, symbol: str, position: Dict[str, float]):
        """Save position to database
        
        Args:
            symbol: Trading symbol
            position: Position data
        """
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO positions 
                    (symbol, pair, amount, avg_entry_price, current_price, 
                     unrealized_pnl, realized_pnl, exchange, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (symbol, symbol, position['amount'], position['avg_entry_price'],
                     position['current_price'], position['unrealized_pnl'],
                     position['realized_pnl'], self.exchange))
        except Exception as e:
            logger.error(f"Failed to save position: {e}")
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current position for symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position data or None
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all current positions
        
        Returns:
            Dictionary of all positions
        """
        return self.positions.copy()
    
    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trade history
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of trades to return
            
        Returns:
            List of trades
        """
        try:
            with get_db_connection(self.db_name) as conn:
                cursor = conn.cursor()
                
                if symbol:
                    cursor.execute("""
                        SELECT * FROM trades 
                        WHERE symbol = ? AND exchange = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (symbol, self.exchange, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM trades 
                        WHERE exchange = ?
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (self.exchange, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get trade history: {e}")
            return []
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response
        
        Args:
            message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            'status': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_portfolio_value(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate total portfolio value
        
        Args:
            current_prices: Optional dict of current prices
            
        Returns:
            Portfolio value summary
        """
        total_value = 0.0
        total_pnl = 0.0
        
        for symbol, position in self.positions.items():
            if position['amount'] > 0:
                current_price = (current_prices.get(symbol) if current_prices 
                               else self._get_market_price(symbol))
                
                position_value = position['amount'] * current_price
                unrealized_pnl = position['amount'] * (current_price - position['avg_entry_price'])
                
                total_value += position_value
                total_pnl += unrealized_pnl + position['realized_pnl']
        
        return {
            'total_value': total_value,
            'total_pnl': total_pnl,
            'num_positions': len([p for p in self.positions.values() if p['amount'] > 0]),
            'positions': self.positions,
            'timestamp': datetime.now().isoformat()
        }


# Global trading engine instance
trading_engine = TradingEngine()
