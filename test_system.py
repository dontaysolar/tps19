#!/usr/bin/env python3
"""Test TPS19 System Components"""

import sys
import os
try:
    from modules.utils.paths import get_base_dir
    modules_path = os.path.join(get_base_dir(), 'modules')
    if modules_path not in sys.path:
        sys.path.append(modules_path)
except Exception:
    pass

def test_modules():
    """Test all TPS19 modules"""
    results = {}
    
    try:
        from trading_engine import TradingEngine
        engine = TradingEngine()
        # perform single step to validate dependent imports
        engine.step("bitcoin", "BTC_USDT")
        results['trading_engine'] = "✅ PASS"
    except Exception as e:
        results['trading_engine'] = f"❌ FAIL: {e}"
        
    try:
        from simulation_engine import SimulationEngine
        sim = SimulationEngine()
        results['simulation_engine'] = "✅ PASS"
    except Exception as e:
        results['simulation_engine'] = f"❌ FAIL: {e}"
        
    try:
        from market_data import MarketData
        market = MarketData()
        results['market_data'] = "✅ PASS"
    except Exception as e:
        results['market_data'] = f"❌ FAIL: {e}"
        
    try:
        from risk_management import RiskManager
        risk = RiskManager()
        results['risk_management'] = "✅ PASS"
    except Exception as e:
        results['risk_management'] = f"❌ FAIL: {e}"
        
    try:
        from ai_council import AICouncil
        ai = AICouncil()
        results['ai_council'] = "✅ PASS"
    except Exception as e:
        results['ai_council'] = f"❌ FAIL: {e}"
        
    return results

if __name__ == "__main__":
    print("🧪 Testing TPS19 System Components...")
    print("=" * 40)
    
    results = test_modules()
    
    for module, status in results.items():
        print(f"{module}: {status}")
        
    passed = sum(1 for status in results.values() if "✅ PASS" in status)
    total = len(results)
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} modules passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    else:
        print("⚠️  Some systems need attention")
