#!/usr/bin/env python3
"""
Digital Twin Simulator
Real-time market simulation twin
Tests strategies in parallel universe
"""

import numpy as np
from datetime import datetime
from typing import Dict

class DigitalTwinSimulator:
    def __init__(self):
        self.name = "Digital_Twin_Simulator"
        self.version = "1.0.0"
        self.enabled = True
        
        self.twin_state = {}
        self.divergence_threshold = 0.05
        
        self.metrics = {'simulations_run': 0, 'predictions_made': 0, 'accuracy': 0}
    
    def create_twin(self, market_state: Dict) -> Dict:
        """Create digital twin of market"""
        self.twin_state = {
            'prices': market_state.get('prices', {}),
            'volumes': market_state.get('volumes', {}),
            'volatility': market_state.get('volatility', 0.02),
            'created_at': datetime.now().isoformat()
        }
        return {'twin_created': True, 'state': self.twin_state}
    
    def simulate_strategy(self, strategy, n_steps: int = 100) -> Dict:
        """Simulate strategy in twin environment"""
        results = []
        
        for step in range(n_steps):
            # Simulate market evolution
            simulated_data = self._evolve_market()
            
            # Test strategy
            signal = strategy(simulated_data) if callable(strategy) else {'signal': 'HOLD'}
            
            results.append({
                'step': step,
                'signal': signal.get('signal'),
                'price': simulated_data.get('price', 0)
            })
        
        self.metrics['simulations_run'] += 1
        
        return {
            'n_steps': n_steps,
            'results': results[:10],  # Return first 10
            'final_state': results[-1] if results else {},
            'timestamp': datetime.now().isoformat()
        }
    
    def _evolve_market(self) -> Dict:
        """Evolve market state by one step"""
        # Simulate random walk
        if 'BTC' in self.twin_state.get('prices', {}):
            current_price = self.twin_state['prices']['BTC']
            volatility = self.twin_state.get('volatility', 0.02)
            
            shock = np.random.randn() * volatility
            new_price = current_price * (1 + shock)
            
            self.twin_state['prices']['BTC'] = new_price
            
            return {'price': new_price, 'symbol': 'BTC'}
        
        return {}
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'twin_active': bool(self.twin_state), 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    simulator = DigitalTwinSimulator()
    print(f"✅ {simulator.name} v{simulator.version} initialized")
