#!/usr/bin/env python3
"""
Harmonic Pattern Engine - Gartley, Butterfly, Bat, Crab patterns
Rapid pattern detection and execution
"""

from typing import Dict, List, Optional
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class HarmonicEngine:
    """
    Harmonic pattern trading engine
    
    Detects and trades:
    - Gartley pattern
    - Butterfly pattern
    - Bat pattern
    - Crab pattern
    - Cypher pattern
    """
    
    def __init__(self):
        self.name = "Harmonic Engine"
        
        # Harmonic pattern ratios (Fibonacci-based)
        self.patterns = {
            'gartley': {'B': 0.618, 'C': (0.382, 0.886), 'D': 0.786},
            'butterfly': {'B': 0.786, 'C': (0.382, 0.886), 'D': 1.272},
            'bat': {'B': (0.382, 0.500), 'C': (0.382, 0.886), 'D': 0.886},
            'crab': {'B': (0.382, 0.618), 'C': (0.382, 0.886), 'D': 1.618},
        }
        
        self.decisions_made = 0
        self.patterns_detected = 0
        
    def rapid_analyze(self, df) -> Optional[Dict]:
        """
        RAPID harmonic pattern detection
        
        Target: <100ms execution
        """
        if not HAS_PANDAS or len(df) < 100:
            return None
        
        start_time = datetime.now()
        
        try:
            # Find recent swing points (XABCD)
            swings = self._find_swing_points(df.tail(100))
            
            if len(swings) < 5:
                return None
            
            # Check for harmonic patterns
            pattern = self._detect_harmonic_pattern(swings)
            
            if pattern:
                self.patterns_detected += 1
                
                # Generate rapid trading decision
                decision = self._generate_pattern_trade(pattern, df['close'].iloc[-1])
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if decision:
                    decision['execution_time_ms'] = execution_time
                    decision['pattern_data'] = pattern
                    self.decisions_made += 1
                
                return decision
            
            return None
            
        except Exception as e:
            logger.error(f"Harmonic analysis error: {e}")
            return None
    
    def _find_swing_points(self, df) -> List[Dict]:
        """Find swing highs and lows"""
        swings = []
        
        high = df['high'].values
        low = df['low'].values
        
        # Find local peaks and troughs
        for i in range(5, len(high) - 5):
            # Swing high
            if high[i] == max(high[i-5:i+6]):
                swings.append({
                    'type': 'high',
                    'price': high[i],
                    'index': i
                })
            
            # Swing low
            elif low[i] == min(low[i-5:i+6]):
                swings.append({
                    'type': 'low',
                    'price': low[i],
                    'index': i
                })
        
        # Return last 5 points (XABCD)
        return swings[-5:] if len(swings) >= 5 else swings
    
    def _detect_harmonic_pattern(self, swings: List[Dict]) -> Optional[Dict]:
        """Detect harmonic patterns (Gartley, Butterfly, etc.)"""
        if len(swings) < 5:
            return None
        
        # Extract XABCD points
        X = swings[0]['price']
        A = swings[1]['price']
        B = swings[2]['price']
        C = swings[3]['price']
        D = swings[4]['price']
        
        # Calculate ratios
        XA = abs(A - X)
        AB = abs(B - A)
        BC = abs(C - B)
        CD = abs(D - C)
        
        # Check each pattern
        for pattern_name, ratios in self.patterns.items():
            if self._matches_pattern(AB, BC, CD, XA, ratios):
                return {
                    'name': pattern_name,
                    'points': {'X': X, 'A': A, 'B': B, 'C': C, 'D': D},
                    'completion_point': D,
                    'target': C,  # Profit target at C
                    'stop': D * 1.01 if A > X else D * 0.99,
                    'bullish': A > X,
                    'detected_at': datetime.now().isoformat()
                }
        
        return None
    
    def _matches_pattern(self, AB: float, BC: float, CD: float, 
                        XA: float, ratios: Dict) -> bool:
        """Check if ratios match harmonic pattern"""
        tolerance = 0.05  # 5% tolerance
        
        # B retracement of XA
        B_ratio = AB / XA
        expected_B = ratios['B']
        
        if isinstance(expected_B, tuple):
            if not (expected_B[0] - tolerance <= B_ratio <= expected_B[1] + tolerance):
                return False
        else:
            if not (expected_B - tolerance <= B_ratio <= expected_B + tolerance):
                return False
        
        # C retracement of AB
        C_ratio = BC / AB
        expected_C = ratios['C']
        
        if isinstance(expected_C, tuple):
            if not (expected_C[0] - tolerance <= C_ratio <= expected_C[1] + tolerance):
                return False
        else:
            if not (expected_C - tolerance <= C_ratio <= expected_C + tolerance):
                return False
        
        # D extension/retracement of XA
        D_ratio = (AB + BC + CD) / XA
        expected_D = ratios['D']
        
        if not (expected_D - tolerance <= D_ratio <= expected_D + tolerance):
            return False
        
        return True
    
    def _generate_pattern_trade(self, pattern: Dict, current_price: float) -> Optional[Dict]:
        """Generate trade from detected pattern"""
        pattern_name = pattern['name']
        D = pattern['completion_point']
        
        # Check if we're at completion point D
        if abs(current_price - D) / D > 0.01:  # More than 1% away
            return None
        
        # Bullish pattern = BUY at D
        if pattern['bullish']:
            return {
                'signal': 'BUY',
                'action': 'BUY',
                'confidence': 0.80,
                'reason': f'{pattern_name.capitalize()} pattern complete at point D',
                'entry_price': current_price,
                'target': pattern['target'],
                'stop': pattern['stop'],
                'strategy': f'Harmonic_{pattern_name}',
                'rapid': True
            }
        # Bearish pattern = SELL at D
        else:
            return {
                'signal': 'SELL',
                'action': 'SELL',
                'confidence': 0.80,
                'reason': f'Bearish {pattern_name.capitalize()} pattern complete',
                'entry_price': current_price,
                'target': pattern['target'],
                'stop': pattern['stop'],
                'strategy': f'Harmonic_{pattern_name}',
                'rapid': True
            }
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'engine': 'Harmonic',
            'patterns_detected': self.patterns_detected,
            'decisions_made': self.decisions_made,
            'avg_decision_time_ms': self.avg_decision_time_ms,
            'patterns_supported': list(self.patterns.keys()),
            'rapid_execution': True
        }


# Global instance
harmonic_engine = HarmonicEngine()
