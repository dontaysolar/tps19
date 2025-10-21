#!/usr/bin/env python3
"""
AEGIS v2.0 State Integrity Protection System
Cryptographic state hashing with tamper detection and forensic analysis
"""

import os
import json
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

class AEGISStateIntegrity:
    """AEGIS-compliant state integrity protection with cryptographic verification"""
    
    def __init__(self, integrity_key_path: str = 'security/integrity.key'):
        self.integrity_key_path = integrity_key_path
        self.state_history = []
        self.tamper_detected = False
        self.logger = logging.getLogger(__name__)
        
        # Initialize integrity key
        self._initialize_integrity_key()
        
        # Load existing state history
        self._load_state_history()
    
    def _initialize_integrity_key(self):
        """Initialize or load integrity verification key"""
        if os.path.exists(self.integrity_key_path):
            with open(self.integrity_key_path, 'rb') as f:
                self.integrity_key = f.read()
        else:
            # Generate new key using PBKDF2
            password = os.urandom(32)
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.integrity_key = base64.urlsafe_b64encode(kdf.derive(password))
            
            os.makedirs(os.path.dirname(self.integrity_key_path), exist_ok=True)
            with open(self.integrity_key_path, 'wb') as f:
                f.write(self.integrity_key)
            
            # Secure the key file
            os.chmod(self.integrity_key_path, 0o600)
    
    def _load_state_history(self):
        """Load existing state history for verification"""
        history_path = 'security/state_history.json'
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.state_history = json.load(f)
                
                # Verify history integrity
                self._verify_state_history()
                
            except Exception as e:
                self.logger.error(f"Failed to load state history: {e}")
                self.state_history = []
    
    def _save_state_history(self):
        """Save state history with integrity protection"""
        os.makedirs('security', exist_ok=True)
        history_path = 'security/state_history.json'
        
        try:
            with open(history_path, 'w') as f:
                json.dump(self.state_history, f, indent=2)
            
            # Create integrity hash
            self._create_integrity_hash(history_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save state history: {e}")
    
    def _create_integrity_hash(self, file_path: str):
        """Create HMAC hash for file integrity"""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        hash_value = hmac.new(
            self.integrity_key,
            file_content,
            hashlib.sha256
        ).hexdigest()
        
        # Save hash
        hash_path = file_path + '.hash'
        with open(hash_path, 'w') as f:
            f.write(hash_value)
    
    def _verify_integrity_hash(self, file_path: str) -> bool:
        """Verify file integrity using HMAC"""
        hash_path = file_path + '.hash'
        
        if not os.path.exists(hash_path):
            return False
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            with open(hash_path, 'r') as f:
                stored_hash = f.read().strip()
            
            calculated_hash = hmac.new(
                self.integrity_key,
                file_content,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(stored_hash, calculated_hash)
            
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {e}")
            return False
    
    def create_state_snapshot(self, state_data: Dict[str, Any], 
                            component: str, operation: str) -> Dict[str, Any]:
        """Create cryptographically protected state snapshot"""
        timestamp = datetime.now().isoformat()
        
        # Serialize state data
        state_json = json.dumps(state_data, sort_keys=True, default=str)
        
        # Create state hash
        state_hash = hashlib.sha256(state_json.encode()).hexdigest()
        
        # Create HMAC signature
        signature = hmac.new(
            self.integrity_key,
            state_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Create snapshot
        snapshot = {
            'timestamp': timestamp,
            'component': component,
            'operation': operation,
            'state_hash': state_hash,
            'signature': signature,
            'data': state_data,
            'sequence_number': len(self.state_history) + 1
        }
        
        # Add to history
        self.state_history.append(snapshot)
        
        # Save history
        self._save_state_history()
        
        self.logger.info(f"Created state snapshot: {component}.{operation}")
        
        return snapshot
    
    def verify_state_integrity(self, snapshot: Dict[str, Any]) -> bool:
        """Verify state snapshot integrity"""
        try:
            # Extract data and signature
            data = snapshot['data']
            signature = snapshot['signature']
            
            # Recreate state JSON
            state_json = json.dumps(data, sort_keys=True, default=str)
            
            # Verify HMAC signature
            expected_signature = hmac.new(
                self.integrity_key,
                state_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                self.tamper_detected = True
                self.logger.critical(f"State tampering detected in snapshot: {snapshot['component']}.{snapshot['operation']}")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"State verification failed: {e}")
            return False
    
    def verify_state_history(self) -> Dict[str, Any]:
        """Verify entire state history integrity"""
        verification_results = {
            'timestamp': datetime.now().isoformat(),
            'total_snapshots': len(self.state_history),
            'valid_snapshots': 0,
            'tampered_snapshots': [],
            'integrity_score': 0,
            'tamper_detected': False
        }
        
        for i, snapshot in enumerate(self.state_history):
            if self.verify_state_integrity(snapshot):
                verification_results['valid_snapshots'] += 1
            else:
                verification_results['tampered_snapshots'].append({
                    'index': i,
                    'component': snapshot.get('component', 'unknown'),
                    'operation': snapshot.get('operation', 'unknown'),
                    'timestamp': snapshot.get('timestamp', 'unknown')
                })
                verification_results['tamper_detected'] = True
        
        # Calculate integrity score
        if verification_results['total_snapshots'] > 0:
            verification_results['integrity_score'] = (
                verification_results['valid_snapshots'] / 
                verification_results['total_snapshots'] * 100
            )
        
        return verification_results
    
    def detect_state_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in state history"""
        anomalies = []
        
        if len(self.state_history) < 2:
            return anomalies
        
        # Check for rapid state changes
        for i in range(1, len(self.state_history)):
            prev_snapshot = self.state_history[i-1]
            curr_snapshot = self.state_history[i]
            
            prev_time = datetime.fromisoformat(prev_snapshot['timestamp'])
            curr_time = datetime.fromisoformat(curr_snapshot['timestamp'])
            
            time_diff = (curr_time - prev_time).total_seconds()
            
            # Flag rapid changes (less than 1 second)
            if time_diff < 1.0:
                anomalies.append({
                    'type': 'rapid_state_change',
                    'description': f"State changed too rapidly: {time_diff:.3f}s",
                    'timestamp': curr_snapshot['timestamp'],
                    'component': curr_snapshot['component']
                })
            
            # Check for state hash collisions
            if prev_snapshot['state_hash'] == curr_snapshot['state_hash']:
                anomalies.append({
                    'type': 'state_hash_collision',
                    'description': "Identical state hashes detected",
                    'timestamp': curr_snapshot['timestamp'],
                    'component': curr_snapshot['component']
                })
        
        return anomalies
    
    def recover_from_tampering(self) -> Dict[str, Any]:
        """Attempt to recover from detected tampering"""
        recovery_results = {
            'timestamp': datetime.now().isoformat(),
            'recovery_attempted': False,
            'recovery_successful': False,
            'actions_taken': [],
            'backup_restored': False
        }
        
        if not self.tamper_detected:
            return recovery_results
        
        try:
            # Find last valid snapshot
            last_valid_index = -1
            for i, snapshot in enumerate(self.state_history):
                if self.verify_state_integrity(snapshot):
                    last_valid_index = i
            
            if last_valid_index >= 0:
                # Restore from last valid state
                valid_snapshot = self.state_history[last_valid_index]
                
                # Remove tampered snapshots
                self.state_history = self.state_history[:last_valid_index + 1]
                
                recovery_results['recovery_attempted'] = True
                recovery_results['recovery_successful'] = True
                recovery_results['actions_taken'].append(f"Restored to snapshot {last_valid_index}")
                recovery_results['backup_restored'] = True
                
                # Save cleaned history
                self._save_state_history()
                
                self.logger.info(f"Recovered from tampering, restored to snapshot {last_valid_index}")
            
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            recovery_results['actions_taken'].append(f"Recovery failed: {str(e)}")
        
        return recovery_results
    
    def get_state_forensics(self) -> Dict[str, Any]:
        """Generate forensic analysis of state history"""
        forensics = {
            'timestamp': datetime.now().isoformat(),
            'total_snapshots': len(self.state_history),
            'time_span': None,
            'component_activity': {},
            'operation_frequency': {},
            'integrity_verification': self.verify_state_history(),
            'anomalies': self.detect_state_anomalies()
        }
        
        if self.state_history:
            # Calculate time span
            first_timestamp = datetime.fromisoformat(self.state_history[0]['timestamp'])
            last_timestamp = datetime.fromisoformat(self.state_history[-1]['timestamp'])
            forensics['time_span'] = str(last_timestamp - first_timestamp)
            
            # Analyze component activity
            for snapshot in self.state_history:
                component = snapshot.get('component', 'unknown')
                operation = snapshot.get('operation', 'unknown')
                
                if component not in forensics['component_activity']:
                    forensics['component_activity'][component] = 0
                forensics['component_activity'][component] += 1
                
                if operation not in forensics['operation_frequency']:
                    forensics['operation_frequency'][operation] = 0
                forensics['operation_frequency'][operation] += 1
        
        return forensics

# AEGIS Recursion Clause Implementation
class AEGISStateAuditor:
    """Autonomous state auditing and integrity monitoring"""
    
    def __init__(self, state_integrity: AEGISStateIntegrity):
        self.state_integrity = state_integrity
        self.logger = logging.getLogger(__name__)
        self.audit_schedule = {}
    
    def schedule_integrity_audit(self, component: str, interval_minutes: int = 60):
        """Schedule regular integrity audits for components"""
        self.audit_schedule[component] = {
            'interval_minutes': interval_minutes,
            'last_audit': None,
            'next_audit': datetime.now() + timedelta(minutes=interval_minutes)
        }
    
    def run_scheduled_audits(self) -> Dict[str, Any]:
        """Run all scheduled integrity audits"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'audits_run': 0,
            'issues_found': 0,
            'components_audited': []
        }
        
        now = datetime.now()
        
        for component, schedule in self.audit_schedule.items():
            if schedule['next_audit'] <= now:
                # Run audit
                verification = self.state_integrity.verify_state_history()
                
                audit_results['audits_run'] += 1
                audit_results['components_audited'].append(component)
                
                if verification['tamper_detected']:
                    audit_results['issues_found'] += 1
                    self.logger.warning(f"Integrity issues found in {component}")
                
                # Update schedule
                schedule['last_audit'] = now
                schedule['next_audit'] = now + timedelta(minutes=schedule['interval_minutes'])
        
        return audit_results

if __name__ == '__main__':
    # Initialize state integrity system
    state_integrity = AEGISStateIntegrity()
    
    # Create test state snapshot
    test_state = {
        'trading_enabled': True,
        'positions': {'BTC/USDT': {'amount': 0.001, 'price': 26500}},
        'balance': 1000.0
    }
    
    snapshot = state_integrity.create_state_snapshot(
        test_state, 'trading_engine', 'position_update'
    )
    
    print(f"Created snapshot: {snapshot['sequence_number']}")
    
    # Verify integrity
    is_valid = state_integrity.verify_state_integrity(snapshot)
    print(f"Snapshot integrity: {is_valid}")
    
    # Run verification
    verification = state_integrity.verify_state_history()
    print(f"History verification: {verification}")
    
    # Generate forensics
    forensics = state_integrity.get_state_forensics()
    print(f"Forensic analysis: {json.dumps(forensics, indent=2)}")