#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED CRYPTO TRADING SYSTEM"""

import sys, os, time, threading, signal
from datetime import datetime
sys.path.insert(0, '/workspace/modules')

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    from market_data import MarketData
    from trading_engine import trading_engine, OrderSide, OrderType, TradingMode
    from telegram_bot import telegram_bot
    from google_sheets_integration import google_sheets
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19UnifiedSystem:
    """TPS19 Definitive Unified Crypto Trading System"""
    
    def __init__(self):
        self.running = False
        self.exchange = 'crypto.com'
        self.system_components = {
            'siul': siul_core,
            'patch_manager': patch_manager,
            'n8n': n8n_integration,
            'market_data': MarketData(),
            'trading_engine': trading_engine,
            'telegram_bot': telegram_bot,
            'google_sheets': google_sheets
        }
        self.notification_interval = 300  # 5 minutes
        self.last_notification = 0
        
    def start_system(self):
        """Start the complete unified system"""
        try:
            print("🚀 Starting TPS19 Definitive Unified Crypto Trading System...")
            print("="*80)
            
            # Initialize all components
            self._initialize_components()
            
            # Start background services
            self._start_background_services()
            
            self.running = True
            
            # Main system loop
            while self.running:
                try:
                    # Get market data
                    market_data = self.system_components['market_data'].get_unified_market_data('BTC_USDT')
                    
                    # Process through SIUL
                    siul_result = siul_core.process_unified_logic({
                        'symbol': 'BTC_USDT',
                        'price': market_data.get('price', 50000),
                        'volume': market_data.get('volume_24h', 1000),
                        'exchange': 'crypto.com'
                    })
                    
                    # Execute trading decisions
                    if siul_result and siul_result.get('final_decision'):
                        self._process_trading_decision(siul_result, market_data)
                    
                    # Send notifications
                    self._send_periodic_notifications(market_data, siul_result)
                    
                    # Log data to Google Sheets
                    self._log_system_data(market_data, siul_result)
                    
                    # System status
                    self._display_system_status(market_data, siul_result)
                    
                    time.sleep(30)  # 30-second cycle
                    
                except KeyboardInterrupt:
                    print("\n🛑 Stopping TPS19 Unified System...")
                    self.running = False
                    break
                except Exception as e:
                    print(f"❌ System error: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            print(f"❌ Critical system error: {e}")
        finally:
            self._cleanup()
    
    def _initialize_components(self):
        """Initialize all system components"""
        print("🔧 Initializing system components...")
        
        # Test market data connections
        market_data = self.system_components['market_data']
        connections = market_data.test_all_connections()
        for exchange, status in connections.items():
            print(f"{'✅' if status else '❌'} {exchange.upper()}: {'Connected' if status else 'Failed'}")
        
        # Test trading engine
        if trading_engine.test_trading_engine():
            print("✅ Trading Engine: Ready")
        else:
            print("❌ Trading Engine: Failed")
        
        # Test Telegram bot
        if telegram_bot.test_telegram_bot():
            print("✅ Telegram Bot: Ready")
        else:
            print("⚠️ Telegram Bot: Not configured")
        
        # Test Google Sheets
        if google_sheets.test_google_sheets():
            print("✅ Google Sheets: Ready")
        else:
            print("⚠️ Google Sheets: Not configured")
        
        print("✅ Component initialization complete")
    
    def _start_background_services(self):
        """Start background services"""
        print("🔄 Starting background services...")
        
        # Start Telegram bot
        if telegram_bot.bot_token and telegram_bot.chat_id:
            telegram_bot.start_bot()
        
        # Start N8N service
        n8n_integration.start_n8n_service()
        
        print("✅ Background services started")
    
    def _process_trading_decision(self, siul_result: dict, market_data: dict):
        """Process SIUL trading decision"""
        try:
            decision = siul_result['final_decision']
            confidence = decision.get('confidence', 0)
            
            # Only execute high-confidence decisions
            if confidence > 0.7:
                symbol = 'BTC_USDT'
                side = OrderSide.BUY if decision['decision'] == 'buy' else OrderSide.SELL
                quantity = 0.001  # Small test quantity
                
                # Place order
                result = trading_engine.place_order(symbol, side, quantity, OrderType.MARKET)
                
                if result.get('success'):
                    # Send trade notification
                    trade_data = {
                        'symbol': symbol,
                        'side': side.value,
                        'quantity': quantity,
                        'price': market_data.get('price', 0),
                        'commission': result.get('commission', 0)
                    }
                    telegram_bot.send_trade_notification(trade_data)
                    
                    # Log to Google Sheets
                    google_sheets.log_trade(trade_data)
                    
                    print(f"✅ Trade executed: {side.value} {quantity} {symbol}")
                else:
                    print(f"❌ Trade failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            print(f"❌ Trading decision processing error: {e}")
    
    def _send_periodic_notifications(self, market_data: dict, siul_result: dict):
        """Send periodic notifications"""
        try:
            current_time = time.time()
            
            # Send notifications every 5 minutes
            if current_time - self.last_notification >= self.notification_interval:
                # Send SIUL decision
                if siul_result and siul_result.get('final_decision'):
                    telegram_bot.send_siul_decision(siul_result['final_decision'])
                
                # Send market update
                telegram_bot.send_market_update(market_data)
                
                # Send portfolio update
                portfolio = trading_engine.get_portfolio_summary()
                telegram_bot.send_portfolio_update(portfolio)
                
                self.last_notification = current_time
                
        except Exception as e:
            print(f"❌ Notification error: {e}")
    
    def _log_system_data(self, market_data: dict, siul_result: dict):
        """Log system data to Google Sheets"""
        try:
            # Log market data
            google_sheets.log_market_data(market_data)
            
            # Log portfolio data
            portfolio = trading_engine.get_portfolio_summary()
            google_sheets.log_portfolio_update(portfolio)
            
            # Sync pending data
            google_sheets.sync_pending_data()
            
        except Exception as e:
            print(f"❌ Data logging error: {e}")
    
    def _display_system_status(self, market_data: dict, siul_result: dict):
        """Display system status"""
        try:
            portfolio = trading_engine.get_portfolio_summary()
            
            print(f"\n💓 TPS19 Unified System - {datetime.now().strftime('%H:%M:%S')}")
            print("="*60)
            print(f"📊 Market: BTC_USDT @ ${market_data.get('price', 0):,.2f}")
            print(f"🧠 SIUL Decision: {siul_result.get('final_decision', {}).get('decision', 'hold').upper()}")
            print(f"🎯 Confidence: {siul_result.get('confidence', 0):.1%}")
            print(f"💰 Balance: ${portfolio.get('balance', 0):,.2f}")
            print(f"💎 Total Value: ${portfolio.get('total_value', 0):,.2f}")
            print(f"📈 P&L: ${portfolio.get('total_pnl', 0):,.2f}")
            print(f"📊 Positions: {portfolio.get('positions', 0)}")
            
        except Exception as e:
            print(f"❌ Status display error: {e}")
    
    def _cleanup(self):
        """Cleanup system resources"""
        try:
            print("🧹 Cleaning up system resources...")
            
            # Stop Telegram bot
            if telegram_bot.running:
                telegram_bot.stop_bot()
            
            # Stop N8N service
            n8n_integration.stop_n8n_service()
            
            print("✅ Cleanup complete")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
    
    def run_comprehensive_tests(self):
        """Run comprehensive system tests"""
        print("🧪 Running Comprehensive System Tests...")
        print("="*80)
        
        test_results = {}
        
        # Test SIUL
        print("🔍 Testing SIUL...")
        test_results['siul'] = siul_core.test_functionality()
        
        # Test Patch Manager
        print("🔍 Testing Patch + Rollback System...")
        test_results['patch_manager'] = patch_manager.test_patch_rollback_system()
        
        # Test N8N Integration
        print("🔍 Testing N8N Integration...")
        test_results['n8n'] = n8n_integration.test_n8n_integration()
        
        # Test Market Data
        print("🔍 Testing Market Data...")
        market_data = self.system_components['market_data']
        connections = market_data.test_all_connections()
        test_results['market_data'] = any(connections.values())
        
        # Test Trading Engine
        print("🔍 Testing Trading Engine...")
        test_results['trading_engine'] = trading_engine.test_trading_engine()
        
        # Test Telegram Bot
        print("🔍 Testing Telegram Bot...")
        test_results['telegram_bot'] = telegram_bot.test_telegram_bot()
        
        # Test Google Sheets
        print("🔍 Testing Google Sheets...")
        test_results['google_sheets'] = google_sheets.test_google_sheets()
        
        # Summary
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*80)
        
        for component, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {component.upper()}")
        
        print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! SYSTEM FULLY OPERATIONAL!")
        else:
            print("⚠️ SOME TESTS FAILED - CHECK COMPONENTS")
        
        return passed == total

if __name__ == "__main__":
    system = TPS19UnifiedSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        system.run_comprehensive_tests()
    else:
        system.start_system()
