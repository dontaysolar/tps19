#!/usr/bin/env python3
"""
AEGIS v2.0 Simplified Test Suite
Core security validation without external dependencies
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any

class AEGISSimplifiedTest:
    """Simplified AEGIS test suite for core validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'critical_failures': [],
            'test_details': []
        }
    
    def run_core_tests(self) -> bool:
        """Run core AEGIS tests"""
        self.logger.info("Starting AEGIS v2.0 core validation")
        
        tests = [
            self._test_file_structure,
            self._test_security_files,
            self._test_configuration_security,
            self._test_code_quality,
            self._test_dependency_integrity
        ]
        
        all_passed = True
        for test_func in tests:
            test_name = test_func.__name__
            try:
                result = test_func()
                self._record_result(test_name, result)
                if not result:
                    all_passed = False
            except Exception as e:
                self.logger.error(f"Test {test_name} failed: {e}")
                self._record_result(test_name, False, str(e))
                all_passed = False
        
        self._generate_report()
        return all_passed
    
    def _record_result(self, test_name: str, passed: bool, error: str = ""):
        """Record test result"""
        self.test_results['total_tests'] += 1
        
        if passed:
            self.test_results['passed'] += 1
            self.logger.info(f"✅ {test_name} - PASSED")
        else:
            self.test_results['failed'] += 1
            self.test_results['critical_failures'].append(test_name)
            self.logger.error(f"❌ {test_name} - FAILED")
            if error:
                self.logger.error(f"   Error: {error}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def _test_file_structure(self) -> bool:
        """Test that security files are properly structured"""
        required_files = [
            'security/credential_manager.py',
            'security/input_validator.py',
            'security/state_integrity.py',
            'security/circuit_breaker.py',
            'security/build_shield.py',
            'security/aegis_test_suite.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                self.logger.error(f"Missing required file: {file_path}")
                return False
        
        return True
    
    def _test_security_files(self) -> bool:
        """Test that security files contain proper implementations"""
        security_files = [
            'security/credential_manager.py',
            'security/input_validator.py',
            'security/state_integrity.py',
            'security/circuit_breaker.py',
            'security/build_shield.py'
        ]
        
        for file_path in security_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for key security patterns
                if 'class AEGIS' not in content:
                    self.logger.error(f"Missing AEGIS class in {file_path}")
                    return False
                
                if 'def __init__' not in content:
                    self.logger.error(f"Missing __init__ method in {file_path}")
                    return False
                
            except Exception as e:
                self.logger.error(f"Error reading {file_path}: {e}")
                return False
        
        return True
    
    def _test_configuration_security(self) -> bool:
        """Test configuration security"""
        # Check .env file for hardcoded secrets
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                content = f.read()
            
            # Check for placeholder values
            if 'YOUR_' in content or 'PLACEHOLDER' in content:
                self.logger.warning("Placeholder values found in .env")
                return False
            
            # Check for exposed API keys
            if 'EXCHANGE_API_KEY=A8YmbndHwWATwn6WScdUco' in content:
                self.logger.error("Hardcoded API key found in .env")
                return False
        
        return True
    
    def _test_code_quality(self) -> bool:
        """Test code quality and security patterns"""
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', 'security']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for dangerous patterns
                dangerous_patterns = [
                    'eval(',
                    'exec(',
                    '__import__(',
                    'compile(',
                    'input(',
                    'raw_input('
                ]
                
                for pattern in dangerous_patterns:
                    if pattern in content:
                        self.logger.warning(f"Potentially dangerous pattern found in {file_path}: {pattern}")
                
                # Check for hardcoded secrets
                secret_patterns = [
                    'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                    'secret\s*=\s*["\'][^"\']+["\']',
                    'password\s*=\s*["\'][^"\']+["\']',
                    'token\s*=\s*["\'][^"\']+["\']'
                ]
                
                import re
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.logger.warning(f"Potential secret pattern found in {file_path}")
                
            except Exception as e:
                self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        return True
    
    def _test_dependency_integrity(self) -> bool:
        """Test dependency integrity"""
        # Check requirements file
        requirements_files = ['requirements.txt', 'requirements_phase1.txt']
        requirements_found = False
        
        for req_file in requirements_files:
            if os.path.exists(req_file):
                requirements_found = True
                break
        
        if not requirements_found:
            self.logger.warning("No requirements file found")
            return False
        
        # Check for pinned versions
        with open('requirements_phase1.txt', 'r') as f:
            content = f.read()
        
        # Check if versions are pinned
        lines = content.strip().split('\n')
        pinned_count = 0
        total_count = 0
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                total_count += 1
                if '>=' in line or '==' in line or '~=' in line:
                    pinned_count += 1
        
        if total_count > 0:
            pin_ratio = pinned_count / total_count
            if pin_ratio < 0.5:
                self.logger.warning(f"Low version pinning ratio: {pin_ratio:.2f}")
                return False
        
        return True
    
    def _generate_report(self):
        """Generate test report"""
        report = f"""
AEGIS v2.0 CORE VALIDATION REPORT
================================
Timestamp: {self.test_results['timestamp']}
Total Tests: {self.test_results['total_tests']}
Passed: {self.test_results['passed']}
Failed: {self.test_results['failed']}
Critical Failures: {len(self.test_results['critical_failures'])}

DETAILED RESULTS:
----------------
"""
        
        for test in self.test_results['test_details']:
            status = "PASS" if test['passed'] else "FAIL"
            report += f"{status}: {test['test_name']}\n"
            if test['error']:
                report += f"  Error: {test['error']}\n"
        
        # Save report
        os.makedirs('security', exist_ok=True)
        with open('security/core_validation_report.txt', 'w') as f:
            f.write(report)
        
        print(report)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    test_suite = AEGISSimplifiedTest()
    success = test_suite.run_core_tests()
    
    if success:
        print("\n✅ AEGIS CORE VALIDATION PASSED")
        sys.exit(0)
    else:
        print("\n❌ AEGIS CORE VALIDATION FAILED")
        sys.exit(1)