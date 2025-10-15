#!/usr/bin/env python3
"""Helios Protocol Coordinator - Ensures agents work in unison without duplication"""

import threading
import time
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid

class HeliosCoordinator:
    """Coordinator to ensure multiple agents work in unison without duplication"""
    
    def __init__(self, helios_protocol):
        self.helios = helios_protocol
        self.active_agents: Set[str] = set()
        self.agent_lock = threading.Lock()
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id
        self.task_lock = threading.Lock()
        self.coordination_log = []
        
    def register_agent(self, agent_id: str) -> bool:
        """Register an agent with the coordinator"""
        with self.agent_lock:
            if agent_id in self.active_agents:
                print(f"⚠️  Agent {agent_id} already registered")
                return False
            
            self.active_agents.add(agent_id)
            self._log_coordination(f"Agent {agent_id} registered", agent_id)
            print(f"✅ Agent {agent_id} registered with Helios Coordinator")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the coordinator"""
        with self.agent_lock:
            if agent_id not in self.active_agents:
                return False
            
            self.active_agents.remove(agent_id)
            
            # Release any tasks assigned to this agent
            with self.task_lock:
                tasks_to_release = [task_id for task_id, assigned_agent 
                                  in self.task_assignments.items() 
                                  if assigned_agent == agent_id]
                for task_id in tasks_to_release:
                    del self.task_assignments[task_id]
                    self._log_coordination(f"Task {task_id} released", agent_id)
            
            self._log_coordination(f"Agent {agent_id} unregistered", agent_id)
            return True
    
    def request_deployment_action(self, agent_id: str, deployment_id: str, 
                                action: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Request to perform a deployment action - ensures no duplication"""
        task_id = f"{action}_{deployment_id}"
        
        with self.task_lock:
            # Check if task is already assigned
            if task_id in self.task_assignments:
                assigned_agent = self.task_assignments[task_id]
                if assigned_agent != agent_id:
                    return {
                        'allowed': False,
                        'reason': f'Task already assigned to agent {assigned_agent}',
                        'task_id': task_id
                    }
            
            # Assign task to requesting agent
            self.task_assignments[task_id] = agent_id
            self._log_coordination(f"Task {task_id} assigned to {agent_id}", agent_id)
            
            return {
                'allowed': True,
                'task_id': task_id,
                'proceed': True
            }
    
    def complete_task(self, agent_id: str, task_id: str, success: bool, 
                     result: Dict[str, Any] = None) -> bool:
        """Mark a task as completed"""
        with self.task_lock:
            if task_id not in self.task_assignments:
                return False
            
            if self.task_assignments[task_id] != agent_id:
                print(f"⚠️  Agent {agent_id} cannot complete task {task_id} - not assigned")
                return False
            
            del self.task_assignments[task_id]
            self._log_coordination(
                f"Task {task_id} completed - Success: {success}", 
                agent_id, 
                {'result': result}
            )
            return True
    
    def coordinate_rollback(self, agent_id: str, deployment_id: str, 
                          phase: str, reason: str) -> Dict[str, Any]:
        """Coordinate rollback across agents"""
        rollback_task_id = f"rollback_{deployment_id}_{int(time.time())}"
        
        with self.task_lock:
            # Check if any rollback is already in progress for this deployment
            active_rollbacks = [task for task in self.task_assignments.keys() 
                              if task.startswith(f"rollback_{deployment_id}")]
            
            if active_rollbacks:
                return {
                    'allowed': False,
                    'reason': 'Rollback already in progress',
                    'active_rollback': active_rollbacks[0]
                }
            
            # Assign rollback task
            self.task_assignments[rollback_task_id] = agent_id
            
            # Notify all agents about rollback
            self._broadcast_rollback_notification(deployment_id, phase, reason, agent_id)
            
            return {
                'allowed': True,
                'task_id': rollback_task_id,
                'coordinator_message': 'Rollback coordinated - all agents notified'
            }
    
    def coordinate_postmortem(self, agent_id: str, postmortem_id: str, 
                            action: str) -> Dict[str, Any]:
        """Coordinate postmortem actions across agents"""
        pm_task_id = f"postmortem_{action}_{postmortem_id}"
        
        with self.task_lock:
            # Check if task already assigned
            if pm_task_id in self.task_assignments:
                assigned_agent = self.task_assignments[pm_task_id]
                if assigned_agent != agent_id:
                    return {
                        'allowed': False,
                        'reason': f'Postmortem task already assigned to {assigned_agent}'
                    }
            
            self.task_assignments[pm_task_id] = agent_id
            return {
                'allowed': True,
                'task_id': pm_task_id
            }
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        with self.agent_lock:
            if agent_id not in self.active_agents:
                return {'registered': False}
            
            with self.task_lock:
                assigned_tasks = [task for task, agent in self.task_assignments.items() 
                                if agent == agent_id]
            
            return {
                'registered': True,
                'active_tasks': assigned_tasks,
                'task_count': len(assigned_tasks)
            }
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get overall coordination status"""
        with self.agent_lock:
            active_agents = list(self.active_agents)
        
        with self.task_lock:
            active_tasks = dict(self.task_assignments)
        
        return {
            'active_agents': active_agents,
            'agent_count': len(active_agents),
            'active_tasks': active_tasks,
            'task_count': len(active_tasks),
            'recent_logs': self.coordination_log[-10:]  # Last 10 entries
        }
    
    def _broadcast_rollback_notification(self, deployment_id: str, phase: str, 
                                       reason: str, initiating_agent: str):
        """Broadcast rollback notification to all agents"""
        notification = {
            'type': 'ROLLBACK_INITIATED',
            'deployment_id': deployment_id,
            'phase': phase,
            'reason': reason,
            'initiated_by': initiating_agent,
            'timestamp': datetime.now().isoformat()
        }
        
        # In a real system, this would send notifications via message queue
        # For now, we log it
        self._log_coordination(
            f"Rollback notification broadcast for {deployment_id}", 
            initiating_agent,
            notification
        )
    
    def _log_coordination(self, message: str, agent_id: str, 
                         metadata: Dict[str, Any] = None):
        """Log coordination activities"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'agent_id': agent_id,
            'metadata': metadata or {}
        }
        
        self.coordination_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.coordination_log) > 1000:
            self.coordination_log = self.coordination_log[-1000:]
    
    def ensure_no_duplicate_operations(self, operation_type: str, 
                                     operation_id: str, agent_id: str) -> bool:
        """Generic method to ensure no duplicate operations"""
        operation_key = f"{operation_type}_{operation_id}"
        
        with self.task_lock:
            if operation_key in self.task_assignments:
                assigned_agent = self.task_assignments[operation_key]
                if assigned_agent != agent_id:
                    print(f"⚠️  Operation {operation_key} already assigned to {assigned_agent}")
                    return False
                return True  # Same agent, allow continuation
            
            # Assign operation to agent
            self.task_assignments[operation_key] = agent_id
            return True
    
    def test_coordinator(self) -> bool:
        """Test the coordinator functionality"""
        try:
            print("🧪 Testing Helios Coordinator...")
            
            # Test 1: Agent registration
            print("1️⃣ Testing agent registration...")
            agent1 = f"test_agent_1_{uuid.uuid4().hex[:8]}"
            agent2 = f"test_agent_2_{uuid.uuid4().hex[:8]}"
            
            self.register_agent(agent1)
            self.register_agent(agent2)
            
            # Test 2: Task assignment
            print("2️⃣ Testing task assignment...")
            deployment_id = f"test_deploy_{int(time.time())}"
            
            # Agent 1 requests deployment
            result1 = self.request_deployment_action(agent1, deployment_id, "deploy")
            if not result1['allowed']:
                print("❌ Agent 1 should be allowed to deploy")
                return False
            
            # Agent 2 tries same deployment
            result2 = self.request_deployment_action(agent2, deployment_id, "deploy")
            if result2['allowed']:
                print("❌ Agent 2 should NOT be allowed duplicate deployment")
                return False
            
            print("   ✅ Duplicate prevention working correctly")
            
            # Test 3: Task completion
            print("3️⃣ Testing task completion...")
            self.complete_task(agent1, result1['task_id'], True)
            
            # Now agent 2 should be able to request
            result3 = self.request_deployment_action(agent2, deployment_id, "verify")
            if not result3['allowed']:
                print("❌ Agent 2 should be allowed different action")
                return False
            
            # Test 4: Coordination status
            print("4️⃣ Testing coordination status...")
            status = self.get_coordination_status()
            print(f"   Active agents: {status['agent_count']}")
            print(f"   Active tasks: {status['task_count']}")
            
            # Cleanup
            self.unregister_agent(agent1)
            self.unregister_agent(agent2)
            
            print("✅ Helios Coordinator test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Coordinator test failed: {e}")
            return False

# Create global coordinator instance
def create_coordinator(helios_protocol):
    """Create a coordinator instance"""
    return HeliosCoordinator(helios_protocol)