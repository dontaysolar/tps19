#!/usr/bin/env python3
"""
Time Filter Bot
Restricts trading to high-volume hours
Part of APEX AI Trading System
"""

import os
from datetime import datetime, time
import pytz

class TimeFilterBot:
    """Filters trading based on time of day and day of week"""
    
    def __init__(self):
        self.name = "TimeFilterBot"
        self.version = "1.0.0"
        
        # Trading hours in EST/EDT
        self.config = {
            'timezone': 'America/New_York',
            'trading_start': time(9, 0),   # 9 AM EST
            'trading_end': time(17, 0),    # 5 PM EST
            'trade_weekends': False,
            'trade_holidays': False
        }
        
        self.metrics = {
            'total_checks': 0,
            'allowed_trades': 0,
            'blocked_trades': 0
        }
    
    def is_trading_hours(self) -> bool:
        """Check if current time is within trading hours"""
        tz = pytz.timezone(self.config['timezone'])
        now = datetime.now(tz)
        
        self.metrics['total_checks'] += 1
        
        # Check day of week
        if not self.config['trade_weekends'] and now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            self.metrics['blocked_trades'] += 1
            return False
        
        # Check time of day
        current_time = now.time()
        if not (self.config['trading_start'] <= current_time <= self.config['trading_end']):
            self.metrics['blocked_trades'] += 1
            return False
        
        self.metrics['allowed_trades'] += 1
        return True
    
    def get_next_trading_window(self) -> datetime:
        """Get next available trading window"""
        tz = pytz.timezone(self.config['timezone'])
        now = datetime.now(tz)
        
        # If weekend, wait until Monday
        if now.weekday() >= 5:
            days_until_monday = (7 - now.weekday()) if now.weekday() == 6 else 1
            next_window = now.replace(hour=self.config['trading_start'].hour, minute=0) + timedelta(days=days_until_monday)
        else:
            # If after trading hours, next day
            if now.time() > self.config['trading_end']:
                next_window = now.replace(hour=self.config['trading_start'].hour, minute=0) + timedelta(days=1)
            else:
                next_window = now.replace(hour=self.config['trading_start'].hour, minute=0)
        
        return next_window
    
    def get_status(self):
        """Get filter status"""
        return {
            'name': self.name,
            'version': self.version,
            'currently_trading_hours': self.is_trading_hours(),
            'config': self.config,
            'metrics': self.metrics
        }
