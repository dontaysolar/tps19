#!/usr/bin/env python3
"""
AEGIS v2.0 Build-Time Shielding System
Active defense during build process with canary transactions
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib
import importlib.util

@dataclass
class BuildShieldConfig:
    enable_canary_tests: bool = True
    enable_security_scan: bool = True
    enable_dependency_check: bool = True
    enable_code_analysis: bool = True
    canary_timeout: int = 30
    max_build_time: int = 600

class AEGISBuildShield:
    """AEGIS-compliant build-time shielding with active defense"""
    
    def __init__(self, config: BuildShieldConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.build_start_time = None
        self.shield_status = {
            'build_id': None,
            'start_time': None,
            'end_time': None,
            'status': 'pending',
            'tests_passed': 0,
            'tests_failed': 0,
            'security_issues': [],
            'canary_results': {},
            'build_artifacts': []
        }
    
    def start_build_shield(self, build_id: str) -> bool:
        """Start build shielding process"""
        self.build_start_time = datetime.now()
        self.shield_status['build_id'] = build_id
        self.shield_status['start_time'] = self.build_start_time.isoformat()
        self.shield_status['status'] = 'running'
        
        self.logger.info(f"Starting AEGIS build shield for build {build_id}")
        
        try:
            # Run all shield checks
            if not self._run_security_scan():
                return False
            
            if not self._run_dependency_check():
                return False
            
            if not self._run_code_analysis():
                return False
            
            if self.config.enable_canary_tests:
                if not self._run_canary_tests():
                    return False
            
            # Build successful
            self.shield_status['status'] = 'success'
            self.shield_status['end_time'] = datetime.now().isoformat()
            
            self.logger.info(f"Build shield completed successfully for build {build_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Build shield failed: {e}")
            self.shield_status['status'] = 'failed'
            self.shield_status['end_time'] = datetime.now().isoformat()
            return False
    
    def _run_security_scan(self) -> bool:
        """Run comprehensive security scan"""
        self.logger.info("Running security scan...")
        
        security_issues = []
        
        # Check for hardcoded secrets
        if self._scan_for_secrets():
            security_issues.append("Hardcoded secrets detected")
        
        # Check for vulnerable dependencies
        if self._scan_dependencies():
            security_issues.append("Vulnerable dependencies found")
        
        # Check for insecure configurations
        if self._scan_configurations():
            security_issues.append("Insecure configurations detected")
        
        # Check for code vulnerabilities
        if self._scan_code_vulnerabilities():
            security_issues.append("Code vulnerabilities found")
        
        self.shield_status['security_issues'] = security_issues
        
        if security_issues:
            self.logger.error(f"Security scan failed: {security_issues}")
            return False
        
        self.logger.info("Security scan passed")
        return True
    
    def _scan_for_secrets(self) -> bool:
        """Scan for hardcoded secrets"""
        secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'private[_-]?key\s*=\s*["\'][^"\']+["\']'
        ]
        
        issues_found = False
        
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.json', '.env', '.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in secret_patterns:
                            import re
                            if re.search(pattern, content, re.IGNORECASE):
                                self.logger.warning(f"Potential secret found in {file_path}")
                                issues_found = True
                    except Exception:
                        continue
        
        return issues_found
    
    def _scan_dependencies(self) -> bool:
        """Scan for vulnerable dependencies"""
        try:
            # Check if requirements file exists
            requirements_files = ['requirements.txt', 'requirements_phase1.txt', 'pyproject.toml']
            requirements_found = False
            
            for req_file in requirements_files:
                if os.path.exists(req_file):
                    requirements_found = True
                    break
            
            if not requirements_found:
                self.logger.warning("No requirements file found")
                return True  # Not a failure, just a warning
            
            # Run safety check if available
            try:
                result = subprocess.run(['safety', 'check', '--json'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    self.logger.warning("Safety check found vulnerabilities")
                    return True  # Vulnerabilities found
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.info("Safety check not available, skipping")
            
            return False  # No vulnerabilities found
            
        except Exception as e:
            self.logger.error(f"Dependency scan failed: {e}")
            return True  # Treat as failure
    
    def _scan_configurations(self) -> bool:
        """Scan for insecure configurations"""
        issues_found = False
        
        # Check .env file
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
                
            # Check for placeholder values
            if 'YOUR_' in content or 'PLACEHOLDER' in content:
                self.logger.warning("Placeholder values found in .env")
                issues_found = True
        
        # Check Dockerfile
        if os.path.exists('Dockerfile'):
            with open('Dockerfile', 'r') as f:
                content = f.read()
                
            # Check for running as root
            if 'USER root' in content and 'USER' not in content.split('USER root')[1]:
                self.logger.warning("Dockerfile runs as root")
                issues_found = True
        
        return issues_found
    
    def _scan_code_vulnerabilities(self) -> bool:
        """Scan for code vulnerabilities"""
        issues_found = False
        
        # Check for dangerous functions
        dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        for pattern in dangerous_patterns:
                            import re
                            if re.search(pattern, content):
                                self.logger.warning(f"Potentially dangerous function found in {file_path}")
                                issues_found = True
                    except Exception:
                        continue
        
        return issues_found
    
    def _run_dependency_check(self) -> bool:
        """Check dependency integrity"""
        self.logger.info("Running dependency check...")
        
        try:
            # Check if all required modules can be imported
            required_modules = [
                'numpy', 'pandas', 'tensorflow', 'sklearn',
                'requests', 'ccxt', 'redis', 'google.auth'
            ]
            
            missing_modules = []
            for module in required_modules:
                try:
                    importlib.import_module(module)
                except ImportError:
                    missing_modules.append(module)
            
            if missing_modules:
                self.logger.error(f"Missing required modules: {missing_modules}")
                return False
            
            self.logger.info("Dependency check passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return False
    
    def _run_code_analysis(self) -> bool:
        """Run static code analysis"""
        self.logger.info("Running code analysis...")
        
        try:
            # Run basic syntax check
            python_files = []
            for root, dirs, files in os.walk('.'):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    self.logger.error(f"Syntax error in {file_path}: {e}")
                    return False
            
            self.logger.info("Code analysis passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            return False
    
    def _run_canary_tests(self) -> bool:
        """Run canary tests to validate core functionality"""
        self.logger.info("Running canary tests...")
        
        canary_results = {}
        
        # Test 1: Basic system initialization
        try:
            from unified_config import UnifiedConfig
            config = UnifiedConfig()
            validation = config.validate()
            canary_results['config_validation'] = validation['valid']
            
            if not validation['valid']:
                self.logger.error(f"Config validation failed: {validation['errors']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Config canary test failed: {e}")
            return False
        
        # Test 2: Bot initialization
        try:
            from bots.god_bot import GODBot
            bot = GODBot()
            status = bot.get_status()
            canary_results['bot_initialization'] = status is not None
            
            if not status:
                self.logger.error("Bot initialization failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Bot canary test failed: {e}")
            return False
        
        # Test 3: Database connectivity (if available)
        try:
            import sqlite3
            # Test basic database operations
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE test (id INTEGER)')
            cursor.execute('INSERT INTO test VALUES (1)')
            cursor.execute('SELECT * FROM test')
            result = cursor.fetchone()
            conn.close()
            
            canary_results['database_operations'] = result == (1,)
            
        except Exception as e:
            self.logger.warning(f"Database canary test failed: {e}")
            canary_results['database_operations'] = False
        
        # Test 4: Network connectivity (if available)
        try:
            import requests
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            canary_results['network_connectivity'] = response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Network canary test failed: {e}")
            canary_results['network_connectivity'] = False
        
        self.shield_status['canary_results'] = canary_results
        
        # Check if critical tests passed
        critical_tests = ['config_validation', 'bot_initialization']
        critical_passed = all(canary_results.get(test, False) for test in critical_tests)
        
        if not critical_passed:
            self.logger.error("Critical canary tests failed")
            return False
        
        self.logger.info("Canary tests passed")
        return True
    
    def get_shield_status(self) -> Dict[str, Any]:
        """Get current shield status"""
        return self.shield_status.copy()
    
    def generate_build_report(self) -> str:
        """Generate comprehensive build report"""
        report = f"""
AEGIS BUILD SHIELD REPORT
========================
Build ID: {self.shield_status['build_id']}
Start Time: {self.shield_status['start_time']}
End Time: {self.shield_status['end_time']}
Status: {self.shield_status['status'].upper()}

Security Issues: {len(self.shield_status['security_issues'])}
"""
        
        if self.shield_status['security_issues']:
            report += "\nSecurity Issues Found:\n"
            for issue in self.shield_status['security_issues']:
                report += f"  - {issue}\n"
        
        if self.shield_status['canary_results']:
            report += "\nCanary Test Results:\n"
            for test, result in self.shield_status['canary_results'].items():
                status = "PASS" if result else "FAIL"
                report += f"  - {test}: {status}\n"
        
        return report

# AEGIS Recursion Clause Implementation
class AEGISBuildAuditor:
    """Autonomous build auditing and optimization"""
    
    def __init__(self, build_shield: AEGISBuildShield):
        self.build_shield = build_shield
        self.logger = logging.getLogger(__name__)
        self.build_history = []
    
    def audit_build_effectiveness(self) -> Dict[str, Any]:
        """Audit build shield effectiveness"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'effectiveness_score': 0,
            'optimization_opportunities': [],
            'recommendations': []
        }
        
        # Analyze build history
        if self.build_history:
            successful_builds = sum(1 for build in self.build_history if build['status'] == 'success')
            total_builds = len(self.build_history)
            audit_results['effectiveness_score'] = (successful_builds / total_builds) * 100
        
        # Generate recommendations
        audit_results['recommendations'] = [
            "Implement parallel test execution",
            "Add performance regression detection",
            "Enhance security scanning with ML",
            "Implement build artifact verification"
        ]
        
        return audit_results

if __name__ == '__main__':
    # Initialize build shield
    config = BuildShieldConfig()
    shield = AEGISBuildShield(config)
    
    # Start build shield
    build_id = f"build_{int(time.time())}"
    success = shield.start_build_shield(build_id)
    
    # Generate report
    report = shield.generate_build_report()
    print(report)
    
    # Show status
    status = shield.get_shield_status()
    print(f"\nShield Status: {json.dumps(status, indent=2)}")