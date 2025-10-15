#!/usr/bin/env python3
"""System Validation and Quality Check Script for TPS19"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules'))

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def check_required_modules():
    """Check if all required modules are present"""
    print("\n📦 Checking required modules...")
    
    required_files = [
        "modules/exchanges/crypto_com.py",
        "modules/exchanges/alpha_vantage.py",
        "modules/market/unified_market_data.py",
        "modules/integrations/google_sheets.py",
        "modules/telegram_bot.py",
        "modules/market_data.py",
        "modules/realtime_data.py",
        "modules/siul/siul_core.py",
        "modules/patching/patch_manager.py",
        "modules/n8n/n8n_integration.py"
    ]
    
    missing = []
    for file in required_files:
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_dependencies():
    """Check Python package dependencies"""
    print("\n📚 Checking Python dependencies...")
    
    optional_packages = {
        'telegram': 'python-telegram-bot',
        'google': 'google-api-python-client google-auth',
        'psutil': 'psutil'
    }
    
    for package, install_name in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"⚠️ {package} - Not installed (optional)")
            print(f"   Install with: pip install {install_name}")

def check_api_configurations():
    """Check API configurations"""
    print("\n🔑 Checking API configurations...")
    
    env_vars = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot',
        'GOOGLE_SHEETS_CREDS': 'Google Sheets Credentials',
        'GOOGLE_SHEETS_ID': 'Google Sheets ID',
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage API Key'
    }
    
    configured = 0
    for var, name in env_vars.items():
        if os.environ.get(var):
            print(f"✅ {name} - Configured")
            configured += 1
        else:
            print(f"⚠️ {name} - Not configured (optional)")
    
    print(f"\n📊 {configured}/{len(env_vars)} APIs configured")

def run_syntax_check():
    """Run syntax check on all Python files"""
    print("\n🔍 Running syntax check...")
    
    errors = []
    for root, dirs, files in os.walk("modules"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        compile(f.read(), filepath, 'exec')
                    print(f"✅ {filepath} - Valid syntax")
                except SyntaxError as e:
                    print(f"❌ {filepath} - Syntax error: {e}")
                    errors.append(filepath)
    
    return len(errors) == 0

def check_coingecko_removal():
    """Verify CoinGecko has been removed"""
    print("\n🔍 Checking for CoinGecko removal...")
    
    found_coingecko = False
    for root, dirs, files in os.walk("modules"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'coingecko' in content.lower() and 'coingecko' not in filepath:
                            # Check if it's in a comment
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'coingecko' in line.lower() and not line.strip().startswith('#'):
                                    print(f"⚠️ Found CoinGecko reference in {filepath}:{i+1}")
                                    found_coingecko = True
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    if not found_coingecko:
        print("✅ No CoinGecko dependencies found (removed successfully)")
    
    return not found_coingecko

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "modules/testing/comprehensive_test_suite.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ All unit tests passed")
            return True
        else:
            print("❌ Some unit tests failed")
            print(result.stdout[-1000:])  # Last 1000 chars
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_integration_test():
    """Run integration test"""
    print("\n🔗 Running integration test...")
    
    try:
        result = subprocess.run(
            [sys.executable, "tps19_main.py", "test"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "SYSTEM OPERATIONAL" in result.stdout or result.returncode == 0:
            print("✅ Integration test passed")
            return True
        else:
            print("❌ Integration test failed")
            print(result.stdout[-1000:])  # Last 1000 chars
            return False
    except Exception as e:
        print(f"❌ Error running integration test: {e}")
        return False

def check_directory_structure():
    """Check required directory structure"""
    print("\n📁 Checking directory structure...")
    
    required_dirs = [
        "modules",
        "modules/exchanges",
        "modules/market",
        "modules/integrations",
        "modules/testing",
        "modules/siul",
        "modules/patching",
        "modules/n8n",
        "modules/brain",
        "modules/simulation",
        "modules/ui",
        "data",
        "data/databases",
        "config",
        "logs"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️ {dir_path} - Creating...")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ {dir_path} - Created")
            except Exception as e:
                print(f"❌ {dir_path} - Failed to create: {e}")
                missing.append(dir_path)
    
    return len(missing) == 0

def generate_validation_report(results):
    """Generate validation report"""
    print("\n" + "=" * 60)
    print("📋 VALIDATION REPORT")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {timestamp}")
    print(f"System: TPS19 Unified Trading System")
    print()
    
    # Calculate overall status
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    pass_rate = passed_checks / total_checks * 100
    
    print("Check Results:")
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check}")
    
    print(f"\nOverall: {passed_checks}/{total_checks} checks passed ({pass_rate:.1f}%)")
    
    # Determine system status
    if pass_rate == 100:
        print("\n🎉 SYSTEM FULLY VALIDATED - Ready for production!")
        status = "READY"
    elif pass_rate >= 80:
        print("\n✅ SYSTEM OPERATIONAL - Minor issues detected")
        status = "OPERATIONAL"
    elif pass_rate >= 60:
        print("\n⚠️ SYSTEM PARTIALLY FUNCTIONAL - Review failures")
        status = "DEGRADED"
    else:
        print("\n❌ SYSTEM NOT READY - Critical issues found")
        status = "FAILED"
    
    # Save report
    report = {
        'timestamp': timestamp,
        'checks': results,
        'pass_rate': pass_rate,
        'status': status
    }
    
    try:
        with open('validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to validation_report.json")
    except Exception as e:
        print(f"\n⚠️ Failed to save report: {e}")
    
    return status

def main():
    """Main validation function"""
    print("🚀 TPS19 System Validation Script")
    print("=" * 60)
    
    results = {}
    
    # Run all checks
    results['Python Version'] = check_python_version()
    results['Directory Structure'] = check_directory_structure()
    results['Required Modules'] = check_required_modules()
    results['Syntax Check'] = run_syntax_check()
    results['CoinGecko Removal'] = check_coingecko_removal()
    
    # Check dependencies and configurations
    check_dependencies()
    check_api_configurations()
    
    # Run tests if basic checks pass
    if results['Required Modules'] and results['Syntax Check']:
        results['Unit Tests'] = run_unit_tests()
        results['Integration Test'] = run_integration_test()
    else:
        print("\n⚠️ Skipping tests due to failed basic checks")
        results['Unit Tests'] = False
        results['Integration Test'] = False
    
    # Generate report
    status = generate_validation_report(results)
    
    # Exit with appropriate code
    if status == "READY":
        sys.exit(0)
    elif status == "OPERATIONAL":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()