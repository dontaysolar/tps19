#!/usr/bin/env python3
"""
Iceberg Order Execution Bot
Hides large orders by showing only small visible portions
Minimizes market impact
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class IcebergOrderBot:
    def __init__(self):
        self.name = "Iceberg_Order"
        self.version = "1.0.0"
        self.enabled = True
        
        self.visible_ratio = 0.10  # Show 10% of total order
        self.min_visible_size = 0.1
        
        self.metrics = {'orders_executed': 0, 'total_volume': 0, 'avg_execution_price': 0}
    
    def create_iceberg_order(self, total_size: float, side: str, limit_price: float = None) -> Dict:
        """Create iceberg order structure"""
        visible_size = max(total_size * self.visible_ratio, self.min_visible_size)
        n_slices = int(np.ceil(total_size / visible_size))
        
        slices = []
        remaining = total_size
        
        for i in range(n_slices):
            slice_size = min(visible_size, remaining)
            slices.append({
                'slice_id': i + 1,
                'size': slice_size,
                'side': side,
                'limit_price': limit_price,
                'status': 'PENDING',
                'filled_size': 0,
                'avg_price': 0
            })
            remaining -= slice_size
        
        self.metrics['orders_executed'] += 1
        
        return {
            'total_size': total_size,
            'visible_size': visible_size,
            'hidden_size': total_size - visible_size,
            'n_slices': n_slices,
            'slices': slices,
            'side': side,
            'limit_price': limit_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_slice(self, slice_data: Dict, market_price: float) -> Dict:
        """Execute one slice of iceberg order"""
        if slice_data['status'] != 'PENDING':
            return {'error': 'Slice already executed'}
        
        execution_price = min(market_price, slice_data['limit_price']) if slice_data['limit_price'] else market_price
        
        slice_data['status'] = 'FILLED'
        slice_data['filled_size'] = slice_data['size']
        slice_data['avg_price'] = execution_price
        
        self.metrics['total_volume'] += slice_data['size']
        
        return {
            'executed': True,
            'slice_id': slice_data['slice_id'],
            'size': slice_data['size'],
            'price': execution_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'visible_ratio': self.visible_ratio,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = IcebergOrderBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
