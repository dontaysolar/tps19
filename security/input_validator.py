#!/usr/bin/env python3
"""
AEGIS v2.0 Input Validation Framework
Comprehensive input validation with schema enforcement and security scanning
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ValidationSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_data: Optional[Any] = None
    security_score: int = 0

class AEGISInputValidator:
    """AEGIS-compliant input validation with security scanning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_rules = self._load_validation_rules()
        self.security_patterns = self._load_security_patterns()
        self.sanitization_rules = self._load_sanitization_rules()
    
    def _load_validation_rules(self) -> Dict:
        """Load validation rules for different data types"""
        return {
            'trading_pair': {
                'pattern': r'^[A-Z]{2,10}/[A-Z]{2,10}$',
                'max_length': 20,
                'required': True
            },
            'price': {
                'type': float,
                'min_value': 0.000001,
                'max_value': 1000000,
                'precision': 8
            },
            'amount': {
                'type': float,
                'min_value': 0.00000001,
                'max_value': 1000000,
                'precision': 8
            },
            'confidence': {
                'type': float,
                'min_value': 0.0,
                'max_value': 1.0,
                'precision': 3
            },
            'symbol': {
                'pattern': r'^[A-Z]{2,10}$',
                'max_length': 10,
                'required': True
            },
            'api_key': {
                'pattern': r'^[A-Za-z0-9+/=]{20,}$',
                'min_length': 20,
                'max_length': 200
            },
            'telegram_token': {
                'pattern': r'^\d+:[A-Za-z0-9_-]{35}$',
                'exact_length': 46
            },
            'chat_id': {
                'pattern': r'^-?\d+$',
                'min_length': 1,
                'max_length': 20
            }
        }
    
    def _load_security_patterns(self) -> Dict[str, List[str]]:
        """Load security patterns for threat detection"""
        return {
            'sql_injection': [
                r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)',
                r'(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)',
                r'(\b(EXEC|EXECUTE|SP_)\b)',
                r'(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)'
            ],
            'xss_attack': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>'
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'%2e%2e%2f',
                r'%2e%2e%5c',
                r'\.\.%2f',
                r'\.\.%5c'
            ],
            'command_injection': [
                r'[;&|`$]',
                r'\b(cat|ls|dir|type|more|less|head|tail)\b',
                r'\b(rm|del|rd|mkdir|rmdir)\b',
                r'\b(net|ipconfig|ifconfig|ping|tracert)\b'
            ],
            'crypto_attack': [
                r'\b(md5|sha1|sha256|sha512)\b.*\b(crack|brute|rainbow)\b',
                r'\b(rsa|aes|des|blowfish)\b.*\b(key|private|secret)\b',
                r'\b(base64|hex|binary)\b.*\b(decode|encode)\b'
            ]
        }
    
    def _load_sanitization_rules(self) -> Dict:
        """Load data sanitization rules"""
        return {
            'html_escape': {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#x27;',
                '/': '&#x2F;'
            },
            'sql_escape': {
                "'": "''",
                '"': '""',
                '\\': '\\\\',
                '\0': '\\0',
                '\n': '\\n',
                '\r': '\\r',
                '\x1a': '\\Z'
            },
            'whitespace_normalize': {
                'pattern': r'\s+',
                'replacement': ' '
            }
        }
    
    def validate_trading_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate trading-related data with comprehensive security checks"""
        errors = []
        warnings = []
        sanitized_data = {}
        
        # Validate trading pair
        if 'pair' in data:
            pair_result = self.validate_field('trading_pair', data['pair'])
            if not pair_result.is_valid:
                errors.extend(pair_result.errors)
            else:
                sanitized_data['pair'] = pair_result.sanitized_data
        
        # Validate price
        if 'price' in data:
            price_result = self.validate_field('price', data['price'])
            if not price_result.is_valid:
                errors.extend(price_result.errors)
            else:
                sanitized_data['price'] = price_result.sanitized_data
        
        # Validate amount
        if 'amount' in data:
            amount_result = self.validate_field('amount', data['amount'])
            if not amount_result.is_valid:
                errors.extend(amount_result.errors)
            else:
                sanitized_data['amount'] = amount_result.sanitized_data
        
        # Validate confidence
        if 'confidence' in data:
            conf_result = self.validate_field('confidence', data['confidence'])
            if not conf_result.is_valid:
                errors.extend(conf_result.errors)
            else:
                sanitized_data['confidence'] = conf_result.sanitized_data
        
        # Security scan
        security_issues = self._security_scan(data)
        if security_issues:
            errors.extend(security_issues)
        
        # Calculate security score
        security_score = self._calculate_security_score(data, errors, warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_data if len(errors) == 0 else None,
            security_score=security_score
        )
    
    def validate_field(self, field_type: str, value: Any) -> ValidationResult:
        """Validate individual field against schema"""
        if field_type not in self.validation_rules:
            return ValidationResult(False, [f"Unknown field type: {field_type}"], [])
        
        rules = self.validation_rules[field_type]
        errors = []
        warnings = []
        sanitized_value = value
        
        # Type validation
        if 'type' in rules:
            if not isinstance(value, rules['type']):
                try:
                    sanitized_value = rules['type'](value)
                except (ValueError, TypeError):
                    errors.append(f"Invalid type for {field_type}: expected {rules['type'].__name__}")
                    return ValidationResult(False, errors, warnings)
        
        # Pattern validation
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str(sanitized_value)):
                errors.append(f"Invalid format for {field_type}")
                return ValidationResult(False, errors, warnings)
        
        # Length validation
        if 'max_length' in rules:
            if len(str(sanitized_value)) > rules['max_length']:
                errors.append(f"{field_type} exceeds maximum length")
                return ValidationResult(False, errors, warnings)
        
        if 'min_length' in rules:
            if len(str(sanitized_value)) < rules['min_length']:
                errors.append(f"{field_type} below minimum length")
                return ValidationResult(False, errors, warnings)
        
        # Value range validation
        if 'min_value' in rules and isinstance(sanitized_value, (int, float)):
            if sanitized_value < rules['min_value']:
                errors.append(f"{field_type} below minimum value")
                return ValidationResult(False, errors, warnings)
        
        if 'max_value' in rules and isinstance(sanitized_value, (int, float)):
            if sanitized_value > rules['max_value']:
                errors.append(f"{field_type} exceeds maximum value")
                return ValidationResult(False, errors, warnings)
        
        # Precision validation
        if 'precision' in rules and isinstance(sanitized_value, float):
            sanitized_value = round(sanitized_value, rules['precision'])
        
        return ValidationResult(True, [], [], sanitized_value)
    
    def _security_scan(self, data: Dict[str, Any]) -> List[str]:
        """Perform comprehensive security scan on input data"""
        security_issues = []
        
        # Convert data to string for pattern matching
        data_str = json.dumps(data, default=str).lower()
        
        for threat_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                if re.search(pattern, data_str, re.IGNORECASE):
                    security_issues.append(f"Potential {threat_type} detected")
                    self.logger.warning(f"Security threat detected: {threat_type} in data: {data}")
        
        return security_issues
    
    def _calculate_security_score(self, data: Dict[str, Any], errors: List[str], warnings: List[str]) -> int:
        """Calculate security score based on validation results"""
        base_score = 100
        
        # Deduct for errors
        base_score -= len(errors) * 20
        
        # Deduct for warnings
        base_score -= len(warnings) * 5
        
        # Deduct for security issues
        security_issues = self._security_scan(data)
        base_score -= len(security_issues) * 30
        
        return max(0, base_score)
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data using configured rules"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # HTML escape
                for char, replacement in self.sanitization_rules['html_escape'].items():
                    value = value.replace(char, replacement)
                
                # SQL escape
                for char, replacement in self.sanitization_rules['sql_escape'].items():
                    value = value.replace(char, replacement)
                
                # Normalize whitespace
                value = re.sub(
                    self.sanitization_rules['whitespace_normalize']['pattern'],
                    self.sanitization_rules['whitespace_normalize']['replacement'],
                    value
                ).strip()
            
            sanitized[key] = value
        
        return sanitized
    
    def validate_api_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate API request with comprehensive security checks"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['endpoint', 'method', 'timestamp']
        for field in required_fields:
            if field not in request_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate endpoint
        if 'endpoint' in request_data:
            endpoint = request_data['endpoint']
            if not re.match(r'^/[a-zA-Z0-9_/-]*$', endpoint):
                errors.append("Invalid endpoint format")
        
        # Validate method
        if 'method' in request_data:
            method = request_data['method'].upper()
            if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                errors.append("Invalid HTTP method")
        
        # Security scan
        security_issues = self._security_scan(request_data)
        if security_issues:
            errors.extend(security_issues)
        
        # Rate limiting check (would implement with Redis)
        # This is a placeholder for rate limiting validation
        
        security_score = self._calculate_security_score(request_data, errors, warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            security_score=security_score
        )

# AEGIS Recursion Clause Implementation
class AEGISValidationAuditor:
    """Autonomous validation auditing and pattern learning"""
    
    def __init__(self, validator: AEGISInputValidator):
        self.validator = validator
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
        self.pattern_learning = {}
    
    def audit_validation_effectiveness(self) -> Dict:
        """Audit validation system effectiveness and suggest improvements"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'effectiveness_score': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'pattern_insights': {},
            'recommendations': []
        }
        
        # Analyze validation history
        if self.validation_history:
            total_validations = len(self.validation_history)
            successful_validations = sum(1 for v in self.validation_history if v['is_valid'])
            
            audit_results['effectiveness_score'] = (successful_validations / total_validations) * 100
            
            # Pattern analysis
            audit_results['pattern_insights'] = self._analyze_patterns()
            
            # Generate recommendations
            audit_results['recommendations'] = self._generate_recommendations()
        
        return audit_results
    
    def _analyze_patterns(self) -> Dict:
        """Analyze validation patterns for insights"""
        # Implementation would analyze validation history
        return {
            'common_errors': [],
            'security_trends': [],
            'performance_metrics': {}
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for validation improvements"""
        return [
            "Implement machine learning-based anomaly detection",
            "Add real-time threat intelligence feeds",
            "Enhance pattern recognition for new attack vectors"
        ]

if __name__ == '__main__':
    # Initialize validator
    validator = AEGISInputValidator()
    
    # Test trading data validation
    test_data = {
        'pair': 'BTC/USDT',
        'price': 26500.50,
        'amount': 0.001,
        'confidence': 0.85
    }
    
    result = validator.validate_trading_data(test_data)
    print(f"Validation Result: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Security Score: {result.security_score}")
    print(f"Sanitized Data: {result.sanitized_data}")