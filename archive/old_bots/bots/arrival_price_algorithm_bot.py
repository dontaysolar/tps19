#!/usr/bin/env python3
"""Arrival Price Algorithm - Minimize cost vs arrival price"""
from datetime import datetime
from typing import Dict

class ArrivalPriceAlgorithmBot:
    def __init__(self):
        self.name = "Arrival_Price_Algorithm"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'executions': 0, 'avg_slippage': 0}
    
    def calculate_execution_schedule(self, total_size: float, arrival_price: float, 
                                     urgency: float = 0.5) -> Dict:
        """Calculate optimal execution to minimize cost vs arrival price"""
        
        # Higher urgency = faster execution (more slippage)
        # Lower urgency = slower execution (less slippage, more risk)
        
        n_slices = int(10 * (1 - urgency) + 2)  # 2-12 slices
        execution_time = int(60 * (1 - urgency) + 5)  # 5-65 minutes
        
        slice_size = total_size / n_slices
        
        schedule = []
        for i in range(n_slices):
            expected_slippage = urgency * 0.001 * (i + 1)  # Increasing slippage
            expected_price = arrival_price * (1 + expected_slippage)
            
            schedule.append({
                'slice': i + 1,
                'size': slice_size,
                'time_offset_min': i * (execution_time / n_slices),
                'expected_price': expected_price,
                'expected_slippage_pct': expected_slippage * 100
            })
        
        total_expected_cost = sum([s['size'] * s['expected_price'] for s in schedule])
        arrival_cost = total_size * arrival_price
        expected_vs_arrival = ((total_expected_cost - arrival_cost) / arrival_cost * 100) if arrival_cost > 0 else 0
        
        self.metrics['executions'] += 1
        
        return {
            'total_size': total_size,
            'n_slices': n_slices,
            'execution_time_min': execution_time,
            'arrival_price': arrival_price,
            'expected_avg_price': total_expected_cost / total_size if total_size > 0 else 0,
            'expected_vs_arrival_pct': expected_vs_arrival,
            'schedule': schedule,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = ArrivalPriceAlgorithmBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
