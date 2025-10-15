#!/usr/bin/env python3
"""TPS19 Interactive Start Menu and Dashboard"""

import sys, os, time, json
from services.path_config import path
from datetime import datetime
sys.path.insert(0, '/opt/tps19/modules')

try:
    from brain.ai_memory import ai_memory
    from market.market_feed import market_feed
    from testing.test_suite import test_suite
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19StartMenu:
    def __init__(self):
        self.running = True
        self.system_status = "Stopped"
        
    def show_banner(self):
        print("\033[2J\033[H")  # Clear screen
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    🚀 TPS19 CRYPTO.COM TRADING SYSTEM 🚀                   ║")
        print("║                                                                              ║")
        print("║  🏢 Exchange: CRYPTO.COM EXCLUSIVE                                          ║")
        print("║  🧠 AI Memory: Advanced Decision Tracking                                   ║")
        print("║  📈 Market Feed: Real-time CRYPTO.COM Data                                  ║")
        print("║  🧪 Testing: Comprehensive Test Suite                                       ║")
        print("║  📊 Dashboard: Live System Monitoring                                       ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print()
        
    def show_main_menu(self):
        self.show_banner()
        print("🎯 MAIN MENU:")
        print("1. 🚀 Start TPS19 System")
        print("2. 🛑 Stop TPS19 System") 
        print("3. 📊 View System Dashboard")
        print("4. 🧪 Run Test Suite")
        print("5. 📈 View Market Data")
        print("6. 🧠 View AI Memory Stats")
        print("7. ⚙️ System Configuration")
        print("8. 📋 Generate Reports")
        print("9. 🔧 System Diagnostics")
        print("0. 🚪 Exit")
        print()
        
    def start_system(self):
        print("🚀 Starting TPS19 CRYPTO.COM System...")
        
        # Start market feeds
        pairs = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOT/USDT']
        for pair in pairs:
            result = market_feed.start_feed(pair)
            if result:
                print(f"✅ Started feed for {pair}")
            else:
                print(f"⚠️ Feed already active for {pair}")
                
        self.system_status = "Running"
        print("✅ TPS19 system started successfully!")
        input("\nPress Enter to continue...")
        
    def stop_system(self):
        print("🛑 Stopping TPS19 system...")
        # In a real implementation, this would stop all feeds
        self.system_status = "Stopped"
        print("✅ TPS19 system stopped!")
        input("\nPress Enter to continue...")
        
    def show_dashboard(self):
        self.show_banner()
        print("📊 SYSTEM DASHBOARD:")
        print("=" * 60)
        
        # System status
        print(f"🔄 System Status: {self.system_status}")
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏢 Exchange: CRYPTO.COM")
        
        # AI Memory stats
        try:
            ai_stats = ai_memory.get_performance_summary()
            print(f"🧠 AI Decisions: {ai_stats.get('total_decisions', 0)}")
            print(f"🎯 Avg Confidence: {ai_stats.get('average_confidence', 0):.3f}")
        except:
            print("🧠 AI Memory: Not available")
            
        # Market Feed stats
        try:
            market_stats = market_feed.get_feed_status()
            print(f"📈 Active Feeds: {market_stats.get('active_feeds', 0)}")
        except:
            print("📈 Market Feed: Not available")
            
        # Latest market data
        print("\n📈 LATEST CRYPTO.COM PRICES:")
        for symbol in ['BTC_USDT', 'ETH_USDT', 'ADA_USDT']:
            try:
                data = market_feed.get_latest_data(symbol, 1)
                if data:
                    price = data[0]['close']
                    print(f"💰 {symbol}: ${price:.4f}")
                else:
                    print(f"💰 {symbol}: No data")
            except:
                print(f"💰 {symbol}: Error")
                
        print("=" * 60)
        input("\nPress Enter to continue...")
        
    def run_tests(self):
        self.show_banner()
        print("🧪 RUNNING COMPREHENSIVE TEST SUITE:")
        print("=" * 60)
        
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! System is fully functional.")
        else:
            print("\n⚠️ Some tests failed. Check individual results above.")
            
        test_suite.generate_test_report()
        input("\nPress Enter to continue...")
        
    def view_market_data(self):
        self.show_banner()
        print("📈 CRYPTO.COM MARKET DATA:")
        print("=" * 60)
        
        symbols = ['BTC_USDT', 'ETH_USDT', 'ADA_USDT', 'DOT_USDT', 'MATIC_USDT']
        
        for symbol in symbols:
            try:
                data = market_feed.get_latest_data(symbol, 5)
                if data:
                    latest = data[0]
                    print(f"\n💰 {symbol}:")
                    print(f"   Price: ${latest['close']:.4f}")
                    print(f"   High:  ${latest['high']:.4f}")
                    print(f"   Low:   ${latest['low']:.4f}")
                    print(f"   Volume: {latest['volume']:.2f}")
                    print(f"   Time: {latest['timestamp']}")
                else:
                    print(f"\n💰 {symbol}: No data available")
            except Exception as e:
                print(f"\n💰 {symbol}: Error - {e}")
                
        input("\nPress Enter to continue...")
        
    def view_ai_stats(self):
        self.show_banner()
        print("🧠 AI MEMORY STATISTICS:")
        print("=" * 60)
        
        try:
            stats = ai_memory.get_performance_summary()
            
            print(f"📊 Total Decisions: {stats.get('total_decisions', 0)}")
            print(f"🎯 Average Confidence: {stats.get('average_confidence', 0):.3f}")
            print(f"🏢 Exchange: {stats.get('exchange', 'crypto.com')}")
            print(f"⏰ Last Updated: {stats.get('last_updated', 'Unknown')}")
            
            personality_stats = stats.get('personality_breakdown', {})
            if personality_stats:
                print("\n🤖 PERSONALITY BREAKDOWN:")
                for personality, count in personality_stats.items():
                    print(f"   {personality}: {count} decisions")
            else:
                print("\n🤖 No personality data available")
                
        except Exception as e:
            print(f"❌ Error retrieving AI stats: {e}")
            
        input("\nPress Enter to continue...")
        
    def system_config(self):
        self.show_banner()
        print("⚙️ SYSTEM CONFIGURATION:")
        print("=" * 60)
        
        config = {
            'exchange': 'crypto.com',
            'supported_pairs': ['BTC_USDT', 'ETH_USDT', 'ADA_USDT', 'DOT_USDT', 'MATIC_USDT'],
            'ai_personalities': ['Athena', 'Apollo', 'Hermes', 'Artemis'],
            'database_path': path('data/'),
            'log_path': path('logs/'),
            'update_interval': 5,
            'max_cache_size': 1000
        }
        
        for key, value in config.items():
            print(f"🔧 {key}: {value}")
            
        input("\nPress Enter to continue...")
        
    def generate_reports(self):
        self.show_banner()
        print("📋 GENERATING SYSTEM REPORTS:")
        print("=" * 60)
        
        try:
            # Generate test report
            report_file = test_suite.generate_test_report()
            print(f"✅ Test report generated: {report_file}")
            
            # Generate system status report
            status_report = {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.system_status,
                'exchange': 'crypto.com',
                'ai_stats': ai_memory.get_performance_summary(),
                'market_stats': market_feed.get_feed_status()
            }
            
            status_file = path(f"reports/status_report_{int(time.time())}.json")
            with open(status_file, 'w') as f:
                json.dump(status_report, f, indent=2)
                
            print(f"✅ Status report generated: {status_file}")
            
        except Exception as e:
            print(f"❌ Report generation error: {e}")
            
        input("\nPress Enter to continue...")
        
    def system_diagnostics(self):
        self.show_banner()
        print("🔧 SYSTEM DIAGNOSTICS:")
        print("=" * 60)
        
        # Check file system
        print("📁 File System Check:")
        required_dirs = ['/opt/tps19/data', '/opt/tps19/logs', '/opt/tps19/modules']
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                print(f"✅ {dir_path}")
            else:
                print(f"❌ {dir_path} - Missing!")
                
        # Check databases
        print("\n🗄️ Database Check:")
        db_files = ['/opt/tps19/data/ai_memory.db', '/opt/tps19/data/market_data.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                size = os.path.getsize(db_file)
                print(f"✅ {db_file} ({size} bytes)")
            else:
                print(f"❌ {db_file} - Missing!")
                
        # Check modules
        print("\n🧩 Module Check:")
        try:
            ai_test = ai_memory.test_functionality()
            print(f"✅ AI Memory: {'Working' if ai_test else 'Failed'}")
        except:
            print("❌ AI Memory: Error")
            
        try:
            market_test = market_feed.test_functionality()
            print(f"✅ Market Feed: {'Working' if market_test else 'Failed'}")
        except:
            print("❌ Market Feed: Error")
            
        input("\nPress Enter to continue...")
        
    def run(self):
        while self.running:
            self.show_main_menu()
            
            try:
                choice = input("🎯 Select option (0-9): ").strip()
                
                if choice == '1':
                    self.start_system()
                elif choice == '2':
                    self.stop_system()
                elif choice == '3':
                    self.show_dashboard()
                elif choice == '4':
                    self.run_tests()
                elif choice == '5':
                    self.view_market_data()
                elif choice == '6':
                    self.view_ai_stats()
                elif choice == '7':
                    self.system_config()
                elif choice == '8':
                    self.generate_reports()
                elif choice == '9':
                    self.system_diagnostics()
                elif choice == '0':
                    print("👋 Goodbye!")
                    self.running = False
                else:
                    print("❌ Invalid option. Please try again.")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    menu = TPS19StartMenu()
    menu.run()
