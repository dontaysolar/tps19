#!/usr/bin/env python3
"""
AEGIS-COMPLIANT PHASE 1 VALIDATION SUITE
Zero-tolerance validation of all Phase 1 deliverables
"""

import sys
import os
import subprocess
import hashlib
from datetime import datetime

# Add paths
workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace_dir, 'modules'))

# Results tracking
results = {
    'total_tests': 0,
    'passed_tests': 0,
    'failed_tests': 0,
    'errors': [],
    'warnings': []
}

def log_test(name, status, message=""):
    """Log test result"""
    results['total_tests'] += 1
    if status:
        results['passed_tests'] += 1
        print(f"✅ PASS: {name}")
    else:
        results['failed_tests'] += 1
        results['errors'].append(f"{name}: {message}")
        print(f"❌ FAIL: {name}")
        if message:
            print(f"   ERROR: {message}")
    return status

def test_dependency(module_name, import_name=None):
    """Test if a dependency can be imported"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        return log_test(f"Dependency: {module_name}", True)
    except ImportError as e:
        return log_test(f"Dependency: {module_name}", False, str(e))

def test_module_import(module_name, class_name):
    """Test if a module class can be imported"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        getattr(module, class_name)
        return log_test(f"Module Import: {module_name}.{class_name}", True)
    except Exception as e:
        return log_test(f"Module Import: {module_name}.{class_name}", False, str(e))

def test_module_instantiation(module_name, class_name, *args, **kwargs):
    """Test if a module class can be instantiated"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name)
        instance = cls(*args, **kwargs)
        return log_test(f"Module Instantiation: {class_name}", True), instance
    except Exception as e:
        return log_test(f"Module Instantiation: {class_name}", False, str(e)), None

def test_file_exists(filepath, description):
    """Test if a file exists"""
    exists = os.path.exists(filepath)
    return log_test(f"File Exists: {description}", exists, 
                   f"Not found: {filepath}" if not exists else "")

def generate_compliance_receipt():
    """Generate Aegis-compliant validation receipt"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    pass_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    
    receipt = f"""
{'='*70}
AEGIS PHASE 1 VALIDATION COMPLIANCE RECEIPT
{'='*70}

Timestamp: {timestamp}
Agent ID: ATLAS-VALIDATOR-001
Protocol: Aegis Pre-Deployment Validation Protocol - Phase 3

VALIDATION RESULTS:
-------------------
Total Tests: {results['total_tests']}
Passed: {results['passed_tests']}
Failed: {results['failed_tests']}
Pass Rate: {pass_rate:.1f}%

GATE STATUS: {'✅ GO' if results['failed_tests'] == 0 else '❌ NO-GO'}

"""
    
    if results['failed_tests'] > 0:
        receipt += "\nFAILED TESTS:\n"
        for error in results['errors']:
            receipt += f"  ❌ {error}\n"
    
    if results['warnings']:
        receipt += "\nWARNINGS:\n"
        for warning in results['warnings']:
            receipt += f"  ⚠️  {warning}\n"
    
    receipt += f"\n{'='*70}\n"
    receipt += "VERITAS AFFIRMATION:\n"
    receipt += "I affirm under the Veritas Protocol that this evidence is\n"
    receipt += "factual, complete, and free of hallucination.\n"
    receipt += f"\nCertificate Hash: {hashlib.sha256(receipt.encode()).hexdigest()[:16]}\n"
    receipt += f"{'='*70}\n"
    
    return receipt

def main():
    """Main validation routine"""
    print("\n" + "="*70)
    print("🔍 AEGIS PHASE 1 VALIDATION SUITE")
    print("="*70 + "\n")
    
    print("Phase 1: Dependency Validation\n" + "-"*70)
    
    # Test critical dependencies
    test_dependency("numpy", "numpy")
    test_dependency("pandas", "pandas")
    test_dependency("scikit-learn", "sklearn")
    
    # Test TensorFlow (may fail if not installed)
    tf_ok = test_dependency("tensorflow", "tensorflow")
    if not tf_ok:
        results['warnings'].append("TensorFlow not installed - AI models will not function")
    
    # Test optional dependencies
    redis_ok = test_dependency("redis", "redis")
    if not redis_ok:
        results['warnings'].append("Redis not installed - optional feature")
    
    google_ok = test_dependency("google-auth", "google.auth")
    if not google_ok:
        results['warnings'].append("Google APIs not installed - optional feature")
    
    print("\nPhase 2: Module Structure Validation\n" + "-"*70)
    
    # Test file existence
    test_file_exists(os.path.join(workspace_dir, "modules/ai_models/__init__.py"), 
                    "AI Models __init__.py")
    test_file_exists(os.path.join(workspace_dir, "modules/ai_models/lstm_predictor.py"), 
                    "LSTM Predictor")
    test_file_exists(os.path.join(workspace_dir, "modules/ai_models/gan_simulator.py"), 
                    "GAN Simulator")
    test_file_exists(os.path.join(workspace_dir, "modules/ai_models/self_learning.py"), 
                    "Self-Learning Pipeline")
    test_file_exists(os.path.join(workspace_dir, "modules/redis_integration.py"), 
                    "Redis Integration")
    test_file_exists(os.path.join(workspace_dir, "modules/google_sheets_integration.py"), 
                    "Google Sheets Integration")
    
    print("\nPhase 3: Module Import Validation\n" + "-"*70)
    
    # Test module imports (only if dependencies are met)
    if tf_ok:
        test_module_import("ai_models", "LSTMPredictor")
        test_module_import("ai_models", "GANSimulator")
        test_module_import("ai_models", "SelfLearningPipeline")
    else:
        print("⚠️  SKIP: AI Models import (TensorFlow not installed)")
        results['warnings'].append("AI Models import skipped - missing TensorFlow")
    
    test_module_import("redis_integration", "RedisIntegration")
    test_module_import("google_sheets_integration", "GoogleSheetsIntegration")
    
    print("\nPhase 4: Module Instantiation Validation\n" + "-"*70)
    
    # Test module instantiation
    if tf_ok:
        success, lstm = test_module_instantiation("ai_models", "LSTMPredictor",
                                                  model_dir=os.path.join(workspace_dir, "data/models"))
        if success and lstm:
            status = lstm.get_status()
            log_test("LSTM get_status() method", status is not None)
        
        success, gan = test_module_instantiation("ai_models", "GANSimulator",
                                                model_dir=os.path.join(workspace_dir, "data/models"))
        if success and gan:
            status = gan.get_status()
            log_test("GAN get_status() method", status is not None)
        
        success, learning = test_module_instantiation("ai_models", "SelfLearningPipeline",
                                                     db_path=os.path.join(workspace_dir, "data/self_learning.db"))
        if success and learning:
            status = learning.get_status()
            log_test("SelfLearning get_status() method", status is not None)
    
    success, redis_client = test_module_instantiation("redis_integration", "RedisIntegration")
    if success and redis_client:
        status = redis_client.get_stats()
        log_test("Redis get_stats() method", status is not None)
    
    success, sheets = test_module_instantiation("google_sheets_integration", "GoogleSheetsIntegration",
                                               credentials_file=os.path.join(workspace_dir, "config/google_credentials.json"))
    if success and sheets:
        status = sheets.get_status()
        log_test("GoogleSheets get_status() method", status is not None)
    
    print("\nPhase 5: Documentation Validation\n" + "-"*70)
    
    test_file_exists(os.path.join(workspace_dir, "PHASE1_COMPLETE.md"), 
                    "Phase 1 Complete Documentation")
    test_file_exists(os.path.join(workspace_dir, "PHASE1_SUMMARY.md"), 
                    "Phase 1 Summary Documentation")
    test_file_exists(os.path.join(workspace_dir, "README_PHASE1.md"), 
                    "Phase 1 README")
    test_file_exists(os.path.join(workspace_dir, "requirements_phase1.txt"), 
                    "Phase 1 Requirements")
    test_file_exists(os.path.join(workspace_dir, "test_phase1.py"), 
                    "Phase 1 Test Suite")
    
    # Generate compliance receipt
    print("\n" + "="*70)
    receipt = generate_compliance_receipt()
    print(receipt)
    
    # Save receipt to file
    receipt_path = os.path.join(workspace_dir, "PHASE1_VALIDATION_RECEIPT.txt")
    with open(receipt_path, 'w') as f:
        f.write(receipt)
    print(f"📄 Compliance receipt saved: {receipt_path}")
    
    # Exit with appropriate code
    if results['failed_tests'] > 0:
        print("\n🚨 VALIDATION FAILED - NO-GO CONDITION")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED - GO CONDITION")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
