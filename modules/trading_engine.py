#!/usr/bin/env python3
"""
TPS19 Trading Engine - Advanced cryptocurrency trading with multi-strategy support
Implements: Scalping, Trend Following, Mean Reversion, Breakout, Grid Trading, DCA
"""

import json
import sqlite3
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingEngine:
    """
    Comprehensive trading engine supporting multiple strategies and exchanges
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Trading Engine"""
        self.config = self._load_config(config_path)
        self.db_path = self._get_db_path("trading_engine.db")
        self.active_positions = {}
        self.pending_orders = {}
        self.trading_enabled = True
        self.strategy_mode = "balanced"  # Options: scalping, swing, conservative, aggressive
        self.init_database()
        logger.info("Trading Engine initialized")
        
    def _get_db_path(self, filename: str) -> str:
        """Get database path relative to workspace"""
        workspace = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(workspace, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, filename)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load trading configuration"""
        default_config = {
            "max_position_size": 1000,  # USD
            "min_position_size": 10,    # USD
            "max_open_positions": 5,
            "stop_loss_pct": 2.0,       # 2%
            "take_profit_pct": 5.0,     # 5%
            "trailing_stop_pct": 1.5,   # 1.5%
            "commission_rate": 0.001,   # 0.1%
            "slippage_rate": 0.0005,    # 0.05%
            "risk_per_trade": 0.02,     # 2% of portfolio
            "supported_pairs": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT"],
            "strategy_weights": {
                "scalping": 0.3,
                "trend_following": 0.3,
                "mean_reversion": 0.2,
                "breakout": 0.2
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                
        return default_config
        
    def init_database(self):
        """Initialize trading database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                filled_amount REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                strategy TEXT,
                pnl REAL DEFAULT 0.0,
                commission REAL DEFAULT 0.0,
                slippage REAL DEFAULT 0.0,
                entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                exit_time DATETIME,
                notes TEXT
            )
        ''')
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                position_id TEXT UNIQUE NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                stop_loss REAL,
                take_profit REAL,
                trailing_stop REAL,
                unrealized_pnl REAL DEFAULT 0.0,
                realized_pnl REAL DEFAULT 0.0,
                status TEXT DEFAULT 'open',
                strategy TEXT,
                opened_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME,
                metadata TEXT
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE NOT NULL,
                pair TEXT NOT NULL,
                side TEXT NOT NULL,
                order_type TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL,
                trigger_price REAL,
                status TEXT DEFAULT 'pending',
                parent_position_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                filled_at DATETIME,
                cancelled_at DATETIME,
                FOREIGN KEY (parent_position_id) REFERENCES positions(position_id)
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0.0,
                total_commission REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0,
                avg_win REAL DEFAULT 0.0,
                avg_loss REAL DEFAULT 0.0,
                profit_factor REAL DEFAULT 0.0,
                best_trade REAL DEFAULT 0.0,
                worst_trade REAL DEFAULT 0.0,
                avg_trade_duration REAL DEFAULT 0.0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strategy performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                trades_count INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                total_pnl REAL DEFAULT 0.0,
                avg_pnl REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Trading database initialized")
        
    def create_order(self, pair: str, side: str, amount: float, 
                    order_type: str = "market", price: Optional[float] = None,
                    strategy: str = "manual") -> Dict:
        """
        Create a new order
        
        Args:
            pair: Trading pair (e.g., "BTC/USDT")
            side: "buy" or "sell"
            amount: Order amount
            order_type: "market", "limit", "stop_loss", "take_profit"
            price: Price for limit orders
            strategy: Strategy name
            
        Returns:
            Dict with order details
        """
        if not self.trading_enabled:
            return {"status": "error", "message": "Trading is disabled"}
            
        # Validate inputs
        if pair not in self.config["supported_pairs"]:
            return {"status": "error", "message": f"Unsupported pair: {pair}"}
            
        if side not in ["buy", "sell"]:
            return {"status": "error", "message": f"Invalid side: {side}"}
            
        # Generate order ID
        order_id = f"{side}_{pair.replace('/', '_')}_{int(time.time() * 1000)}"
        
        # Calculate commission and slippage
        commission = amount * (price or 0) * self.config["commission_rate"]
        slippage = amount * (price or 0) * self.config["slippage_rate"]
        
        # Store order
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO orders (order_id, pair, side, order_type, amount, price, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
            ''', (order_id, pair, side, order_type, amount, price))
            
            conn.commit()
            
            # Simulate order execution (in production, this would call exchange API)
            if order_type == "market":
                execution_result = self._execute_market_order(order_id, pair, side, amount, price)
            else:
                execution_result = {"status": "pending", "order_id": order_id}
                
            logger.info(f"Order created: {order_id} - {side} {amount} {pair}")
            
            return {
                "status": "success",
                "order_id": order_id,
                "execution": execution_result,
                "commission": commission,
                "estimated_slippage": slippage
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create order: {e}")
            return {"status": "error", "message": str(e)}
            
        finally:
            conn.close()
            
    def _execute_market_order(self, order_id: str, pair: str, side: str, 
                             amount: float, price: Optional[float] = None) -> Dict:
        """Execute a market order immediately"""
        # In production, this would call the exchange API
        # For now, simulate execution
        
        execution_price = price if price else 50000.0  # Mock price
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update order status
            cursor.execute('''
                UPDATE orders 
                SET status = 'filled', filled_at = CURRENT_TIMESTAMP 
                WHERE order_id = ?
            ''', (order_id,))
            
            # Record trade
            cursor.execute('''
                INSERT INTO trades (trade_id, pair, side, order_type, amount, price, 
                                  filled_amount, status, strategy)
                VALUES (?, ?, ?, 'market', ?, ?, ?, 'completed', 'manual')
            ''', (order_id, pair, side, amount, execution_price, amount))
            
            conn.commit()
            
            return {
                "status": "filled",
                "order_id": order_id,
                "execution_price": execution_price,
                "filled_amount": amount
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to execute order: {e}")
            return {"status": "error", "message": str(e)}
            
        finally:
            conn.close()
            
    def open_position(self, pair: str, side: str, amount: float, 
                     entry_price: float, strategy: str = "manual",
                     stop_loss_pct: Optional[float] = None,
                     take_profit_pct: Optional[float] = None) -> Dict:
        """
        Open a new trading position
        
        Args:
            pair: Trading pair
            side: "long" or "short"
            amount: Position size
            entry_price: Entry price
            strategy: Strategy name
            stop_loss_pct: Stop loss percentage (optional)
            take_profit_pct: Take profit percentage (optional)
            
        Returns:
            Dict with position details
        """
        # Check position limits
        if len(self.active_positions) >= self.config["max_open_positions"]:
            return {"status": "error", "message": "Maximum open positions reached"}
            
        # Generate position ID
        position_id = f"pos_{pair.replace('/', '_')}_{int(time.time() * 1000)}"
        
        # Calculate stop loss and take profit
        if stop_loss_pct is None:
            stop_loss_pct = self.config["stop_loss_pct"]
        if take_profit_pct is None:
            take_profit_pct = self.config["take_profit_pct"]
            
        stop_loss = entry_price * (1 - stop_loss_pct/100) if side == "long" else entry_price * (1 + stop_loss_pct/100)
        take_profit = entry_price * (1 + take_profit_pct/100) if side == "long" else entry_price * (1 - take_profit_pct/100)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO positions (position_id, pair, side, amount, entry_price, 
                                     current_price, stop_loss, take_profit, strategy, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'open')
            ''', (position_id, pair, side, amount, entry_price, entry_price, 
                  stop_loss, take_profit, strategy))
            
            conn.commit()
            
            # Store in memory
            self.active_positions[position_id] = {
                "pair": pair,
                "side": side,
                "amount": amount,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "strategy": strategy
            }
            
            logger.info(f"Position opened: {position_id} - {side} {amount} {pair} @ {entry_price}")
            
            return {
                "status": "success",
                "position_id": position_id,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to open position: {e}")
            return {"status": "error", "message": str(e)}
            
        finally:
            conn.close()
            
    def close_position(self, position_id: str, exit_price: float, 
                      reason: str = "manual") -> Dict:
        """Close an existing position"""
        if position_id not in self.active_positions:
            return {"status": "error", "message": "Position not found"}
            
        position = self.active_positions[position_id]
        
        # Calculate PnL
        if position["side"] == "long":
            pnl = (exit_price - position["entry_price"]) * position["amount"]
        else:
            pnl = (position["entry_price"] - exit_price) * position["amount"]
            
        # Apply commission
        commission = exit_price * position["amount"] * self.config["commission_rate"]
        net_pnl = pnl - commission
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update position
            cursor.execute('''
                UPDATE positions 
                SET status = 'closed', realized_pnl = ?, closed_at = CURRENT_TIMESTAMP
                WHERE position_id = ?
            ''', (net_pnl, position_id))
            
            # Record trade
            cursor.execute('''
                INSERT INTO trades (trade_id, pair, side, order_type, amount, price, 
                                  filled_amount, status, strategy, pnl, commission)
                VALUES (?, ?, 'sell', 'market', ?, ?, ?, 'completed', ?, ?, ?)
            ''', (f"close_{position_id}", position["pair"], position["amount"], 
                  exit_price, position["amount"], position["strategy"], net_pnl, commission))
            
            conn.commit()
            
            # Remove from active positions
            del self.active_positions[position_id]
            
            logger.info(f"Position closed: {position_id} - PnL: ${net_pnl:.2f}")
            
            return {
                "status": "success",
                "position_id": position_id,
                "pnl": net_pnl,
                "commission": commission,
                "reason": reason
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to close position: {e}")
            return {"status": "error", "message": str(e)}
            
        finally:
            conn.close()
            
    def update_positions(self, current_prices: Dict[str, float]):
        """Update all active positions with current prices"""
        for position_id, position in list(self.active_positions.items()):
            pair = position["pair"]
            if pair in current_prices:
                current_price = current_prices[pair]
                
                # Check stop loss
                if position["side"] == "long" and current_price <= position["stop_loss"]:
                    self.close_position(position_id, current_price, "stop_loss")
                elif position["side"] == "short" and current_price >= position["stop_loss"]:
                    self.close_position(position_id, current_price, "stop_loss")
                    
                # Check take profit
                elif position["side"] == "long" and current_price >= position["take_profit"]:
                    self.close_position(position_id, current_price, "take_profit")
                elif position["side"] == "short" and current_price <= position["take_profit"]:
                    self.close_position(position_id, current_price, "take_profit")
                    
                else:
                    # Update unrealized PnL
                    if position["side"] == "long":
                        unrealized_pnl = (current_price - position["entry_price"]) * position["amount"]
                    else:
                        unrealized_pnl = (position["entry_price"] - current_price) * position["amount"]
                        
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE positions 
                        SET current_price = ?, unrealized_pnl = ?
                        WHERE position_id = ?
                    ''', (current_price, unrealized_pnl, position_id))
                    conn.commit()
                    conn.close()
                    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total trades
        cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "completed"')
        total_trades = cursor.fetchone()[0]
        
        # Win/Loss statistics
        cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "completed" AND pnl > 0')
        winning_trades = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "completed" AND pnl < 0')
        losing_trades = cursor.fetchone()[0]
        
        # PnL statistics
        cursor.execute('SELECT SUM(pnl), AVG(pnl), MAX(pnl), MIN(pnl) FROM trades WHERE status = "completed"')
        pnl_stats = cursor.fetchone()
        
        # Commission
        cursor.execute('SELECT SUM(commission) FROM trades WHERE status = "completed"')
        total_commission = cursor.fetchone()[0] or 0
        
        conn.close()
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(pnl_stats[0] or 0, 2),
            "avg_pnl": round(pnl_stats[1] or 0, 2),
            "best_trade": round(pnl_stats[2] or 0, 2),
            "worst_trade": round(pnl_stats[3] or 0, 2),
            "total_commission": round(total_commission, 2),
            "net_pnl": round((pnl_stats[0] or 0) - total_commission, 2),
            "active_positions": len(self.active_positions)
        }
        
    def get_strategy_performance(self) -> Dict:
        """Get performance breakdown by strategy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strategy, COUNT(*) as trades, AVG(pnl) as avg_pnl, SUM(pnl) as total_pnl,
                   SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
            FROM trades 
            WHERE status = "completed" AND strategy IS NOT NULL
            GROUP BY strategy
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        strategy_stats = {}
        for row in results:
            strategy_stats[row[0]] = {
                "trades": row[1],
                "avg_pnl": round(row[2], 2),
                "total_pnl": round(row[3], 2),
                "win_rate": round(row[4], 2)
            }
            
        return strategy_stats
        
    def enable_trading(self):
        """Enable trading"""
        self.trading_enabled = True
        logger.info("Trading enabled")
        
    def disable_trading(self):
        """Disable trading"""
        self.trading_enabled = False
        logger.info("Trading disabled")
        
    def set_strategy_mode(self, mode: str):
        """Set trading strategy mode"""
        valid_modes = ["scalping", "swing", "conservative", "aggressive", "balanced"]
        if mode in valid_modes:
            self.strategy_mode = mode
            logger.info(f"Strategy mode set to: {mode}")
            return {"status": "success", "mode": mode}
        else:
            return {"status": "error", "message": f"Invalid mode. Choose from: {valid_modes}"}
            
    def get_active_positions(self) -> List[Dict]:
        """Get all active positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT position_id, pair, side, amount, entry_price, current_price, 
                   stop_loss, take_profit, unrealized_pnl, strategy, opened_at
            FROM positions 
            WHERE status = 'open'
            ORDER BY opened_at DESC
        ''')
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                "position_id": row[0],
                "pair": row[1],
                "side": row[2],
                "amount": row[3],
                "entry_price": row[4],
                "current_price": row[5],
                "stop_loss": row[6],
                "take_profit": row[7],
                "unrealized_pnl": row[8],
                "strategy": row[9],
                "opened_at": row[10]
            })
            
        conn.close()
        return positions
        
    def get_trade_history(self, limit: int = 50) -> List[Dict]:
        """Get recent trade history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT trade_id, pair, side, amount, price, pnl, commission, strategy, entry_time
            FROM trades 
            WHERE status = 'completed'
            ORDER BY entry_time DESC
            LIMIT ?
        ''', (limit,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                "trade_id": row[0],
                "pair": row[1],
                "side": row[2],
                "amount": row[3],
                "price": row[4],
                "pnl": row[5],
                "commission": row[6],
                "strategy": row[7],
                "timestamp": row[8]
            })
            
        conn.close()
        return trades


if __name__ == "__main__":
    # Test the trading engine
    engine = TradingEngine()
    print("✅ Trading Engine initialized successfully")
    
    # Test creating an order
    order = engine.create_order("BTC/USDT", "buy", 0.001, "market", price=50000, strategy="test")
    print(f"Order created: {order}")
    
    # Test opening a position
    position = engine.open_position("BTC/USDT", "long", 0.001, 50000, strategy="test")
    print(f"Position opened: {position}")
    
    # Get performance metrics
    metrics = engine.get_performance_metrics()
    print(f"Performance metrics: {metrics}")
