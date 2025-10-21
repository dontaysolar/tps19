#!/usr/bin/env python3
"""
Continuity Bot v2.0 - Long-Term Position Holder
MIGRATED TO AEGIS ARCHITECTURE
Holds positions through market cycles
"""

import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class ContinuityBot(TradingBotBase):
    def __init__(self, exchange_config=None):
        super().__init__(
            bot_name="CONTINUITY_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        assert hasattr(self, 'exchange_adapter'), "Base init failed"
        self.config = {'min_hold_hours': 24, 'profit_target_pct': 15.0, 'max_loss_pct': 10.0}
        self.metrics.update({'long_term_trades': 0, 'avg_hold_hours': 0.0})
    
    def should_close_position(self, position: Dict, current_price: float) -> Dict:
        assert isinstance(position, dict), "Position must be dict"
        assert current_price > 0, "Price must be positive"
        
        entry_time = datetime.fromisoformat(position['created_at'])
        hours_held = (datetime.now() - entry_time).total_seconds() / 3600
        profit_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
        
        should_close = hours_held >= self.config['min_hold_hours'] and (
            profit_pct >= self.config['profit_target_pct'] or 
            profit_pct <= -self.config['max_loss_pct']
        )
        
        result = {
            'should_close': should_close,
            'hours_held': hours_held,
            'profit_pct': profit_pct,
            'reason': 'Target reached' if profit_pct >= self.config['profit_target_pct'] else 
                     'Stop-loss' if profit_pct <= -self.config['max_loss_pct'] else 'Still holding'
        }
        assert isinstance(result, dict), "Result must be dict"
        return result

if __name__ == '__main__':
    print("🔄 Continuity Bot v2.0 - Test")
    bot = ContinuityBot()
    print(f"Min hold: {bot.config['min_hold_hours']}h")
    bot.close()
    print("✅ Continuity Bot v2.0 migration complete!")
