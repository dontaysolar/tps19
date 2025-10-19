#!/usr/bin/env python3
"""Queen Bot #2 - Adaptable Specialist"""
import os, sys, json
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class QueenBot2:
    def __init__(self):
        self.name, self.version = "Queen_Bot_2", "1.0.0"
        self.current_mode = 'TREND_FOLLOWING'
        self.modes = ['SCALPING', 'TREND_FOLLOWING', 'BREAKOUT']
        self.metrics = {'mode_switches': 0, 'trades_executed': 0}
    
    def switch_mode(self, new_mode: str) -> Dict:
        if new_mode in self.modes:
            self.current_mode = new_mode
            self.metrics['mode_switches'] += 1
            return {'success': True, 'new_mode': new_mode}
        return {'success': False}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'current_mode': self.current_mode, 'metrics': self.metrics}

if __name__ == '__main__':
    print("👑 Queen Bot #2")
