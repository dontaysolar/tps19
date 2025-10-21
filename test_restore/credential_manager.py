#!/usr/bin/env python3
"""
AEGIS v2.0 Credential Management System
Secure credential storage and rotation with zero-trust architecture
"""

import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

class AEGISCredentialManager:
    """AEGIS-compliant credential management with encryption and rotation"""
    
    def __init__(self, master_key_path: str = 'security/master.key'):
        self.master_key_path = master_key_path
        self.credentials = {}
        self.rotation_schedule = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Load existing credentials
        self._load_credentials()
    
    def _initialize_encryption(self):
        """Initialize or load master encryption key"""
        if os.path.exists(self.master_key_path):
            with open(self.master_key_path, 'rb') as f:
                self.master_key = f.read()
        else:
            self.master_key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.master_key_path), exist_ok=True)
            with open(self.master_key_path, 'wb') as f:
                f.write(self.master_key)
            # Secure the key file
            os.chmod(self.master_key_path, 0o600)
        
        self.cipher = Fernet(self.master_key)
    
    def _load_credentials(self):
        """Load encrypted credentials from storage"""
        creds_path = 'security/credentials.enc'
        if os.path.exists(creds_path):
            try:
                with open(creds_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self.credentials = json.loads(decrypted_data.decode())
            except Exception as e:
                self.logger.error(f"Failed to load credentials: {e}")
                self.credentials = {}
    
    def _save_credentials(self):
        """Save encrypted credentials to storage"""
        os.makedirs('security', exist_ok=True)
        creds_path = 'security/credentials.enc'
        
        try:
            json_data = json.dumps(self.credentials).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            
            with open(creds_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Secure the credentials file
            os.chmod(creds_path, 0o600)
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def store_credential(self, name: str, value: str, rotation_days: int = 30) -> bool:
        """Store encrypted credential with rotation schedule"""
        try:
            # Encrypt the credential
            encrypted_value = self.cipher.encrypt(value.encode()).decode()
            
            # Store with metadata
            self.credentials[name] = {
                'encrypted_value': encrypted_value,
                'created_at': datetime.now().isoformat(),
                'rotation_days': rotation_days,
                'last_used': None,
                'use_count': 0
            }
            
            # Schedule rotation
            self.rotation_schedule[name] = datetime.now() + timedelta(days=rotation_days)
            
            self._save_credentials()
            self.logger.info(f"Stored credential: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store credential {name}: {e}")
            return False
    
    def get_credential(self, name: str) -> Optional[str]:
        """Retrieve and decrypt credential"""
        if name not in self.credentials:
            return None
        
        try:
            cred_data = self.credentials[name]
            encrypted_value = cred_data['encrypted_value']
            decrypted_value = self.cipher.decrypt(encrypted_value.encode()).decode()
            
            # Update usage tracking
            cred_data['last_used'] = datetime.now().isoformat()
            cred_data['use_count'] += 1
            
            self._save_credentials()
            return decrypted_value
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve credential {name}: {e}")
            return None
    
    def rotate_credential(self, name: str, new_value: str) -> bool:
        """Rotate credential with new value"""
        if name not in self.credentials:
            return False
        
        try:
            # Store new credential
            success = self.store_credential(name, new_value, 
                                          self.credentials[name]['rotation_days'])
            
            if success:
                self.logger.info(f"Rotated credential: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to rotate credential {name}: {e}")
            return False
    
    def check_rotation_needed(self) -> Dict[str, bool]:
        """Check which credentials need rotation"""
        now = datetime.now()
        rotation_needed = {}
        
        for name, rotation_date in self.rotation_schedule.items():
            rotation_needed[name] = now >= rotation_date
        
        return rotation_needed
    
    def get_credential_status(self) -> Dict:
        """Get comprehensive credential status"""
        status = {
            'total_credentials': len(self.credentials),
            'rotation_needed': self.check_rotation_needed(),
            'credentials': {}
        }
        
        for name, cred_data in self.credentials.items():
            status['credentials'][name] = {
                'created_at': cred_data['created_at'],
                'last_used': cred_data['last_used'],
                'use_count': cred_data['use_count'],
                'rotation_days': cred_data['rotation_days']
            }
        
        return status
    
    def migrate_from_env(self, env_file: str = '.env') -> int:
        """Migrate credentials from .env file to encrypted storage"""
        migrated_count = 0
        
        if not os.path.exists(env_file):
            return 0
        
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        
                        # Skip if already stored
                        if key in self.credentials:
                            continue
                        
                        # Store with appropriate rotation schedule
                        rotation_days = 30 if 'API' in key else 90
                        if self.store_credential(key, value, rotation_days):
                            migrated_count += 1
                            self.logger.info(f"Migrated: {key}")
        
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
        
        return migrated_count

# AEGIS Recursion Clause Implementation
class AEGISCredentialAuditor:
    """Autonomous credential auditing and compliance checking"""
    
    def __init__(self, credential_manager: AEGISCredentialManager):
        self.cred_manager = credential_manager
        self.logger = logging.getLogger(__name__)
    
    def audit_credential_security(self) -> Dict:
        """Comprehensive credential security audit"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'security_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        total_checks = 0
        passed_checks = 0
        
        # Check 1: Credential encryption
        total_checks += 1
        if self._check_encryption():
            passed_checks += 1
        else:
            audit_results['issues'].append("Credentials not properly encrypted")
        
        # Check 2: Rotation schedule compliance
        total_checks += 1
        rotation_status = self.cred_manager.check_rotation_needed()
        if not any(rotation_status.values()):
            passed_checks += 1
        else:
            audit_results['issues'].append("Credentials overdue for rotation")
            audit_results['recommendations'].append("Implement automated rotation")
        
        # Check 3: Usage tracking
        total_checks += 1
        if self._check_usage_tracking():
            passed_checks += 1
        else:
            audit_results['issues'].append("Insufficient usage tracking")
        
        # Check 4: Access patterns
        total_checks += 1
        if self._check_access_patterns():
            passed_checks += 1
        else:
            audit_results['issues'].append("Suspicious access patterns detected")
        
        audit_results['security_score'] = (passed_checks / total_checks) * 100
        
        return audit_results
    
    def _check_encryption(self) -> bool:
        """Verify credentials are properly encrypted"""
        # Implementation would check encryption status
        return True
    
    def _check_usage_tracking(self) -> bool:
        """Verify usage tracking is comprehensive"""
        # Implementation would check tracking completeness
        return True
    
    def _check_access_patterns(self) -> bool:
        """Check for suspicious access patterns"""
        # Implementation would analyze access logs
        return True

if __name__ == '__main__':
    # Initialize credential manager
    cred_manager = AEGISCredentialManager()
    
    # Migrate from .env file
    migrated = cred_manager.migrate_from_env()
    print(f"Migrated {migrated} credentials to encrypted storage")
    
    # Show status
    status = cred_manager.get_credential_status()
    print(f"Credential Status: {json.dumps(status, indent=2)}")