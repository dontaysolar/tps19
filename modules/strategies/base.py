#!/usr/bin/env python3
"""Base Strategy Class"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    np = None

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.win_rate = 0.50
        self.avg_win = 0.04
        self.avg_loss = 0.02
        self.profit_factor = 1.0
        self.trades_executed = 0
        self.winning_trades = 0
        
    @abstractmethod
    def analyze(self, df) -> Optional[Dict]:
        """
        Analyze market data and generate signal
        
        Args:
            df: pandas DataFrame or dict with OHLCV data
        
        Returns:
            Signal dict or None
        """
        pass
    
    def calculate_rsi(self, prices, period: int = 14) -> float:
        """Calculate RSI indicator (works with pandas Series or list)"""
        if not HAS_PANDAS or not hasattr(prices, 'diff'):
            # Fallback for list/tuple
            if isinstance(prices, (list, tuple)):
                prices = list(prices)[-period-1:]
                if len(prices) < 2:
                    return 50.0
                
                gains = []
                losses = []
                for i in range(1, len(prices)):
                    change = prices[i] - prices[i-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                avg_gain = sum(gains) / len(gains) if gains else 0
                avg_loss = sum(losses) / len(losses) if losses else 0
                
                if avg_loss == 0:
                    return 100.0
                
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
            return 50.0
        
        # Pandas Series handling
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def calculate_macd(self, prices) -> tuple:
        """Calculate MACD"""
        if not HAS_PANDAS:
            # Simple moving average fallback
            if isinstance(prices, (list, tuple)):
                prices = list(prices)
                if len(prices) < 26:
                    return 0, 0
                
                # Simple MA instead of EMA
                ma12 = sum(prices[-12:]) / 12
                ma26 = sum(prices[-26:]) / 26
                macd = ma12 - ma26
                return macd, 0
            return 0, 0
        
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], signal.iloc[-1]
    
    def calculate_bollinger_bands(self, prices, period: int = 20, std: float = 2.0) -> tuple:
        """Calculate Bollinger Bands"""
        if not HAS_PANDAS:
            if isinstance(prices, (list, tuple)):
                prices = list(prices)[-period:]
                if len(prices) < period:
                    return 0, 0, 0
                
                ma = sum(prices) / len(prices)
                variance = sum((p - ma) ** 2 for p in prices) / len(prices)
                std_dev = variance ** 0.5
                
                upper = ma + (std_dev * std)
                lower = ma - (std_dev * std)
                return upper, ma, lower
            return 0, 0, 0
        
        ma = prices.rolling(window=period).mean()
        std_dev = prices.rolling(window=period).std()
        upper = ma + (std_dev * std)
        lower = ma - (std_dev * std)
        return upper.iloc[-1], ma.iloc[-1], lower.iloc[-1]
    
    def update_performance(self, trade_result: Dict):
        """Update strategy performance metrics"""
        self.trades_executed += 1
        if trade_result.get('pnl', 0) > 0:
            self.winning_trades += 1
        
        self.win_rate = self.winning_trades / max(self.trades_executed, 1)
