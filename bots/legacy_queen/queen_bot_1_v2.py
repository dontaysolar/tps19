#!/usr/bin/env python3
"""Queen Bot #1 v2.0 | AEGIS"""
import os, sys
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class QueenBot1(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="QUEEN_BOT_1", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.current_mode = 'SCALPING'
    
    def switch_mode(self, new_mode: str) -> Dict:
        self.current_mode = new_mode
        return {'success': True}

if __name__ == '__main__':
    bot = QueenBot1()
    bot.close()
    print("✅ Queen Bot #1 v2.0 complete!")
