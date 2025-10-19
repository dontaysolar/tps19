#!/usr/bin/env python3
"""
SYSTEM VERIFICATION SCRIPT
Quick check to verify everything is working
"""

import sys
import os
from pathlib import Path

def check_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_files():
    """Check that all required files exist"""
    check_section("CHECKING FILES")
    
    required_files = [
        'apex_v3_integrated.py',
        'market_analysis_layer.py',
        'signal_generation_layer.py',
        'ai_ml_layer.py',
        'risk_management_layer.py',
        'execution_layer.py',
        'sentiment_layer.py',
        'onchain_layer.py',
        'portfolio_layer.py',
        'backtesting_layer.py',
        'infrastructure_layer.py',
        'trade_persistence.py',
        'test_suite.py',
        'requirements.txt',
        '.env',
        '.env.example'
    ]
    
    missing = []
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_dependencies():
    """Check Python dependencies"""
    check_section("CHECKING DEPENDENCIES")
    
    required = {
        'ccxt': 'ccxt',
        'numpy': 'numpy',
        'dotenv': 'python-dotenv',
        'requests': 'requests',
        'psutil': 'psutil'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n  Install with: pip3 install {' '.join(missing)}")
    
    return len(missing) == 0

def check_credentials():
    """Check if credentials are configured"""
    check_section("CHECKING CREDENTIALS")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get('EXCHANGE_API_KEY', '')
    api_secret = os.environ.get('EXCHANGE_API_SECRET', '')
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    
    creds_ok = True
    
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("  ❌ EXCHANGE_API_KEY not set")
        creds_ok = False
    else:
        print(f"  ✅ EXCHANGE_API_KEY set (starts with: {api_key[:5]}...)")
    
    if not api_secret or api_secret == 'YOUR_API_SECRET_HERE':
        print("  ❌ EXCHANGE_API_SECRET not set")
        creds_ok = False
    else:
        print(f"  ✅ EXCHANGE_API_SECRET set")
    
    if not telegram_token or telegram_token == 'YOUR_TELEGRAM_TOKEN_HERE':
        print("  ⚠️  TELEGRAM_BOT_TOKEN not set (optional)")
    else:
        print(f"  ✅ TELEGRAM_BOT_TOKEN set")
    
    if not creds_ok:
        print("\n  ⚠️  Update .env file with your credentials")
        print("  See: USER_ACTION_REQUIRED.md")
    
    return creds_ok

def check_imports():
    """Check that all layers can be imported"""
    check_section("CHECKING LAYER IMPORTS")
    
    layers = [
        ('infrastructure_layer', 'InfrastructureLayer'),
        ('market_analysis_layer', 'MarketAnalysisLayer'),
        ('signal_generation_layer', 'SignalGenerationLayer'),
        ('ai_ml_layer', 'AIMLLayer'),
        ('risk_management_layer', 'RiskManagementLayer'),
        ('execution_layer', 'ExecutionLayer'),
        ('sentiment_layer', 'SentimentLayer'),
        ('onchain_layer', 'OnChainLayer'),
        ('portfolio_layer', 'PortfolioLayer'),
        ('backtesting_layer', 'BacktestingLayer'),
        ('trade_persistence', 'PersistenceManager')
    ]
    
    all_ok = True
    for module, class_name in layers:
        try:
            mod = __import__(module)
            getattr(mod, class_name)
            print(f"  ✅ {class_name}")
        except Exception as e:
            print(f"  ❌ {class_name} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def check_data_directories():
    """Check data directories"""
    check_section("CHECKING DATA DIRECTORIES")
    
    directories = ['data', 'archive/old_bots', 'archive/old_systems']
    
    all_ok = True
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ⚠️  {directory}/ - Creating...")
            path.mkdir(parents=True, exist_ok=True)
            all_ok = False
    
    return all_ok

def run_quick_test():
    """Run a quick functionality test"""
    check_section("RUNNING QUICK TEST")
    
    try:
        from market_analysis_layer import MarketAnalysisLayer
        from signal_generation_layer import SignalGenerationLayer
        
        # Generate test data
        import numpy as np
        ohlcv = [[i, 100+i, 102+i, 98+i, 101+i, 1000] for i in range(100)]
        
        # Test analysis
        analysis = MarketAnalysisLayer()
        result = analysis.analyze_comprehensive(ohlcv)
        
        if 'trend' in result:
            print("  ✅ Market analysis working")
        else:
            print("  ❌ Market analysis failed")
            return False
        
        # Test signal generation
        signal_gen = SignalGenerationLayer()
        signal = signal_gen.generate_unified_signal(result)
        
        if 'signal' in signal:
            print("  ✅ Signal generation working")
        else:
            print("  ❌ Signal generation failed")
            return False
        
        print("  ✅ Quick test passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Quick test failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("="*60)
    print("🔍 APEX V3 SYSTEM VERIFICATION")
    print("="*60)
    
    results = {
        'Files': check_files(),
        'Dependencies': check_dependencies(),
        'Credentials': check_credentials(),
        'Layer Imports': check_imports(),
        'Data Directories': check_data_directories(),
        'Quick Test': run_quick_test()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check}")
    
    print(f"\n  Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ SYSTEM READY")
        print("\nTo start the system:")
        print("  python3 apex_v3_integrated.py")
        return 0
    else:
        print("\n⚠️  ISSUES FOUND - Review errors above")
        if not results['Credentials']:
            print("\n📄 Next step: Update .env file with your credentials")
            print("   See: USER_ACTION_REQUIRED.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())
