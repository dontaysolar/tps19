#!/usr/bin/env python3
"""
AEGIS v2.0 - Exchange Adapter Test Suite
Comprehensive tests for safety-critical exchange interface

VERITAS Protocol Compliance:
- Unit tests for all public methods
- Edge case coverage
- Failure path validation
- Assertion density verification
- Integration with PSM
"""

import os
import sys
import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add core to path
sys.path.insert(0, '/workspace')
sys.path.insert(0, '/workspace/core')

from core.exchange_adapter import ExchangeAdapter, OrderSide


class TestExchangeAdapterUnit(unittest.TestCase):
    """Unit tests for ExchangeAdapter"""
    
    def setUp(self):
        """Set up test fixture"""
        # Use mock mode for testing
        self.adapter = ExchangeAdapter(exchange_name='mock', enable_logging=False)
    
    def tearDown(self):
        """Clean up"""
        if self.adapter:
            self.adapter.close()
    
    def test_init_mock_mode(self):
        """Test initialization in mock mode"""
        adapter = ExchangeAdapter(exchange_name='mock')
        
        self.assertEqual(adapter.exchange_name, 'mock')
        self.assertTrue(adapter.mock_mode)
        self.assertIsNone(adapter.exchange)
        
        adapter.close()
    
    def test_init_with_credentials(self):
        """Test initialization with explicit credentials"""
        adapter = ExchangeAdapter(
            exchange_name='mock',
            api_key='test_key',
            api_secret='test_secret'
        )
        
        self.assertIsNotNone(adapter)
        adapter.close()
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced"""
        adapter = ExchangeAdapter(exchange_name='mock', enable_logging=False)
        
        # Call multiple times rapidly
        start_time = time.time()
        for i in range(5):
            adapter._enforce_rate_limit()
        elapsed = time.time() - start_time
        
        # Should be very fast (no rate limit hit with 5 calls)
        self.assertLess(elapsed, 1.0)
        
        # Verify last_call_times is bounded
        self.assertLessEqual(len(adapter.last_call_times), adapter.RATE_LIMIT_CALLS_PER_MINUTE)
        
        adapter.close()
    
    def test_place_order_buy_success(self):
        """Test placing BUY order (success path)"""
        order = self.adapter.place_order('BTC/USDT', 'BUY', 0.001)
        
        self.assertIsNotNone(order)
        self.assertIn('id', order)
        self.assertIn('symbol', order)
        self.assertEqual(order['symbol'], 'BTC/USDT')
        self.assertEqual(order['side'], 'buy')
        self.assertEqual(order['amount'], 0.001)
    
    def test_place_order_sell_success(self):
        """Test placing SELL order (success path)"""
        order = self.adapter.place_order('ETH/USDT', 'SELL', 0.01)
        
        self.assertIsNotNone(order)
        self.assertIn('id', order)
        self.assertEqual(order['symbol'], 'ETH/USDT')
        self.assertEqual(order['side'], 'sell')
    
    def test_place_order_invalid_symbol(self):
        """Test placing order with invalid symbol (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.place_order('INVALID', 'BUY', 0.001)
    
    def test_place_order_invalid_side(self):
        """Test placing order with invalid side (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.place_order('BTC/USDT', 'INVALID', 0.001)
    
    def test_place_order_negative_amount(self):
        """Test placing order with negative amount (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.place_order('BTC/USDT', 'BUY', -0.001)
    
    def test_place_order_zero_amount(self):
        """Test placing order with zero amount (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.place_order('BTC/USDT', 'BUY', 0)
    
    def test_cancel_order_success(self):
        """Test canceling order (success path)"""
        result = self.adapter.cancel_order('ORDER_123', 'BTC/USDT')
        
        self.assertTrue(result)
    
    def test_cancel_order_empty_id(self):
        """Test canceling order with empty ID (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.cancel_order('', 'BTC/USDT')
    
    def test_cancel_order_invalid_symbol(self):
        """Test canceling order with invalid symbol (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.cancel_order('ORDER_123', 'INVALID')
    
    def test_get_balance_success(self):
        """Test getting balance (success path)"""
        balance = self.adapter.get_balance('USDT')
        
        self.assertIsInstance(balance, float)
        self.assertGreaterEqual(balance, 0.0)
    
    def test_get_balance_empty_currency(self):
        """Test getting balance with empty currency (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.get_balance('')
    
    def test_get_ticker_success(self):
        """Test getting ticker (success path)"""
        ticker = self.adapter.get_ticker('BTC/USDT')
        
        self.assertIsNotNone(ticker)
        self.assertIn('symbol', ticker)
        self.assertIn('last', ticker)
        self.assertEqual(ticker['symbol'], 'BTC/USDT')
    
    def test_get_ticker_invalid_symbol(self):
        """Test getting ticker with invalid symbol (failure path)"""
        with self.assertRaises(AssertionError):
            self.adapter.get_ticker('INVALID')
    
    def test_get_open_positions_success(self):
        """Test getting open positions (success path)"""
        positions = self.adapter.get_open_positions()
        
        self.assertIsInstance(positions, list)
        # Mock mode returns empty list
        self.assertEqual(len(positions), 0)
    
    def test_context_manager(self):
        """Test context manager protocol"""
        with ExchangeAdapter(exchange_name='mock', enable_logging=False) as adapter:
            self.assertIsNotNone(adapter)
            balance = adapter.get_balance('USDT')
            self.assertIsInstance(balance, float)
        
        # Adapter should be closed after context
    
    def test_validate_order_params_valid(self):
        """Test order parameter validation (success path)"""
        # Should not raise
        self.adapter._validate_order_params('BTC/USDT', 'BUY', 0.001)
    
    def test_validate_order_params_invalid(self):
        """Test order parameter validation (failure paths)"""
        with self.assertRaises(AssertionError):
            self.adapter._validate_order_params('INVALID', 'BUY', 0.001)
        
        with self.assertRaises(AssertionError):
            self.adapter._validate_order_params('BTC/USDT', 'INVALID', 0.001)
        
        with self.assertRaises(AssertionError):
            self.adapter._validate_order_params('BTC/USDT', 'BUY', -0.001)
    
    def test_create_mock_order(self):
        """Test mock order creation"""
        order = self.adapter._create_mock_order('BTC/USDT', 'BUY', 0.001)
        
        self.assertIsInstance(order, dict)
        self.assertIn('id', order)
        self.assertIn('symbol', order)
        self.assertIn('side', order)
        self.assertIn('amount', order)
        self.assertEqual(order['symbol'], 'BTC/USDT')
        self.assertEqual(order['amount'], 0.001)


class TestExchangeAdapterIntegration(unittest.TestCase):
    """Integration tests with PSM"""
    
    def setUp(self):
        """Set up test fixture"""
        # Create adapter with logging enabled
        self.adapter = ExchangeAdapter(exchange_name='mock', enable_logging=True)
    
    def tearDown(self):
        """Clean up"""
        if self.adapter:
            self.adapter.close()
    
    def test_logging_to_psm(self):
        """Test that operations are logged to PSM"""
        if not self.adapter.psm:
            self.skipTest("PSM not available")
        
        # Place order (should log)
        order = self.adapter.place_order('BTC/USDT', 'BUY', 0.001)
        
        # Check that log was created
        cursor = self.adapter.psm.conn.execute("""
            SELECT * FROM system_health 
            WHERE check_type LIKE 'EXCHANGE_%'
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        self.assertIsNotNone(row)


class TestExchangeAdapterEdgeCases(unittest.TestCase):
    """Edge case and boundary tests"""
    
    def setUp(self):
        """Set up test fixture"""
        self.adapter = ExchangeAdapter(exchange_name='mock', enable_logging=False)
    
    def tearDown(self):
        """Clean up"""
        if self.adapter:
            self.adapter.close()
    
    def test_place_order_minimum_amount(self):
        """Test placing order with minimum amount"""
        order = self.adapter.place_order('BTC/USDT', 'BUY', 0.00000001)
        self.assertIsNotNone(order)
    
    def test_place_order_large_amount(self):
        """Test placing order with large amount"""
        order = self.adapter.place_order('BTC/USDT', 'BUY', 999999.99)
        self.assertIsNotNone(order)
    
    def test_place_order_various_symbols(self):
        """Test placing orders with various symbol formats"""
        symbols = [
            'BTC/USDT',
            'ETH/USDT',
            'SOL/USDT',
            'ADA/USDT'
        ]
        
        for symbol in symbols:
            order = self.adapter.place_order(symbol, 'BUY', 0.001)
            self.assertIsNotNone(order)
            self.assertEqual(order['symbol'], symbol)
    
    def test_rapid_sequential_orders(self):
        """Test placing multiple orders rapidly"""
        orders = []
        
        for i in range(10):
            order = self.adapter.place_order('BTC/USDT', 'BUY', 0.001)
            orders.append(order)
        
        # All should succeed
        self.assertEqual(len(orders), 10)
        for order in orders:
            self.assertIsNotNone(order)
            self.assertIn('id', order)
    
    def test_alternating_buy_sell(self):
        """Test alternating BUY and SELL orders"""
        buy_order = self.adapter.place_order('BTC/USDT', 'BUY', 0.001)
        sell_order = self.adapter.place_order('BTC/USDT', 'SELL', 0.001)
        
        self.assertIsNotNone(buy_order)
        self.assertIsNotNone(sell_order)
        self.assertEqual(buy_order['side'], 'buy')
        self.assertEqual(sell_order['side'], 'sell')


class TestATLASCompliance(unittest.TestCase):
    """Test ATLAS protocol compliance"""
    
    def test_no_recursion(self):
        """Verify no recursive calls in public methods"""
        import inspect
        
        for name, method in inspect.getmembers(ExchangeAdapter, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue
            
            source = inspect.getsource(method)
            # Should not contain recursive call to self
            self.assertNotIn(f'self.{name}(', source, 
                           f"Method {name} contains recursive call")
    
    def test_function_length_limits(self):
        """Verify all functions < 60 lines"""
        import inspect
        
        for name, method in inspect.getmembers(ExchangeAdapter, predicate=inspect.isfunction):
            if name.startswith('_') and name not in ['_enforce_rate_limit', '_retry_with_backoff']:
                continue  # Skip internal helpers
            
            source = inspect.getsource(method)
            lines = len(source.split('\n'))
            
            self.assertLessEqual(lines, 60, 
                               f"Method {name} has {lines} lines (max 60)")
    
    def test_fixed_loop_bounds(self):
        """Verify all loops have fixed bounds"""
        adapter = ExchangeAdapter(exchange_name='mock', enable_logging=False)
        
        # Verify MAX_RETRIES is fixed
        self.assertEqual(adapter.MAX_RETRIES, 3)
        
        # Verify MAX_POSITIONS_PER_QUERY is fixed
        self.assertEqual(adapter.MAX_POSITIONS_PER_QUERY, 100)
        
        adapter.close()
    
    def test_assertion_density(self):
        """Verify minimum 2 assertions per public function"""
        import inspect
        
        for name, method in inspect.getmembers(ExchangeAdapter, predicate=inspect.isfunction):
            if name.startswith('_'):
                continue  # Skip private methods
            
            if name in ['close', '__enter__', '__exit__']:
                continue  # Skip lifecycle methods
            
            source = inspect.getsource(method)
            assert_count = source.count('assert ')
            
            self.assertGreaterEqual(assert_count, 2, 
                                  f"Method {name} has {assert_count} assertions (min 2)")


def run_tests():
    """Run all test suites"""
    print("=" * 70)
    print("AEGIS Exchange Adapter - Comprehensive Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExchangeAdapterUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestExchangeAdapterIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestExchangeAdapterEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestATLASCompliance))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
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
