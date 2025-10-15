"""
Backtesting Engine
Comprehensive backtesting framework for trading strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from core.logging_config import get_logger
from simulation.market_simulator import MarketSimulator, MarketCondition


logger = get_logger(__name__)


class OrderType(Enum):
    """Order types for backtesting"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class BacktestOrder:
    """Order in backtesting"""
    order_id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: OrderType
    quantity: float
    price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None  # For stop orders
    timestamp: datetime = field(default_factory=datetime.now)
    filled: bool = False
    fill_price: Optional[float] = None
    fill_timestamp: Optional[datetime] = None
    commission: float = 0.0


@dataclass
class Position:
    """Trading position"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


@dataclass
class BacktestResult:
    """Complete backtest results"""
    # Performance metrics
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_duration: timedelta
    
    # Trade statistics
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    avg_trade_duration: timedelta
    
    # Financial metrics
    initial_capital: float
    final_capital: float
    total_commission: float
    net_profit: float
    
    # Time series data
    equity_curve: List[Dict[str, Any]]
    trade_log: List[Dict[str, Any]]
    daily_returns: List[float]
    
    # Additional metrics
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    trades_per_day: float = 0.0
    exposure_time: float = 0.0  # Percentage of time in market


class BacktestingEngine:
    """
    Comprehensive backtesting engine with:
    - Multiple order types
    - Realistic commission and slippage
    - Position tracking
    - Performance metrics
    - Risk management
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,  # 0.1%
        slippage_rate: float = 0.0005,   # 0.05%
        max_positions: int = 5,
        max_position_size: float = 0.2    # 20% of capital per position
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.max_positions = max_positions
        self.max_position_size = max_position_size
        
        # State tracking
        self.positions: Dict[str, Position] = {}
        self.orders: List[BacktestOrder] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.peak_equity = initial_capital
        self.max_drawdown = 0.0
        self.drawdown_start = None
        self.max_drawdown_duration = timedelta(0)
        
        # Market simulator
        self.market_simulator = None
        
        logger.info("Backtesting engine initialized", extra={
            "initial_capital": initial_capital,
            "commission_rate": commission_rate,
            "max_positions": max_positions
        })
    
    def set_market_simulator(self, simulator: MarketSimulator):
        """Set the market simulator to use"""
        self.market_simulator = simulator
    
    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> BacktestOrder:
        """
        Place an order in the backtesting system
        
        Args:
            symbol: Asset symbol
            side: "buy" or "sell"
            quantity: Order quantity
            order_type: Type of order
            price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            
        Returns:
            BacktestOrder object
        """
        order = BacktestOrder(
            order_id=f"ORDER_{len(self.orders)}_{int(datetime.now().timestamp())}",
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        self.orders.append(order)
        
        # Execute market orders immediately
        if order_type == OrderType.MARKET:
            self._execute_order(order)
        
        return order
    
    def _execute_order(self, order: BacktestOrder):
        """Execute an order"""
        if not self.market_simulator:
            logger.error("No market simulator set")
            return
        
        current_prices = self.market_simulator.current_prices
        current_price = current_prices.get(order.symbol, 0)
        
        if current_price == 0:
            logger.error(f"No price available for {order.symbol}")
            return
        
        # Apply slippage
        if order.side == "buy":
            fill_price = current_price * (1 + self.slippage_rate)
        else:
            fill_price = current_price * (1 - self.slippage_rate)
        
        # Calculate commission
        commission = order.quantity * fill_price * self.commission_rate
        
        # Check if we have enough capital for buy orders
        if order.side == "buy":
            required_capital = order.quantity * fill_price + commission
            if required_capital > self.current_capital:
                logger.warning(f"Insufficient capital for order: required {required_capital}, available {self.current_capital}")
                return
        
        # Execute the order
        order.filled = True
        order.fill_price = fill_price
        order.fill_timestamp = datetime.now()
        order.commission = commission
        
        # Update positions
        if order.side == "buy":
            self._open_position(order)
        else:
            self._close_position(order)
        
        # Record trade
        trade = {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side,
            "quantity": order.quantity,
            "fill_price": fill_price,
            "commission": commission,
            "timestamp": order.fill_timestamp,
            "capital_after": self.current_capital
        }
        self.trade_history.append(trade)
        
        logger.info(f"Order executed: {order.side} {order.quantity} {order.symbol} @ {fill_price:.2f}")
    
    def _open_position(self, order: BacktestOrder):
        """Open a new position"""
        if order.symbol in self.positions:
            # Add to existing position (averaging)
            position = self.positions[order.symbol]
            total_quantity = position.quantity + order.quantity
            position.entry_price = (
                (position.entry_price * position.quantity + order.fill_price * order.quantity) / 
                total_quantity
            )
            position.quantity = total_quantity
        else:
            # Create new position
            self.positions[order.symbol] = Position(
                symbol=order.symbol,
                quantity=order.quantity,
                entry_price=order.fill_price,
                entry_time=order.fill_timestamp,
                current_price=order.fill_price
            )
        
        # Update capital
        self.current_capital -= (order.quantity * order.fill_price + order.commission)
    
    def _close_position(self, order: BacktestOrder):
        """Close or reduce a position"""
        if order.symbol not in self.positions:
            logger.warning(f"No position to close for {order.symbol}")
            return
        
        position = self.positions[order.symbol]
        
        # Calculate P&L
        pnl = order.quantity * (order.fill_price - position.entry_price)
        
        # Update position
        if order.quantity >= position.quantity:
            # Close entire position
            position.realized_pnl += pnl
            self.positions.pop(order.symbol)
        else:
            # Partial close
            position.quantity -= order.quantity
            position.realized_pnl += pnl
        
        # Update capital
        self.current_capital += (order.quantity * order.fill_price - order.commission)
    
    def update_positions(self):
        """Update position values with current prices"""
        if not self.market_simulator:
            return
        
        current_prices = self.market_simulator.current_prices
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position.current_price = current_prices[symbol]
                position.unrealized_pnl = position.quantity * (position.current_price - position.entry_price)
    
    def check_pending_orders(self):
        """Check and execute pending orders based on current prices"""
        if not self.market_simulator:
            return
        
        current_prices = self.market_simulator.current_prices
        
        for order in self.orders:
            if order.filled:
                continue
            
            current_price = current_prices.get(order.symbol, 0)
            if current_price == 0:
                continue
            
            # Check limit orders
            if order.order_type == OrderType.LIMIT and order.price:
                if order.side == "buy" and current_price <= order.price:
                    self._execute_order(order)
                elif order.side == "sell" and current_price >= order.price:
                    self._execute_order(order)
            
            # Check stop orders
            elif order.order_type == OrderType.STOP_LOSS and order.stop_price:
                if order.side == "sell" and current_price <= order.stop_price:
                    self._execute_order(order)
    
    def calculate_equity(self) -> float:
        """Calculate current total equity"""
        equity = self.current_capital
        
        # Add unrealized P&L from open positions
        for position in self.positions.values():
            equity += position.quantity * position.current_price
        
        return equity
    
    def record_equity_snapshot(self, timestamp: datetime):
        """Record current equity state"""
        equity = self.calculate_equity()
        
        # Update drawdown
        if equity > self.peak_equity:
            self.peak_equity = equity
            if self.drawdown_start:
                duration = timestamp - self.drawdown_start
                if duration > self.max_drawdown_duration:
                    self.max_drawdown_duration = duration
            self.drawdown_start = None
        else:
            drawdown = (self.peak_equity - equity) / self.peak_equity
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
            if not self.drawdown_start:
                self.drawdown_start = timestamp
        
        # Record snapshot
        snapshot = {
            "timestamp": timestamp,
            "equity": equity,
            "capital": self.current_capital,
            "positions_value": equity - self.current_capital,
            "num_positions": len(self.positions),
            "drawdown": (self.peak_equity - equity) / self.peak_equity if self.peak_equity > 0 else 0
        }
        
        self.equity_curve.append(snapshot)
    
    def run_backtest(
        self,
        strategy: Callable,
        start_date: datetime,
        end_date: datetime,
        symbols: List[str],
        timeframe: str = "5m"
    ) -> BacktestResult:
        """
        Run a complete backtest
        
        Args:
            strategy: Strategy function that takes market data and returns signals
            start_date: Backtest start date
            end_date: Backtest end date
            symbols: List of symbols to trade
            timeframe: Trading timeframe
            
        Returns:
            BacktestResult with comprehensive metrics
        """
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        # Initialize market simulator if not set
        if not self.market_simulator:
            self.market_simulator = MarketSimulator()
        
        # Simulate market cycle
        duration_hours = int((end_date - start_date).total_seconds() / 3600)
        self.market_simulator.simulate_market_cycle(duration_hours)
        
        # Main backtest loop
        current_time = start_date
        update_count = 0
        
        while current_time < end_date:
            # Update market prices
            self.market_simulator.update_prices()
            
            # Update position values
            self.update_positions()
            
            # Check pending orders
            self.check_pending_orders()
            
            # Get market data for strategy
            market_data = {}
            for symbol in symbols:
                market_data[symbol] = {
                    "price": self.market_simulator.current_prices[symbol],
                    "stats": self.market_simulator.get_market_stats(symbol),
                    "order_book": self.market_simulator.get_order_book(symbol, depth=10)
                }
            
            # Get portfolio state
            portfolio_state = {
                "capital": self.current_capital,
                "equity": self.calculate_equity(),
                "positions": self.positions.copy(),
                "pending_orders": [o for o in self.orders if not o.filled]
            }
            
            # Run strategy
            signals = strategy(market_data, portfolio_state, current_time)
            
            # Process signals
            for signal in signals:
                if signal["action"] == "buy":
                    self.place_order(
                        symbol=signal["symbol"],
                        side="buy",
                        quantity=signal.get("quantity", 1.0),
                        order_type=signal.get("order_type", OrderType.MARKET),
                        price=signal.get("price"),
                        stop_price=signal.get("stop_price")
                    )
                elif signal["action"] == "sell":
                    self.place_order(
                        symbol=signal["symbol"],
                        side="sell",
                        quantity=signal.get("quantity", 1.0),
                        order_type=signal.get("order_type", OrderType.MARKET),
                        price=signal.get("price"),
                        stop_price=signal.get("stop_price")
                    )
            
            # Record equity snapshot every hour
            if update_count % 12 == 0:  # 12 * 5min = 1 hour
                self.record_equity_snapshot(current_time)
            
            # Advance time
            current_time += timedelta(minutes=5)
            update_count += 1
        
        # Calculate final metrics
        return self._calculate_results(start_date, end_date)
    
    def _calculate_results(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Calculate comprehensive backtest results"""
        # Basic metrics
        final_equity = self.calculate_equity()
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # Trade analysis
        winning_trades = [t for t in self.trade_history if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.trade_history if t.get("pnl", 0) < 0]
        
        win_rate = len(winning_trades) / len(self.trade_history) if self.trade_history else 0
        
        # Calculate average wins/losses
        avg_win = np.mean([t["pnl"] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t["pnl"]) for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(t["pnl"] for t in winning_trades)
        gross_loss = sum(abs(t["pnl"]) for t in losing_trades)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate returns series
        equity_values = [e["equity"] for e in self.equity_curve]
        if len(equity_values) > 1:
            returns = np.diff(equity_values) / equity_values[:-1]
            
            # Sharpe ratio (annualized)
            periods_per_year = 252 * 24  # Hourly snapshots
            sharpe_ratio = np.sqrt(periods_per_year) * np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
            sortino_ratio = np.sqrt(periods_per_year) * np.mean(returns) / downside_std if downside_std > 0 else 0
        else:
            sharpe_ratio = 0
            sortino_ratio = 0
            returns = []
        
        # Calmar ratio
        calmar_ratio = total_return / self.max_drawdown if self.max_drawdown > 0 else 0
        
        # Trade duration
        trade_durations = []
        for i in range(len(self.trade_history) - 1):
            duration = self.trade_history[i+1]["timestamp"] - self.trade_history[i]["timestamp"]
            trade_durations.append(duration)
        
        avg_trade_duration = sum(trade_durations, timedelta()) / len(trade_durations) if trade_durations else timedelta()
        
        # Total commission
        total_commission = sum(t["commission"] for t in self.trade_history)
        
        # Exposure time
        total_time = (end_date - start_date).total_seconds()
        time_in_market = sum(
            (e["timestamp"] - self.equity_curve[i-1]["timestamp"]).total_seconds()
            for i, e in enumerate(self.equity_curve[1:])
            if e["num_positions"] > 0
        )
        exposure_time = time_in_market / total_time if total_time > 0 else 0
        
        return BacktestResult(
            total_return=total_return,
            total_trades=len(self.trade_history),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=self.max_drawdown,
            max_drawdown_duration=self.max_drawdown_duration,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=max([t.get("pnl", 0) for t in self.trade_history], default=0),
            largest_loss=min([t.get("pnl", 0) for t in self.trade_history], default=0),
            avg_trade_duration=avg_trade_duration,
            initial_capital=self.initial_capital,
            final_capital=final_equity,
            total_commission=total_commission,
            net_profit=final_equity - self.initial_capital,
            equity_curve=self.equity_curve,
            trade_log=self.trade_history,
            daily_returns=returns.tolist() if isinstance(returns, np.ndarray) else returns,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            trades_per_day=len(self.trade_history) / ((end_date - start_date).days or 1),
            exposure_time=exposure_time
        )


# Example strategy for testing
def example_momentum_strategy(market_data: Dict, portfolio: Dict, timestamp: datetime) -> List[Dict]:
    """
    Simple momentum strategy for testing
    
    Buy when price is above 20 SMA and RSI < 70
    Sell when price is below 20 SMA or RSI > 80
    """
    signals = []
    
    for symbol, data in market_data.items():
        stats = data["stats"]
        price = data["price"]
        
        # Check if we have a position
        has_position = symbol in portfolio["positions"]
        
        # Buy signal
        if not has_position and price > stats["sma_20"] and stats["rsi"] < 70:
            # Calculate position size (10% of equity)
            position_size = portfolio["equity"] * 0.1 / price
            
            signals.append({
                "action": "buy",
                "symbol": symbol,
                "quantity": position_size,
                "order_type": OrderType.MARKET
            })
        
        # Sell signal
        elif has_position and (price < stats["sma_20"] or stats["rsi"] > 80):
            position = portfolio["positions"][symbol]
            
            signals.append({
                "action": "sell",
                "symbol": symbol,
                "quantity": position.quantity,
                "order_type": OrderType.MARKET
            })
    
    return signals


if __name__ == "__main__":
    # Example backtest
    engine = BacktestingEngine(initial_capital=10000)
    
    # Run backtest
    results = engine.run_backtest(
        strategy=example_momentum_strategy,
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        symbols=["BTC_USDT", "ETH_USDT"]
    )
    
    # Print results
    print(f"Total Return: {results.total_return:.2%}")
    print(f"Win Rate: {results.win_rate:.2%}")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {results.max_drawdown:.2%}")
    print(f"Total Trades: {results.total_trades}")