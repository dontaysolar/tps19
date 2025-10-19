#!/usr/bin/env python3
"""Portfolio Rebalancer - Maintains target allocations"""
import numpy as np
from datetime import datetime
from typing import Dict

class PortfolioRebalancerBot:
    def __init__(self):
        self.name = "Portfolio_Rebalancer"
        self.version = "1.0.0"
        self.enabled = True
        
        self.rebalance_threshold = 0.05  # 5% drift triggers rebalance
        self.metrics = {'rebalances': 0, 'trades_executed': 0}
    
    def calculate_rebalancing_trades(self, target_allocation: Dict, current_allocation: Dict,
                                    total_value: float) -> Dict:
        """Calculate trades needed to rebalance portfolio"""
        trades = []
        
        for asset, target_pct in target_allocation.items():
            current_pct = current_allocation.get(asset, 0)
            drift = abs(current_pct - target_pct)
            
            if drift > self.rebalance_threshold:
                target_value = total_value * target_pct
                current_value = total_value * current_pct
                trade_value = target_value - current_value
                
                trades.append({
                    'asset': asset,
                    'action': 'BUY' if trade_value > 0 else 'SELL',
                    'amount': abs(trade_value),
                    'current_pct': current_pct * 100,
                    'target_pct': target_pct * 100,
                    'drift_pct': drift * 100
                })
        
        self.metrics['rebalances'] += 1
        self.metrics['trades_executed'] += len(trades)
        
        return {
            'rebalancing_needed': len(trades) > 0,
            'trades': trades,
            'total_trades': len(trades),
            'total_value_adjusted': sum([t['amount'] for t in trades]),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'rebalance_threshold': self.rebalance_threshold * 100, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = PortfolioRebalancerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
