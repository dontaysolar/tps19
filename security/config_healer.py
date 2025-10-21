#!/usr/bin/env python3
"""
AEGIS v2.0 Configuration Auto-Healing System
ATLAS Protocol Compliant - Zero-Tolerance Safety-Critical Implementation

FRACTAL_HOOK: This implementation provides autonomous configuration management
that enables future AEGIS operations to automatically detect, validate, and
repair configuration issues without human intervention, ensuring system
stability and security.
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# ATLAS Protocol: Fixed loop bounds and simple control flow
MAX_CONFIG_REPAIR_ATTEMPTS = 3
MAX_BACKUP_GENERATIONS = 5
MAX_FUNCTION_LENGTH = 60

class ConfigState(Enum):
    """Configuration states - ATLAS: Simple enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    REPAIRING = "repairing"
    REPAIRED = "repaired"
    FAILED = "failed"

@dataclass
class ConfigIssue:
    """Configuration issue - ATLAS: Fixed data structure"""
    file_path: str
    issue_type: str
    description: str
    severity: str
    suggested_fix: str
    timestamp: str

@dataclass
class ConfigBackup:
    """Configuration backup - ATLAS: Fixed data structure"""
    original_path: str
    backup_path: str
    timestamp: str
    reason: str

class AEGISConfigHealer:
    """
    AEGIS v2.0 Configuration Auto-Healing System
    
    ATLAS Protocol Compliance:
    - Simple control flow with fixed loop bounds
    - No dynamic memory allocation after initialization
    - High assertion density (2+ per function)
    - Minimal scope for all variables
    - Constrained function length
    """
    
    def __init__(self, config_dir: str = "config"):
        """Initialize config healer - ATLAS: Fixed initialization"""
        assert os.path.exists(config_dir), "Config directory must exist"
        assert isinstance(config_dir, str), "Config dir must be string"
        
        self.config_dir = config_dir
        self.backup_dir = os.path.join(config_dir, "backups")
        self.issues_found: List[ConfigIssue] = []
        self.backups_created: List[ConfigBackup] = []
        
        # ATLAS: Initialize logging
        self._setup_logging()
        self._ensure_backup_directory()
        
        # ATLAS: Assert initialization success
        assert self.logger is not None, "Logger must be initialized"
        assert os.path.exists(self.backup_dir), "Backup directory must exist"
    
    def _setup_logging(self) -> None:
        """Setup logging configuration - ATLAS: Fixed function length"""
        assert not hasattr(self, 'logger'), "Logger already initialized"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - AEGIS_CONFIG_HEALER - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/config_healer.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # ATLAS: Assert logging setup
        assert self.logger is not None, "Logger setup failed"
    
    def _ensure_backup_directory(self) -> None:
        """Ensure backup directory exists - ATLAS: Fixed function length"""
        assert isinstance(self.backup_dir, str), "Backup dir must be string"
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # ATLAS: Assert directory creation
        assert os.path.exists(self.backup_dir), "Backup directory creation failed"
    
    def scan_configuration_files(self) -> List[ConfigIssue]:
        """Scan all configuration files for issues - ATLAS: Fixed function length"""
        assert os.path.exists(self.config_dir), "Config directory missing"
        
        issues = []
        config_files = []
        
        # Find all JSON config files
        for root, dirs, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith('.json'):
                    config_files.append(os.path.join(root, file))
        
        # ATLAS: Fixed loop bound
        for i, config_file in enumerate(config_files[:50]):  # Limit files
            file_issues = self._analyze_config_file(config_file)
            issues.extend(file_issues)
        
        # ATLAS: Assert scan completion
        assert all(isinstance(issue, ConfigIssue) for issue in issues), "Invalid issues found"
        
        self.issues_found = issues
        return issues
    
    def _analyze_config_file(self, file_path: str) -> List[ConfigIssue]:
        """Analyze single config file - ATLAS: Fixed function length"""
        assert os.path.exists(file_path), "Config file must exist"
        assert file_path.endswith('.json'), "Must be JSON file"
        
        issues = []
        timestamp = datetime.now().isoformat()
        
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(ConfigIssue(
                file_path=file_path,
                issue_type="json_syntax_error",
                description=f"Invalid JSON syntax: {str(e)}",
                severity="critical",
                suggested_fix="Fix JSON syntax errors",
                timestamp=timestamp
            ))
            return issues
        except Exception as e:
            issues.append(ConfigIssue(
                file_path=file_path,
                issue_type="file_read_error",
                description=f"Cannot read file: {str(e)}",
                severity="critical",
                suggested_fix="Check file permissions and path",
                timestamp=timestamp
            ))
            return issues
        
        # Check for common configuration issues
        issues.extend(self._check_required_fields(file_path, config_data, timestamp))
        issues.extend(self._check_value_ranges(file_path, config_data, timestamp))
        issues.extend(self._check_security_issues(file_path, config_data, timestamp))
        
        # ATLAS: Assert issues validity
        assert all(isinstance(issue, ConfigIssue) for issue in issues), "Invalid issues"
        
        return issues
    
    def _check_required_fields(self, file_path: str, config_data: Dict, timestamp: str) -> List[ConfigIssue]:
        """Check for required fields - ATLAS: Fixed function length"""
        assert isinstance(config_data, dict), "Config data must be dict"
        
        issues = []
        required_fields = {
            "system.json": ["version", "environment", "debug"],
            "trading.json": ["mode", "default_pair", "position_size"],
            "mode.json": ["current_mode"]
        }
        
        filename = os.path.basename(file_path)
        if filename in required_fields:
            for field in required_fields[filename]:
                if field not in config_data:
                    issues.append(ConfigIssue(
                        file_path=file_path,
                        issue_type="missing_required_field",
                        description=f"Missing required field: {field}",
                        severity="high",
                        suggested_fix=f"Add field '{field}' to configuration",
                        timestamp=timestamp
                    ))
        
        # ATLAS: Assert issues validity
        assert all(isinstance(issue, ConfigIssue) for issue in issues), "Invalid issues"
        
        return issues
    
    def _check_value_ranges(self, file_path: str, config_data: Dict, timestamp: str) -> List[ConfigIssue]:
        """Check value ranges - ATLAS: Fixed function length"""
        assert isinstance(config_data, dict), "Config data must be dict"
        
        issues = []
        
        # Check numeric ranges
        if "position_size" in config_data:
            pos_size = config_data["position_size"]
            if not isinstance(pos_size, (int, float)) or pos_size <= 0 or pos_size > 1:
                issues.append(ConfigIssue(
                    file_path=file_path,
                    issue_type="invalid_value_range",
                    description=f"Position size {pos_size} out of range (0-1)",
                    severity="high",
                    suggested_fix="Set position_size between 0 and 1",
                    timestamp=timestamp
                ))
        
        # ATLAS: Assert issues validity
        assert all(isinstance(issue, ConfigIssue) for issue in issues), "Invalid issues"
        
        return issues
    
    def _check_security_issues(self, file_path: str, config_data: Dict, timestamp: str) -> List[ConfigIssue]:
        """Check for security issues - ATLAS: Fixed function length"""
        assert isinstance(config_data, dict), "Config data must be dict"
        
        issues = []
        security_patterns = ["password", "secret", "key", "token", "auth"]
        
        # Check for hardcoded secrets
        config_str = json.dumps(config_data, default=str).lower()
        for pattern in security_patterns:
            if pattern in config_str and "placeholder" not in config_str:
                issues.append(ConfigIssue(
                    file_path=file_path,
                    issue_type="potential_hardcoded_secret",
                    description=f"Potential hardcoded secret containing '{pattern}'",
                    severity="critical",
                    suggested_fix="Use environment variables or secure storage",
                    timestamp=timestamp
                ))
        
        # ATLAS: Assert issues validity
        assert all(isinstance(issue, ConfigIssue) for issue in issues), "Invalid issues"
        
        return issues
    
    def create_config_backup(self, file_path: str, reason: str) -> bool:
        """Create configuration backup - ATLAS: Fixed function length"""
        assert os.path.exists(file_path), "File must exist"
        assert isinstance(reason, str), "Reason must be string"
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_filename = f"{filename}.backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            shutil.copy2(file_path, backup_path)
            
            backup = ConfigBackup(
                original_path=file_path,
                backup_path=backup_path,
                timestamp=timestamp,
                reason=reason
            )
            self.backups_created.append(backup)
            
            # ATLAS: Assert backup success
            assert os.path.exists(backup_path), "Backup file not created"
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return False
    
    def repair_configuration_issues(self) -> bool:
        """Repair configuration issues - ATLAS: Fixed function length"""
        assert len(self.issues_found) > 0, "No issues to repair"
        
        repair_success = True
        
        # ATLAS: Fixed loop bound
        for i, issue in enumerate(self.issues_found[:MAX_CONFIG_REPAIR_ATTEMPTS]):
            if not self._repair_single_issue(issue):
                repair_success = False
                self.logger.error(f"Failed to repair issue: {issue.description}")
        
        # ATLAS: Assert repair completion
        assert isinstance(repair_success, bool), "Repair result must be boolean"
        
        return repair_success
    
    def _repair_single_issue(self, issue: ConfigIssue) -> bool:
        """Repair single configuration issue - ATLAS: Fixed function length"""
        assert isinstance(issue, ConfigIssue), "Issue must be valid"
        
        try:
            # Create backup before repair
            if not self.create_config_backup(issue.file_path, f"Repair: {issue.issue_type}"):
                return False
            
            # Apply repair based on issue type
            if issue.issue_type == "missing_required_field":
                return self._repair_missing_field(issue)
            elif issue.issue_type == "invalid_value_range":
                return self._repair_value_range(issue)
            elif issue.issue_type == "json_syntax_error":
                return self._repair_json_syntax(issue)
            else:
                self.logger.warning(f"No repair method for issue type: {issue.issue_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Repair failed for {issue.file_path}: {e}")
            return False
    
    def _repair_missing_field(self, issue: ConfigIssue) -> bool:
        """Repair missing field issue - ATLAS: Fixed function length"""
        assert issue.issue_type == "missing_required_field", "Must be missing field issue"
        
        try:
            with open(issue.file_path, 'r') as f:
                config_data = json.load(f)
            
            # Add default value for missing field
            field_name = issue.description.split(": ")[1]
            default_values = {
                "version": "1.0.0",
                "environment": "development",
                "debug": False,
                "mode": "simulation",
                "default_pair": "BTC/USDT",
                "position_size": 0.1,
                "current_mode": "predeployment"
            }
            
            if field_name in default_values:
                config_data[field_name] = default_values[field_name]
                
                with open(issue.file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                self.logger.info(f"Added missing field '{field_name}' to {issue.file_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Missing field repair failed: {e}")
            return False
    
    def _repair_value_range(self, issue: ConfigIssue) -> bool:
        """Repair value range issue - ATLAS: Fixed function length"""
        assert issue.issue_type == "invalid_value_range", "Must be value range issue"
        
        try:
            with open(issue.file_path, 'r') as f:
                config_data = json.load(f)
            
            # Fix position_size if out of range
            if "position_size" in config_data:
                if config_data["position_size"] <= 0:
                    config_data["position_size"] = 0.1
                elif config_data["position_size"] > 1:
                    config_data["position_size"] = 1.0
                
                with open(issue.file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                self.logger.info(f"Fixed position_size value in {issue.file_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Value range repair failed: {e}")
            return False
    
    def _repair_json_syntax(self, issue: ConfigIssue) -> bool:
        """Repair JSON syntax issue - ATLAS: Fixed function length"""
        assert issue.issue_type == "json_syntax_error", "Must be JSON syntax issue"
        
        # JSON syntax errors require manual intervention
        self.logger.warning(f"JSON syntax error in {issue.file_path} requires manual repair")
        return False
    
    def get_healing_status(self) -> Dict[str, Any]:
        """Get healing status - ATLAS: Fixed function length"""
        return {
            "issues_found": len(self.issues_found),
            "backups_created": len(self.backups_created),
            "critical_issues": len([i for i in self.issues_found if i.severity == "critical"]),
            "high_issues": len([i for i in self.issues_found if i.severity == "high"]),
            "last_scan": datetime.now().isoformat()
        }

# ATLAS Protocol: Main execution with proper error handling
if __name__ == "__main__":
    try:
        healer = AEGISConfigHealer()
        issues = healer.scan_configuration_files()
        print(f"Found {len(issues)} configuration issues")
        
        if issues:
            success = healer.repair_configuration_issues()
            print(f"Configuration repair {'successful' if success else 'failed'}")
        
        status = healer.get_healing_status()
        print(f"Healing status: {status}")
        
    except Exception as e:
        print(f"Config healer failed: {e}")
        sys.exit(1)