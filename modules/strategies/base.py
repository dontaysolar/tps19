#!/usr/bin/env python3
"""Base Strategy Class"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
import numpy as np
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
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analyze market data and generate signal"""
        pass
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD"""
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd.iloc[-1], signal.iloc[-1]
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std: float = 2.0) -> tuple:
        """Calculate Bollinger Bands"""
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
