#!/usr/bin/env python3
"""KING BOT v2.0 - Master Commander | AEGIS"""
import os, sys
from datetime import datetime
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class KINGBot(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="KING_BOT", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.profiles = {
            'GORILLA': {'risk': 'HIGH', 'volume': 'MAX', 'confidence_min': 0.95},
            'FOX': {'risk': 'LOW', 'volume': 'MIN', 'confidence_min': 0.98},
            'SCHOLAR': {'risk': 'ZERO', 'volume': 'ZERO', 'confidence_min': 1.0},
            'GUARDIAN': {'risk': 'LOW', 'volume': 'LOW', 'confidence_min': 0.85}
        }
        self.active_profile = 'GUARDIAN'
        self.bot_assignments = {}
        self.metrics.update({'profile_switches': 0, 'commands_executed': 0, 'bots_deployed': 0})
    
    def switch_profile(self, new_profile: str, reason: str = '') -> Dict:
        assert len(new_profile) > 0, "Profile required"
        if new_profile not in self.profiles:
            return {'success': False, 'error': f'Invalid profile: {new_profile}'}
        old_profile = self.active_profile
        self.active_profile = new_profile
        self.metrics['profile_switches'] += 1
        result = {'success': True, 'old_profile': old_profile, 'new_profile': new_profile, 'reason': reason, 'config': self.profiles[new_profile], 'timestamp': datetime.now().isoformat()}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def deploy_bot(self, bot_name: str, symbol: str, profile: str = None) -> Dict:
        assert len(bot_name) > 0 and len(symbol) > 0, "Bot name and symbol required"
        target_profile = profile or self.active_profile
        self.bot_assignments[symbol] = {'bot': bot_name, 'profile': target_profile, 'deployed_at': datetime.now().isoformat()}
        self.metrics['bots_deployed'] += 1
        result = {'deployed': True, 'bot': bot_name, 'symbol': symbol, 'profile': target_profile, 'config': self.profiles[target_profile]}
        assert isinstance(result, dict), "Result must be dict"
        return result

if __name__ == '__main__':
    bot = KINGBot()
    bot.switch_profile('GORILLA', 'Bull market')
    bot.deploy_bot('MomentumRider', 'BTC/USDT')
    bot.close()
    print("✅ KING BOT v2.0 complete!")
