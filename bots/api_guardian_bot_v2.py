#!/usr/bin/env python3
"""API Guardian Bot v2.0 - API Rate Limit Protection | AEGIS"""
import os, sys, time
from datetime import datetime, timedelta
from collections import deque
from typing import Dict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase

class APIGuardianBot(TradingBotBase):
    def __init__(self):
        super().__init__(bot_name="API_GUARDIAN_BOT", bot_version="2.0.0", exchange_name='mock', enable_psm=False, enable_logging=False)
        self.config = {'max_requests_per_minute': 100, 'max_requests_per_second': 10, 'cooldown_on_limit': 60, 'warning_threshold_pct': 80.0}
        self.request_history = {'minute': deque(maxlen=100), 'second': deque(maxlen=10)}
        self.state = {'rate_limited': False, 'cooldown_until': None}
        self.metrics.update({'total_requests': 0, 'requests_blocked': 0, 'rate_limit_hits': 0})
    
    def can_make_request(self) -> Dict:
        now = datetime.now()
        if self.state['cooldown_until']:
            cooldown_end = datetime.fromisoformat(self.state['cooldown_until'])
            if now < cooldown_end:
                return {'allowed': False, 'reason': 'Cooldown', 'cooldown_remaining': (cooldown_end - now).total_seconds()}
            else:
                self.state['rate_limited'] = False
                self.state['cooldown_until'] = None
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_second = now - timedelta(seconds=1)
        self.request_history['minute'] = deque([t for t in self.request_history['minute'] if t > cutoff_minute], maxlen=100)
        self.request_history['second'] = deque([t for t in self.request_history['second'] if t > cutoff_second], maxlen=10)
        requests_this_minute = len(self.request_history['minute'])
        requests_this_second = len(self.request_history['second'])
        if requests_this_second >= self.config['max_requests_per_second']:
            self.metrics['requests_blocked'] += 1
            return {'allowed': False, 'reason': 'Per-second limit', 'wait_time': 1.0}
        if requests_this_minute >= self.config['max_requests_per_minute']:
            self.metrics['requests_blocked'] += 1
            self.state['rate_limited'] = True
            self.state['cooldown_until'] = (now + timedelta(seconds=self.config['cooldown_on_limit'])).isoformat()
            self.metrics['rate_limit_hits'] += 1
            return {'allowed': False, 'reason': 'Per-minute limit', 'cooldown_seconds': self.config['cooldown_on_limit']}
        warning = False
        if requests_this_minute >= (self.config['max_requests_per_minute'] * self.config['warning_threshold_pct'] / 100):
            warning = True
        result = {'allowed': True, 'warning': warning, 'requests_this_minute': requests_this_minute, 'requests_remaining': self.config['max_requests_per_minute'] - requests_this_minute}
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def record_request(self):
        now = datetime.now()
        self.request_history['minute'].append(now)
        self.request_history['second'].append(now)
        self.metrics['total_requests'] += 1

if __name__ == '__main__':
    bot = APIGuardianBot()
    check = bot.can_make_request()
    print(f"Request allowed: {check['allowed']}")
    if check['allowed']:
        bot.record_request()
    bot.close()
    print("✅ API Guardian Bot v2.0 complete!")
