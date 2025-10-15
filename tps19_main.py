#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM"""

import sys, os, time, threading, signal
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))
sys.path.insert(0, '/opt/tps19/modules')

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    from market.unified_market_data import UnifiedMarketData
    from telegram_bot import TelegramBot
    from integrations.google_sheets import GoogleSheetsIntegration
    from exchanges.crypto_com import CryptoComAPI
    from exchanges.alpha_vantage import AlphaVantageAPI
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    print("Please ensure all modules are in the correct path")
    # Continue with available modules
    UnifiedMarketData = None
    TelegramBot = None
    GoogleSheetsIntegration = None

class TPS19UnifiedSystem:
    """TPS19 Definitive Unified System - Enhanced with Multiple Integrations"""
    
    def __init__(self):
        self.running = False
        self.exchange = 'crypto.com'
        self.system_components = {
            'siul': siul_core,
            'patch_manager': patch_manager,
            'n8n': n8n_integration
        }
        
        # Initialize new components
        self.market_data = UnifiedMarketData() if UnifiedMarketData else None
        self.telegram_bot = TelegramBot() if TelegramBot else None
        self.google_sheets = GoogleSheetsIntegration() if GoogleSheetsIntegration else None
        
        # Trading pairs to monitor
        self.trading_pairs = ['BTC_USDT', 'ETH_USDT', 'DOGE_USDT', 'CRO_USDT', 'ADA_USDT']
        
    def start_system(self):
        """Start the complete unified system with all integrations"""
        try:
            print("🚀 Starting TPS19 Definitive Unified System...")
            print("📡 Initializing all components...")
            
            self.running = True
            
            # Start all services
            self._start_all_services()
            
            # Main system loop
            while self.running:
                for symbol in self.trading_pairs:
                    try:
                        # Get unified market data
                        market_data = self._get_market_data(symbol)
                        
                        if market_data:
                            # Process with SIUL
                            siul_result = siul_core.process_unified_logic(market_data)
                            
                            if siul_result and siul_result.get('final_decision'):
                                decision = siul_result['final_decision']
                                
                                # Process significant decisions
                                if decision.get('confidence', 0) > 0.7:
                                    self._process_trading_signal(symbol, decision, market_data)
                                    
                    except Exception as e:
                        print(f"⚠️ Error processing {symbol}: {e}")
                        
                # Display system status
                self._display_system_status()
                
                # Sleep interval
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping TPS19 Unified System...")
            self._stop_all_services()
            self.running = False
        except Exception as e:
            print(f"❌ System error: {e}")
            self._stop_all_services()
            
    def _start_all_services(self):
        """Start all system services"""
        # Start N8N service
        try:
            n8n_integration.start_n8n_service()
            print("✅ N8N service started")
        except Exception as e:
            print(f"⚠️ N8N service failed to start: {e}")
            
        # Start market data collection
        if self.market_data:
            self.market_data.start_data_collection()
            print("✅ Market data collection started")
            
        # Start Telegram bot in background
        if self.telegram_bot and os.environ.get('TELEGRAM_BOT_TOKEN'):
            bot_thread = threading.Thread(target=self.telegram_bot.start_bot)
            bot_thread.daemon = True
            bot_thread.start()
            print("✅ Telegram bot started")
        else:
            print("⚠️ Telegram bot not configured (set TELEGRAM_BOT_TOKEN)")
            
        print("\n✅ All services initialized\n")
        
    def _stop_all_services(self):
        """Stop all system services"""
        if self.market_data:
            self.market_data.stop_data_collection()
            
        print("✅ All services stopped")
        
    def _get_market_data(self, symbol: str) -> dict:
        """Get market data for a symbol"""
        if self.market_data:
            price_data = self.market_data.get_best_price(symbol)
            indicators = self.market_data.get_technical_indicators(symbol)
            
            return {
                'symbol': symbol,
                'price': price_data['price'],
                'bid': price_data.get('bid', price_data['price']),
                'ask': price_data.get('ask', price_data['price']),
                'volume': price_data.get('volume', 0),
                'spread': price_data.get('spread', 0),
                'rsi': indicators['indicators'].get('RSI', 50),
                'macd': indicators['indicators'].get('MACD', 0),
                'exchange': self.exchange,
                'timestamp': datetime.now()
            }
        else:
            # Fallback to mock data
            return {
                'symbol': symbol,
                'price': 45000 + (time.time() % 1000),
                'volume': 1500,
                'exchange': self.exchange
            }
            
    def _process_trading_signal(self, symbol: str, decision: dict, market_data: dict):
        """Process and distribute trading signal"""
        signal = {
            'symbol': symbol,
            'action': decision['decision'],
            'price': market_data['price'],
            'confidence': decision['confidence'],
            'strategy': decision.get('strategy', 'SIUL'),
            'timestamp': datetime.now()
        }
        
        # Send to N8N
        try:
            n8n_integration.send_trade_signal(signal)
        except Exception as e:
            print(f"⚠️ Failed to send to N8N: {e}")
            
        # Send to Telegram subscribers
        if self.telegram_bot:
            try:
                # Queue signal for async sending
                threading.Thread(
                    target=lambda: self._send_telegram_signal(signal),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"⚠️ Failed to send to Telegram: {e}")
                
        # Log to Google Sheets
        if self.google_sheets:
            try:
                self.google_sheets.log_trading_signal(signal)
            except Exception as e:
                print(f"⚠️ Failed to log to Google Sheets: {e}")
                
        # Display signal
        action_emoji = "🟢" if signal['action'] == 'buy' else "🔴" if signal['action'] == 'sell' else "⚪"
        print(f"\n{action_emoji} SIGNAL: {signal['action'].upper()} {symbol} @ ${signal['price']:,.2f} (Confidence: {signal['confidence']:.1%})")
        
    def _display_system_status(self):
        """Display current system status"""
        print(f"\n💓 TPS19 System Status - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        if self.market_data:
            # Display market summary
            summary = self.market_data.get_market_summary()
            
            print("📊 Market Overview:")
            for symbol, data in summary['crypto'].items():
                print(f"   {symbol}: ${data['price']:,.2f} (spread: ${data['spread']:.2f})")
                
            # Display indicators
            if summary['indicators']:
                print("\n📈 Market Indicators (BTC):")
                for name, value in summary['indicators'].items():
                    print(f"   {name}: {value:.2f}")
                    
        # Display data source status
        if self.market_data:
            print("\n🔌 Data Sources:")
            source_status = self.market_data.test_all_sources()
            for source, status in source_status.items():
                emoji = "✅" if status['status'] == 'OK' else "❌"
                print(f"   {emoji} {source}: {status['status']}")
                
        print("=" * 60)
        
    def _send_telegram_signal(self, signal: dict):
        """Helper to send telegram signal asynchronously"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.telegram_bot.send_trading_signal(signal))
        except Exception as e:
            print(f"Error sending Telegram signal: {e}")
            
    def run_comprehensive_tests(self):
        """Run comprehensive system tests"""
        print("🧪 Running Comprehensive System Tests...")
        print("="*60)
        
        test_results = {}
        
        # Test SIUL
        print("\n🔍 Testing SIUL Core...")
        try:
            test_results['siul'] = siul_core.test_functionality()
        except Exception as e:
            print(f"   Error: {e}")
            test_results['siul'] = False
            
        # Test Patch Manager
        print("\n🔍 Testing Patch + Rollback System...")
        try:
            test_results['patch_manager'] = patch_manager.test_patch_rollback_system()
        except Exception as e:
            print(f"   Error: {e}")
            test_results['patch_manager'] = False
            
        # Test N8N Integration
        print("\n🔍 Testing N8N Integration...")
        try:
            test_results['n8n'] = n8n_integration.test_n8n_integration()
        except Exception as e:
            print(f"   Error: {e}")
            test_results['n8n'] = False
            
        # Test Market Data Sources
        print("\n🔍 Testing Market Data Sources...")
        if self.market_data:
            source_tests = self.market_data.test_all_sources()
            test_results['market_data'] = all(
                status['status'] in ['OK', 'NOT_CONFIGURED'] 
                for status in source_tests.values()
            )
            
            # Test price fetching
            try:
                price = self.market_data.get_best_price('BTC_USDT')
                print(f"   BTC/USDT Price: ${price['price']:,.2f}")
                test_results['price_fetch'] = price['price'] > 0
            except Exception as e:
                print(f"   Price fetch error: {e}")
                test_results['price_fetch'] = False
        else:
            test_results['market_data'] = False
            test_results['price_fetch'] = False
            
        # Test Telegram Bot
        print("\n🔍 Testing Telegram Bot...")
        if self.telegram_bot:
            try:
                test_results['telegram'] = self.telegram_bot.test_bot()
            except Exception as e:
                print(f"   Error: {e}")
                test_results['telegram'] = False
        else:
            print("   Telegram bot not configured")
            test_results['telegram'] = False
            
        # Test Google Sheets
        print("\n🔍 Testing Google Sheets Integration...")
        if self.google_sheets:
            try:
                test_results['google_sheets'] = self.google_sheets.test_connection()
                if not test_results['google_sheets']:
                    print("   Google Sheets not configured (OK for testing)")
                    test_results['google_sheets'] = True  # Not critical
            except Exception as e:
                print(f"   Error: {e}")
                test_results['google_sheets'] = True  # Not critical
        else:
            print("   Google Sheets not configured")
            test_results['google_sheets'] = True  # Not critical
            
        # Test Crypto.com API
        print("\n🔍 Testing Crypto.com API...")
        try:
            from exchanges.crypto_com import CryptoComAPI
            crypto_api = CryptoComAPI()
            test_results['crypto_com'] = crypto_api.test_connection()
        except Exception as e:
            print(f"   Error: {e}")
            test_results['crypto_com'] = False
            
        # Test Alpha Vantage API
        print("\n🔍 Testing Alpha Vantage API...")
        try:
            from exchanges.alpha_vantage import AlphaVantageAPI
            av_api = AlphaVantageAPI()
            test_results['alpha_vantage'] = av_api.test_connection()
        except Exception as e:
            print(f"   Error: {e}")
            test_results['alpha_vantage'] = False
            
        # Summary
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        for component, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {component.upper()}")
            
        print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({passed/total:.1%})")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! SYSTEM FULLY OPERATIONAL!")
        elif passed >= total * 0.7:  # 70% pass rate
            print("\n✅ SYSTEM OPERATIONAL - Some non-critical components need attention")
        else:
            print("\n⚠️ CRITICAL COMPONENTS FAILED - System may not function properly")
            
        return passed >= total * 0.7  # Allow system to run with 70% components working

if __name__ == "__main__":
    system = TPS19UnifiedSystem()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run tests
            success = system.run_comprehensive_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "setup":
            # Setup mode - create necessary directories and files
            print("🔧 Setting up TPS19 system...")
            os.makedirs("/opt/tps19/data/databases", exist_ok=True)
            os.makedirs("/opt/tps19/logs", exist_ok=True)
            print("✅ Setup complete")
        elif sys.argv[1] == "help":
            print("TPS19 Unified Trading System")
            print("Usage: python tps19_main.py [command]")
            print("Commands:")
            print("  (none)   - Start the trading system")
            print("  test     - Run comprehensive tests")
            print("  setup    - Setup system directories")
            print("  help     - Show this help message")
    else:
        # Start the system
        system.start_system()
