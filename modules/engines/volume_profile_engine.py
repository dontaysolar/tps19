#!/usr/bin/env python3
"""
Volume Profile Engine - Order flow and volume analysis
Rapid execution based on high-volume nodes (HVN) and low-volume nodes (LVN)
"""

from typing import Dict, List, Optional
from datetime import datetime
import statistics

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class VolumeProfileEngine:
    """
    Volume Profile trading engine
    
    Analyzes:
    - Point of Control (POC) - Highest volume price
    - Value Area High/Low (VAH/VAL)
    - High Volume Nodes (HVN) - Support/resistance
    - Low Volume Nodes (LVN) - Quick moves expected
    """
    
    def __init__(self):
        self.name = "Volume Profile Engine"
        
        # Volume profile parameters
        self.num_price_levels = 20
        self.value_area_pct = 0.70  # 70% of volume
        
        self.decisions_made = 0
        
    def rapid_analyze(self, df) -> Optional[Dict]:
        """
        RAPID volume profile analysis
        
        Target: <100ms execution
        """
        if not HAS_PANDAS or len(df) < 50:
            return None
        
        start_time = datetime.now()
        
        try:
            # Use last 50 candles for speed
            recent_df = df.tail(50)
            
            # Calculate volume profile
            profile = self._calculate_volume_profile(recent_df)
            
            # Get current price
            current_price = recent_df['close'].iloc[-1]
            
            # Make rapid decision
            decision = self._make_volume_decision(profile, current_price)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if decision:
                decision['execution_time_ms'] = execution_time
                decision['volume_profile'] = profile
                self.decisions_made += 1
            
            return decision
            
        except Exception as e:
            logger.error(f"Volume profile error: {e}")
            return None
    
    def _calculate_volume_profile(self, df) -> Dict:
        """Calculate volume profile"""
        # Create price levels
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_levels = np.linspace(price_min, price_max, self.num_price_levels)
        
        # Aggregate volume at each price level
        volume_at_price = []
        
        for i in range(len(price_levels) - 1):
            level_low = price_levels[i]
            level_high = price_levels[i + 1]
            
            # Sum volume for candles in this price range
            in_range = df[(df['low'] <= level_high) & (df['high'] >= level_low)]
            total_volume = in_range['volume'].sum()
            
            volume_at_price.append({
                'price': (level_low + level_high) / 2,
                'volume': total_volume
            })
        
        # Find Point of Control (POC) - highest volume
        poc = max(volume_at_price, key=lambda x: x['volume'])
        
        # Calculate Value Area (70% of volume)
        total_volume = sum(v['volume'] for v in volume_at_price)
        value_area_volume = total_volume * self.value_area_pct
        
        # Sort by volume
        sorted_levels = sorted(volume_at_price, key=lambda x: x['volume'], reverse=True)
        
        # Find Value Area High/Low
        accumulated_volume = 0
        value_area_prices = []
        
        for level in sorted_levels:
            accumulated_volume += level['volume']
            value_area_prices.append(level['price'])
            if accumulated_volume >= value_area_volume:
                break
        
        vah = max(value_area_prices)
        val = min(value_area_prices)
        
        return {
            'poc': poc['price'],
            'vah': vah,
            'val': val,
            'volume_at_price': volume_at_price,
            'total_volume': total_volume
        }
    
    def _make_volume_decision(self, profile: Dict, 
                             current_price: float) -> Optional[Dict]:
        """
        Make RAPID decision based on volume profile
        
        Logic:
        - At VAL (Value Area Low) = BUY
        - At VAH (Value Area High) = SELL
        - At POC = NEUTRAL (high liquidity)
        - In LVN (Low Volume Node) = Expect quick move
        """
        poc = profile['poc']
        vah = profile['vah']
        val = profile['val']
        
        # Check if at Value Area Low (BUY opportunity)
        if abs(current_price - val) / val < 0.005:  # Within 0.5%
            return {
                'signal': 'BUY',
                'action': 'BUY',
                'confidence': 0.78,
                'reason': 'Price at Value Area Low (VAL) - support zone',
                'entry_price': current_price,
                'target': poc,  # Target POC
                'stop': val * 0.995,
                'strategy': 'Volume_Profile_VAL',
                'rapid': True
            }
        
        # Check if at Value Area High (SELL opportunity)
        if abs(current_price - vah) / vah < 0.005:  # Within 0.5%
            return {
                'signal': 'SELL',
                'action': 'SELL',
                'confidence': 0.78,
                'reason': 'Price at Value Area High (VAH) - resistance zone',
                'entry_price': current_price,
                'target': poc,  # Target POC
                'stop': vah * 1.005,
                'strategy': 'Volume_Profile_VAH',
                'rapid': True
            }
        
        # Check if at Point of Control (neutral, high liquidity)
        if abs(current_price - poc) / poc < 0.003:
            # At POC, wait for breakout direction
            return None
        
        # Check if in low volume area (expect quick move)
        current_volume = self._get_volume_at_price(current_price, profile)
        avg_volume = profile['total_volume'] / len(profile['volume_at_price'])
        
        if current_volume < avg_volume * 0.5:  # Low volume node
            # Determine likely direction
            if current_price < poc:
                # Below POC in LVN = likely to drop to VAL
                direction = 'SELL'
            else:
                # Above POC in LVN = likely to rise to VAH
                direction = 'BUY'
            
            return {
                'signal': direction,
                'action': direction,
                'confidence': 0.72,
                'reason': f'Low Volume Node - expect rapid move {direction}',
                'entry_price': current_price,
                'target': vah if direction == 'BUY' else val,
                'stop': current_price * 1.008 if direction == 'BUY' else current_price * 0.992,
                'strategy': 'Volume_Profile_LVN',
                'rapid': True
            }
        
        return None
    
    def _get_volume_at_price(self, price: float, profile: Dict) -> float:
        """Get volume at specific price level"""
        volume_at_price = profile['volume_at_price']
        
        # Find closest price level
        closest = min(volume_at_price, key=lambda x: abs(x['price'] - price))
        return closest['volume']
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'engine': 'Volume_Profile',
            'patterns_detected': self.patterns_detected,
            'decisions_made': self.decisions_made,
            'patterns_supported': list(self.patterns.keys()),
            'rapid_execution': True
        }


# Global instance
volume_profile_engine = VolumeProfileEngine()
