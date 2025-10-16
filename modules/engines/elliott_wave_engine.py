#!/usr/bin/env python3
"""
Elliott Wave Engine - Rapid Elliott Wave analysis
Detects impulse and corrective waves for trading
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


class ElliottWaveEngine:
    """
    Elliott Wave trading engine
    
    Detects:
    - Impulse waves (5-wave pattern: 1-2-3-4-5)
    - Corrective waves (3-wave pattern: A-B-C)
    - Wave 3 and Wave 5 entries (strongest moves)
    """
    
    def __init__(self):
        self.name = "Elliott Wave Engine"
        
        self.decisions_made = 0
        self.waves_detected = 0
        
    def rapid_analyze(self, df) -> Optional[Dict]:
        """
        RAPID Elliott Wave detection
        
        Simplified but fast implementation
        """
        if not HAS_PANDAS or len(df) < 50:
            return None
        
        start_time = datetime.now()
        
        try:
            # Find swing points
            swings = self._find_swing_points_fast(df.tail(50))
            
            if len(swings) < 5:
                return None
            
            # Detect wave pattern
            wave_pattern = self._detect_wave_pattern(swings)
            
            if wave_pattern:
                self.waves_detected += 1
                
                # Generate trade decision
                decision = self._generate_wave_trade(wave_pattern, df['close'].iloc[-1])
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if decision:
                    decision['execution_time_ms'] = execution_time
                    decision['wave_pattern'] = wave_pattern
                    self.decisions_made += 1
                
                return decision
            
            return None
            
        except Exception as e:
            logger.error(f"Elliott Wave error: {e}")
            return None
    
    def _find_swing_points_fast(self, df) -> List[Dict]:
        """Find swing points quickly"""
        swings = []
        
        high = df['high'].values
        low = df['low'].values
        
        # Alternate high and low swings
        last_was_high = None
        
        for i in range(3, len(high) - 3):
            # Swing high
            if high[i] == max(high[i-3:i+4]):
                if last_was_high != True:
                    swings.append({
                        'type': 'high',
                        'price': high[i],
                        'index': i
                    })
                    last_was_high = True
            
            # Swing low
            elif low[i] == min(low[i-3:i+4]):
                if last_was_high != False:
                    swings.append({
                        'type': 'low',
                        'price': low[i],
                        'index': i
                    })
                    last_was_high = False
        
        return swings
    
    def _detect_wave_pattern(self, swings: List[Dict]) -> Optional[Dict]:
        """Detect Elliott Wave pattern"""
        if len(swings) < 5:
            return None
        
        # Get last 5 swings for impulse wave (1-2-3-4-5)
        last_5 = swings[-5:]
        
        # Check if it's a valid impulse wave (bullish)
        if self._is_bullish_impulse(last_5):
            return {
                'type': 'impulse',
                'direction': 'bullish',
                'waves': last_5,
                'current_wave': 5,  # Assume we're at wave 5
                'next_move': 'correction_expected'
            }
        
        # Check if it's a valid impulse wave (bearish)
        if self._is_bearish_impulse(last_5):
            return {
                'type': 'impulse',
                'direction': 'bearish',
                'waves': last_5,
                'current_wave': 5,
                'next_move': 'correction_expected'
            }
        
        # Check for ABC correction
        if len(swings) >= 3:
            last_3 = swings[-3:]
            if self._is_abc_correction(last_3):
                return {
                    'type': 'correction',
                    'direction': 'ending',
                    'waves': last_3,
                    'current_wave': 'C',
                    'next_move': 'impulse_expected'
                }
        
        return None
    
    def _is_bullish_impulse(self, waves: List[Dict]) -> bool:
        """Check if bullish impulse wave (1-2-3-4-5)"""
        # Wave 1: up, Wave 2: down, Wave 3: up, Wave 4: down, Wave 5: up
        # Simplified: just check alternating and overall upward
        if len(waves) != 5:
            return False
        
        # Check wave 3 is longest (Elliott rule)
        w1_size = abs(waves[1]['price'] - waves[0]['price'])
        w3_size = abs(waves[3]['price'] - waves[2]['price'])
        w5_size = abs(waves[4]['price'] - waves[3]['price'])
        
        # Wave 3 should be longest
        if w3_size > w1_size and w3_size > w5_size:
            # Wave 5 should be higher than wave 3
            if waves[4]['price'] > waves[2]['price']:
                return True
        
        return False
    
    def _is_bearish_impulse(self, waves: List[Dict]) -> bool:
        """Check if bearish impulse wave"""
        if len(waves) != 5:
            return False
        
        # Inverse of bullish
        w3_size = abs(waves[3]['price'] - waves[2]['price'])
        w1_size = abs(waves[1]['price'] - waves[0]['price'])
        
        if w3_size > w1_size:
            if waves[4]['price'] < waves[2]['price']:
                return True
        
        return False
    
    def _is_abc_correction(self, waves: List[Dict]) -> bool:
        """Check if ABC correction pattern"""
        if len(waves) != 3:
            return False
        
        # ABC correction typically retraces 50-78% of previous impulse
        # Simplified: just check it's a 3-wave move
        return True
    
    def _generate_wave_trade(self, pattern: Dict, 
                            current_price: float) -> Optional[Dict]:
        """Generate trade from Elliott Wave pattern"""
        wave_type = pattern['type']
        direction = pattern['direction']
        current_wave = pattern['current_wave']
        
        # If at end of wave 5 (impulse complete), expect correction
        if wave_type == 'impulse' and current_wave == 5:
            if direction == 'bullish':
                return {
                    'signal': 'SELL',
                    'action': 'SELL',
                    'confidence': 0.72,
                    'reason': 'Elliott Wave 5 complete - correction expected',
                    'entry_price': current_price,
                    'target': current_price * 0.95,  # 5% correction
                    'stop': current_price * 1.02,
                    'strategy': 'Elliott_Wave_5_Top',
                    'rapid': True
                }
        
        # If at end of ABC correction, expect new impulse
        if wave_type == 'correction' and current_wave == 'C':
            return {
                'signal': 'BUY',
                'action': 'BUY',
                'confidence': 0.75,
                'reason': 'Elliott Wave ABC correction complete - impulse expected',
                'entry_price': current_price,
                'target': current_price * 1.08,  # 8% impulse
                'stop': current_price * 0.98,
                'strategy': 'Elliott_Wave_ABC_End',
                'rapid': True
            }
        
        return None
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'engine': 'Elliott_Wave',
            'waves_detected': self.waves_detected,
            'decisions_made': self.decisions_made,
            'rapid_execution': True
        }


# Global instance
elliott_wave_engine = ElliottWaveEngine()
