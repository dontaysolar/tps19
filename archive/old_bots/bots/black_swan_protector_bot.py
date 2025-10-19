#!/usr/bin/env python3
"""
Black Swan Protector Bot
Hedges against extreme tail risk events
Protects portfolio from catastrophic losses
"""

import numpy as np
from datetime import datetime
from typing import Dict

class BlackSwanProtectorBot:
    def __init__(self):
        self.name = "Black_Swan_Protector"
        self.version = "1.0.0"
        self.enabled = True
        
        self.tail_risk_threshold = 0.01  # 1% tail events
        self.hedge_ratio = 0.05  # 5% of portfolio in hedges
        
        self.metrics = {'events_detected': 0, 'hedges_activated': 0, 'portfolio_saved': 0}
    
    def detect_tail_risk(self, returns: np.ndarray, current_volatility: float) -> Dict:
        """Detect potential black swan event"""
        if len(returns) < 20:
            return {'tail_risk': False}
        
        # Calculate kurtosis (fat tails)
        mean = np.mean(returns)
        std = np.std(returns)
        kurtosis = np.mean(((returns - mean) / std) ** 4) - 3
        
        # Extreme volatility spike
        historical_vol = np.std(returns[-100:]) if len(returns) >= 100 else std
        vol_spike = current_volatility / historical_vol if historical_vol > 0 else 1
        
        # Check for tail risk
        tail_risk_score = 0
        
        if kurtosis > 3:  # Fat tails
            tail_risk_score += 30
        
        if vol_spike > 2:  # 2x normal volatility
            tail_risk_score += 40
            
        if abs(returns[-1]) > 3 * std:  # 3-sigma move
            tail_risk_score += 30
            self.metrics['events_detected'] += 1
        
        is_tail_risk = tail_risk_score > 50
        
        return {
            'tail_risk': is_tail_risk,
            'tail_risk_score': tail_risk_score,
            'kurtosis': kurtosis,
            'volatility_spike': vol_spike,
            'recommended_action': 'ACTIVATE_HEDGES' if is_tail_risk else 'MONITOR',
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_hedge_allocation(self, portfolio_value: float) -> Dict:
        """Calculate optimal hedge allocation"""
        hedge_value = portfolio_value * self.hedge_ratio
        
        # Hedge portfolio allocation
        hedges = {
            'put_options': hedge_value * 0.40,  # 40% in protective puts
            'gold': hedge_value * 0.30,  # 30% in gold
            'volatility': hedge_value * 0.20,  # 20% in VIX
            'cash': hedge_value * 0.10  # 10% cash buffer
        }
        
        return {
            'total_hedge_allocation': hedge_value,
            'hedge_percentage': self.hedge_ratio * 100,
            'hedges': hedges,
            'timestamp': datetime.now().isoformat()
        }
    
    def activate_protection(self, severity: str) -> Dict:
        """Activate black swan protection"""
        self.metrics['hedges_activated'] += 1
        
        if severity == 'EXTREME':
            actions = ['CLOSE_ALL_POSITIONS', 'ACTIVATE_HEDGES', 'MOVE_TO_CASH']
            hedge_multiplier = 2.0
        elif severity == 'HIGH':
            actions = ['REDUCE_EXPOSURE_50%', 'ACTIVATE_HEDGES', 'TIGHTEN_STOPS']
            hedge_multiplier = 1.5
        else:
            actions = ['REDUCE_EXPOSURE_25%', 'MONITOR_CLOSELY']
            hedge_multiplier = 1.0
        
        return {
            'protection_activated': True,
            'severity': severity,
            'actions': actions,
            'hedge_multiplier': hedge_multiplier,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'tail_risk_threshold': self.tail_risk_threshold,
            'hedge_ratio': self.hedge_ratio,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = BlackSwanProtectorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
