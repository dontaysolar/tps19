#!/usr/bin/env python3
"""Signal Generation and Integration"""

from typing import Dict, List, Optional
import pandas as pd
from modules.strategies.trend_following import TrendFollowingStrategy
from modules.strategies.mean_reversion import MeanReversionStrategy
from modules.strategies.breakout import BreakoutStrategy
from modules.strategies.momentum import MomentumStrategy
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class SignalGenerator:
    """Generates and integrates signals from multiple strategies"""
    
    def __init__(self):
        self.strategies = {
            'trend_following': TrendFollowingStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'breakout': BreakoutStrategy(),
            'momentum': MomentumStrategy(),
        }
        
    def generate_signals(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """Generate signals from all strategies"""
        signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                signal = strategy.analyze(df)
                if signal:
                    signal['symbol'] = symbol
                    signal['strategy_name'] = strategy_name
                    signals.append(signal)
                    logger.info(f"✅ {strategy_name} generated signal for {symbol}")
            except Exception as e:
                logger.error(f"Strategy {strategy_name} error: {e}")
        
        return signals
    
    def integrate_signals(self, signals: List[Dict]) -> Optional[Dict]:
        """Integrate multiple signals into one"""
        if not signals:
            return None
        
        if len(signals) == 1:
            return signals[0]
        
        # Separate by direction
        buy_signals = [s for s in signals if s.get('signal') == 'BUY']
        sell_signals = [s for s in signals if s.get('signal') == 'SELL']
        
        # If conflicting, take highest confidence
        if buy_signals and sell_signals:
            all_signals = buy_signals + sell_signals
            return max(all_signals, key=lambda s: s.get('confidence', 0))
        
        # All agree - combine
        if buy_signals:
            return self._combine_signals(buy_signals)
        elif sell_signals:
            return self._combine_signals(sell_signals)
        
        return None
    
    def _combine_signals(self, signals: List[Dict]) -> Dict:
        """Combine agreeing signals"""
        avg_confidence = sum(s['confidence'] for s in signals) / len(signals)
        
        combined = signals[0].copy()
        combined['confidence'] = min(avg_confidence * 1.1, 0.95)  # Boost for agreement
        combined['strategies'] = [s['strategy_name'] for s in signals]
        combined['signal_count'] = len(signals)
        
        return combined


signal_generator = SignalGenerator()
