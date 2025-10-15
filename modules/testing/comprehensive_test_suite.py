#!/usr/bin/env python3
"""Comprehensive Test Suite for TPS19 Unified Trading System"""

import sys
import os
import time
import json
import sqlite3
import unittest
from datetime import datetime
from typing import Dict, List, Tuple

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all modules to test
try:
    from exchanges.crypto_com import CryptoComAPI
    from exchanges.alpha_vantage import AlphaVantageAPI
    from market.unified_market_data import UnifiedMarketData
    from integrations.google_sheets import GoogleSheetsIntegration
    from telegram_bot import TelegramBot
    from market_data import MarketData
    from realtime_data import RealtimeDataFeed
except ImportError as e:
    print(f"Warning: Some modules not found for testing: {e}")

class TestCryptoComAPI(unittest.TestCase):
    """Test Crypto.com API integration"""
    
    def setUp(self):
        self.api = CryptoComAPI()
        
    def test_connection(self):
        """Test API connection"""
        result = self.api.test_connection()
        self.assertTrue(result, "Crypto.com API connection should work")
        
    def test_get_ticker(self):
        """Test ticker data retrieval"""
        ticker = self.api.get_ticker("BTC_USDT")
        self.assertIsInstance(ticker, dict)
        self.assertIn('price', ticker)
        self.assertGreater(ticker['price'], 0)
        
    def test_get_order_book(self):
        """Test order book retrieval"""
        book = self.api.get_order_book("BTC_USDT", 5)
        self.assertIsInstance(book, dict)
        self.assertIn('bids', book)
        self.assertIn('asks', book)
        self.assertEqual(len(book['bids']), 5)
        
    def test_get_trades(self):
        """Test trade history retrieval"""
        trades = self.api.get_trades("BTC_USDT", 10)
        self.assertIsInstance(trades, list)
        self.assertGreater(len(trades), 0)
        if trades:
            self.assertIn('price', trades[0])
            self.assertIn('quantity', trades[0])
            
    def test_get_candlestick(self):
        """Test candlestick data retrieval"""
        candles = self.api.get_candlestick("BTC_USDT", "1h", 10)
        self.assertIsInstance(candles, list)
        self.assertEqual(len(candles), 10)
        if candles:
            self.assertIn('open', candles[0])
            self.assertIn('high', candles[0])
            self.assertIn('low', candles[0])
            self.assertIn('close', candles[0])

class TestAlphaVantageAPI(unittest.TestCase):
    """Test Alpha Vantage API integration"""
    
    def setUp(self):
        self.api = AlphaVantageAPI()
        
    def test_connection(self):
        """Test API connection"""
        result = self.api.test_connection()
        self.assertTrue(result, "Alpha Vantage API connection should work")
        
    def test_crypto_exchange_rate(self):
        """Test crypto exchange rate"""
        rate = self.api.get_crypto_exchange_rate("BTC", "USD")
        self.assertIsInstance(rate, dict)
        self.assertIn('exchange_rate', rate)
        self.assertGreater(rate['exchange_rate'], 0)
        
    def test_technical_indicators(self):
        """Test technical indicators"""
        rsi = self.api.get_technical_indicators("BTC", "RSI")
        self.assertIsInstance(rsi, dict)
        self.assertIn('value', rsi)
        self.assertGreaterEqual(rsi['value'], 0)
        self.assertLessEqual(rsi['value'], 100)

class TestUnifiedMarketData(unittest.TestCase):
    """Test Unified Market Data aggregator"""
    
    def setUp(self):
        self.umd = UnifiedMarketData()
        
    def test_best_price(self):
        """Test best price aggregation"""
        price = self.umd.get_best_price("BTC_USDT")
        self.assertIsInstance(price, dict)
        self.assertIn('price', price)
        self.assertIn('bid', price)
        self.assertIn('ask', price)
        self.assertGreater(price['price'], 0)
        
    def test_market_depth(self):
        """Test market depth aggregation"""
        depth = self.umd.get_market_depth("BTC_USDT", 5)
        self.assertIsInstance(depth, dict)
        self.assertIn('bids', depth)
        self.assertIn('asks', depth)
        
    def test_technical_indicators(self):
        """Test technical indicators"""
        indicators = self.umd.get_technical_indicators("BTC_USDT")
        self.assertIsInstance(indicators, dict)
        self.assertIn('indicators', indicators)
        self.assertIn('RSI', indicators['indicators'])
        
    def test_market_summary(self):
        """Test market summary"""
        summary = self.umd.get_market_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn('crypto', summary)
        self.assertIn('timestamp', summary)
        
    def test_data_quality_metrics(self):
        """Test data quality metrics"""
        metrics = self.umd.get_data_quality_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('sources', metrics)

class TestGoogleSheetsIntegration(unittest.TestCase):
    """Test Google Sheets integration"""
    
    def setUp(self):
        self.gs = GoogleSheetsIntegration()
        
    def test_database_operations(self):
        """Test local database operations"""
        # Test signal logging
        signal = {
            'symbol': 'BTC/USDT',
            'action': 'BUY',
            'price': 45000,
            'confidence': 0.85,
            'strategy': 'test'
        }
        result = self.gs.log_trading_signal(signal)
        self.assertTrue(result)
        
        # Test portfolio update
        position = {
            'symbol': 'BTC/USDT',
            'quantity': 0.1,
            'entry_price': 45000,
            'current_price': 46000
        }
        result = self.gs.update_portfolio_position(position)
        self.assertTrue(result)
        
        # Test performance metrics
        metrics = {
            'total_value': 10000,
            'daily_pnl': 100,
            'win_rate': 65.5
        }
        result = self.gs.log_performance_metrics(metrics)
        self.assertTrue(result)

class TestTelegramBot(unittest.TestCase):
    """Test Telegram Bot functionality"""
    
    def setUp(self):
        self.bot = TelegramBot()
        
    def test_database_operations(self):
        """Test bot database operations"""
        # Test user registration
        self.bot._register_user(123456, "test_user")
        
        # Test settings retrieval
        settings = self.bot._get_user_settings(123456)
        self.assertIsInstance(settings, dict)
        
        # Test alert creation
        alert_id = self.bot._create_price_alert(123456, "BTC_USDT", 50000, "above")
        self.assertIsNotNone(alert_id)
        
        # Test alert retrieval
        alerts = self.bot._get_user_alerts(123456)
        self.assertIsInstance(alerts, list)
        self.assertGreater(len(alerts), 0)

class TestMarketData(unittest.TestCase):
    """Test Market Data module"""
    
    def setUp(self):
        self.market = MarketData()
        
    def test_get_price(self):
        """Test price retrieval"""
        price = self.market.get_price("BTC_USDT")
        self.assertIsInstance(price, (int, float))
        self.assertGreater(price, 0)
        
    def test_get_market_stats(self):
        """Test market statistics"""
        stats = self.market.get_market_stats("BTC_USDT")
        self.assertIsInstance(stats, dict)
        self.assertIn('price', stats)
        self.assertIn('high_24h', stats)
        self.assertIn('low_24h', stats)
        
    def test_get_candlestick_data(self):
        """Test candlestick data"""
        candles = self.market.get_candlestick_data("BTC_USDT", "1h", 10)
        self.assertIsInstance(candles, list)
        self.assertEqual(len(candles), 10)

class TestSystemIntegration(unittest.TestCase):
    """Test system-wide integration"""
    
    def test_data_flow(self):
        """Test data flow between components"""
        # Get market data
        market = MarketData()
        price = market.get_price("BTC_USDT")
        self.assertGreater(price, 0)
        
        # Test unified data
        umd = UnifiedMarketData()
        unified_price = umd.get_best_price("BTC_USDT")
        self.assertGreater(unified_price['price'], 0)
        
        # Test Google Sheets logging
        gs = GoogleSheetsIntegration()
        signal = {
            'symbol': 'BTC_USDT',
            'action': 'TEST',
            'price': price,
            'confidence': 0.5
        }
        result = gs.log_trading_signal(signal)
        self.assertTrue(result)

class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling"""
    
    def test_invalid_symbols(self):
        """Test handling of invalid symbols"""
        api = CryptoComAPI()
        ticker = api.get_ticker("INVALID_SYMBOL")
        self.assertIsInstance(ticker, dict)
        self.assertIn('price', ticker)  # Should return mock data
        
    def test_api_fallbacks(self):
        """Test API fallback mechanisms"""
        market = MarketData()
        # Even with invalid symbol, should return mock data
        price = market.get_price("INVALID_COIN")
        self.assertGreater(price, 0)

class TestDatabaseIntegrity(unittest.TestCase):
    """Test database integrity and operations"""
    
    def test_database_creation(self):
        """Test database table creation"""
        # Test market data DB
        db_path = "/tmp/test_market.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO test_table (data) VALUES (?)", ("test",))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        conn.close()
        os.remove(db_path)

def run_comprehensive_tests():
    """Run all tests and generate report"""
    print("🧪 Running Comprehensive Test Suite for TPS19")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCryptoComAPI,
        TestAlphaVantageAPI,
        TestUnifiedMarketData,
        TestGoogleSheetsIntegration,
        TestTelegramBot,
        TestMarketData,
        TestSystemIntegration,
        TestDataValidation,
        TestDatabaseIntegrity
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    
    # Calculate pass rate
    pass_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 Pass Rate: {pass_rate:.1f}%")
    
    if pass_rate == 100:
        print("\n🎉 ALL TESTS PASSED! System is fully functional!")
    elif pass_rate >= 80:
        print("\n✅ System is operational with minor issues")
    elif pass_rate >= 60:
        print("\n⚠️ System has issues but core functionality works")
    else:
        print("\n❌ System has critical issues and may not function properly")
    
    return result.wasSuccessful()

def run_performance_tests():
    """Run performance benchmarks"""
    print("\n⚡ Running Performance Tests")
    print("=" * 60)
    
    results = {}
    
    # Test API response times
    print("\n📡 Testing API Response Times:")
    
    # Crypto.com API
    api = CryptoComAPI()
    start = time.time()
    for _ in range(10):
        api.get_ticker("BTC_USDT")
    crypto_time = (time.time() - start) / 10
    results['crypto.com'] = crypto_time
    print(f"   Crypto.com average: {crypto_time*1000:.2f}ms")
    
    # Database operations
    print("\n💾 Testing Database Operations:")
    gs = GoogleSheetsIntegration()
    
    start = time.time()
    for i in range(100):
        gs.log_trading_signal({
            'symbol': 'TEST',
            'action': 'BUY',
            'price': 100 + i,
            'confidence': 0.5
        })
    db_time = (time.time() - start) / 100
    results['database'] = db_time
    print(f"   Database write average: {db_time*1000:.2f}ms")
    
    # Memory usage
    import psutil
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"\n💾 Memory Usage: {memory_mb:.2f} MB")
    
    return results

if __name__ == "__main__":
    # Run comprehensive tests
    success = run_comprehensive_tests()
    
    # Run performance tests
    perf_results = run_performance_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)