#!/usr/bin/env python3
"""
Fibonacci Trading Engine - Rapid Fibonacci-based trading
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime

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


class FibonacciEngine:
    """
    Fibonacci retracement and extension trading engine
    
    Rapid execution based on Fibonacci levels
    """
    
    def __init__(self):
        self.name = "Fibonacci Engine"
        
        # Fibonacci levels
        self.retracement_levels = [0.236, 0.382, 0.500, 0.618, 0.786]
        self.extension_levels = [1.272, 1.414, 1.618, 2.000, 2.618]
        
        # Decision speed tracking
        self.avg_decision_time_ms = 0
        self.decisions_made = 0
        
    def rapid_analyze(self, df, current_price: float) -> Optional[Dict]:
        """
        RAPID Fibonacci analysis (<50ms target)
        
        Args:
            df: Price data
            current_price: Current price
            
        Returns:
            Immediate trading decision
        """
        if not HAS_PANDAS or len(df) < 50:
            return None
        
        start_time = datetime.now()
        
        try:
            # Find swing high and low (last 50 candles for speed)
            recent_data = df.tail(50)
            swing_high = recent_data['high'].max()
            swing_low = recent_data['low'].min()
            
            # Calculate Fibonacci levels
            fib_range = swing_high - swing_low
            
            # Retracement levels (in downtrend from high)
            retracements = {
                level: swing_high - (fib_range * level)
                for level in self.retracement_levels
            }
            
            # Extension levels (in uptrend from low)
            extensions = {
                level: swing_high + (fib_range * (level - 1))
                for level in self.extension_levels
            }
            
            # RAPID decision logic
            decision = self._make_rapid_decision(
                current_price, 
                swing_high, 
                swing_low,
                retracements, 
                extensions
            )
            
            # Track execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_speed_metrics(execution_time)
            
            if decision:
                decision['execution_time_ms'] = execution_time
                decision['fibonacci_levels'] = {
                    'swing_high': swing_high,
                    'swing_low': swing_low,
                    'retracements': retracements,
                    'extensions': extensions
                }
            
            return decision
            
        except Exception as e:
            logger.error(f"Fibonacci analysis error: {e}")
            return None
    
    def _make_rapid_decision(self, current_price: float,
                            swing_high: float, swing_low: float,
                            retracements: Dict, extensions: Dict) -> Optional[Dict]:
        """
        Make INSTANT trading decision based on Fibonacci
        
        Speed target: <10ms for this function
        """
        # Check if near key retracement (BUY opportunity)
        for level, price in retracements.items():
            distance = abs(current_price - price) / price
            
            if distance < 0.003:  # Within 0.3% of Fibonacci level
                if level in [0.618, 0.786]:  # Strong retracement levels
                    return {
                        'signal': 'BUY',
                        'action': 'BUY',
                        'confidence': 0.75 + (level * 0.2),
                        'reason': f'Price at Fibonacci {level:.3f} retracement',
                        'entry_price': current_price,
                        'target': retracements[0.236],  # Next level up
                        'stop': swing_low * 0.998,
                        'strategy': 'Fibonacci_Retracement',
                        'level': level,
                        'rapid': True
                    }
        
        # Check if near extension (profit target / resistance)
        for level, price in extensions.items():
            distance = abs(current_price - price) / price
            
            if distance < 0.005:  # Within 0.5% of extension
                if level >= 1.618:  # At major extension
                    return {
                        'signal': 'SELL',
                        'action': 'SELL',
                        'confidence': 0.70,
                        'reason': f'Price at Fibonacci {level:.3f} extension (resistance)',
                        'entry_price': current_price,
                        'target': retracements[0.618],  # Pullback target
                        'stop': current_price * 1.015,
                        'strategy': 'Fibonacci_Extension',
                        'level': level,
                        'rapid': True
                    }
        
        # Check if bouncing off golden ratio (0.618)
        golden_ratio = retracements.get(0.618)
        if golden_ratio:
            if swing_low < current_price < golden_ratio * 1.01:
                # Just bounced off 0.618, strong BUY
                return {
                    'signal': 'BUY',
                    'action': 'BUY',
                    'confidence': 0.85,
                    'reason': 'Golden ratio (0.618) bounce',
                    'entry_price': current_price,
                    'target': swing_high,
                    'stop': swing_low * 0.998,
                    'strategy': 'Fibonacci_Golden_Ratio',
                    'level': 0.618,
                    'rapid': True
                }
        
        return None
    
    def _update_speed_metrics(self, execution_time_ms: float):
        """Track decision speed"""
        self.decisions_made += 1
        self.avg_decision_time_ms = (
            (self.avg_decision_time_ms * (self.decisions_made - 1) + execution_time_ms) 
            / self.decisions_made
        )
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'engine': 'Fibonacci',
            'decisions_made': self.decisions_made,
            'avg_decision_time_ms': self.avg_decision_time_ms,
            'retracement_levels': self.retracement_levels,
            'extension_levels': self.extension_levels,
            'rapid_execution': True
        }


# Global instance
fibonacci_engine = FibonacciEngine()
