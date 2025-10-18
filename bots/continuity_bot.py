#!/usr/bin/env python3
"""
Continuity Bot - Long-Term Position Holder
Holds positions through market cycles
Part of APEX AI Trading System - ATN
"""

import os, sys, json
from datetime import datetime, timedelta
from typing import Dict, List
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class ContinuityBot:
    def __init__(self, exchange_config=None):
        self.name, self.version = "ContinuityBot", "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({'apiKey': os.getenv('EXCHANGE_API_KEY'), 'secret': os.getenv('EXCHANGE_API_SECRET'), 'enableRateLimit': True})
        
        self.config = {'min_hold_hours': 24, 'profit_target_pct': 15.0, 'max_loss_pct': 10.0}
        self.positions = {}
        self.metrics = {'long_term_trades': 0, 'avg_hold_hours': 0.0}
    
    def should_close_position(self, pos_id: str, current_price: float) -> Dict:
        if pos_id not in self.positions: return {'should_close': False}
        
        pos = self.positions[pos_id]
        entry_time = datetime.fromisoformat(pos['entry_time'])
        hours_held = (datetime.now() - entry_time).total_seconds() / 3600
        
        profit_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
        
        should_close = hours_held >= self.config['min_hold_hours'] and (profit_pct >= self.config['profit_target_pct'] or profit_pct <= -self.config['max_loss_pct'])
        
        return {'should_close': should_close, 'hours_held': hours_held, 'profit_pct': profit_pct, 'reason': 'Target reached' if profit_pct >= self.config['profit_target_pct'] else 'Stop-loss' if profit_pct <= -self.config['max_loss_pct'] else 'Still holding'}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'active_positions': len(self.positions), 'metrics': self.metrics}

if __name__ == '__main__':
    bot = ContinuityBot()
    print("🔄 Continuity Bot - Test\n")
    print(f"Min hold: {bot.config['min_hold_hours']}h, Target: {bot.config['profit_target_pct']}%")
