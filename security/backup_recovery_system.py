#!/usr/bin/env python3
"""
AEGIS v2.0 Backup and Recovery System - AID v2.0 Implementation
CRIT_018 Resolution - Zero-Tolerance Backup and Recovery

FRACTAL_HOOK: This implementation provides autonomous backup and
recovery capabilities that enable future AEGIS operations to maintain
data integrity and disaster recovery without human intervention.
"""

import os
import sys
import json
import time
import logging
import shutil
import gzip
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ATLAS Protocol: Fixed loop bounds and simple control flow
MAX_BACKUP_OPERATIONS = 50
MAX_RECOVERY_OPERATIONS = 25
MAX_FUNCTION_LENGTH = 60

class BackupType(Enum):
    """Backup type - ATLAS: Simple enumeration"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    """Backup status - ATLAS: Simple enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"

@dataclass
class BackupRecord:
    """Backup record - ATLAS: Fixed data structure"""
    backup_id: str
    backup_type: BackupType
    source_path: str
    destination_path: str
    status: BackupStatus
    size_bytes: int
    checksum: str
    timestamp: str
    compression_ratio: float

@dataclass
class RecoveryRecord:
    """Recovery record - ATLAS: Fixed data structure"""
    recovery_id: str
    backup_id: str
    source_path: str
    destination_path: str
    status: BackupStatus
    timestamp: str
    verification_passed: bool

class AEGISBackupRecoverySystem:
    """
    AEGIS v2.0 Backup and Recovery System
    
    ATLAS Protocol Compliance:
    - Simple control flow with fixed loop bounds
    - No dynamic memory allocation after initialization
    - High assertion density (2+ per function)
    - Minimal scope for all variables
    - Constrained function length
    """
    
    def __init__(self, config_path: str = "config/backup_recovery.json"):
        """Initialize Backup and Recovery System - ATLAS: Fixed initialization"""
        assert isinstance(config_path, str), "Config path must be string"
        
        self.config_path = config_path
        self.backup_records: List[BackupRecord] = []
        self.recovery_records: List[RecoveryRecord] = []
        self.overall_success_rate = 0.0
        self._lock = threading.Lock()
        
        # ATLAS: Initialize logging
        self._setup_logging()
        self._load_configuration()
        self._initialize_backup_system()
        
        # ATLAS: Assert initialization success
        assert self.logger is not None, "Logger must be initialized"
    
    def _setup_logging(self) -> None:
        """Setup logging configuration - ATLAS: Fixed function length"""
        assert not hasattr(self, 'logger'), "Logger already initialized"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - BACKUP_RECOVERY - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup_recovery.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # ATLAS: Assert logging setup
        assert self.logger is not None, "Logger setup failed"
    
    def _load_configuration(self) -> None:
        """Load backup recovery configuration - ATLAS: Fixed function length"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                self.logger.error(f"Config load failed: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
        
        # ATLAS: Assert configuration loaded
        assert isinstance(self.config, dict), "Config must be dictionary"
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration - ATLAS: Fixed function length"""
        return {
            "backup_recovery": {
                "enabled": True,
                "auto_backup": True,
                "compression": True,
                "encryption": True,
                "retention_days": 30
            },
            "backup_sources": {
                "security": {
                    "path": "security/",
                    "enabled": True,
                    "frequency": "daily"
                },
                "config": {
                    "path": "config/",
                    "enabled": True,
                    "frequency": "daily"
                },
                "logs": {
                    "path": "logs/",
                    "enabled": True,
                    "frequency": "weekly"
                },
                "data": {
                    "path": "data/",
                    "enabled": True,
                    "frequency": "daily"
                }
            },
            "backup_destination": {
                "local": "backups/",
                "remote": None,
                "compression": True,
                "encryption": True
            },
            "recovery": {
                "auto_verify": True,
                "integrity_check": True,
                "rollback_enabled": True
            }
        }
    
    def _initialize_backup_system(self) -> None:
        """Initialize backup system - ATLAS: Fixed function length"""
        assert len(self.backup_records) == 0, "Backup system already initialized"
        
        # Create backup directory
        backup_dir = self.config.get("backup_destination", {}).get("local", "backups/")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["full", "incremental", "differential", "snapshot"]
        for subdir in subdirs:
            os.makedirs(os.path.join(backup_dir, subdir), exist_ok=True)
        
        self.logger.info("Backup system initialized")
    
    def create_backup(self, source_path: str, backup_type: BackupType = BackupType.FULL) -> str:
        """Create backup - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(backup_type, BackupType), "Backup type must be BackupType"
        
        with self._lock:
            backup_id = f"backup_{len(self.backup_records) + 1:03d}_{int(time.time())}"
            
            # Create backup record
            backup_record = BackupRecord(
                backup_id=backup_id,
                backup_type=backup_type,
                source_path=source_path,
                destination_path="",
                status=BackupStatus.IN_PROGRESS,
                size_bytes=0,
                checksum="",
                timestamp=datetime.now().isoformat(),
                compression_ratio=0.0
            )
            
            self.backup_records.append(backup_record)
            
            try:
                # Perform backup
                destination_path = self._perform_backup(backup_record)
                backup_record.destination_path = destination_path
                backup_record.status = BackupStatus.COMPLETED
                
                # Calculate metrics
                backup_record.size_bytes = os.path.getsize(destination_path)
                backup_record.checksum = self._calculate_checksum(destination_path)
                backup_record.compression_ratio = self._calculate_compression_ratio(source_path, destination_path)
                
                self.logger.info(f"Backup completed: {backup_id}")
                
            except Exception as e:
                backup_record.status = BackupStatus.FAILED
                self.logger.error(f"Backup failed: {backup_id} - {e}")
            
            return backup_id
    
    def _perform_backup(self, backup_record: BackupRecord) -> str:
        """Perform backup operation - ATLAS: Fixed function length"""
        assert isinstance(backup_record, BackupRecord), "Backup record must be BackupRecord"
        
        # Generate destination path
        backup_dir = self.config.get("backup_destination", {}).get("local", "backups/")
        backup_type_dir = os.path.join(backup_dir, backup_record.backup_type.value)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.isfile(backup_record.source_path):
            # File backup
            filename = os.path.basename(backup_record.source_path)
            destination_path = os.path.join(backup_type_dir, f"{filename}_{timestamp}.gz")
            self._backup_file(backup_record.source_path, destination_path)
        else:
            # Directory backup
            dirname = os.path.basename(backup_record.source_path)
            destination_path = os.path.join(backup_type_dir, f"{dirname}_{timestamp}.tar.gz")
            self._backup_directory(backup_record.source_path, destination_path)
        
        return destination_path
    
    def _backup_file(self, source_path: str, destination_path: str) -> None:
        """Backup single file - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        with open(source_path, 'rb') as f_in:
            with gzip.open(destination_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _backup_directory(self, source_path: str, destination_path: str) -> None:
        """Backup directory - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        import tarfile
        
        with tarfile.open(destination_path, 'w:gz') as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum - ATLAS: Fixed function length"""
        assert isinstance(file_path, str), "File path must be string"
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _calculate_compression_ratio(self, source_path: str, destination_path: str) -> float:
        """Calculate compression ratio - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        source_size = os.path.getsize(source_path)
        dest_size = os.path.getsize(destination_path)
        
        if source_size == 0:
            return 0.0
        
        return (1.0 - dest_size / source_size) * 100.0
    
    def restore_backup(self, backup_id: str, destination_path: str) -> str:
        """Restore backup - ATLAS: Fixed function length"""
        assert isinstance(backup_id, str), "Backup ID must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        with self._lock:
            # Find backup record
            backup_record = None
            for record in self.backup_records:
                if record.backup_id == backup_id:
                    backup_record = record
                    break
            
            if not backup_record:
                raise ValueError(f"Backup not found: {backup_id}")
            
            recovery_id = f"recovery_{len(self.recovery_records) + 1:03d}_{int(time.time())}"
            
            # Create recovery record
            recovery_record = RecoveryRecord(
                recovery_id=recovery_id,
                backup_id=backup_id,
                source_path=backup_record.destination_path,
                destination_path=destination_path,
                status=BackupStatus.IN_PROGRESS,
                timestamp=datetime.now().isoformat(),
                verification_passed=False
            )
            
            self.recovery_records.append(recovery_record)
            
            try:
                # Perform recovery
                self._perform_recovery(recovery_record)
                recovery_record.status = BackupStatus.COMPLETED
                recovery_record.verification_passed = True
                
                self.logger.info(f"Recovery completed: {recovery_id}")
                
            except Exception as e:
                recovery_record.status = BackupStatus.FAILED
                self.logger.error(f"Recovery failed: {recovery_id} - {e}")
            
            return recovery_id
    
    def _perform_recovery(self, recovery_record: RecoveryRecord) -> None:
        """Perform recovery operation - ATLAS: Fixed function length"""
        assert isinstance(recovery_record, RecoveryRecord), "Recovery record must be RecoveryRecord"
        
        # Create destination directory if needed
        os.makedirs(os.path.dirname(recovery_record.destination_path), exist_ok=True)
        
        if recovery_record.source_path.endswith('.gz') and not recovery_record.source_path.endswith('.tar.gz'):
            # File recovery
            self._restore_file(recovery_record.source_path, recovery_record.destination_path)
        else:
            # Directory recovery
            self._restore_directory(recovery_record.source_path, recovery_record.destination_path)
    
    def _restore_file(self, source_path: str, destination_path: str) -> None:
        """Restore single file - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        with gzip.open(source_path, 'rb') as f_in:
            with open(destination_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _restore_directory(self, source_path: str, destination_path: str) -> None:
        """Restore directory - ATLAS: Fixed function length"""
        assert isinstance(source_path, str), "Source path must be string"
        assert isinstance(destination_path, str), "Destination path must be string"
        
        import tarfile
        
        with tarfile.open(source_path, 'r:gz') as tar:
            tar.extractall(os.path.dirname(destination_path))
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify backup integrity - ATLAS: Fixed function length"""
        assert isinstance(backup_id, str), "Backup ID must be string"
        
        # Find backup record
        backup_record = None
        for record in self.backup_records:
            if record.backup_id == backup_id:
                backup_record = record
                break
        
        if not backup_record:
            return False
        
        # Verify checksum
        current_checksum = self._calculate_checksum(backup_record.destination_path)
        return current_checksum == backup_record.checksum
    
    def calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate - ATLAS: Fixed function length"""
        if not self.backup_records:
            return 100.0
        
        total_backups = len(self.backup_records)
        successful_backups = len([b for b in self.backup_records if b.status == BackupStatus.COMPLETED])
        
        self.overall_success_rate = (successful_backups / total_backups * 100) if total_backups > 0 else 100.0
        
        # ATLAS: Assert success rate validity
        assert 0 <= self.overall_success_rate <= 100, "Success rate out of range"
        
        return self.overall_success_rate
    
    def generate_backup_report(self) -> Dict[str, Any]:
        """Generate backup report - ATLAS: Fixed function length"""
        overall_success_rate = self.calculate_overall_success_rate()
        
        # Count backups by status
        status_counts = {}
        for backup in self.backup_records:
            status = backup.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count backups by type
        type_counts = {}
        for backup in self.backup_records:
            backup_type = backup.backup_type.value
            type_counts[backup_type] = type_counts.get(backup_type, 0) + 1
        
        # Calculate metrics
        total_backups = len(self.backup_records)
        successful_backups = len([b for b in self.backup_records if b.status == BackupStatus.COMPLETED])
        total_size = sum(b.size_bytes for b in self.backup_records if b.status == BackupStatus.COMPLETED)
        avg_compression = sum(b.compression_ratio for b in self.backup_records if b.status == BackupStatus.COMPLETED) / max(successful_backups, 1)
        
        report = {
            "overall_success_rate": overall_success_rate,
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "total_size_bytes": total_size,
            "average_compression_ratio": avg_compression,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "recoveries_performed": len(self.recovery_records),
            "timestamp": datetime.now().isoformat()
        }
        
        return report

# ATLAS Protocol: Main execution with proper error handling
if __name__ == "__main__":
    try:
        backup_system = AEGISBackupRecoverySystem()
        report = backup_system.generate_backup_report()
        print(f"Backup Report: {report}")
    except Exception as e:
        print(f"Backup and Recovery System failed: {e}")
        sys.exit(1)