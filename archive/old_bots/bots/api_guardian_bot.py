#!/usr/bin/env python3
"""
API Guardian Bot
Manages API rate limits and prevents abuse
Part of APEX AI Trading System
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from collections import deque
from typing import Dict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

class APIGuardianBot:
    """Protects against API rate limit violations"""
    
    def __init__(self):
        self.name = "APIGuardianBot"
        self.version = "1.0.0"
        
        self.config = {
            'max_requests_per_minute': 100,
            'max_requests_per_second': 10,
            'cooldown_on_limit': 60,          # 60s cooldown if limit hit
            'warning_threshold_pct': 80.0     # Warn at 80% of limit
        }
        
        self.request_history = {
            'minute': deque(maxlen=100),
            'second': deque(maxlen=10)
        }
        
        self.state = {
            'rate_limited': False,
            'cooldown_until': None
        }
        
        self.metrics = {
            'total_requests': 0,
            'requests_blocked': 0,
            'rate_limit_hits': 0,
            'avg_requests_per_minute': 0.0
        }
    
    def can_make_request(self) -> Dict:
        """Check if API request is allowed"""
        now = datetime.now()
        
        # Check if in cooldown
        if self.state['cooldown_until']:
            cooldown_end = datetime.fromisoformat(self.state['cooldown_until'])
            if now < cooldown_end:
                return {
                    'allowed': False,
                    'reason': 'Rate limit cooldown',
                    'cooldown_remaining': (cooldown_end - now).total_seconds()
                }
            else:
                self.state['rate_limited'] = False
                self.state['cooldown_until'] = None
        
        # Clean old requests
        cutoff_minute = now - timedelta(minutes=1)
        cutoff_second = now - timedelta(seconds=1)
        
        self.request_history['minute'] = deque(
            [t for t in self.request_history['minute'] if t > cutoff_minute],
            maxlen=100
        )
        self.request_history['second'] = deque(
            [t for t in self.request_history['second'] if t > cutoff_second],
            maxlen=10
        )
        
        # Check limits
        requests_this_minute = len(self.request_history['minute'])
        requests_this_second = len(self.request_history['second'])
        
        # Check per-second limit
        if requests_this_second >= self.config['max_requests_per_second']:
            self.metrics['requests_blocked'] += 1
            return {
                'allowed': False,
                'reason': 'Per-second limit reached',
                'wait_time': 1.0
            }
        
        # Check per-minute limit
        if requests_this_minute >= self.config['max_requests_per_minute']:
            self.metrics['requests_blocked'] += 1
            self.metrics['rate_limit_hits'] += 1
            
            # Enter cooldown
            self.state['rate_limited'] = True
            self.state['cooldown_until'] = (now + timedelta(seconds=self.config['cooldown_on_limit'])).isoformat()
            
            return {
                'allowed': False,
                'reason': 'Per-minute limit reached',
                'cooldown': self.config['cooldown_on_limit']
            }
        
        # Check warning threshold
        usage_pct = (requests_this_minute / self.config['max_requests_per_minute']) * 100
        if usage_pct >= self.config['warning_threshold_pct']:
            return {
                'allowed': True,
                'warning': f'API usage at {usage_pct:.0f}%',
                'requests_remaining': self.config['max_requests_per_minute'] - requests_this_minute
            }
        
        return {'allowed': True}
    
    def record_request(self) -> None:
        """Record an API request"""
        now = datetime.now()
        self.request_history['minute'].append(now)
        self.request_history['second'].append(now)
        self.metrics['total_requests'] += 1
        
        # Update average
        if self.metrics['total_requests'] > 0:
            self.metrics['avg_requests_per_minute'] = len(self.request_history['minute'])
    
    def get_api_usage(self) -> Dict:
        """Get current API usage statistics"""
        requests_this_minute = len(self.request_history['minute'])
        requests_this_second = len(self.request_history['second'])
        
        return {
            'requests_this_minute': requests_this_minute,
            'requests_this_second': requests_this_second,
            'limit_minute': self.config['max_requests_per_minute'],
            'limit_second': self.config['max_requests_per_second'],
            'usage_pct': (requests_this_minute / self.config['max_requests_per_minute']) * 100,
            'rate_limited': self.state['rate_limited'],
            'cooldown_until': self.state['cooldown_until']
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'state': self.state,
            'metrics': self.metrics,
            'current_usage': self.get_api_usage()
        }

if __name__ == '__main__':
    bot = APIGuardianBot()
    print("🛡️ API Guardian Bot - Test Mode\n")
    
    # Simulate requests
    for i in range(5):
        check = bot.can_make_request()
        if check['allowed']:
            bot.record_request()
            print(f"Request {i+1}: ✅ Allowed")
        else:
            print(f"Request {i+1}: ❌ {check['reason']}")
    
    usage = bot.get_api_usage()
    print(f"\nAPI Usage: {usage['requests_this_minute']}/{usage['limit_minute']} ({usage['usage_pct']:.1f}%)")
