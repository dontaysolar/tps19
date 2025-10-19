#!/usr/bin/env python3
"""Dynamic Leverage Manager - Risk-adjusted leverage control"""
import numpy as np
from datetime import datetime
from typing import Dict

class DynamicLeverageManagerBot:
    def __init__(self):
        self.name = "Dynamic_Leverage_Manager"
        self.version = "1.0.0"
        self.enabled = True
        
        self.max_leverage = 3.0
        self.min_leverage = 1.0
        
        self.metrics = {'adjustments': 0, 'max_leverage_used': 1.0}
    
    def calculate_optimal_leverage(self, win_rate: float, avg_win: float, avg_loss: float,
                                  current_volatility: float, account_health: float) -> Dict:
        """Calculate optimal leverage based on conditions"""
        
        # Base leverage from Kelly Criterion
        if avg_loss > 0:
            win_loss_ratio = avg_win / avg_loss
            kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            base_leverage = 1 + max(0, min(kelly, 0.5)) * 2  # 1x to 2x
        else:
            base_leverage = 1.0
        
        # Adjust for volatility (reduce in high vol)
        if current_volatility > 0.05:
            volatility_adj = 0.5
        elif current_volatility > 0.03:
            volatility_adj = 0.75
        else:
            volatility_adj = 1.0
        
        # Adjust for account health (reduce if unhealthy)
        health_adj = max(0.5, account_health)
        
        # Final leverage
        optimal_leverage = base_leverage * volatility_adj * health_adj
        optimal_leverage = max(self.min_leverage, min(self.max_leverage, optimal_leverage))
        
        self.metrics['adjustments'] += 1
        self.metrics['max_leverage_used'] = max(self.metrics['max_leverage_used'], optimal_leverage)
        
        return {
            'optimal_leverage': optimal_leverage,
            'base_leverage': base_leverage,
            'volatility_adjustment': volatility_adj,
            'health_adjustment': health_adj,
            'max_position_multiplier': optimal_leverage,
            'current_volatility': current_volatility,
            'recommendation': f"Use {optimal_leverage:.2f}x leverage",
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'max_leverage': self.max_leverage,
            'min_leverage': self.min_leverage,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = DynamicLeverageManagerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
