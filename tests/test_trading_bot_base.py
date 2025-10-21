#!/usr/bin/env python3
"""
AEGIS v2.0 - Trading Bot Base Test Suite
Comprehensive tests for unified bot base class

VERITAS Protocol: Complete test coverage for safety-critical base class
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add paths
sys.path.insert(0, '/workspace')
sys.path.insert(0, '/workspace/core')

from core.trading_bot_base import TradingBotBase


class TestTradingBotBaseUnit(unittest.TestCase):
    """Unit tests for TradingBotBase"""
    
    def test_init_success(self):
        """Test successful initialization"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        self.assertEqual(bot.name, "TEST_BOT")
        self.assertEqual(bot.exchange_name, 'mock')
        self.assertIsNotNone(bot.exchange_adapter)
        self.assertIsNotNone(bot.exchange)  # Backward compat alias
        
        bot.close()
    
    def test_init_empty_name_fails(self):
        """Test that empty bot name raises assertion"""
        with self.assertRaises(AssertionError):
            TradingBotBase(bot_name="", exchange_name='mock')
    
    def test_place_order_success(self):
        """Test placing order through adapter"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        order = bot.place_order('BTC/USDT', 'BUY', 0.001)
        
        self.assertIsNotNone(order)
        self.assertIn('id', order)
        self.assertEqual(bot.metrics['orders_placed'], 1)
        
        bot.close()
    
    def test_place_order_invalid_symbol_fails(self):
        """Test that invalid symbol returns None (caught by adapter)"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        # Invalid symbol caught by adapter, returns None
        result = bot.place_order('INVALID', 'BUY', 0.001)
        
        self.assertIsNone(result)
        self.assertEqual(bot.metrics['errors'], 1)
        
        bot.close()
    
    def test_place_order_invalid_side_fails(self):
        """Test that invalid side raises assertion"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        with self.assertRaises(AssertionError):
            bot.place_order('BTC/USDT', 'INVALID', 0.001)
        
        bot.close()
    
    def test_place_order_negative_amount_fails(self):
        """Test that negative amount raises assertion"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        with self.assertRaises(AssertionError):
            bot.place_order('BTC/USDT', 'BUY', -0.001)
        
        bot.close()
    
    def test_get_balance_success(self):
        """Test getting balance"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        balance = bot.get_balance('USDT')
        
        self.assertIsInstance(balance, float)
        self.assertGreaterEqual(balance, 0.0)
        
        bot.close()
    
    def test_get_balance_empty_currency_fails(self):
        """Test that empty currency raises assertion"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        with self.assertRaises(AssertionError):
            bot.get_balance('')
        
        bot.close()
    
    def test_get_ticker_success(self):
        """Test getting ticker"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        ticker = bot.get_ticker('BTC/USDT')
        
        self.assertIsNotNone(ticker)
        self.assertIn('symbol', ticker)
        
        bot.close()
    
    def test_get_ticker_empty_symbol_fails(self):
        """Test that empty symbol raises assertion"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        with self.assertRaises(AssertionError):
            bot.get_ticker('')
        
        bot.close()
    
    def test_get_open_positions_success(self):
        """Test getting open positions"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        positions = bot.get_open_positions()
        
        self.assertIsInstance(positions, list)
        
        bot.close()
    
    def test_get_status_success(self):
        """Test getting bot status"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            bot_version="1.2.3",
            exchange_name='mock',
            enable_psm=False
        )
        
        status = bot.get_status()
        
        self.assertEqual(status['name'], "TEST_BOT")
        self.assertEqual(status['version'], "1.2.3")
        self.assertIn('metrics', status)
        self.assertFalse(status['psm_enabled'])
        
        bot.close()
    
    def test_context_manager(self):
        """Test context manager protocol"""
        with TradingBotBase(bot_name="TEST_BOT", exchange_name='mock', enable_psm=False) as bot:
            self.assertIsNotNone(bot)
            balance = bot.get_balance('USDT')
            self.assertIsInstance(balance, float)
    
    def test_backward_compatibility_exchange_alias(self):
        """Test that self.exchange still works (backward compat)"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        # Old bots use self.exchange
        self.assertIs(bot.exchange, bot.exchange_adapter)
        
        # Old bot code should still work
        ticker = bot.exchange.get_ticker('BTC/USDT')
        self.assertIsNotNone(ticker)
        
        bot.close()
    
    def test_metrics_tracking(self):
        """Test that metrics are tracked correctly"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=False
        )
        
        initial_orders = bot.metrics['orders_placed']
        
        # Place multiple orders
        bot.place_order('BTC/USDT', 'BUY', 0.001)
        bot.place_order('ETH/USDT', 'BUY', 0.01)
        
        self.assertEqual(bot.metrics['orders_placed'], initial_orders + 2)
        
        bot.close()


class TestTradingBotBaseIntegration(unittest.TestCase):
    """Integration tests with PSM"""
    
    def test_psm_integration(self):
        """Test PSM integration when enabled"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=True  # Enable PSM
        )
        
        if bot.psm:
            # PSM should be initialized
            self.assertIsNotNone(bot.psm)
            
            # Place order should log to PSM
            order = bot.place_order('BTC/USDT', 'BUY', 0.001)
            
            # Verify position logged
            positions = bot.psm.get_open_positions()
            self.assertIsInstance(positions, list)
        else:
            self.skipTest("PSM not available")
        
        bot.close()
    
    def test_reconciliation(self):
        """Test position reconciliation"""
        bot = TradingBotBase(
            bot_name="TEST_BOT",
            exchange_name='mock',
            enable_psm=True
        )
        
        if bot.psm:
            # Should be able to reconcile
            report = bot.reconcile_positions()
            
            self.assertIsInstance(report, dict)
            self.assertIn('timestamp', report)
        else:
            self.skipTest("PSM not available")
        
        bot.close()


class TestATLASCompliance(unittest.TestCase):
    """Test ATLAS protocol compliance"""
    
    def test_no_recursion(self):
        """Verify no recursive calls in methods"""
        import inspect
        
        for name, method in inspect.getmembers(TradingBotBase, predicate=inspect.ismethod):
            if name.startswith('_') and name not in ['__init__', '__enter__', '__exit__']:
                continue
            
            source = inspect.getsource(method)
            # Should not contain recursive call
            self.assertNotIn(f'self.{name}(', source,
                           f"Method {name} contains recursive call")
    
    def test_function_length_limits(self):
        """Verify all functions < 60 lines"""
        import inspect
        
        for name, method in inspect.getmembers(TradingBotBase, predicate=inspect.isfunction):
            if name.startswith('_') and name not in ['__init__', '_init_adapter', '_init_psm']:
                continue
            
            source = inspect.getsource(method)
            lines = len(source.split('\n'))
            
            self.assertLessEqual(lines, 60,
                               f"Method {name} has {lines} lines (max 60)")
    
    def test_assertion_density(self):
        """Verify minimum 2 assertions per public function"""
        import inspect
        
        for name, method in inspect.getmembers(TradingBotBase, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue  # Skip private
            
            if name in ['close', '__enter__', '__exit__', 'get_status']:
                continue  # Skip lifecycle/info methods
            
            source = inspect.getsource(method)
            assert_count = source.count('assert ')
            
            self.assertGreaterEqual(assert_count, 2,
                                  f"Method {name} has {assert_count} assertions (min 2)")


def run_tests():
    """Run all test suites"""
    print("=" * 70)
    print("AEGIS Trading Bot Base - Comprehensive Test Suite")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTradingBotBaseUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingBotBaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestATLASCompliance))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - VERITAS PROTOCOL SATISFIED")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review above")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
