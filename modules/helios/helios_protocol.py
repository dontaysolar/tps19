#!/usr/bin/env python3
"""Helios Protocol - Automated Rollback and Postmortem System

This module implements the Helios Protocol with the following features:
- Monitors for NO-GO decisions from any phase
- Automatically triggers rollback to last known stable version
- Creates Severity-1 postmortem tasks
- Enforces postmortem completion before new deployments
"""

import os
import json
import sqlite3
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import hashlib
import uuid

class HeliosPhase(Enum):
    """Helios Protocol Phases"""
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post_deployment"
    VERIFICATION = "verification"
    MONITORING = "monitoring"

class DecisionStatus(Enum):
    """Decision Status Types"""
    GO = "GO"
    NO_GO = "NO-GO"
    PENDING = "PENDING"

class PostmortemSeverity(Enum):
    """Postmortem Severity Levels"""
    SEVERITY_1 = 1  # Critical - Must be resolved before new deployments
    SEVERITY_2 = 2  # High - Should be resolved soon
    SEVERITY_3 = 3  # Medium - Can be scheduled
    SEVERITY_4 = 4  # Low - Informational

class HeliosProtocol:
    """Main Helios Protocol Implementation"""
    
    def __init__(self, db_path='/opt/tps19/data/helios_protocol.db'):
        self.db_path = db_path
        self.rollback_lock = threading.Lock()
        self.postmortem_lock = threading.Lock()
        self.monitoring_active = False
        self.current_deployment_id = None
        self.patch_manager_path = '/opt/tps19/modules/patching/patch_manager.py'
        
        # Initialize database
        self._init_database()
        
        # Start monitoring thread
        self.monitoring_thread = None
        
    def _init_database(self):
        """Initialize Helios Protocol database"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Deployments table
            cursor.execute("""CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT UNIQUE NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                stable_version_id TEXT,
                rollback_version_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                deployed_at DATETIME,
                rolled_back_at DATETIME
            )""")
            
            # Phase decisions table
            cursor.execute("""CREATE TABLE IF NOT EXISTS phase_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
            )""")
            
            # Postmortems table
            cursor.execute("""CREATE TABLE IF NOT EXISTS postmortems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                postmortem_id TEXT UNIQUE NOT NULL,
                deployment_id TEXT NOT NULL,
                severity INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                root_cause TEXT,
                corrective_actions TEXT,
                status TEXT DEFAULT 'open',
                assigned_to TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
            )""")
            
            # Rollback history table
            cursor.execute("""CREATE TABLE IF NOT EXISTS rollback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rollback_id TEXT UNIQUE NOT NULL,
                deployment_id TEXT NOT NULL,
                trigger_phase TEXT NOT NULL,
                trigger_reason TEXT NOT NULL,
                from_version TEXT NOT NULL,
                to_version TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                rollback_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deployment_id) REFERENCES deployments(deployment_id)
            )""")
            
            # Stable versions table
            cursor.execute("""CREATE TABLE IF NOT EXISTS stable_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT UNIQUE NOT NULL,
                version_number TEXT NOT NULL,
                deployment_id TEXT,
                stability_score REAL DEFAULT 1.0,
                metadata TEXT,
                is_current BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_verified DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            
            conn.commit()
            conn.close()
            print("✅ Helios Protocol database initialized")
            
        except Exception as e:
            print(f"❌ Helios Protocol database initialization failed: {e}")
            raise
    
    def register_deployment(self, deployment_id: str, version: str, description: str = "") -> bool:
        """Register a new deployment with Helios Protocol"""
        try:
            # Get current stable version
            stable_version = self.get_current_stable_version()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO deployments 
                (deployment_id, version, description, stable_version_id, status)
                VALUES (?, ?, ?, ?, 'pending')""",
                (deployment_id, version, description, stable_version))
            
            conn.commit()
            conn.close()
            
            self.current_deployment_id = deployment_id
            print(f"✅ Deployment {deployment_id} registered with Helios Protocol")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register deployment: {e}")
            return False
    
    def record_phase_decision(self, phase: HeliosPhase, decision: DecisionStatus, 
                            reason: str = "", metadata: Dict[str, Any] = None) -> bool:
        """Record a phase decision"""
        try:
            if not self.current_deployment_id:
                print("❌ No active deployment to record decision for")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO phase_decisions 
                (deployment_id, phase, decision, reason, metadata)
                VALUES (?, ?, ?, ?, ?)""",
                (self.current_deployment_id, phase.value, decision.value, 
                 reason, json.dumps(metadata or {})))
            
            conn.commit()
            conn.close()
            
            print(f"📝 Phase decision recorded: {phase.value} - {decision.value}")
            
            # Check if NO-GO decision
            if decision == DecisionStatus.NO_GO:
                self._handle_no_go_decision(phase, reason)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to record phase decision: {e}")
            return False
    
    def _handle_no_go_decision(self, phase: HeliosPhase, reason: str):
        """Handle NO-GO decision - trigger automatic rollback"""
        print(f"🚨 NO-GO decision detected in {phase.value} phase!")
        print(f"📋 Reason: {reason}")
        
        # Execute automatic rollback in a separate thread
        rollback_thread = threading.Thread(
            target=self._execute_automatic_rollback,
            args=(phase, reason)
        )
        rollback_thread.daemon = True
        rollback_thread.start()
    
    def _execute_automatic_rollback(self, phase: HeliosPhase, reason: str):
        """Execute automatic rollback to last known stable version"""
        with self.rollback_lock:
            try:
                print("🔄 Initiating automatic rollback...")
                
                # Get stable version to rollback to
                stable_version = self.get_current_stable_version()
                if not stable_version:
                    print("❌ No stable version found for rollback!")
                    return
                
                # Create rollback ID
                rollback_id = f"rollback_{self.current_deployment_id}_{int(time.time())}"
                
                # Get deployment info
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM deployments WHERE deployment_id = ?", 
                             (self.current_deployment_id,))
                current_version = cursor.fetchone()[0]
                conn.close()
                
                # Execute rollback using patch manager
                rollback_success = self._perform_rollback(stable_version)
                
                # Record rollback
                self._record_rollback(rollback_id, phase, reason, current_version, 
                                    stable_version, rollback_success)
                
                if rollback_success:
                    print(f"✅ Automatic rollback completed successfully to version {stable_version}")
                    
                    # Create mandatory postmortem
                    self._create_postmortem(phase, reason)
                    
                    # Update deployment status
                    self._update_deployment_status("rolled_back")
                else:
                    print("❌ Automatic rollback failed!")
                    
            except Exception as e:
                print(f"❌ Rollback execution error: {e}")
    
    def _perform_rollback(self, target_version: str) -> bool:
        """Perform actual rollback using patch manager"""
        try:
            # Import patch manager dynamically
            import sys
            sys.path.insert(0, '/opt/tps19/modules')
            from patching.patch_manager import patch_manager
            
            # Execute rollback to backup
            return patch_manager.rollback_to_backup(target_version)
            
        except Exception as e:
            print(f"❌ Rollback execution failed: {e}")
            return False
    
    def _record_rollback(self, rollback_id: str, phase: HeliosPhase, reason: str,
                        from_version: str, to_version: str, success: bool):
        """Record rollback in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO rollback_history 
                (rollback_id, deployment_id, trigger_phase, trigger_reason, 
                 from_version, to_version, success, rollback_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (rollback_id, self.current_deployment_id, phase.value, reason,
                 from_version, to_version, success, json.dumps({
                     'timestamp': datetime.now().isoformat(),
                     'automatic': True
                 })))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Failed to record rollback: {e}")
    
    def _create_postmortem(self, phase: HeliosPhase, reason: str):
        """Create mandatory Severity-1 postmortem task"""
        with self.postmortem_lock:
            try:
                postmortem_id = f"PM-{self.current_deployment_id}-{uuid.uuid4().hex[:8]}"
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""INSERT INTO postmortems 
                    (postmortem_id, deployment_id, severity, title, description, status)
                    VALUES (?, ?, ?, ?, ?, 'open')""",
                    (postmortem_id, self.current_deployment_id, PostmortemSeverity.SEVERITY_1.value,
                     f"Automatic Rollback - {phase.value} NO-GO Decision",
                     f"Deployment {self.current_deployment_id} was automatically rolled back due to a NO-GO decision in {phase.value} phase. Reason: {reason}"))
                
                conn.commit()
                conn.close()
                
                print(f"🚨 SEVERITY-1 POSTMORTEM CREATED: {postmortem_id}")
                print("⚠️  New deployments are BLOCKED until this postmortem is completed!")
                
            except Exception as e:
                print(f"❌ Failed to create postmortem: {e}")
    
    def can_deploy(self) -> Tuple[bool, str]:
        """Check if new deployments are allowed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for open Severity-1 postmortems
            cursor.execute("""SELECT COUNT(*), GROUP_CONCAT(postmortem_id) 
                FROM postmortems 
                WHERE severity = ? AND status = 'open'""",
                (PostmortemSeverity.SEVERITY_1.value,))
            
            count, postmortem_ids = cursor.fetchone()
            conn.close()
            
            if count > 0:
                return False, f"Deployment blocked: {count} open Severity-1 postmortem(s): {postmortem_ids}"
            
            return True, "Deployments allowed"
            
        except Exception as e:
            return False, f"Error checking deployment status: {e}"
    
    def complete_postmortem(self, postmortem_id: str, root_cause: str, 
                          corrective_actions: List[str]) -> bool:
        """Complete a postmortem with root cause analysis"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""UPDATE postmortems 
                SET root_cause = ?, corrective_actions = ?, status = 'completed', 
                    completed_at = CURRENT_TIMESTAMP
                WHERE postmortem_id = ?""",
                (root_cause, json.dumps(corrective_actions), postmortem_id))
            
            if cursor.rowcount == 0:
                conn.close()
                print(f"❌ Postmortem {postmortem_id} not found")
                return False
            
            conn.commit()
            conn.close()
            
            print(f"✅ Postmortem {postmortem_id} completed")
            
            # Check if deployments are now allowed
            can_deploy, message = self.can_deploy()
            if can_deploy:
                print("✅ All Severity-1 postmortems resolved - deployments are now allowed")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to complete postmortem: {e}")
            return False
    
    def get_current_stable_version(self) -> Optional[str]:
        """Get the current stable version ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""SELECT version_id FROM stable_versions 
                WHERE is_current = 1 ORDER BY created_at DESC LIMIT 1""")
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"❌ Failed to get stable version: {e}")
            return None
    
    def mark_version_stable(self, version_id: str, deployment_id: str = None) -> bool:
        """Mark a version as stable"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Unmark current stable version
            cursor.execute("UPDATE stable_versions SET is_current = 0")
            
            # Check if version exists
            cursor.execute("SELECT id FROM stable_versions WHERE version_id = ?", (version_id,))
            if cursor.fetchone():
                # Update existing
                cursor.execute("""UPDATE stable_versions 
                    SET is_current = 1, deployment_id = ?, last_verified = CURRENT_TIMESTAMP
                    WHERE version_id = ?""",
                    (deployment_id, version_id))
            else:
                # Insert new
                cursor.execute("""INSERT INTO stable_versions 
                    (version_id, version_number, deployment_id, is_current)
                    VALUES (?, ?, ?, 1)""",
                    (version_id, version_id, deployment_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Version {version_id} marked as stable")
            return True
            
        except Exception as e:
            print(f"❌ Failed to mark version stable: {e}")
            return False
    
    def _update_deployment_status(self, status: str):
        """Update deployment status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            update_field = "deployed_at" if status == "deployed" else "rolled_back_at"
            cursor.execute(f"""UPDATE deployments 
                SET status = ?, {update_field} = CURRENT_TIMESTAMP
                WHERE deployment_id = ?""",
                (status, self.current_deployment_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Failed to update deployment status: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get Helios Protocol status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total deployments
            cursor.execute("SELECT COUNT(*) FROM deployments")
            total_deployments = cursor.fetchone()[0]
            
            # Rolled back deployments
            cursor.execute("SELECT COUNT(*) FROM deployments WHERE status = 'rolled_back'")
            rolled_back = cursor.fetchone()[0]
            
            # Open postmortems by severity
            cursor.execute("""SELECT severity, COUNT(*) FROM postmortems 
                WHERE status = 'open' GROUP BY severity""")
            open_postmortems = dict(cursor.fetchall())
            
            # Recent rollbacks
            cursor.execute("""SELECT COUNT(*) FROM rollback_history 
                WHERE created_at > datetime('now', '-7 days')""")
            recent_rollbacks = cursor.fetchone()[0]
            
            # Current stable version
            stable_version = self.get_current_stable_version()
            
            # Can deploy status
            can_deploy, deploy_message = self.can_deploy()
            
            conn.close()
            
            return {
                'total_deployments': total_deployments,
                'rolled_back_deployments': rolled_back,
                'open_postmortems': open_postmortems,
                'recent_rollbacks_7d': recent_rollbacks,
                'current_stable_version': stable_version,
                'can_deploy': can_deploy,
                'deploy_status_message': deploy_message,
                'monitoring_active': self.monitoring_active
            }
            
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
            return {}
    
    def start_monitoring(self):
        """Start Helios Protocol monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            print("✅ Helios Protocol monitoring started")
    
    def stop_monitoring(self):
        """Stop Helios Protocol monitoring"""
        self.monitoring_active = False
        print("🛑 Helios Protocol monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Monitor for system health
                # This would integrate with actual system monitoring
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
    
    def test_helios_protocol(self) -> bool:
        """Test the Helios Protocol system"""
        try:
            print("🧪 Testing Helios Protocol...")
            print("="*60)
            
            # Test 1: Register deployment
            print("1️⃣ Testing deployment registration...")
            test_deployment_id = f"test_deploy_{int(time.time())}"
            if not self.register_deployment(test_deployment_id, "1.0.0", "Test deployment"):
                return False
            
            # Test 2: Record GO decisions
            print("2️⃣ Testing GO decisions...")
            self.record_phase_decision(HeliosPhase.PRE_DEPLOYMENT, DecisionStatus.GO, "All checks passed")
            self.record_phase_decision(HeliosPhase.DEPLOYMENT, DecisionStatus.GO, "Deployment successful")
            
            # Test 3: Check deployment allowed
            print("3️⃣ Testing deployment checks...")
            can_deploy, message = self.can_deploy()
            print(f"   Can deploy: {can_deploy} - {message}")
            
            # Test 4: Simulate NO-GO decision
            print("4️⃣ Testing NO-GO decision and automatic rollback...")
            self.record_phase_decision(HeliosPhase.VERIFICATION, DecisionStatus.NO_GO, 
                                     "Critical error detected in verification")
            
            # Wait for rollback to complete
            time.sleep(2)
            
            # Test 5: Check deployment blocked
            print("5️⃣ Testing deployment blocking...")
            can_deploy, message = self.can_deploy()
            if can_deploy:
                print("❌ Deployments should be blocked after NO-GO!")
                return False
            print(f"   ✅ Deployments correctly blocked: {message}")
            
            # Test 6: Get status
            print("6️⃣ Testing status retrieval...")
            status = self.get_status()
            print(f"   Status: {json.dumps(status, indent=2)}")
            
            print("\n✅ Helios Protocol test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Helios Protocol test failed: {e}")
            return False

# Global Helios Protocol instance
helios_protocol = HeliosProtocol()