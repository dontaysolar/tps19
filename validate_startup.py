#!/usr/bin/env python3
"""
TPS19 - STARTUP VALIDATION
Checks everything before system starts
"""

import os
import sys
from datetime import datetime

print("="*80)
print("🔍 TPS19 - STARTUP VALIDATION")
print("="*80)
print()

all_checks_passed = True

# =============================================================================
# CHECK 1: Python Environment
# =============================================================================
print("1️⃣ Python Environment")
print("-" * 60)

if sys.version_info < (3, 8):
    print("  ❌ Python 3.8+ required")
    print(f"     You have: {sys.version}")
    all_checks_passed = False
else:
    print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# =============================================================================
# CHECK 2: Required Files
# =============================================================================
print("\n2️⃣ Required Files")
print("-" * 60)

required_files = [
    'tps19_integrated.py',
    'websocket_layer.py',
    'advanced_orders.py',
    'paper_trading.py',
    'news_api_integration.py',
    'market_analysis_layer.py',
    'signal_generation_layer.py',
    'risk_management_layer.py',
    'execution_layer.py',
    'ai_ml_layer.py',
    'infrastructure_layer.py',
    'trade_persistence.py',
]

for file in required_files:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file} - MISSING")
        all_checks_passed = False

# =============================================================================
# CHECK 3: Dependencies
# =============================================================================
print("\n3️⃣ Python Dependencies")
print("-" * 60)

required_packages = {
    'ccxt': 'ccxt',
    'numpy': 'numpy',
    'requests': 'requests',
    'flask': 'flask',
    'flask_cors': 'flask-cors',
    'psutil': 'psutil',
}

for package, pip_name in required_packages.items():
    try:
        __import__(package)
        print(f"  ✅ {pip_name}")
    except ImportError:
        print(f"  ❌ {pip_name} - Run: pip3 install {pip_name}")
        all_checks_passed = False

# Check for optional packages
optional_packages = {
    'sklearn': 'scikit-learn',
    'pandas': 'pandas',
    'scipy': 'scipy',
}

print("\n   Optional packages:")
for package, pip_name in optional_packages.items():
    try:
        __import__(package)
        print(f"  ✅ {pip_name}")
    except ImportError:
        print(f"  ⚠️  {pip_name} (optional)")

# =============================================================================
# CHECK 4: Environment Variables
# =============================================================================
print("\n4️⃣ Environment Configuration")
print("-" * 60)

# Load .env
if os.path.exists('.env'):
    print("  ✅ .env file exists")
    with open('.env') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v
else:
    print("  ⚠️  .env file not found")

# Check critical variables
critical_vars = {
    'EXCHANGE_API_KEY': 'Exchange API Key',
    'EXCHANGE_API_SECRET': 'Exchange API Secret',
}

placeholder_values = ['YOUR_', 'your_', '']

for key, name in critical_vars.items():
    value = os.environ.get(key, '')
    
    if not value:
        print(f"  ⚠️  {name}: Not set")
    elif any(value.startswith(p) for p in placeholder_values):
        print(f"  ⚠️  {name}: Placeholder value")
    else:
        print(f"  ✅ {name}: Configured")

# Optional variables
optional_vars = {
    'TELEGRAM_BOT_TOKEN': 'Telegram Bot',
    'TELEGRAM_CHAT_ID': 'Telegram Chat ID',
    'NEWS_API_KEY': 'NewsAPI Key',
    'CRYPTOPANIC_API_KEY': 'CryptoPanic Key',
}

print("\n   Optional configuration:")
for key, name in optional_vars.items():
    value = os.environ.get(key, '')
    
    if value and not any(value.startswith(p) for p in placeholder_values):
        print(f"  ✅ {name}: Configured")
    else:
        print(f"  ⚪ {name}: Not configured (optional)")

# =============================================================================
# CHECK 5: Module Imports
# =============================================================================
print("\n5️⃣ Module Import Tests")
print("-" * 60)

modules_to_test = [
    ('tps19_integrated', 'TPS19Integrated'),
    ('websocket_layer', 'WebSocketLayer'),
    ('advanced_orders', 'AdvancedOrderManager'),
    ('paper_trading', 'PaperTradingEngine'),
    ('news_api_integration', 'NewsAPIIntegration'),
    ('market_analysis_layer', 'MarketAnalysisLayer'),
    ('signal_generation_layer', 'SignalGenerationLayer'),
]

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name)
        getattr(module, class_name)
        print(f"  ✅ {module_name}")
    except Exception as e:
        print(f"  ❌ {module_name}: {e}")
        all_checks_passed = False

# =============================================================================
# CHECK 6: Data Directories
# =============================================================================
print("\n6️⃣ Data Directories")
print("-" * 60)

data_dirs = ['data', 'logs']

for dir_name in data_dirs:
    if os.path.exists(dir_name):
        print(f"  ✅ {dir_name}/ exists")
    else:
        print(f"  ⚠️  {dir_name}/ not found - will be created")
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"     Created {dir_name}/")
        except Exception as e:
            print(f"     ❌ Could not create: {e}")
            all_checks_passed = False

# =============================================================================
# CHECK 7: Web Dashboard
# =============================================================================
print("\n7️⃣ Web Dashboard")
print("-" * 60)

if os.path.exists('web-dashboard'):
    print("  ✅ web-dashboard/ exists")
    
    if os.path.exists('web-dashboard/package.json'):
        print("  ✅ package.json exists")
    else:
        print("  ❌ package.json missing")
        all_checks_passed = False
    
    if os.path.exists('web-dashboard/node_modules'):
        print("  ✅ node_modules/ exists (dependencies installed)")
    else:
        print("  ⚠️  node_modules/ not found")
        print("     Run: cd web-dashboard && npm install")
else:
    print("  ❌ web-dashboard/ missing")
    all_checks_passed = False

# =============================================================================
# FINAL RESULT
# =============================================================================
print("\n" + "="*80)
print("📊 VALIDATION RESULTS")
print("="*80)

if all_checks_passed:
    print("✅ ALL CHECKS PASSED - SYSTEM READY")
    print()
    print("You can now run:")
    print("  python3 tps19_integrated.py paper")
    print("  ./quick_start_integrated.sh")
    print()
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED")
    print()
    print("Fix the issues above before starting the system.")
    print()
    print("Quick fix:")
    print("  pip3 install -r requirements.txt")
    print("  cd web-dashboard && npm install")
    print()
    sys.exit(1)
