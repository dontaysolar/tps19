#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM"""

import sys, os, time, threading, signal
from datetime import datetime
try:
    # Prefer local modules path via environment
    modules_dir = os.getenv('TPS19_MODULES_DIR')
    if modules_dir:
        sys.path.insert(0, modules_dir)
    else:
        sys.path.insert(0, '/opt/tps19/modules')
except Exception:
    pass

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    from integrations.telegram_notifier import telegram_notifier
    from integrations.google_sheets_logger import sheets_logger
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19UnifiedSystem:
    """TPS19 Definitive Unified System"""
    
    def __init__(self):
        self.running = False
        self.exchange = 'crypto.com'
        self.system_components = {
            'siul': siul_core,
            'patch_manager': patch_manager,
            'n8n': n8n_integration
        }
        
    def start_system(self):
        """Start the complete unified system"""
        try:
            print("🚀 Starting TPS19 Definitive Unified System...")
            self.running = True
            # Optional integrations
            try:
                from services import telegram_service as _tg
            except Exception:
                _tg = None
            
            # Start N8N service
            n8n_integration.start_n8n_service()

            # Notify start
            if _tg and getattr(_tg, 'enabled', lambda: False)():
                _tg.send_message("🚀 TPS19 Unified System started (crypto.com primary)")
            
            # Main system loop
            while self.running:
                # SIUL processing
                test_data = {
                    'symbol': 'BTC_USDT',
                    'price': 45000 + (time.time() % 1000),
                    'volume': 1500,
                    'exchange': 'crypto.com'
                }
                
                siul_result = siul_core.process_unified_logic(test_data)
                
                if siul_result and siul_result.get('final_decision'):
                    decision = siul_result['final_decision']
                    
                    # Send to N8N if significant decision
                    if decision.get('confidence', 0) > 0.7:
                        signal_payload = {
                            'symbol': test_data['symbol'],
                            'action': decision['decision'],
                            'price': test_data['price'],
                            'confidence': decision['confidence']
                        }
                        n8n_integration.send_trade_signal(signal_payload)
                        # Notify Telegram (no-op if not configured)
                        telegram_notifier.send_trade_signal(
                            test_data['symbol'], decision['decision'], test_data['price'], decision['confidence']
                        )
                        # Log to Google Sheets via webhook (no-op if not configured)
                        sheets_logger.log_event('trade_signal', {
                            'symbol': test_data['symbol'],
                            'action': decision['decision'],
                            'price': test_data['price'],
                            'confidence': decision['confidence']
                        })
                        
                print(f"💓 TPS19 Unified System - {datetime.now()}")
                print(f"🧠 SIUL Decision: {siul_result.get('final_decision', {}).get('decision', 'hold')}")
                print(f"📊 Confidence: {siul_result.get('confidence', 0):.2%}")
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("🛑 Stopping TPS19 Unified System...")
            self.running = False
            try:
                from services import telegram_service as _tg
                if _tg.enabled():
                    _tg.send_message("🛑 TPS19 Unified System stopped")
            except Exception:
                pass
        except Exception as e:
            print(f"❌ System error: {e}")
            
    def run_comprehensive_tests(self):
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

if __name__ == "__main__":
    system = TPS19UnifiedSystem()
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        system.run_comprehensive_tests()
    else:
        system.start_system()
