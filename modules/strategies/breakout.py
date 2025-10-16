#!/usr/bin/env python3
"""Breakout Strategy - Capture Explosive Moves"""

from typing import Dict, Optional

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None
    np = None

from .base import BaseStrategy
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class BreakoutStrategy(BaseStrategy):
    """
    Breakout: Capture explosive moves from consolidation
    
    Entry: Consolidation 5+ days, BB squeeze, breakout with volume
    Exit: Failed breakout, volume declining
    
    Win Rate: 35-40%
    Risk/Reward: 1:4
    Best For: News catalysts, consolidation breaks
    """
    
    def __init__(self):
        super().__init__("Breakout")
        self.win_rate = 0.38
        self.avg_win = 0.08
        self.avg_loss = 0.02
        self.profit_factor = 2.2
        
    def analyze(self, df) -> Optional[Dict]:
        """
        Analyze for breakout opportunities
        
        Args:
            df: OHLCV DataFrame (pandas) or dict
            
        Returns:
            Signal dict or None
        """
        if not HAS_PANDAS:
            logger.warning("Pandas not available, breakout disabled")
            return None
        
        if len(df) < 50:
            return None
        
        try:
            latest = df.iloc[-1]
            close_prices = df['close']
            
            # Bollinger Bands
            upper_band, middle_band, lower_band = self.calculate_bollinger_bands(close_prices)
            bb_width = (upper_band - lower_band) / middle_band
            
            # Historical BB width for comparison
            bb_widths = []
            for i in range(max(20, len(df) - 20), len(df)):
                window = df['close'].iloc[max(0, i-20):i]
                if len(window) >= 20:
                    u, m, l = self.calculate_bollinger_bands(window)
                    bb_widths.append((u - l) / m if m > 0 else 0)
            
            avg_bb_width = np.mean(bb_widths) if bb_widths else bb_width
            is_squeezing = bb_width < avg_bb_width * 0.7  # 30% narrower than average
            
            # Consolidation detection
            recent_range = df['high'].iloc[-10:].max() - df['low'].iloc[-10:].min()
            consolidating = recent_range / latest['close'] < 0.05  # <5% range
            
            # Volume analysis
            volume_ma = df['volume'].rolling(20).mean().iloc[-1]
            volume_drying = latest['volume'] < volume_ma * 0.8
            
            # Resistance/Support
            resistance = df['high'].iloc[-20:].max()
            support = df['low'].iloc[-20:].min()
            
            # BREAKOUT UP
            if (consolidating and
                is_squeezing and
                latest['close'] > resistance and
                latest['volume'] > volume_ma * 1.5):  # Volume spike
                
                confirmations = sum([
                    consolidating,
                    is_squeezing,
                    latest['close'] > resistance,
                    latest['volume'] > volume_ma * 1.5,
                    latest['close'] > upper_band
                ])
                
                confidence = min(confirmations / 5.0, 0.85)
                
                # Calculate range for target
                consolidation_range = resistance - support
                
                return {
                    'signal': 'BUY',
                    'strategy': self.name,
                    'confidence': confidence,
                    'confirmations': confirmations,
                    'entry_price': latest['close'],
                    'stop_loss': support,  # Below consolidation
                    'target': latest['close'] + (consolidation_range * 2),  # 2x range
                    'reasoning': f"Breakout: BB squeeze, volume spike, above resistance",
                    'strategy_win_rate': self.win_rate,
                    'strategy_avg_win': self.avg_win,
                    'strategy_avg_loss': self.avg_loss,
                    'indicators': {
                        'bb_width': bb_width,
                        'avg_bb_width': avg_bb_width,
                        'resistance': resistance,
                        'support': support,
                        'volume': latest['volume'],
                        'volume_ma': volume_ma
                    }
                }
            
            # FAILED BREAKOUT (reversal)
            elif (latest['close'] < support and
                  latest['volume'] < volume_ma):
                
                return {
                    'signal': 'SELL',
                    'strategy': self.name,
                    'confidence': 0.60,
                    'reasoning': "Failed breakout: Returned to range"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Breakout analysis error: {e}")
            return None
