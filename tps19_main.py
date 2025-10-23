#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM"""

import sys, os, time, threading, signal
from datetime import datetime

# Add module paths
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace_dir, 'modules'))
# Support both workspace and production paths
if os.path.exists('/opt/tps19/modules'):
    sys.path.insert(0, '/opt/tps19/modules')

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    print(f"   Workspace: {workspace_dir}")
    sys.exit(1)

# Import Phase 1 AI/ML modules
try:
    from ai_models import LSTMPredictor, GANSimulator, SelfLearningPipeline
    from redis_integration import RedisIntegration
    from google_sheets_integration import GoogleSheetsIntegration
    print("✅ Phase 1 AI/ML modules imported successfully")
    PHASE1_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Phase 1 modules not available: {e}")
    print("   Install dependencies: pip install -r requirements_phase1.txt")
    PHASE1_AVAILABLE = False

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
        
        # Initialize Phase 1 components if available
        if PHASE1_AVAILABLE:
            self._init_phase1_components()
            
    def _init_phase1_components(self):
        """Initialize Phase 1 AI/ML components"""
        try:
            # Initialize LSTM predictor
            self.lstm_predictor = LSTMPredictor()
            self.system_components['lstm'] = self.lstm_predictor
            print("✅ LSTM Predictor initialized")
            
            # Initialize GAN simulator
            self.gan_simulator = GANSimulator()
            self.system_components['gan'] = self.gan_simulator
            print("✅ GAN Simulator initialized")
            
            # Initialize self-learning pipeline
            self.learning_pipeline = SelfLearningPipeline()
            self.system_components['learning'] = self.learning_pipeline
            print("✅ Self-Learning Pipeline initialized")
            
            # Initialize Redis (optional)
            try:
                self.redis = RedisIntegration()
                if self.redis.connected:
                    self.system_components['redis'] = self.redis
                    print("✅ Redis connected")
                else:
                    print("⚠️ Redis not available (optional)")
            except Exception as e:
                print(f"⚠️ Redis initialization failed (optional): {e}")
                
            # Initialize Google Sheets (optional)
            try:
                self.google_sheets = GoogleSheetsIntegration()
                if self.google_sheets.connected:
                    self.system_components['google_sheets'] = self.google_sheets
                    print("✅ Google Sheets connected")
                else:
                    print("⚠️ Google Sheets not available (optional)")
            except Exception as e:
                print(f"⚠️ Google Sheets initialization failed (optional): {e}")
                
        except Exception as e:
            print(f"⚠️ Phase 1 component initialization error: {e}")
        
    def start_system(self):
        """Start the complete unified system"""
        try:
            print("🚀 Starting TPS19 Definitive Unified System...")
            self.running = True
            
            # Start N8N service
            n8n_integration.start_n8n_service()
            
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
                        n8n_integration.send_trade_signal({
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
        # Start health check server for Cloud Run
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthCheckHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK')
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress HTTP logs
        
        # Start health check server in background
        port = int(os.environ.get('PORT', 8080))
        health_server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        health_thread = threading.Thread(target=health_server.serve_forever, daemon=True)
        health_thread.start()
        print(f"✅ Health check server running on port {port}")
        
        # Start main trading system
        system.start_system()
