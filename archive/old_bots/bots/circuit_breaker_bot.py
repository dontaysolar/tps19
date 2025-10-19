#!/usr/bin/env python3
"""Circuit Breaker - Stops trading on repeated failures"""
from datetime import datetime, timedelta
from typing import Dict

class CircuitBreakerBot:
    def __init__(self):
        self.name = "Circuit_Breaker"
        self.version = "1.0.0"
        self.enabled = True
        
        self.failure_threshold = 5
        self.cooldown_minutes = 10
        
        self.failures = []
        self.circuit_open = False
        self.open_time = None
        
        self.metrics = {'trips': 0, 'total_failures': 0}
    
    def record_failure(self, error_type: str = 'UNKNOWN') -> Dict:
        """Record a failure"""
        self.failures.append({
            'time': datetime.now(),
            'type': error_type
        })
        
        self.metrics['total_failures'] += 1
        
        # Remove old failures (>1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.failures = [f for f in self.failures if f['time'] > cutoff]
        
        # Check if should trip
        recent_failures = [f for f in self.failures 
                          if f['time'] > datetime.now() - timedelta(minutes=5)]
        
        if len(recent_failures) >= self.failure_threshold and not self.circuit_open:
            self.circuit_open = True
            self.open_time = datetime.now()
            self.metrics['trips'] += 1
            
            return {
                'circuit_tripped': True,
                'reason': f"{len(recent_failures)} failures in 5 minutes",
                'cooldown_minutes': self.cooldown_minutes,
                'resume_time': (self.open_time + timedelta(minutes=self.cooldown_minutes)).isoformat()
            }
        
        return {
            'circuit_tripped': False,
            'recent_failures': len(recent_failures),
            'threshold': self.failure_threshold
        }
    
    def check_circuit(self) -> Dict:
        """Check if circuit breaker is open"""
        if not self.circuit_open:
            return {'status': 'CLOSED', 'trading_allowed': True}
        
        # Check if cooldown expired
        if datetime.now() > self.open_time + timedelta(minutes=self.cooldown_minutes):
            self.circuit_open = False
            self.open_time = None
            self.failures = []  # Reset failures
            
            return {
                'status': 'RESET',
                'trading_allowed': True,
                'message': 'Circuit breaker reset - trading resumed'
            }
        
        time_remaining = (self.open_time + timedelta(minutes=self.cooldown_minutes) - datetime.now()).total_seconds()
        
        return {
            'status': 'OPEN',
            'trading_allowed': False,
            'cooldown_remaining_seconds': time_remaining,
            'message': 'Trading halted - circuit breaker active'
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'circuit_open': self.circuit_open,
            'recent_failures': len(self.failures),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = CircuitBreakerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
