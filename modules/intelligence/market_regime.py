#!/usr/bin/env python3
"""Market Regime Detection"""

import pandas as pd
import numpy as np
from enum import Enum
from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MarketRegime(Enum):
    STRONG_TREND = "strong_trend"
    WEAK_TREND = "weak_trend"
    RANGING = "ranging"
    BREAKOUT_SETUP = "breakout_setup"
    HIGH_VOLATILITY = "high_volatility"
    UNCERTAIN = "uncertain"


class MarketRegimeDetector:
    """Detects current market regime"""
    
    def detect(self, df: pd.DataFrame) -> MarketRegime:
        """Detect market regime from price data"""
        if len(df) < 50:
            return MarketRegime.UNCERTAIN
        
        try:
            # Calculate metrics
            volatility = self._calculate_volatility(df)
            trend_strength = self._calculate_trend_strength(df)
            is_consolidating = self._detect_consolidation(df)
            
            # Regime logic
            if trend_strength > 0.7 and volatility < 0.05:
                return MarketRegime.STRONG_TREND
            elif trend_strength > 0.4 and volatility < 0.08:
                return MarketRegime.WEAK_TREND
            elif volatility > 0.10:
                return MarketRegime.HIGH_VOLATILITY
            elif is_consolidating:
                return MarketRegime.BREAKOUT_SETUP
            elif volatility < 0.05 and trend_strength < 0.3:
                return MarketRegime.RANGING
            else:
                return MarketRegime.UNCERTAIN
                
        except Exception as e:
            logger.error(f"Regime detection error: {e}")
            return MarketRegime.UNCERTAIN
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate price volatility"""
        returns = df['close'].pct_change()
        return returns.std() if len(returns) > 1 else 0.05
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength (0-1)"""
        if len(df) < 50:
            return 0.5
        
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        ma50 = df['close'].rolling(50).mean().iloc[-1]
        
        if pd.isna(ma20) or pd.isna(ma50) or ma50 == 0:
            return 0.5
        
        diff = abs(ma20 - ma50) / ma50
        return min(diff * 10, 1.0)
    
    def _detect_consolidation(self, df: pd.DataFrame) -> bool:
        """Detect consolidation pattern"""
        if len(df) < 10:
            return False
        
        recent = df.iloc[-10:]
        price_range = recent['high'].max() - recent['low'].min()
        avg_price = recent['close'].mean()
        
        return (price_range / avg_price) < 0.03 if avg_price > 0 else False


regime_detector = MarketRegimeDetector()
