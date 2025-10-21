#!/usr/bin/env python3
"""
AEGIS v2.0 Circuit Breaker Pattern Implementation
Multi-level circuit breakers with predictive failure detection
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass
import threading
import json

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: int = 30
    max_concurrent_calls: int = 10

class CircuitBreaker:
    """AEGIS-compliant circuit breaker with predictive capabilities"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.concurrent_calls = 0
        self.call_history = []
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Predictive failure detection
        self.failure_patterns = []
        self.prediction_threshold = 0.7
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenException(f"Circuit {self.name} is OPEN")
            
            # Check concurrent call limit
            if self.concurrent_calls >= self.config.max_concurrent_calls:
                raise CircuitBreakerOverloadException(f"Circuit {self.name} overloaded")
            
            self.concurrent_calls += 1
        
        try:
            # Execute function with timeout
            result = self._execute_with_timeout(func, *args, **kwargs)
            
            with self.lock:
                self._on_success()
            
            return result
            
        except Exception as e:
            with self.lock:
                self._on_failure(e)
            raise
        
        finally:
            with self.lock:
                self.concurrent_calls -= 1
    
    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout protection"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutException(f"Function {func.__name__} timed out")
        
        # Set timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.config.timeout)
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def _on_success(self):
        """Handle successful call"""
        self.success_count += 1
        self.last_success_time = datetime.now()
        
        # Record successful call
        self.call_history.append({
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'concurrent_calls': self.concurrent_calls
        })
        
        # Reset failure count
        self.failure_count = 0
        
        # Check if we should close the circuit
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.logger.info(f"Circuit {self.name} closed after successful recovery")
        
        # Clean old history
        self._clean_call_history()
    
    def _on_failure(self, exception: Exception):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        # Record failed call
        self.call_history.append({
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(exception),
            'concurrent_calls': self.concurrent_calls
        })
        
        # Check if we should open the circuit
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit {self.name} opened after {self.failure_count} failures")
        
        # Update failure patterns
        self._update_failure_patterns(exception)
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout
    
    def _clean_call_history(self):
        """Remove old entries from call history"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.call_history = [
            call for call in self.call_history
            if datetime.fromisoformat(call['timestamp']) > cutoff_time
        ]
    
    def _update_failure_patterns(self, exception: Exception):
        """Update failure patterns for predictive analysis"""
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(exception).__name__,
            'error_message': str(exception),
            'concurrent_calls': self.concurrent_calls,
            'failure_count': self.failure_count
        }
        
        self.failure_patterns.append(pattern)
        
        # Keep only recent patterns
        if len(self.failure_patterns) > 100:
            self.failure_patterns = self.failure_patterns[-50:]
    
    def predict_failure_probability(self) -> float:
        """Predict probability of next call failing"""
        if not self.call_history:
            return 0.0
        
        recent_calls = self.call_history[-10:]  # Last 10 calls
        failure_rate = sum(1 for call in recent_calls if not call['success']) / len(recent_calls)
        
        # Adjust based on failure patterns
        pattern_factor = self._analyze_failure_patterns()
        
        return min(1.0, failure_rate + pattern_factor)
    
    def _analyze_failure_patterns(self) -> float:
        """Analyze failure patterns for prediction"""
        if len(self.failure_patterns) < 3:
            return 0.0
        
        # Look for increasing failure rate
        recent_patterns = self.failure_patterns[-5:]
        if len(recent_patterns) >= 3:
            failure_counts = [p['failure_count'] for p in recent_patterns]
            if failure_counts == sorted(failure_counts):
                return 0.3  # Increasing failure pattern
        
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'concurrent_calls': self.concurrent_calls,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'failure_probability': self.predict_failure_probability(),
            'total_calls': len(self.call_history)
        }

class CircuitBreakerManager:
    """Manages multiple circuit breakers with coordination"""
    
    def __init__(self):
        self.circuits = {}
        self.logger = logging.getLogger(__name__)
        self.global_failure_threshold = 0.8
    
    def create_circuit(self, name: str, config: CircuitBreakerConfig) -> CircuitBreaker:
        """Create a new circuit breaker"""
        circuit = CircuitBreaker(name, config)
        self.circuits[name] = circuit
        self.logger.info(f"Created circuit breaker: {name}")
        return circuit
    
    def get_circuit(self, name: str) -> Optional[CircuitBreaker]:
        """Get existing circuit breaker"""
        return self.circuits.get(name)
    
    def call_with_circuit(self, circuit_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with specified circuit breaker"""
        circuit = self.get_circuit(circuit_name)
        if not circuit:
            raise ValueError(f"Circuit breaker {circuit_name} not found")
        
        return circuit.call(func, *args, **kwargs)
    
    def get_global_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'total_circuits': len(self.circuits),
            'open_circuits': 0,
            'half_open_circuits': 0,
            'closed_circuits': 0,
            'circuits': {}
        }
        
        for name, circuit in self.circuits.items():
            circuit_status = circuit.get_status()
            status['circuits'][name] = circuit_status
            
            if circuit.state == CircuitState.OPEN:
                status['open_circuits'] += 1
            elif circuit.state == CircuitState.HALF_OPEN:
                status['half_open_circuits'] += 1
            else:
                status['closed_circuits'] += 1
        
        return status
    
    def check_global_health(self) -> bool:
        """Check if system is healthy based on circuit breaker status"""
        if not self.circuits:
            return True
        
        open_circuits = sum(1 for c in self.circuits.values() if c.state == CircuitState.OPEN)
        total_circuits = len(self.circuits)
        
        failure_rate = open_circuits / total_circuits
        return failure_rate < self.global_failure_threshold

# Exception classes
class CircuitBreakerException(Exception):
    """Base exception for circuit breaker"""
    pass

class CircuitBreakerOpenException(CircuitBreakerException):
    """Circuit breaker is open"""
    pass

class CircuitBreakerOverloadException(CircuitBreakerException):
    """Circuit breaker is overloaded"""
    pass

class TimeoutException(CircuitBreakerException):
    """Function call timed out"""
    pass

# AEGIS Recursion Clause Implementation
class AEGISCircuitAuditor:
    """Autonomous circuit breaker auditing and optimization"""
    
    def __init__(self, manager: CircuitBreakerManager):
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        self.audit_history = []
    
    def audit_circuit_effectiveness(self) -> Dict[str, Any]:
        """Audit circuit breaker effectiveness and suggest optimizations"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'effectiveness_score': 0,
            'optimization_opportunities': [],
            'recommendations': []
        }
        
        total_circuits = len(self.manager.circuits)
        if total_circuits == 0:
            return audit_results
        
        # Analyze each circuit
        effective_circuits = 0
        for name, circuit in self.manager.circuits.items():
            if self._is_circuit_effective(circuit):
                effective_circuits += 1
            else:
                audit_results['optimization_opportunities'].append({
                    'circuit': name,
                    'issues': self._identify_circuit_issues(circuit)
                })
        
        audit_results['effectiveness_score'] = (effective_circuits / total_circuits) * 100
        
        # Generate recommendations
        audit_results['recommendations'] = self._generate_optimization_recommendations()
        
        return audit_results
    
    def _is_circuit_effective(self, circuit: CircuitBreaker) -> bool:
        """Check if circuit breaker is effective"""
        # Check if circuit is responding appropriately
        if circuit.state == CircuitState.OPEN and circuit.failure_count > circuit.config.failure_threshold:
            return True
        
        if circuit.state == CircuitState.CLOSED and circuit.failure_count == 0:
            return True
        
        return False
    
    def _identify_circuit_issues(self, circuit: CircuitBreaker) -> List[str]:
        """Identify issues with circuit breaker configuration"""
        issues = []
        
        # Check if failure threshold is too high
        if circuit.config.failure_threshold > 10:
            issues.append("Failure threshold too high")
        
        # Check if recovery timeout is too long
        if circuit.config.recovery_timeout > 300:
            issues.append("Recovery timeout too long")
        
        # Check if timeout is too short
        if circuit.config.timeout < 5:
            issues.append("Function timeout too short")
        
        return issues
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        return [
            "Implement adaptive thresholds based on historical data",
            "Add machine learning-based failure prediction",
            "Implement circuit breaker cascading for dependent services",
            "Add real-time monitoring and alerting"
        ]

if __name__ == '__main__':
    # Initialize circuit breaker manager
    manager = CircuitBreakerManager()
    
    # Create circuit breaker for exchange API
    exchange_config = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=30,
        success_threshold=2,
        timeout=10,
        max_concurrent_calls=5
    )
    
    exchange_circuit = manager.create_circuit('exchange_api', exchange_config)
    
    # Test function that might fail
    def test_exchange_call():
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise Exception("Exchange API error")
        return "Success"
    
    # Test circuit breaker
    for i in range(10):
        try:
            result = exchange_circuit.call(test_exchange_call)
            print(f"Call {i+1}: {result}")
        except CircuitBreakerOpenException as e:
            print(f"Call {i+1}: Circuit open - {e}")
        except Exception as e:
            print(f"Call {i+1}: Error - {e}")
        
        time.sleep(0.1)
    
    # Show status
    status = exchange_circuit.get_status()
    print(f"\nCircuit Status: {json.dumps(status, indent=2)}")
    
    # Show global status
    global_status = manager.get_global_status()
    print(f"\nGlobal Status: {json.dumps(global_status, indent=2)}")