#!/usr/bin/env python3
"""Triangular Arbitrage - Multi-leg cross-exchange arbitrage"""
import numpy as np
from datetime import datetime
from typing import Dict, List

class TriangularArbitrageBot:
    def __init__(self):
        self.name = "Triangular_Arbitrage"
        self.version = "1.0.0"
        self.enabled = True
        
        self.min_profit_pct = 0.003  # 0.3% minimum profit
        
        self.metrics = {'opportunities': 0, 'executed': 0}
    
    def find_triangular_opportunity(self, pair_a: str, pair_b: str, pair_c: str,
                                   price_a: float, price_b: float, price_c: float) -> Dict:
        """Find triangular arbitrage opportunity
        
        Example: BTC/USDT -> ETH/BTC -> ETH/USDT
        """
        
        # Calculate triangular path profit
        # Start with 1 unit of base currency
        initial_amount = 1.0
        
        # Trade 1: Base -> A
        amount_after_1 = initial_amount * price_a
        
        # Trade 2: A -> B
        amount_after_2 = amount_after_1 * price_b
        
        # Trade 3: B -> Base
        final_amount = amount_after_2 * price_c
        
        # Calculate profit
        profit = final_amount - initial_amount
        profit_pct = (profit / initial_amount) * 100
        
        # Account for fees (assume 0.1% per trade, 3 trades = 0.3%)
        fees_pct = 0.3
        net_profit_pct = profit_pct - fees_pct
        
        if net_profit_pct > self.min_profit_pct * 100:
            self.metrics['opportunities'] += 1
            
            return {
                'opportunity': True,
                'path': f"{pair_a} -> {pair_b} -> {pair_c}",
                'gross_profit_pct': profit_pct,
                'fees_pct': fees_pct,
                'net_profit_pct': net_profit_pct,
                'prices': {
                    'pair_a': price_a,
                    'pair_b': price_b,
                    'pair_c': price_c
                },
                'signal': 'EXECUTE',
                'confidence': 0.90,
                'reason': f"Tri-arb profit: {net_profit_pct:.3f}%",
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'opportunity': False,
            'net_profit_pct': net_profit_pct,
            'reason': 'Profit below threshold'
        }
    
    def calculate_optimal_size(self, opportunity: Dict, available_capital: float,
                              liquidity_limits: List[float]) -> Dict:
        """Calculate optimal position size for tri-arb"""
        
        # Limited by smallest liquidity in path
        max_size_by_liquidity = min(liquidity_limits)
        
        # Limited by capital
        max_size_by_capital = available_capital * 0.20  # Use max 20% per arb
        
        optimal_size = min(max_size_by_liquidity, max_size_by_capital)
        
        net_profit_pct = opportunity.get('net_profit_pct', 0) / 100
        expected_profit = optimal_size * net_profit_pct
        
        return {
            'optimal_size': optimal_size,
            'expected_profit': expected_profit,
            'limited_by': 'liquidity' if max_size_by_liquidity < max_size_by_capital else 'capital',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'min_profit_pct': self.min_profit_pct * 100,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = TriangularArbitrageBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
