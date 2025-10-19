#!/usr/bin/env python3
"""
TWAP (Time Weighted Average Price) Execution Bot
Splits large orders over time to minimize market impact
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class TWAPExecutionBot:
    def __init__(self):
        self.name = "TWAP_Execution"
        self.version = "1.0.0"
        self.enabled = True
        
        self.metrics = {
            'orders_split': 0,
            'total_slices': 0,
            'avg_execution_time': 0
        }
    
    def calculate_twap_schedule(self, 
                                total_quantity: float,
                                duration_minutes: int,
                                num_slices: int = None) -> Dict:
        """
        Calculate TWAP execution schedule
        
        Args:
            total_quantity: Total amount to trade
            duration_minutes: Time window for execution
            num_slices: Number of slices (auto if None)
        """
        if num_slices is None:
            # Auto-calculate slices: 1 per minute for small duration, max 20
            num_slices = min(duration_minutes, 20)
        
        slice_size = total_quantity / num_slices
        slice_interval = duration_minutes / num_slices
        
        # Create execution schedule
        schedule = []
        current_time = datetime.now()
        
        for i in range(num_slices):
            exec_time = current_time + timedelta(minutes=i * slice_interval)
            schedule.append({
                'slice': i + 1,
                'quantity': slice_size,
                'time': exec_time.isoformat(),
                'status': 'pending'
            })
        
        self.metrics['orders_split'] += 1
        self.metrics['total_slices'] += num_slices
        
        return {
            'total_quantity': total_quantity,
            'num_slices': num_slices,
            'slice_size': slice_size,
            'slice_interval_minutes': slice_interval,
            'total_duration_minutes': duration_minutes,
            'schedule': schedule,
            'start_time': current_time.isoformat(),
            'estimated_completion': (current_time + timedelta(minutes=duration_minutes)).isoformat(),
            'timestamp': datetime.now().isoformat()
        }
    
    def adaptive_twap(self,
                     total_quantity: float,
                     duration_minutes: int,
                     market_volatility: float,
                     volume_profile: List[float] = None) -> Dict:
        """
        Adaptive TWAP that adjusts to market conditions
        
        Args:
            total_quantity: Total to trade
            duration_minutes: Time window
            market_volatility: Current volatility (0-100)
            volume_profile: Expected volume distribution
        """
        # More slices in high volatility
        if market_volatility > 50:
            num_slices = min(duration_minutes, 30)
        else:
            num_slices = min(duration_minutes // 2, 15)
        
        schedule = []
        remaining_qty = total_quantity
        current_time = datetime.now()
        
        for i in range(num_slices):
            # Adjust slice size based on volume profile
            if volume_profile and i < len(volume_profile):
                # Trade more when volume is higher
                weight = volume_profile[i] / sum(volume_profile)
                slice_qty = total_quantity * weight
            else:
                slice_qty = remaining_qty / (num_slices - i)
            
            exec_time = current_time + timedelta(minutes=(duration_minutes / num_slices) * i)
            
            schedule.append({
                'slice': i + 1,
                'quantity': slice_qty,
                'time': exec_time.isoformat(),
                'adjusted_for_volume': bool(volume_profile),
                'status': 'pending'
            })
            
            remaining_qty -= slice_qty
        
        return {
            'type': 'ADAPTIVE_TWAP',
            'total_quantity': total_quantity,
            'num_slices': num_slices,
            'schedule': schedule,
            'volatility_adjustment': market_volatility > 50,
            'volume_weighted': bool(volume_profile),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = TWAPExecutionBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
