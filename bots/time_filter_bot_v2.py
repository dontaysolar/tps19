#!/usr/bin/env python3
"""Time Filter Bot v2.0 - Trading Hours Restriction | AEGIS"""
import os, sys
from datetime import datetime, time
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class TimeFilterBot(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="TIME_FILTER_BOT", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.config = {'trading_start_hour': 9, 'trading_end_hour': 17, 'trade_weekends': False}
        self.metrics.update({'total_checks': 0, 'allowed_trades': 0, 'blocked_trades': 0})
    
    def is_trading_hours(self) -> bool:
        now = datetime.now()
        self.metrics['total_checks'] += 1
        if not self.config['trade_weekends'] and now.weekday() >= 5:
            self.metrics['blocked_trades'] += 1
            return False
        if not (self.config['trading_start_hour'] <= now.hour <= self.config['trading_end_hour']):
            self.metrics['blocked_trades'] += 1
            return False
        self.metrics['allowed_trades'] += 1
        return True

if __name__ == '__main__':
    bot = TimeFilterBot()
    print(f"Trading hours: {bot.is_trading_hours()}")
    bot.close()
    print("✅ Time Filter Bot v2.0 complete!")
