#!/usr/bin/env python3
"""
Unit Test Framework
Comprehensive testing for all bots
Validates functionality and integration
"""

import sys
from datetime import datetime
from typing import Dict, List, Callable

class UnitTestFramework:
    def __init__(self):
        self.name = "Unit_Test_Framework"
        self.version = "1.0.0"
        self.enabled = True
        
        self.tests = []
        self.results = []
        
        self.metrics = {'tests_run': 0, 'tests_passed': 0, 'tests_failed': 0, 'coverage': 0}
    
    def add_test(self, test_name: str, test_func: Callable, category: str = 'general'):
        """Register a test"""
        self.tests.append({
            'name': test_name,
            'func': test_func,
            'category': category
        })
    
    def run_test(self, test: Dict) -> Dict:
        """Run single test"""
        try:
            result = test['func']()
            
            if result.get('passed', False):
                return {
                    'test_name': test['name'],
                    'status': 'PASSED',
                    'message': result.get('message', 'Test passed'),
                    'duration_ms': result.get('duration_ms', 0)
                }
            else:
                return {
                    'test_name': test['name'],
                    'status': 'FAILED',
                    'message': result.get('message', 'Test failed'),
                    'error': result.get('error', '')
                }
        except Exception as e:
            return {
                'test_name': test['name'],
                'status': 'ERROR',
                'error': str(e)
            }
    
    def run_all_tests(self) -> Dict:
        """Run all registered tests"""
        self.results = []
        
        for test in self.tests:
            result = self.run_test(test)
            self.results.append(result)
            
            self.metrics['tests_run'] += 1
            
            if result['status'] == 'PASSED':
                self.metrics['tests_passed'] += 1
            else:
                self.metrics['tests_failed'] += 1
        
        pass_rate = (self.metrics['tests_passed'] / self.metrics['tests_run'] * 100) if self.metrics['tests_run'] > 0 else 0
        
        return {
            'total_tests': len(self.tests),
            'passed': self.metrics['tests_passed'],
            'failed': self.metrics['tests_failed'],
            'pass_rate': pass_rate,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_bot_initialization(self, bot_class) -> Dict:
        """Test if bot can be initialized"""
        try:
            bot = bot_class()
            status = bot.get_status() if hasattr(bot, 'get_status') else {}
            
            return {
                'passed': True,
                'bot_name': getattr(bot, 'name', 'Unknown'),
                'version': getattr(bot, 'version', 'Unknown'),
                'status': status
            }
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def test_bot_methods(self, bot_instance, required_methods: List[str]) -> Dict:
        """Test if bot has required methods"""
        missing = []
        
        for method in required_methods:
            if not hasattr(bot_instance, method):
                missing.append(method)
        
        return {
            'passed': len(missing) == 0,
            'required_methods': required_methods,
            'missing_methods': missing
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'total_tests': len(self.tests),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    framework = UnitTestFramework()
    print(f"✅ {framework.name} v{framework.version} initialized")
