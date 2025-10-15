#!/usr/bin/env python3
"""TPS19 Comprehensive Testing Suite"""

import sys, os, time, json
from datetime import datetime
modules_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if modules_root not in sys.path:
    sys.path.insert(0, modules_root)
if '/opt/tps19/modules' not in sys.path:
    sys.path.insert(0, '/opt/tps19/modules')

try:
    from brain.ai_memory import ai_memory
    from market.market_feed import market_feed
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19TestSuite:
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Starting TPS19 Comprehensive Test Suite...")
        print("=" * 60)
        
        tests = [
            ("AI Memory Test", self.test_ai_memory),
            ("Market Feed Test", self.test_market_feed),
            ("Database Connectivity Test", self.test_database_connectivity),
            ("Data Integrity Test", self.test_data_integrity),
            ("Performance Test", self.test_performance),
            ("Integration Test", self.test_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                result = test_func()
                if result:
                    print(f"✅ {test_name} PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name} FAILED")
                self.test_results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                self.test_results[test_name] = False
                
        print("\n" + "=" * 60)
        print(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL TESTS PASSED - TPS19 SYSTEM IS FULLY FUNCTIONAL!")
        else:
            print("⚠️ SOME TESTS FAILED - CHECK INDIVIDUAL RESULTS")

        # Optional notifications and logging
        try:
            from services import telegram_service, sheets_service
        except Exception:
            telegram_service = None
            sheets_service = None

        try:
            if telegram_service and telegram_service.enabled():
                telegram_service.send_message(f"🧪 TPS19 Test Suite: {passed}/{total} passed")
        except Exception:
            pass

        try:
            if sheets_service and sheets_service.enabled():
                sheets_service.append_row(
                    "TestResults",
                    [
                        datetime.now().isoformat(),
                        str(passed),
                        str(total),
                        "PASS" if passed == total else "PARTIAL",
                    ],
                )
        except Exception:
            pass
            
        return passed == total
        
    def test_ai_memory(self):
        """Test AI Memory functionality"""
        try:
            return ai_memory.test_functionality()
        except Exception as e:
            print(f"AI Memory test error: {e}")
            return False
            
    def test_market_feed(self):
        """Test Market Feed functionality"""
        try:
            return market_feed.test_functionality()
        except Exception as e:
            print(f"Market Feed test error: {e}")
            return False
            
    def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            import sqlite3
            
            # Test AI Memory database
            from services.path_config import path
            conn = sqlite3.connect(path('data/ai_memory.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ai_decisions")
            ai_count = cursor.fetchone()[0]
            conn.close()
            
            # Test Market Feed database
            conn = sqlite3.connect(path('data/market_data.db'))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM market_data")
            market_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"📊 AI Decisions: {ai_count}, Market Data: {market_count}")
            return True
            
        except Exception as e:
            print(f"Database connectivity error: {e}")
            return False
            
    def test_data_integrity(self):
        """Test data integrity"""
        try:
            # Test AI Memory data integrity
            ai_summary = ai_memory.get_performance_summary()
            
            # Test Market Feed data integrity
            market_status = market_feed.get_feed_status()
            
            if ai_summary and market_status:
                print(f"📈 AI Decisions: {ai_summary.get('total_decisions', 0)}")
                print(f"📊 Active Feeds: {market_status.get('active_feeds', 0)}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Data integrity error: {e}")
            return False
            
    def test_performance(self):
        """Test system performance"""
        try:
            start_time = time.time()
            
            # Performance test: Store 10 decisions
            for i in range(10):
                ai_memory.store_decision(
                    f"perf_test_{i}_{int(time.time())}",
                    "PerfTest",
                    "performance_test",
                    {"test_id": i, "exchange": "crypto.com"},
                    0.8
                )
                
            # Performance test: Get market data
            for symbol in ['BTC_USDT', 'ETH_USDT']:
                market_feed.get_latest_data(symbol, 5)
                
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️ Performance test completed in {duration:.2f} seconds")
            
            # Pass if under 5 seconds
            return duration < 5.0
            
        except Exception as e:
            print(f"Performance test error: {e}")
            return False
            
    def test_integration(self):
        """Test system integration"""
        try:
            # Test AI Memory + Market Feed integration
            market_data = market_feed.get_latest_data("BTC_USDT", 1)
            
            if market_data:
                # Store decision based on market data
                decision_result = ai_memory.store_decision(
                    f"integration_test_{int(time.time())}",
                    "IntegrationAI",
                    "market_analysis",
                    {
                        "symbol": "BTC_USDT",
                        "price": market_data[0]['close'],
                        "exchange": "crypto.com"
                    },
                    0.85
                )
                
                return decision_result
            else:
                return False
                
        except Exception as e:
            print(f"Integration test error: {e}")
            return False
            
    def generate_test_report(self):
        """Generate detailed test report"""
        report = {
            'test_suite': 'TPS19 Comprehensive Testing',
            'timestamp': datetime.now().isoformat(),
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'results': self.test_results,
            'system_info': {
                'exchange': 'crypto.com',
                'modules_tested': ['ai_memory', 'market_feed', 'database', 'integration'],
                'test_environment': 'production'
            }
        }
        
        # Save report
        from services.path_config import path
        os.makedirs(path('reports'), exist_ok=True)
        report_file = path(f"reports/test_report_{int(time.time())}.json")
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📋 Test report saved: {report_file}")
        return report_file

# Global test suite instance
test_suite = TPS19TestSuite()

if __name__ == "__main__":
    test_suite.run_all_tests()
    test_suite.generate_test_report()
