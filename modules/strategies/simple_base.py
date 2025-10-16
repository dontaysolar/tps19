#!/usr/bin/env python3
"""
Simple Base Strategy - No External Dependencies
Works without pandas/numpy for basic functionality
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class SimpleBaseStrategy(ABC):
    """Base strategy that works without pandas"""
    
    def __init__(self, name: str):
        self.name = name
        self.win_rate = 0.50
        self.avg_win = 0.04
        self.avg_loss = 0.02
        self.profit_factor = 1.0
        self.trades_executed = 0
        self.winning_trades = 0
    
    @abstractmethod
    def analyze(self, data: Dict) -> Optional[Dict]:
        """
        Analyze market data and generate signal
        
        Args:
            data: Dict with 'close', 'high', 'low', 'open', 'volume' lists
        
        Returns:
            Signal dict or None
        """
        pass
    
    def simple_moving_average(self, prices: List[float], period: int) -> float:
        """Calculate simple moving average"""
        if len(prices) < period:
            return 0
        
        recent = prices[-period:]
        return sum(recent) / len(recent)
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(len(prices) - period, len(prices)):
            if i == 0:
                continue
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
    
    def update_performance(self, trade_result: Dict):
        """Update strategy performance"""
        self.trades_executed += 1
        if trade_result.get('pnl', 0) > 0:
            self.winning_trades += 1
        
        if self.trades_executed > 0:
            self.win_rate = self.winning_trades / self.trades_executed
