"""TPS19 Backtesting Module"""

try:
    from .engine import BacktestEngine, quick_backtest
    HAS_BACKTESTING = True
except ImportError:
    HAS_BACKTESTING = False
    BacktestEngine = None
    quick_backtest = None

__all__ = ['BacktestEngine', 'quick_backtest', 'HAS_BACKTESTING']
