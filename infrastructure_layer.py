#!/usr/bin/env python3
"""
INFRASTRUCTURE LAYER
All system infrastructure consolidated
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Callable
from collections import deque

class InfrastructureLayer:
    """System infrastructure services"""
    
    def __init__(self):
        self.name = "Infrastructure_Layer"
        self.version = "1.0.0"
        
        self.cache = CacheManager()
        self.logger = LogManager()
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.health_monitor = HealthMonitor()
        self.notifications = NotificationManager()

class CacheManager:
    """Redis-like caching"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}
        
    def set(self, key: str, value, ttl: int = 300):
        """Set cache value"""
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
    
    def get(self, key: str):
        """Get cache value"""
        if key in self.cache:
            if time.time() < self.ttl.get(key, 0):
                return self.cache[key]
            else:
                del self.cache[key]
                del self.ttl[key]
        return None

class LogManager:
    """Centralized logging"""
    
    def __init__(self):
        self.logs = deque(maxlen=1000)
        
    def log(self, level: str, message: str, component: str = 'SYSTEM'):
        """Write log entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'component': component,
            'message': message
        }
        self.logs.append(entry)
        print(f"[{level}] {component}: {message}")
    
    def info(self, message: str, component: str = 'SYSTEM'):
        self.log('INFO', message, component)
    
    def warning(self, message: str, component: str = 'SYSTEM'):
        self.log('WARNING', message, component)
    
    def error(self, message: str, component: str = 'SYSTEM'):
        self.log('ERROR', message, component)
    
    def get_recent(self, n: int = 100):
        """Get recent logs"""
        return list(self.logs)[-n:]

class RateLimiter:
    """API rate limiting"""
    
    def __init__(self):
        self.requests_per_second = 10
        self.requests_per_minute = 100
        self.second_window = deque(maxlen=self.requests_per_second)
        self.minute_window = deque(maxlen=self.requests_per_minute)
    
    def check(self) -> Dict:
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
            return {'allowed': False, 'wait_seconds': 1}
        
        if len(self.minute_window) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_window[0])
            return {'allowed': False, 'wait_seconds': max(0, wait_time)}
        
        # Allow request
        self.second_window.append(current_time)
        self.minute_window.append(current_time)
        
        return {'allowed': True}

class CircuitBreaker:
    """Circuit breaker pattern"""
    
    def __init__(self):
        self.failures = []
        self.circuit_open = False
        self.open_time = None
        self.failure_threshold = 5
        self.cooldown_seconds = 300
    
    def record_failure(self, error_type: str = 'UNKNOWN'):
        """Record a failure"""
        self.failures.append(time.time())
        
        # Clean old failures (>5 minutes)
        cutoff = time.time() - 300
        self.failures = [f for f in self.failures if f > cutoff]
        
        # Trip circuit if too many recent failures
        if len(self.failures) >= self.failure_threshold:
            self.circuit_open = True
            self.open_time = time.time()
    
    def check(self) -> Dict:
        """Check circuit breaker status"""
        if not self.circuit_open:
            return {'allowed': True, 'status': 'CLOSED'}
        
        # Check if cooldown expired
        if time.time() > self.open_time + self.cooldown_seconds:
            self.circuit_open = False
            self.open_time = None
            self.failures = []
            return {'allowed': True, 'status': 'RESET'}
        
        return {
            'allowed': False,
            'status': 'OPEN',
            'cooldown_remaining': self.cooldown_seconds - (time.time() - self.open_time)
        }

class HealthMonitor:
    """System health monitoring"""
    
    def check_health(self) -> Dict:
        """Basic health check"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            
            if cpu > 80 or memory > 85:
                status = 'WARNING'
            else:
                status = 'HEALTHY'
            
            return {
                'status': status,
                'cpu_percent': cpu,
                'memory_percent': memory
            }
        except:
            return {'status': 'UNKNOWN', 'error': 'psutil not available'}

class NotificationManager:
    """Unified notifications"""
    
    def __init__(self):
        self.channels = {}
        
    def send(self, message: str, priority: str = 'NORMAL'):
        """Send notification to all configured channels"""
        # Placeholder - would send to Telegram, Discord, etc
        print(f"[NOTIFICATION - {priority}] {message}")

if __name__ == '__main__':
    layer = AIMLLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
