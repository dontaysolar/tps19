#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM"""

import sys, os, time, threading, signal
from urllib.parse import urlparse
from datetime import datetime

# Add module paths
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace_dir, 'modules'))
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
    from ai_models import (
        LSTMPredictor,
        GANSimulator,
        SelfLearningPipeline,
        TransformerAnalyzer,
    )
    from redis_integration import RedisIntegration
    from google_sheets_integration import GoogleSheetsIntegration
    from risk_management import RiskManager
    from nexus_coordinator import NexusCoordinator
    from strategy_hub import StrategyHub
    from env_validation import print_validation_summary
    try:
        from websocket_feeds import WebSocketFeeds
    except Exception:
        WebSocketFeeds = None  # type: ignore
    try:
        from strategies import FoxModeStrategy, MarketMakerStrategy, ArbitrageKingStrategy
    except Exception:
        FoxModeStrategy = MarketMakerStrategy = ArbitrageKingStrategy = None  # type: ignore
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
        self._price_history = []
        
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

            # Initialize Transformer analyzer
            try:
                self.transformer_analyzer = TransformerAnalyzer()
                self.system_components['transformer'] = self.transformer_analyzer
                print("✅ Transformer Analyzer initialized")
            except Exception as e:
                print(f"⚠️ Transformer Analyzer initialization failed (optional): {e}")

            # Initialize Risk Manager
            try:
                self.risk_manager = RiskManager()
                self.system_components['risk_manager'] = self.risk_manager
                print("✅ Risk Manager initialized")
            except Exception as e:
                print(f"⚠️ Risk Manager initialization failed (optional): {e}")

            # Initialize NEXUS Coordinator
            try:
                self.nexus_coordinator = NexusCoordinator()
                self.system_components['nexus'] = self.nexus_coordinator
                print("✅ NEXUS Coordinator initialized")
            except Exception as e:
                print(f"⚠️ NEXUS Coordinator initialization failed (optional): {e}")

            # Initialize Strategy Hub
            try:
                self.strategy_hub = StrategyHub()
                self.system_components['strategy_hub'] = self.strategy_hub
                print("✅ Strategy Hub initialized")
            except Exception as e:
                print(f"⚠️ Strategy Hub initialization failed (optional): {e}")

            # Initialize advanced strategies (optional)
            try:
                self.fox_mode = FoxModeStrategy() if 'FoxModeStrategy' in globals() and FoxModeStrategy else None
                self.market_maker = MarketMakerStrategy() if 'MarketMakerStrategy' in globals() and MarketMakerStrategy else None
                self.arbitrage_king = ArbitrageKingStrategy() if 'ArbitrageKingStrategy' in globals() and ArbitrageKingStrategy else None
                print("✅ Advanced strategies ready")
            except Exception as e:
                print(f"⚠️ Advanced strategies init failed (optional): {e}")

            # Initialize WebSocket Feeds (optional)
            try:
                if 'WebSocketFeeds' in globals() and WebSocketFeeds is not None:
                    self.websocket_feeds = WebSocketFeeds()
                    self.system_components['websocket_feeds'] = self.websocket_feeds
                    print("✅ WebSocket Feeds ready")
                else:
                    print("⚠️ WebSocket Feeds not available (optional)")
            except Exception as e:
                print(f"⚠️ WebSocket Feeds initialization failed (optional): {e}")
            
            # Initialize Redis (optional)
            try:
                # Support REDIS_URL or individual vars
                redis_url = os.environ.get('REDIS_URL')
                if redis_url:
                    parsed = urlparse(redis_url)
                    redis_host = parsed.hostname or 'localhost'
                    redis_port = parsed.port or 6379
                    # For URLs like redis://:password@host:port/db
                    redis_password = parsed.password
                    try:
                        redis_db = int((parsed.path or '/0').lstrip('/'))
                    except Exception:
                        redis_db = 0
                else:
                    redis_host = os.environ.get('REDIS_HOST', 'localhost')
                    redis_port = int(os.environ.get('REDIS_PORT', '6379') or 6379)
                    redis_db = int(os.environ.get('REDIS_DB', '0') or 0)
                    redis_password = os.environ.get('REDIS_PASSWORD')
                self.redis = RedisIntegration(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
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
                    # Ensure a dashboard exists
                    if not getattr(self.google_sheets, 'spreadsheet_id', None):
                        try:
                            self.google_sheets.create_dashboard('TPS19 Trading Dashboard')
                        except Exception as e:
                            print(f"⚠️ Could not create Google Sheets dashboard: {e}")
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

            # Environment validation summary
            try:
                print_validation_summary()
            except Exception as e:
                print(f"⚠️ Env validation unavailable: {e}")
            
            # Start N8N service
            n8n_integration.start_n8n_service()
            
            # Optional WebSocket subscription
            try:
                if hasattr(self, 'websocket_feeds'):
                    ws_url = os.environ.get('WEBSOCKET_URL')
                    if ws_url and not hasattr(self, '_ws_started'):
                        self.websocket_feeds.subscribe_generic(ws_url, lambda msg: None)
                        self._ws_started = True
                        print(f"🔌 Subscribed to WebSocket: {ws_url}")
            except Exception as e:
                print(f"⚠️ WebSocket subscription error: {e}")

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
                
                # Update price history and run transformer prediction (optional)
                try:
                    self._price_history.append(float(test_data['price']))
                    if len(self._price_history) > 500:
                        self._price_history = self._price_history[-500:]
                except Exception:
                    pass

                transformer_pred = None
                if hasattr(self, 'transformer_analyzer') and self._price_history:
                    try:
                        transformer_pred = self.transformer_analyzer.predict_direction(self._price_history, horizon_steps=30)
                    except Exception as e:
                        print(f"⚠️ Transformer prediction error: {e}")

                # Kelly-based position size (optional)
                recommended_pos_value = None
                if hasattr(self, 'risk_manager') and transformer_pred:
                    try:
                        p = float(transformer_pred.get('confidence', 0.0) or 0.0)
                        portfolio_value = float(os.environ.get('PORTFOLIO_VALUE', '100') or 100)
                        recommended_pos_value = self.risk_manager.calculate_kelly_position(
                            portfolio_value=portfolio_value,
                            win_rate=max(0.0, min(1.0, p)),
                            reward_risk=1.5,
                        )
                    except Exception as e:
                        print(f"⚠️ Kelly sizing error: {e}")

                # NEXUS combined decision (optional)
                combined = None
                if hasattr(self, 'nexus_coordinator'):
                    try:
                        combined = self.nexus_coordinator.combine_decisions(
                            siul_result.get('final_decision', {}) if isinstance(siul_result, dict) else {},
                            transformer_pred,
                            recommended_pos_value,
                        )
                    except Exception as e:
                        print(f"⚠️ NEXUS combination error: {e}")

                # Optional: StrategyHub could pick best among multiple strategy candidates
                if hasattr(self, 'strategy_hub'):
                    try:
                        candidates = []
                        if transformer_pred:
                            candidates.append({
                                'strategy': 'transformer',
                                'pair': test_data['symbol'].replace('_', '/'),
                                'signal': 'BUY' if transformer_pred.get('direction') == 'UP' else 'SELL' if transformer_pred.get('direction') == 'DOWN' else 'HOLD',
                                'confidence': transformer_pred.get('confidence', 0.0)
                            })
                        if siul_result and siul_result.get('final_decision'):
                            candidates.append({
                                'strategy': 'siul',
                                'pair': test_data['symbol'].replace('_', '/'),
                                'signal': siul_result['final_decision'].get('decision', 'hold').upper(),
                                'confidence': float(siul_result.get('confidence', 0.0))
                            })
                        # Advanced strategies candidates (use simple anchors/momentum heuristics)
                        if hasattr(self, 'fox_mode') and self.fox_mode and transformer_pred is not None:
                            candidates.append(self.fox_mode.generate_signal(test_data['symbol'].replace('_', '/'), momentum=transformer_pred.get('momentum', 0.0) or 0.0, volatility=transformer_pred.get('volatility', 0.0) or 0.0))
                        if hasattr(self, 'market_maker') and self.market_maker:
                            anchor = self._price_history[-50] if len(self._price_history) >= 50 else (self._price_history[0] if self._price_history else 0.0)
                            candidates.append(self.market_maker.generate_signal(test_data['symbol'].replace('_', '/'), last_price=float(test_data['price']), anchor_price=float(anchor)))
                        if hasattr(self, 'arbitrage_king') and self.arbitrage_king:
                            # Placeholder: compare current price vs last recorded price
                            prev_price = self._price_history[-2] if len(self._price_history) >= 2 else float(test_data['price'])
                            candidates.append(self.arbitrage_king.generate_signal(test_data['symbol'].replace('_', '/'), price_a=float(test_data['price']), price_b=float(prev_price)))
                        best_candidate = self.strategy_hub.select(candidates)
                        if best_candidate:
                            print(f"🧭 StrategyHub selected: {best_candidate.get('strategy')} -> {best_candidate.get('signal')} ({best_candidate.get('confidence', 0.0):.0%})")
                    except Exception as e:
                        print(f"⚠️ StrategyHub selection error: {e}")

                if siul_result and siul_result.get('final_decision'):
                    decision = siul_result['final_decision']
                    
                    # Send to N8N if significant decision
                    if decision.get('confidence', 0) > 0.7:
                        payload = {
                            'symbol': test_data['symbol'],
                            'action': decision['decision'],
                            'price': test_data['price'],
                            'confidence': decision['confidence'],
                        }
                        if recommended_pos_value is not None:
                            payload['kelly_position_value'] = round(float(recommended_pos_value), 2)
                        if transformer_pred:
                            payload['transformer'] = {
                                'direction': transformer_pred.get('direction'),
                                'confidence': transformer_pred.get('confidence')
                            }
                        n8n_integration.send_trade_signal(payload)
                        
                print(f"💓 TPS19 Unified System - {datetime.now()}")
                print(f"🧠 SIUL Decision: {siul_result.get('final_decision', {}).get('decision', 'hold')}")
                print(f"📊 Confidence: {siul_result.get('confidence', 0):.2%}")
                if transformer_pred:
                    print(f"🔎 Transformer: {transformer_pred.get('direction')} ({transformer_pred.get('confidence', 0.0):.0%})")
                if combined:
                    print(f"🎛️ Combined: {combined.get('signal')} ({combined.get('confidence', 0.0):.0%})")
                if recommended_pos_value is not None:
                    print(f"💰 Kelly position (value): ${recommended_pos_value:.2f}")

                # Persist lightweight system status for Telegram queries
                try:
                    os.makedirs('data', exist_ok=True)
                    status_payload = {
                        'transformer': {
                            'direction': transformer_pred.get('direction') if transformer_pred else None,
                            'confidence': transformer_pred.get('confidence') if transformer_pred else None,
                        },
                        'kelly': {
                            'position_value': float(recommended_pos_value) if recommended_pos_value is not None else 0.0,
                            'win_rate': float(transformer_pred.get('confidence', 0.0)) if transformer_pred else 0.0,
                        },
                        'combined': combined or {},
                        'timestamp': datetime.now().isoformat(),
                    }
                    with open('data/system_status.json', 'w') as f:
                        import json as _json
                        _json.dump(status_payload, f, indent=2)
                except Exception as _e:
                    pass

                # Google Sheets overview update (light)
                try:
                    if hasattr(self, 'google_sheets') and self.google_sheets.connected and getattr(self.google_sheets, 'spreadsheet_id', None):
                        ai_models_running = sum(1 for k in ['lstm', 'gan', 'learning', 'transformer'] if k in self.system_components)
                        self.google_sheets.update_overview({
                            'trading_status': 'Active' if self.running else 'Stopped',
                            'strategies_active': 1,  # placeholder: SIUL
                            'ai_models_running': ai_models_running,
                            'last_trade': '',
                        })
                except Exception as e:
                    print(f"⚠️ Google Sheets update failed: {e}")
                
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
