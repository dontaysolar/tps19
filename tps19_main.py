#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM"""

import sys, os, time, threading, signal, asyncio
from datetime import datetime
sys.path.insert(0, '/opt/tps19/modules')
sys.path.insert(0, '/workspace/modules')

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    from market_data import MarketData
    from realtime_data import RealtimeDataFeed
    from telegram_bot import telegram_bot, send_trade_signal, initialize_telegram
    from google_sheets import sheets_integration, log_trade_to_sheets
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19UnifiedSystem:
    """TPS19 Definitive Unified System"""
    
    def __init__(self):
        self.running = False
        self.exchange = 'crypto.com'
        self.market_data = MarketData()
        self.realtime_feed = RealtimeDataFeed()
        self.system_components = {
            'siul': siul_core,
            'patch_manager': patch_manager,
            'n8n': n8n_integration,
            'market_data': self.market_data,
            'realtime_feed': self.realtime_feed,
            'telegram': telegram_bot,
            'sheets': sheets_integration
        }
        
    async def start_system(self):
        """Start the complete unified system"""
        try:
            print("🚀 Starting TPS19 Definitive Unified System...")
            self.running = True
            
            # Initialize integrations
            await self.initialize_integrations()
            
            # Start real-time data feed
            self.realtime_feed.start_feed()
            
            # Start N8N service
            n8n_integration.start_n8n_service()
            
            # Main system loop
            while self.running:
                # Get real market data
                symbol = 'BTC_USDT'
                market_price = self.market_data.get_price(symbol)
                market_stats = self.market_data.get_market_stats(symbol)
                
                test_data = {
                    'symbol': symbol,
                    'price': market_price,
                    'volume': market_stats.get('volume', 1500),
                    'exchange': 'crypto.com',
                    'high_24h': market_stats.get('high_24h', 0),
                    'low_24h': market_stats.get('low_24h', 0),
                    'change_24h': market_stats.get('change_24h', 0)
                }
                
                siul_result = siul_core.process_unified_logic(test_data)
                
                if siul_result and siul_result.get('final_decision'):
                    decision = siul_result['final_decision']
                    confidence = decision.get('confidence', 0)
                    action = decision.get('decision', 'hold')
                    
                    # Send to N8N if significant decision
                    if confidence > 0.7:
                        n8n_integration.send_trade_signal({
                            'symbol': symbol,
                            'action': action,
                            'price': market_price,
                            'confidence': confidence
                        })
                        
                        # Send Telegram alert
                        await send_trade_signal(symbol, action, market_price, confidence)
                        
                        # Log to Google Sheets
                        log_trade_to_sheets(symbol, action, market_price, 
                                          confidence=confidence, 
                                          notes="Automated SIUL decision")
                        
                print(f"💓 TPS19 Unified System - {datetime.now()}")
                print(f"📊 {symbol}: ${market_price:,.2f} ({market_stats.get('change_24h', 0):.2f}%)")
                print(f"🧠 SIUL Decision: {action}")
                print(f"📊 Confidence: {confidence:.2%}")
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("🛑 Stopping TPS19 Unified System...")
            await self.stop_system()
        except Exception as e:
            print(f"❌ System error: {e}")
            await self.stop_system()
            
    async def initialize_integrations(self):
        """Initialize all system integrations"""
        print("🔧 Initializing system integrations...")
        
        # Initialize Telegram
        if await initialize_telegram():
            print("✅ Telegram integration ready")
        else:
            print("⚠️ Telegram integration failed")
            
        # Initialize Google Sheets
        if sheets_integration.authenticate():
            sheets_integration.get_or_create_spreadsheet()
            print("✅ Google Sheets integration ready")
        else:
            print("⚠️ Google Sheets integration failed")
            
    async def stop_system(self):
        """Stop all system components"""
        self.running = False
        
        # Stop real-time feed
        if hasattr(self, 'realtime_feed'):
            self.realtime_feed.stop_feed()
            
        print("✅ TPS19 Unified System stopped")
            
    async def run_comprehensive_tests(self):
        """Run comprehensive system tests"""
        print("🧪 Running Comprehensive System Tests...")
        print("="*60)
        
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
        print("🔍 Testing Market Data Integration...")
        try:
            price = self.market_data.get_price('BTC_USDT')
            test_results['market_data'] = price > 0
            print(f"✅ Market Data: BTC price ${price:,.2f}")
        except Exception as e:
            test_results['market_data'] = False
            print(f"❌ Market Data failed: {e}")
            
        # Test Telegram
        print("🔍 Testing Telegram Integration...")
        try:
            test_results['telegram'] = await initialize_telegram()
        except Exception as e:
            test_results['telegram'] = False
            print(f"❌ Telegram failed: {e}")
            
        # Test Google Sheets
        print("🔍 Testing Google Sheets Integration...")
        try:
            test_results['sheets'] = sheets_integration.authenticate()
        except Exception as e:
            test_results['sheets'] = False
            print(f"❌ Google Sheets failed: {e}")
        
        # Summary
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        for component, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {component.upper()}")
            
        print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! SYSTEM FULLY OPERATIONAL!")
        else:
            print("⚠️ SOME TESTS FAILED - CHECK COMPONENTS")
            
        return passed == total

async def main():
    """Main async function"""
    system = TPS19UnifiedSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await system.run_comprehensive_tests()
    else:
        await system.start_system()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)
