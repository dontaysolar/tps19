#!/usr/bin/env python3
"""Queen Bot #1 - Adaptable Trading Specialist
Can switch between scalping, trend-following, mean-reversion modes
Part of APEX ATN Layer"""
import os, sys, json
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class QueenBot1:
    def __init__(self):
        self.name, self.version = "Queen_Bot_1", "1.0.0"
        self.current_mode = 'SCALPING'
        self.modes = ['SCALPING', 'TREND_FOLLOWING', 'MEAN_REVERSION']
        self.metrics = {'mode_switches': 0, 'trades_executed': 0}
    
    def switch_mode(self, new_mode: str, reason: str = '') -> Dict:
        if new_mode not in self.modes:
            return {'success': False, 'error': 'Invalid mode'}
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.metrics['mode_switches'] += 1
        return {'success': True, 'old_mode': old_mode, 'new_mode': new_mode, 'reason': reason}
    
    def execute_in_current_mode(self, signal_data: Dict) -> Dict:
        self.metrics['trades_executed'] += 1
        return {'mode': self.current_mode, 'signal': signal_data.get('signal', 'HOLD'), 'executed': True}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'current_mode': self.current_mode, 'metrics': self.metrics}

if __name__ == '__main__':
    print("👑 Queen Bot #1 - Adaptable Specialist")
