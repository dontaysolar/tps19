#!/usr/bin/env python3
"""
Walk-Forward Backtester
Out-of-sample testing methodology
Prevents overfitting and validates strategies
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class WalkForwardBacktester:
    def __init__(self):
        self.name = "Walk_Forward_Backtester"
        self.version = "1.0.0"
        self.enabled = True
        
        self.train_period = 0.70  # 70% training
        self.test_period = 0.30   # 30% testing
        self.n_iterations = 5
        
        self.metrics = {'tests_run': 0, 'avg_oos_performance': 0}
    
    def run_walk_forward(self, data: List, strategy_func) -> Dict:
        """Run walk-forward analysis"""
        n_samples = len(data)
        train_size = int(n_samples * self.train_period)
        test_size = int(n_samples * self.test_period)
        
        results = []
        
        for i in range(self.n_iterations):
            start_idx = i * test_size
            end_train = start_idx + train_size
            end_test = end_train + test_size
            
            if end_test > n_samples:
                break
            
            train_data = data[start_idx:end_train]
            test_data = data[end_train:end_test]
            
            # Train strategy
            try:
                strategy_params = strategy_func['train'](train_data)
                
                # Test out-of-sample
                test_results = strategy_func['test'](test_data, strategy_params)
                
                results.append({
                    'iteration': i + 1,
                    'train_period': f"{start_idx}-{end_train}",
                    'test_period': f"{end_train}-{end_test}",
                    'train_performance': test_results.get('train_perf', 0),
                    'test_performance': test_results.get('test_perf', 0),
                    'degradation': test_results.get('train_perf', 0) - test_results.get('test_perf', 0)
                })
            except Exception as e:
                results.append({'iteration': i + 1, 'error': str(e)})
        
        # Calculate statistics
        valid_results = [r for r in results if 'test_performance' in r]
        avg_test_perf = np.mean([r['test_performance'] for r in valid_results]) if valid_results else 0
        avg_degradation = np.mean([r['degradation'] for r in valid_results]) if valid_results else 0
        
        self.metrics['tests_run'] += 1
        self.metrics['avg_oos_performance'] = avg_test_perf
        
        # Assess robustness
        if avg_degradation < 0.10:  # Less than 10% degradation
            robustness = 'EXCELLENT'
        elif avg_degradation < 0.25:
            robustness = 'GOOD'
        elif avg_degradation < 0.50:
            robustness = 'FAIR'
        else:
            robustness = 'POOR'
        
        return {
            'n_iterations': len(results),
            'avg_test_performance': avg_test_perf,
            'avg_degradation': avg_degradation * 100,
            'robustness_assessment': robustness,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    backtester = WalkForwardBacktester()
    print(f"✅ {backtester.name} v{backtester.version} initialized")
