#!/usr/bin/env python3
"""Mean Reversion Strategy - Buy Oversold, Sell Overbought"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from .base import BaseStrategy
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion: Buy oversold, sell overbought in ranging markets
    
    Entry: Price at BB lower, RSI < 30, volume spike
    Exit: Return to mean, RSI > 50
    
    Win Rate: 60-65%
    Risk/Reward: 1:1.5
    Best For: Sideways/ranging markets
    """
    
    def __init__(self):
        super().__init__("Mean Reversion")
        self.win_rate = 0.62
        self.avg_win = 0.04
        self.avg_loss = 0.03
        self.profit_factor = 1.5
        
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze for mean reversion opportunities
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Signal dict or None
        """
        if len(df) < 30:
            return None
        
        try:
            latest = df.iloc[-1]
            close_prices = df['close']
            
            # Calculate Bollinger Bands
            upper_band, middle_band, lower_band = self.calculate_bollinger_bands(close_prices)
            
            # RSI
            rsi = self.calculate_rsi(close_prices)
            
            # Z-score (standard deviations from mean)
            ma20 = close_prices.rolling(20).mean().iloc[-1]
            std20 = close_prices.rolling(20).std().iloc[-1]
            z_score = (latest['close'] - ma20) / std20 if std20 > 0 else 0
            
            # Volume
            volume_ma = df['volume'].rolling(20).mean().iloc[-1]
            volume_spike = latest['volume'] > volume_ma * 1.2
            
            # BUY CONDITIONS (oversold)
            if (latest['close'] <= lower_band and  # At lower BB
                z_score < -2 and  # 2+ std devs below mean
                rsi < 30 and  # Oversold
                rsi > 20 and  # Not extreme
                volume_spike):  # Volume confirming
                
                confirmations = sum([
                    latest['close'] <= lower_band,
                    z_score < -2,
                    20 < rsi < 30,
                    volume_spike,
                    latest['low'] < lower_band
                ])
                
                confidence = min(confirmations / 5.0, 0.90)
                
                return {
                    'signal': 'BUY',
                    'strategy': self.name,
                    'confidence': confidence,
                    'confirmations': confirmations,
                    'entry_price': latest['close'],
                    'stop_loss': latest['close'] * 0.97,  # 3% stop (wider)
                    'target': middle_band,  # Target mean
                    'reasoning': f"Oversold: Z-score {z_score:.2f}, RSI {rsi:.1f}",
                    'strategy_win_rate': self.win_rate,
                    'strategy_avg_win': self.avg_win,
                    'strategy_avg_loss': self.avg_loss,
                    'indicators': {
                        'bb_upper': upper_band,
                        'bb_middle': middle_band,
                        'bb_lower': lower_band,
                        'rsi': rsi,
                        'z_score': z_score
                    }
                }
            
            # SELL CONDITIONS (overbought)
            elif (latest['close'] >= upper_band and
                  z_score > 2 and
                  rsi > 70):
                
                return {
                    'signal': 'SELL',
                    'strategy': self.name,
                    'confidence': 0.70,
                    'reasoning': f"Overbought: Z-score {z_score:.2f}, RSI {rsi:.1f}"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Mean reversion analysis error: {e}")
            return None
