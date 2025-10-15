#!/usr/bin/env python3
"""TPS19 Unified Trading Engine - Comprehensive Trading System"""

import json
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
import sys
from enum import Enum

# Add exchanges module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'exchanges'))

try:
    from exchanges.crypto_com_api import crypto_com_api
    from exchanges.alpha_vantage_api import alpha_vantage_api
except ImportError as e:
    print(f"⚠️ Exchange modules not available: {e}")
    crypto_com_api = None
    alpha_vantage_api = None

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"

class TradingMode(Enum):
    SIMULATION = "SIMULATION"
    LIVE = "LIVE"
    PAPER = "PAPER"

class UnifiedTradingEngine:
    """Unified Trading Engine for TPS19 Crypto Trading System"""
    
    def __init__(self, mode: TradingMode = TradingMode.SIMULATION):
        self.mode = mode
        self.db_path = "/workspace/data/databases/trading_engine.db"
        self.portfolio = {}
        self.orders = {}
        self.positions = {}
        self.balance = 10000.0  # Starting balance
        self.commission_rate = 0.001  # 0.1% commission
        self.slippage_rate = 0.0005  # 0.05% slippage
        self.lock = threading.Lock()
        
        self._init_database()
        self._load_portfolio()
        
    def _init_database(self):
        """Initialize trading engine database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Orders table
            cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL,
                stop_price REAL,
                status TEXT NOT NULL,
                filled_quantity REAL DEFAULT 0,
                average_price REAL,
                commission REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )""")
            
            # Positions table
            cursor.execute("""CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )""")
            
            # Portfolio table
            cursor.execute("""CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                current_price REAL,
                total_value REAL,
                unrealized_pnl REAL DEFAULT 0,
                realized_pnl REAL DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            # Trade history table
            cursor.execute("""CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                commission REAL NOT NULL,
                pnl REAL DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                exchange TEXT DEFAULT 'crypto.com'
            )""")
            
            conn.commit()
            conn.close()
            print("✅ Trading Engine database initialized")
            
        except Exception as e:
            print(f"❌ Trading Engine database initialization failed: {e}")
    
    def _load_portfolio(self):
        """Load portfolio from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load positions
            cursor.execute("SELECT symbol, quantity, average_price FROM positions")
            positions = cursor.fetchall()
            
            for symbol, quantity, avg_price in positions:
                self.positions[symbol] = {
                    'quantity': quantity,
                    'average_price': avg_price,
                    'unrealized_pnl': 0,
                    'realized_pnl': 0
                }
            
            # Load portfolio
            cursor.execute("SELECT asset, quantity, average_price FROM portfolio")
            portfolio = cursor.fetchall()
            
            for asset, quantity, avg_price in portfolio:
                self.portfolio[asset] = {
                    'quantity': quantity,
                    'average_price': avg_price,
                    'current_price': 0,
                    'total_value': 0,
                    'unrealized_pnl': 0,
                    'realized_pnl': 0
                }
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Failed to load portfolio: {e}")
    
    def place_order(self, symbol: str, side: OrderSide, quantity: float, 
                   order_type: OrderType = OrderType.MARKET, price: float = None, 
                   stop_price: float = None) -> Dict:
        """Place a trading order"""
        try:
            with self.lock:
                order_id = f"tps19_{int(time.time() * 1000)}"
                
                # Validate order
                if not self._validate_order(symbol, side, quantity, order_type, price):
                    return {'success': False, 'error': 'Invalid order parameters'}
                
                # Create order
                order = {
                    'order_id': order_id,
                    'symbol': symbol,
                    'side': side.value,
                    'order_type': order_type.value,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'status': OrderStatus.PENDING.value,
                    'filled_quantity': 0,
                    'average_price': 0,
                    'commission': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'exchange': 'crypto.com'
                }
                
                # Store order in database
                self._store_order(order)
                
                # Process order based on mode
                if self.mode == TradingMode.SIMULATION:
                    result = self._process_simulation_order(order)
                elif self.mode == TradingMode.LIVE:
                    result = self._process_live_order(order)
                else:  # PAPER
                    result = self._process_paper_order(order)
                
                return result
                
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_order(self, symbol: str, side: OrderSide, quantity: float, 
                       order_type: OrderType, price: float = None) -> bool:
        """Validate order parameters"""
        try:
            # Check quantity
            if quantity <= 0:
                return False
            
            # Check price for limit orders
            if order_type == OrderType.LIMIT and (price is None or price <= 0):
                return False
            
            # Check balance for buy orders
            if side == OrderSide.BUY:
                required_balance = quantity * (price or self._get_current_price(symbol))
                if required_balance > self.balance:
                    return False
            
            # Check position for sell orders
            if side == OrderSide.SELL:
                current_position = self.positions.get(symbol, {}).get('quantity', 0)
                if quantity > current_position:
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Order validation error: {e}")
            return False
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            if crypto_com_api:
                ticker_data = crypto_com_api.get_ticker(symbol)
                if ticker_data and 'price' in ticker_data:
                    return ticker_data['price']
            
            # Fallback to mock price
            return 50000.0 + (time.time() % 1000)
            
        except Exception as e:
            print(f"❌ Error getting current price: {e}")
            return 50000.0
    
    def _process_simulation_order(self, order: Dict) -> Dict:
        """Process order in simulation mode"""
        try:
            symbol = order['symbol']
            side = order['side']
            quantity = order['quantity']
            order_type = order['order_type']
            price = order['price']
            
            # Get current price
            current_price = self._get_current_price(symbol)
            
            # Calculate execution price
            if order_type == OrderType.MARKET.value:
                execution_price = current_price
            else:  # LIMIT
                execution_price = price if price else current_price
            
            # Apply slippage
            slippage = execution_price * self.slippage_rate
            if side == OrderSide.BUY.value:
                execution_price += slippage
            else:
                execution_price -= slippage
            
            # Calculate commission
            commission = execution_price * quantity * self.commission_rate
            
            # Calculate total cost
            total_cost = execution_price * quantity + commission
            
            # Check if we can execute
            if side == OrderSide.BUY.value and total_cost > self.balance:
                order['status'] = OrderStatus.REJECTED.value
                order['updated_at'] = datetime.now().isoformat()
                self._update_order(order)
                return {'success': False, 'error': 'Insufficient balance'}
            
            # Execute order
            order['status'] = OrderStatus.FILLED.value
            order['filled_quantity'] = quantity
            order['average_price'] = execution_price
            order['commission'] = commission
            order['updated_at'] = datetime.now().isoformat()
            
            # Update balance and positions
            if side == OrderSide.BUY.value:
                self.balance -= total_cost
                self._update_position(symbol, quantity, execution_price, 'BUY')
            else:
                self.balance += total_cost
                self._update_position(symbol, quantity, execution_price, 'SELL')
            
            # Update order in database
            self._update_order(order)
            
            # Record trade
            self._record_trade(order, execution_price)
            
            return {
                'success': True,
                'order_id': order['order_id'],
                'status': order['status'],
                'filled_quantity': order['filled_quantity'],
                'average_price': order['average_price'],
                'commission': order['commission']
            }
            
        except Exception as e:
            print(f"❌ Simulation order processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_live_order(self, order: Dict) -> Dict:
        """Process order in live mode"""
        try:
            if not crypto_com_api:
                return {'success': False, 'error': 'Crypto.com API not available'}
            
            symbol = order['symbol']
            side = order['side']
            quantity = order['quantity']
            order_type = order['order_type']
            price = order['price']
            
            # Place order on exchange
            if order_type == OrderType.MARKET.value:
                result = crypto_com_api.place_order(symbol, side, quantity)
            else:  # LIMIT
                result = crypto_com_api.place_order(symbol, side, quantity, price, order_type)
            
            if result and 'order_id' in result:
                order['status'] = OrderStatus.PENDING.value
                order['exchange_order_id'] = result['order_id']
                self._update_order(order)
                
                return {
                    'success': True,
                    'order_id': order['order_id'],
                    'exchange_order_id': result['order_id'],
                    'status': order['status']
                }
            else:
                order['status'] = OrderStatus.REJECTED.value
                self._update_order(order)
                return {'success': False, 'error': 'Order rejected by exchange'}
                
        except Exception as e:
            print(f"❌ Live order processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_paper_order(self, order: Dict) -> Dict:
        """Process order in paper trading mode"""
        # Similar to simulation but with more realistic delays and conditions
        return self._process_simulation_order(order)
    
    def _update_position(self, symbol: str, quantity: float, price: float, side: str):
        """Update position after trade execution"""
        try:
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'quantity': 0,
                    'average_price': 0,
                    'unrealized_pnl': 0,
                    'realized_pnl': 0
                }
            
            current_pos = self.positions[symbol]
            
            if side == 'BUY':
                if current_pos['quantity'] == 0:
                    # New position
                    current_pos['quantity'] = quantity
                    current_pos['average_price'] = price
                else:
                    # Add to existing position
                    total_quantity = current_pos['quantity'] + quantity
                    total_value = (current_pos['quantity'] * current_pos['average_price']) + (quantity * price)
                    current_pos['average_price'] = total_value / total_quantity
                    current_pos['quantity'] = total_quantity
            else:  # SELL
                if current_pos['quantity'] >= quantity:
                    # Calculate realized P&L
                    realized_pnl = (price - current_pos['average_price']) * quantity
                    current_pos['realized_pnl'] += realized_pnl
                    current_pos['quantity'] -= quantity
                    
                    if current_pos['quantity'] == 0:
                        # Position closed
                        del self.positions[symbol]
                else:
                    print(f"⚠️ Attempting to sell more than owned: {quantity} > {current_pos['quantity']}")
            
            # Update database
            self._update_position_in_db(symbol, current_pos)
            
        except Exception as e:
            print(f"❌ Position update error: {e}")
    
    def _update_position_in_db(self, symbol: str, position: Dict):
        """Update position in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if position['quantity'] > 0:
                cursor.execute("""INSERT OR REPLACE INTO positions 
                    (symbol, quantity, average_price, unrealized_pnl, realized_pnl, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (symbol, position['quantity'], position['average_price'],
                     position['unrealized_pnl'], position['realized_pnl'], datetime.now().isoformat()))
            else:
                cursor.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Database position update error: {e}")
    
    def _store_order(self, order: Dict):
        """Store order in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO orders 
                (order_id, symbol, side, order_type, quantity, price, stop_price, status, 
                 filled_quantity, average_price, commission, created_at, updated_at, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order['order_id'], order['symbol'], order['side'], order['order_type'],
                 order['quantity'], order['price'], order['stop_price'], order['status'],
                 order['filled_quantity'], order['average_price'], order['commission'],
                 order['created_at'], order['updated_at'], order['exchange']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Order storage error: {e}")
    
    def _update_order(self, order: Dict):
        """Update order in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""UPDATE orders SET 
                status = ?, filled_quantity = ?, average_price = ?, commission = ?, updated_at = ?
                WHERE order_id = ?""",
                (order['status'], order['filled_quantity'], order['average_price'],
                 order['commission'], order['updated_at'], order['order_id']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Order update error: {e}")
    
    def _record_trade(self, order: Dict, execution_price: float):
        """Record trade in history"""
        try:
            trade_id = f"trade_{int(time.time() * 1000)}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO trade_history 
                (trade_id, order_id, symbol, side, quantity, price, commission, timestamp, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (trade_id, order['order_id'], order['symbol'], order['side'],
                 order['filled_quantity'], execution_price, order['commission'],
                 datetime.now().isoformat(), order['exchange']))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Trade recording error: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        try:
            total_value = self.balance
            total_unrealized_pnl = 0
            total_realized_pnl = 0
            
            for symbol, position in self.positions.items():
                current_price = self._get_current_price(symbol)
                position_value = position['quantity'] * current_price
                unrealized_pnl = (current_price - position['average_price']) * position['quantity']
                
                total_value += position_value
                total_unrealized_pnl += unrealized_pnl
                total_realized_pnl += position['realized_pnl']
            
            return {
                'balance': self.balance,
                'total_value': total_value,
                'total_unrealized_pnl': total_unrealized_pnl,
                'total_realized_pnl': total_realized_pnl,
                'total_pnl': total_unrealized_pnl + total_realized_pnl,
                'positions': len(self.positions),
                'mode': self.mode.value
            }
            
        except Exception as e:
            print(f"❌ Portfolio summary error: {e}")
            return {}
    
    def get_open_orders(self) -> List[Dict]:
        """Get all open orders"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""SELECT * FROM orders 
                WHERE status IN ('PENDING', 'PARTIALLY_FILLED')
                ORDER BY created_at DESC""")
            
            orders = cursor.fetchall()
            conn.close()
            
            return [dict(zip([col[0] for col in cursor.description], order)) for order in orders]
            
        except Exception as e:
            print(f"❌ Get open orders error: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        try:
            if self.mode == TradingMode.LIVE and crypto_com_api:
                # Cancel on exchange
                result = crypto_com_api.cancel_order(order_id)
                if not result:
                    return {'success': False, 'error': 'Failed to cancel on exchange'}
            
            # Update order status
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""UPDATE orders SET 
                status = ?, updated_at = ?
                WHERE order_id = ?""",
                (OrderStatus.CANCELLED.value, datetime.now().isoformat(), order_id))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'order_id': order_id}
            
        except Exception as e:
            print(f"❌ Cancel order error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_trading_engine(self) -> bool:
        """Test trading engine functionality"""
        try:
            print("🧪 Testing Trading Engine...")
            
            # Test order placement
            result = self.place_order("BTC_USDT", OrderSide.BUY, 0.001, OrderType.MARKET)
            if not result.get('success'):
                print("❌ Order placement test failed")
                return False
            
            # Test portfolio summary
            portfolio = self.get_portfolio_summary()
            if not portfolio:
                print("❌ Portfolio summary test failed")
                return False
            
            # Test order cancellation
            cancel_result = self.cancel_order(result['order_id'])
            if not cancel_result.get('success'):
                print("❌ Order cancellation test failed")
                return False
            
            print("✅ Trading Engine test passed")
            return True
            
        except Exception as e:
            print(f"❌ Trading Engine test error: {e}")
            return False

# Global instance
trading_engine = UnifiedTradingEngine()
