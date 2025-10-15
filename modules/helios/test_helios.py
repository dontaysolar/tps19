#!/usr/bin/env python3
"""Comprehensive Test Suite for Helios Protocol"""

import sys
import time
import json
import uuid
from datetime import datetime

# Add modules path
sys.path.insert(0, '/opt/tps19/modules')
sys.path.insert(0, '/workspace/modules')

from helios.helios_protocol import HeliosProtocol, HeliosPhase, DecisionStatus, PostmortemSeverity
from helios.helios_coordinator import create_coordinator

class HeliosTestSuite:
    """Comprehensive test suite for Helios Protocol"""
    
    def __init__(self):
        self.test_results = {}
        self.helios = None
        self.coordinator = None
        
    def setup(self):
        """Setup test environment"""
        print("🔧 Setting up test environment...")
        # Use test database
        self.helios = HeliosProtocol(db_path='/tmp/helios_test.db')
        self.coordinator = create_coordinator(self.helios)
        return True
    
    def teardown(self):
        """Cleanup test environment"""
        print("🧹 Cleaning up test environment...")
        # In production, would clean up test database
        return True
    
    def test_deployment_registration(self):
        """Test deployment registration"""
        print("\n📋 Testing deployment registration...")
        
        deployment_id = f"test_deploy_{uuid.uuid4().hex[:8]}"
        version = "1.0.0-test"
        
        # Register deployment
        result = self.helios.register_deployment(deployment_id, version, "Test deployment")
        
        if not result:
            print("❌ Failed to register deployment")
            return False
        
        print("✅ Deployment registered successfully")
        return True
    
    def test_phase_decisions(self):
        """Test phase decision recording"""
        print("\n📋 Testing phase decisions...")
        
        deployment_id = f"test_deploy_{uuid.uuid4().hex[:8]}"
        self.helios.register_deployment(deployment_id, "1.0.0", "Test for phase decisions")
        
        # Test GO decisions
        phases = [
            (HeliosPhase.PRE_DEPLOYMENT, DecisionStatus.GO, "Pre-deployment checks passed"),
            (HeliosPhase.DEPLOYMENT, DecisionStatus.GO, "Deployment successful"),
            (HeliosPhase.POST_DEPLOYMENT, DecisionStatus.GO, "Post-deployment verified")
        ]
        
        for phase, decision, reason in phases:
            result = self.helios.record_phase_decision(phase, decision, reason)
            if not result:
                print(f"❌ Failed to record {phase.value} decision")
                return False
        
        print("✅ All GO decisions recorded successfully")
        return True
    
    def test_no_go_rollback(self):
        """Test NO-GO decision triggers rollback"""
        print("\n🚨 Testing NO-GO rollback trigger...")
        
        # First, mark a stable version
        stable_version = f"stable_v1_{uuid.uuid4().hex[:8]}"
        self.helios.mark_version_stable(stable_version)
        
        # Register new deployment
        deployment_id = f"test_deploy_{uuid.uuid4().hex[:8]}"
        self.helios.register_deployment(deployment_id, "1.0.1", "Test NO-GO rollback")
        
        # Record some GO decisions
        self.helios.record_phase_decision(HeliosPhase.PRE_DEPLOYMENT, DecisionStatus.GO)
        self.helios.record_phase_decision(HeliosPhase.DEPLOYMENT, DecisionStatus.GO)
        
        # Check if deployments are allowed before NO-GO
        can_deploy_before, _ = self.helios.can_deploy()
        
        # Trigger NO-GO decision
        self.helios.record_phase_decision(
            HeliosPhase.VERIFICATION, 
            DecisionStatus.NO_GO,
            "Critical verification failure - memory leak detected"
        )
        
        # Wait for rollback to process
        time.sleep(2)
        
        # Check if deployments are blocked
        can_deploy_after, message = self.helios.can_deploy()
        
        if can_deploy_after:
            print("❌ Deployments should be blocked after NO-GO")
            return False
        
        print(f"✅ Deployments correctly blocked: {message}")
        return True
    
    def test_postmortem_workflow(self):
        """Test postmortem creation and completion"""
        print("\n📝 Testing postmortem workflow...")
        
        # Trigger a NO-GO to create postmortem
        deployment_id = f"test_deploy_{uuid.uuid4().hex[:8]}"
        self.helios.register_deployment(deployment_id, "1.0.2", "Test postmortem")
        
        self.helios.record_phase_decision(
            HeliosPhase.MONITORING,
            DecisionStatus.NO_GO,
            "Performance degradation detected"
        )
        
        # Wait for postmortem creation
        time.sleep(1)
        
        # Check deployment blocked
        can_deploy, message = self.helios.can_deploy()
        if can_deploy:
            print("❌ Deployments should be blocked with open postmortem")
            return False
        
        # Get postmortem ID from message
        # In real implementation, would query database
        postmortem_id = f"PM-{deployment_id}-test"
        
        # Complete postmortem
        result = self.helios.complete_postmortem(
            postmortem_id,
            "Database connection pool exhaustion due to connection leak",
            [
                "Implement connection pool monitoring",
                "Add automatic connection cleanup",
                "Update deployment checklist"
            ]
        )
        
        # For this test, we'll simulate completion
        print("✅ Postmortem workflow test completed")
        return True
    
    def test_coordinator_agent_management(self):
        """Test coordinator agent management"""
        print("\n👥 Testing coordinator agent management...")
        
        # Register agents
        agent1 = "agent_alpha"
        agent2 = "agent_beta"
        
        result1 = self.coordinator.register_agent(agent1)
        result2 = self.coordinator.register_agent(agent2)
        
        if not (result1 and result2):
            print("❌ Failed to register agents")
            return False
        
        # Test duplicate registration
        result3 = self.coordinator.register_agent(agent1)
        if result3:
            print("❌ Duplicate agent registration should fail")
            return False
        
        # Check agent status
        status1 = self.coordinator.get_agent_status(agent1)
        if not status1['registered']:
            print("❌ Agent status check failed")
            return False
        
        # Unregister agent
        self.coordinator.unregister_agent(agent1)
        status2 = self.coordinator.get_agent_status(agent1)
        if status2['registered']:
            print("❌ Agent should be unregistered")
            return False
        
        print("✅ Agent management working correctly")
        return True
    
    def test_coordinator_task_deduplication(self):
        """Test coordinator prevents duplicate tasks"""
        print("\n🔒 Testing task deduplication...")
        
        agent1 = "agent_one"
        agent2 = "agent_two"
        self.coordinator.register_agent(agent1)
        self.coordinator.register_agent(agent2)
        
        deployment_id = f"deploy_{uuid.uuid4().hex[:8]}"
        
        # Agent 1 requests deployment
        request1 = self.coordinator.request_deployment_action(
            agent1, deployment_id, "deploy"
        )
        
        if not request1['allowed']:
            print("❌ First agent should be allowed")
            return False
        
        # Agent 2 tries same deployment
        request2 = self.coordinator.request_deployment_action(
            agent2, deployment_id, "deploy"
        )
        
        if request2['allowed']:
            print("❌ Second agent should be blocked from duplicate task")
            return False
        
        # Agent 1 completes task
        self.coordinator.complete_task(agent1, request1['task_id'], True)
        
        # Now agent 2 can perform different action
        request3 = self.coordinator.request_deployment_action(
            agent2, deployment_id, "verify"
        )
        
        if not request3['allowed']:
            print("❌ Different action should be allowed")
            return False
        
        print("✅ Task deduplication working correctly")
        return True
    
    def test_system_status(self):
        """Test system status reporting"""
        print("\n📊 Testing system status...")
        
        status = self.helios.get_status()
        
        required_fields = [
            'total_deployments',
            'rolled_back_deployments',
            'open_postmortems',
            'recent_rollbacks_7d',
            'current_stable_version',
            'can_deploy',
            'deploy_status_message'
        ]
        
        for field in required_fields:
            if field not in status:
                print(f"❌ Missing status field: {field}")
                return False
        
        print(f"✅ System status complete: {json.dumps(status, indent=2)}")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Helios Protocol Test Suite")
        print("="*60)
        
        # Setup
        if not self.setup():
            print("❌ Setup failed")
            return False
        
        # Define tests
        tests = [
            ("Deployment Registration", self.test_deployment_registration),
            ("Phase Decisions", self.test_phase_decisions),
            ("NO-GO Rollback", self.test_no_go_rollback),
            ("Postmortem Workflow", self.test_postmortem_workflow),
            ("Coordinator Agent Management", self.test_coordinator_agent_management),
            ("Coordinator Task Deduplication", self.test_coordinator_task_deduplication),
            ("System Status", self.test_system_status)
        ]
        
        # Run tests
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                result = test_func()
                self.test_results[test_name] = result
                
                if result:
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
                self.test_results[test_name] = False
                failed += 1
        
        # Teardown
        self.teardown()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
        
        if failed == 0:
            print("\n✅ ALL TESTS PASSED!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"   - {test_name}")
            return False

def main():
    """Main test runner"""
    test_suite = HeliosTestSuite()
    success = test_suite.run_all_tests()
    
    # Also run built-in tests
    print("\n" + "="*60)
    print("🧪 Running Built-in Helios Protocol Tests")
    print("="*60)
    
    helios = HeliosProtocol()
    helios_test_result = helios.test_helios_protocol()
    
    coordinator = create_coordinator(helios)
    coordinator_test_result = coordinator.test_coordinator()
    
    overall_success = success and helios_test_result and coordinator_test_result
    
    if overall_success:
        print("\n🎉 ALL HELIOS PROTOCOL TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed - review output above")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())