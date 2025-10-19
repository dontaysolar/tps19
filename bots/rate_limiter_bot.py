#!/usr/bin/env python3
"""Rate Limiter - Protects against API rate limits"""
import time
from datetime import datetime
from typing import Dict
from collections import deque

class RateLimiterBot:
    def __init__(self):
        self.name = "Rate_Limiter"
        self.version = "1.0.0"
        self.enabled = True
        
        self.requests_per_second = 10
        self.requests_per_minute = 100
        
        self.second_window = deque(maxlen=self.requests_per_second)
        self.minute_window = deque(maxlen=self.requests_per_minute)
        
        self.metrics = {'total_requests': 0, 'blocked_requests': 0, 'wait_time_total': 0}
    
    def check_rate_limit(self) -> Dict:
        """Check if request is allowed"""
        current_time = time.time()
        
        # Clean old entries
        cutoff_second = current_time - 1
        cutoff_minute = current_time - 60
        
        self.second_window = deque([t for t in self.second_window if t > cutoff_second], 
                                   maxlen=self.requests_per_second)
        self.minute_window = deque([t for t in self.minute_window if t > cutoff_minute],
                                   maxlen=self.requests_per_minute)
        
        # Check limits
        if len(self.second_window) >= self.requests_per_second:
            wait_time = 1 - (current_time - self.second_window[0])
            self.metrics['blocked_requests'] += 1
            return {
                'allowed': False,
                'reason': 'Per-second limit reached',
                'wait_seconds': max(0, wait_time),
                'requests_in_second': len(self.second_window)
            }
        
        if len(self.minute_window) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_window[0])
            self.metrics['blocked_requests'] += 1
            return {
                'allowed': False,
                'reason': 'Per-minute limit reached',
                'wait_seconds': max(0, wait_time),
                'requests_in_minute': len(self.minute_window)
            }
        
        # Allow request
        self.second_window.append(current_time)
        self.minute_window.append(current_time)
        self.metrics['total_requests'] += 1
        
        return {
            'allowed': True,
            'requests_in_second': len(self.second_window),
            'requests_in_minute': len(self.minute_window),
            'remaining_per_second': self.requests_per_second - len(self.second_window),
            'remaining_per_minute': self.requests_per_minute - len(self.minute_window)
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'limits': {
                'per_second': self.requests_per_second,
                'per_minute': self.requests_per_minute
            },
            'current_usage': {
                'second': len(self.second_window),
                'minute': len(self.minute_window)
            },
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = RateLimiterBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
