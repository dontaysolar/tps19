#!/usr/bin/env python3
"""
Comprehensive Backtesting Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from modules.strategies.base import BaseStrategy
from modules.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Trade:
    """Single trade record"""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    side: str  # 'long' or 'short'
    entry_price: float
    exit_price: Optional[float]
    size: float
    pnl: float = 0.0
    pnl_pct: float = 0.0
    strategy: str = ''
    closed: bool = False


@dataclass
class BacktestResults:
    """Backtest results container"""
    trades: List[Trade]
    equity_curve: pd.DataFrame
    metrics: Dict
    by_strategy: Dict = None
    by_regime: Dict = None
    drawdown_periods: List = None


class BacktestEngine:
    """
    Vectorized backtesting with realistic execution
    """
    
    def __init__(self, strategies: List[BaseStrategy]):
        self.strategies = strategies
        self.commission = 0.001  # 0.1% per trade
        self.slippage = 0.0005  # 0.05% slippage
        
    def run(self, historical_data: pd.DataFrame, 
            initial_capital: float = 500,
            position_size_pct: float = 0.10) -> BacktestResults:
        """
        Run backtest on historical data
        
        Args:
            historical_data: OHLCV DataFrame
            initial_capital: Starting capital
            position_size_pct: Position size as % of capital
            
        Returns:
            BacktestResults object
        """
        logger.info(f"Starting backtest on {len(historical_data)} candles...")
        
        trades = []
        equity = [initial_capital]
        capital = initial_capital
        open_position = None
        
        # Generate signals from each strategy
        all_signals = self._generate_all_signals(historical_data)
        
        # Simulate trading
        for i in range(100, len(historical_data)):  # Start after warm-up
            current_bar = historical_data.iloc[i]
            current_time = historical_data.index[i]
            current_price = current_bar['close']
            
            # Check exit conditions for open position
            if open_position:
                exit_signal = self._check_exit(open_position, current_bar, i, historical_data)
                
                if exit_signal:
                    # Close position
                    exit_price = current_price * (1 - self.slippage)  # Pessimistic exit
                    pnl = (exit_price - open_position.entry_price) * open_position.size
                    pnl -= (open_position.entry_price * open_position.size * self.commission)  # Entry commission
                    pnl -= (exit_price * open_position.size * self.commission)  # Exit commission
                    
                    open_position.exit_time = current_time
                    open_position.exit_price = exit_price
                    open_position.pnl = pnl
                    open_position.pnl_pct = pnl / (open_position.entry_price * open_position.size)
                    open_position.closed = True
                    
                    trades.append(open_position)
                    capital += pnl
                    open_position = None
            
            # Check entry signals if no position
            if not open_position:
                for strategy_name, signals in all_signals.items():
                    if i >= len(signals):
                        continue
                    
                    signal = signals.iloc[i]
                    if pd.isna(signal) or signal.get('signal') != 'BUY':
                        continue
                    
                    # Enter position
                    entry_price = current_price * (1 + self.slippage)  # Pessimistic entry
                    position_value = capital * position_size_pct
                    position_size = position_value / entry_price
                    
                    open_position = Trade(
                        entry_time=current_time,
                        exit_time=None,
                        symbol='BTC/USDT',
                        side='long',
                        entry_price=entry_price,
                        exit_price=None,
                        size=position_size,
                        strategy=strategy_name
                    )
                    break  # Only one position at a time
            
            # Update equity
            current_equity = capital
            if open_position:
                unrealized_pnl = (current_price - open_position.entry_price) * open_position.size
                current_equity += unrealized_pnl
            
            equity.append(current_equity)
        
        # Close any remaining position
        if open_position:
            final_price = historical_data.iloc[-1]['close']
            pnl = (final_price - open_position.entry_price) * open_position.size
            open_position.exit_time = historical_data.index[-1]
            open_position.exit_price = final_price
            open_position.pnl = pnl
            open_position.pnl_pct = pnl / (open_position.entry_price * open_position.size)
            open_position.closed = True
            trades.append(open_position)
            capital += pnl
        
        # Create equity curve DataFrame
        equity_df = pd.DataFrame({
            'equity': equity,
            'timestamp': historical_data.index[:len(equity)]
        }).set_index('timestamp')
        
        # Calculate drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, equity_df, initial_capital)
        
        logger.info(f"Backtest complete: {len(trades)} trades, "
                   f"Final capital: ${capital:.2f}, "
                   f"Return: {metrics['total_return']:.2%}")
        
        return BacktestResults(
            trades=trades,
            equity_curve=equity_df,
            metrics=metrics,
            by_strategy=self._analyze_by_strategy(trades),
            drawdown_periods=self._find_drawdown_periods(equity_df)
        )
    
    def _generate_all_signals(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Generate signals from all strategies"""
        all_signals = {}
        
        for strategy in self.strategies:
            logger.info(f"Generating signals for {strategy.name}...")
            signals = []
            
            for i in range(len(df)):
                if i < 100:  # Need warm-up period
                    signals.append(None)
                    continue
                
                window = df.iloc[:i+1]
                signal = strategy.analyze(window)
                signals.append(signal)
            
            all_signals[strategy.name] = pd.DataFrame(signals, index=df.index)
        
        return all_signals
    
    def _check_exit(self, position: Trade, current_bar: pd.Series,
                   current_idx: int, df: pd.DataFrame) -> bool:
        """Check if position should be exited"""
        current_price = current_bar['close']
        
        # Time-based exit (5 days = 5 * 288 5-min candles)
        bars_held = current_idx - df.index.get_loc(position.entry_time)
        if bars_held > 1440:  # 5 days
            return True
        
        # Stop loss (-2%)
        if current_price < position.entry_price * 0.98:
            return True
        
        # Take profit levels
        profit_pct = (current_price - position.entry_price) / position.entry_price
        if profit_pct > 0.10:  # 10%+ profit
            return True
        
        return False
    
    def _calculate_metrics(self, trades: List[Trade], 
                          equity_curve: pd.DataFrame,
                          initial_capital: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not trades:
            return {'error': 'No trades executed'}
        
        final_capital = equity_curve['equity'].iloc[-1]
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Trade statistics
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        profit_factor = (
            sum([t.pnl for t in winning_trades]) / abs(sum([t.pnl for t in losing_trades]))
            if losing_trades and sum([t.pnl for t in losing_trades]) != 0 else 0
        )
        
        # Returns analysis
        returns = equity_curve['equity'].pct_change().dropna()
        
        # Sharpe ratio (annualized)
        if len(returns) > 0 and returns.std() > 0:
            periods_per_year = 365 * 288  # 5-min candles per year
            sharpe_ratio = (returns.mean() * periods_per_year) / (returns.std() * np.sqrt(periods_per_year))
        else:
            sharpe_ratio = 0
        
        # Sortino ratio (only downside volatility)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            periods_per_year = 365 * 288
            sortino_ratio = (returns.mean() * periods_per_year) / (downside_returns.std() * np.sqrt(periods_per_year))
        else:
            sortino_ratio = 0
        
        # Max drawdown
        max_drawdown = equity_curve['drawdown'].min()
        
        # Trade duration
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 
                    for t in trades if t.exit_time]
        avg_duration_hours = np.mean(durations) if durations else 0
        
        return {
            'total_return': total_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'avg_trade_duration_hours': avg_duration_hours,
            'final_capital': final_capital,
            'total_profit': final_capital - initial_capital
        }
    
    def _analyze_by_strategy(self, trades: List[Trade]) -> Dict:
        """Analyze performance by strategy"""
        by_strategy = {}
        
        for trade in trades:
            if trade.strategy not in by_strategy:
                by_strategy[trade.strategy] = []
            by_strategy[trade.strategy].append(trade)
        
        results = {}
        for strategy_name, strategy_trades in by_strategy.items():
            winning = [t for t in strategy_trades if t.pnl > 0]
            
            results[strategy_name] = {
                'total_trades': len(strategy_trades),
                'win_rate': len(winning) / len(strategy_trades) if strategy_trades else 0,
                'total_pnl': sum([t.pnl for t in strategy_trades]),
                'avg_pnl': np.mean([t.pnl for t in strategy_trades])
            }
        
        return results
    
    def _find_drawdown_periods(self, equity_df: pd.DataFrame) -> List[Dict]:
        """Find significant drawdown periods"""
        drawdown_periods = []
        in_drawdown = False
        dd_start = None
        dd_peak = 0
        
        for idx, row in equity_df.iterrows():
            if row['drawdown'] < -0.05 and not in_drawdown:  # Start of 5%+ drawdown
                in_drawdown = True
                dd_start = idx
                dd_peak = row['peak']
            elif row['drawdown'] >= 0 and in_drawdown:  # Recovery
                in_drawdown = False
                max_dd = equity_df.loc[dd_start:idx, 'drawdown'].min()
                drawdown_periods.append({
                    'start': dd_start,
                    'end': idx,
                    'max_drawdown': max_dd,
                    'duration': (idx - dd_start).days
                })
        
        return drawdown_periods


# Helper function for easy backtesting
def quick_backtest(strategy: BaseStrategy, data: pd.DataFrame) -> BacktestResults:
    """Quick backtest for single strategy"""
    engine = BacktestEngine([strategy])
    return engine.run(data)
