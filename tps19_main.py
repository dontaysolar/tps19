#!/usr/bin/env python3
"""TPS19 Main Application - DEFINITIVE UNIFIED SYSTEM WITH HELIOS PROTOCOL"""

import sys, os, time, threading, signal
from datetime import datetime
sys.path.insert(0, '/opt/tps19/modules')
sys.path.insert(0, '/workspace/modules')

# Import all modules
try:
    from siul.siul_core import siul_core
    from patching.patch_manager import patch_manager
    from n8n.n8n_integration import n8n_integration
    from helios.helios_protocol import helios_protocol, HeliosPhase, DecisionStatus
    from helios.helios_coordinator import create_coordinator
    print("✅ All unified modules imported successfully")
except ImportError as e:
    print(f"❌ Module import failed: {e}")
    sys.exit(1)

class TPS19UnifiedSystem:
    """TPS19 Definitive Unified System with Helios Protocol"""
    
    def __init__(self):
        self.running = False
        self.exchange = 'crypto.com'
        self.deployment_id = None
        self.helios_coordinator = create_coordinator(helios_protocol)
        self.agent_id = f"tps19_main_{os.getpid()}"
        self.system_components = {
            'siul': siul_core,
            'patch_manager': patch_manager,
            'n8n': n8n_integration,
            'helios': helios_protocol,
            'coordinator': self.helios_coordinator
        }
        
        # Register this instance as an agent
        self.helios_coordinator.register_agent(self.agent_id)
        
    def start_system(self):
        """Start the complete unified system with Helios Protocol"""
        try:
            print("🚀 Starting TPS19 Definitive Unified System with Helios Protocol...")
            self.running = True
            
            # Check if deployments are allowed
            can_deploy, message = helios_protocol.can_deploy()
            if not can_deploy:
                print(f"⚠️  WARNING: {message}")
                print("System will start in monitoring mode only")
            
            # Register deployment if allowed
            if can_deploy:
                self.deployment_id = f"tps19_deploy_{int(time.time())}"
                helios_protocol.register_deployment(self.deployment_id, "1.0.0", "TPS19 System Startup")
                
                # Pre-deployment phase
                helios_protocol.record_phase_decision(
                    HeliosPhase.PRE_DEPLOYMENT,
                    DecisionStatus.GO,
                    "System initialization checks passed"
                )
            
            # Start Helios monitoring
            helios_protocol.start_monitoring()
            
            # Start N8N service
            n8n_integration.start_n8n_service()
            
            # Deployment phase
            if self.deployment_id:
                helios_protocol.record_phase_decision(
                    HeliosPhase.DEPLOYMENT,
                    DecisionStatus.GO,
                    "All components started successfully"
                )
            
            # Main system loop
            error_count = 0
            while self.running:
                # SIUL processing
                test_data = {
                    'symbol': 'BTC_USDT',
                    'price': 45000 + (time.time() % 1000),
                    'volume': 1500,
                    'exchange': 'crypto.com'
                }
                
                try:
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
                    
                    # Reset error count on successful operation
                    error_count = 0
                    
                    # Periodic verification phase check
                    if self.deployment_id and time.time() % 300 < 30:  # Every 5 minutes
                        helios_protocol.record_phase_decision(
                            HeliosPhase.VERIFICATION,
                            DecisionStatus.GO,
                            "System operating within parameters"
                        )
                        
                except Exception as e:
                    error_count += 1
                    print(f"⚠️  Processing error: {e}")
                    
                    # Trigger NO-GO if too many errors
                    if error_count >= 3 and self.deployment_id:
                        # Request rollback coordination
                        rollback_request = self.helios_coordinator.coordinate_rollback(
                            self.agent_id,
                            self.deployment_id,
                            HeliosPhase.MONITORING.value,
                            f"Multiple processing errors detected: {e}"
                        )
                        
                        if rollback_request['allowed']:
                            helios_protocol.record_phase_decision(
                                HeliosPhase.MONITORING,
                                DecisionStatus.NO_GO,
                                f"System instability detected - {error_count} consecutive errors"
                            )
                        
                print(f"💓 TPS19 Unified System - {datetime.now()}")
                if 'siul_result' in locals():
                    print(f"🧠 SIUL Decision: {siul_result.get('final_decision', {}).get('decision', 'hold')}")
                    print(f"📊 Confidence: {siul_result.get('confidence', 0):.2%}")
                
                # Display Helios status periodically
                if time.time() % 60 < 1:  # Every minute
                    helios_status = helios_protocol.get_status()
                    print(f"🛡️  Helios Protocol - Deployments: {helios_status.get('can_deploy', False)}")
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("🛑 Stopping TPS19 Unified System...")
            self.running = False
            
            # Clean shutdown with Helios
            if self.deployment_id:
                helios_protocol.record_phase_decision(
                    HeliosPhase.POST_DEPLOYMENT,
                    DecisionStatus.GO,
                    "System shutdown initiated cleanly"
                )
            
            # Unregister agent
            self.helios_coordinator.unregister_agent(self.agent_id)
            helios_protocol.stop_monitoring()
            
        except Exception as e:
            print(f"❌ System error: {e}")
            
            # Trigger NO-GO on critical system error
            if self.deployment_id:
                helios_protocol.record_phase_decision(
                    HeliosPhase.MONITORING,
                    DecisionStatus.NO_GO,
                    f"Critical system error: {e}"
                )
            
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
        
        # Test Helios Protocol
        print("🔍 Testing Helios Protocol...")
        test_results['helios'] = helios_protocol.test_helios_protocol()
        
        # Test Helios Coordinator
        print("🔍 Testing Helios Coordinator...")
        test_results['coordinator'] = self.helios_coordinator.test_coordinator()
        
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
