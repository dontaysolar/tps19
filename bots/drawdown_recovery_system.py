#!/usr/bin/env python3
"""Drawdown Recovery System - Fast recovery from losses"""
from datetime import datetime
from typing import Dict

class DrawdownRecoverySystem:
    def __init__(self):
        self.name = "Drawdown_Recovery_System"
        self.version = "1.0.0"
        self.enabled = True
        
        self.max_drawdown_threshold = 0.15  # 15%
        self.recovery_mode_active = False
        
        self.metrics = {'drawdowns': 0, 'recoveries': 0, 'avg_recovery_time': 0}
    
    def assess_drawdown(self, current_equity: float, peak_equity: float) -> Dict:
        """Assess current drawdown"""
        drawdown = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0
        drawdown_pct = drawdown * 100
        
        if drawdown > self.max_drawdown_threshold:
            self.recovery_mode_active = True
            self.metrics['drawdowns'] += 1
            
            # Recovery strategy
            if drawdown > 0.25:  # >25% drawdown
                strategy = 'AGGRESSIVE_RECOVERY'
                position_size_mult = 0.5  # Reduce size 50%
                selectivity = 'VERY_HIGH'
            elif drawdown > 0.15:
                strategy = 'MODERATE_RECOVERY'
                position_size_mult = 0.75
                selectivity = 'HIGH'
            else:
                strategy = 'NORMAL'
                position_size_mult = 1.0
                selectivity = 'NORMAL'
        else:
            self.recovery_mode_active = False
            strategy = 'NORMAL'
            position_size_mult = 1.0
            selectivity = 'NORMAL'
        
        return {
            'current_equity': current_equity,
            'peak_equity': peak_equity,
            'drawdown_pct': drawdown_pct,
            'recovery_mode': self.recovery_mode_active,
            'recovery_strategy': strategy,
            'position_size_multiplier': position_size_mult,
            'selectivity': selectivity,
            'distance_to_peak_pct': drawdown_pct,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'recovery_mode_active': self.recovery_mode_active, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    system = DrawdownRecoverySystem()
    print(f"✅ {system.name} v{system.version} initialized")
