#!/usr/bin/env python3
"""
TPS19 COMPREHENSIVE TEST SUITE
Tests all 10 layers for functionality
"""

import sys
sys.path.insert(0, '.')

import numpy as np
from datetime import datetime

def generate_test_ohlcv(length=100):
    """Generate realistic test OHLCV data"""
    ohlcv = []
    price = 100
    for i in range(length):
        # Random walk
        change = np.random.normal(0, 2)
        price = max(price + change, 10)  # Don't go negative
        
        high = price + abs(np.random.normal(0, 1))
        low = price - abs(np.random.normal(0, 1))
        close = price + np.random.normal(0, 0.5)
        volume = abs(np.random.normal(1000, 200))
        
        ohlcv.append([i, price, high, low, close, volume])
    
    return ohlcv

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test(self, name, condition, error_msg=""):
        if condition:
            print(f"  ✅ {name}")
            self.passed += 1
        else:
            print(f"  ❌ {name}: {error_msg}")
            self.failed += 1
            self.errors.append(f"{name}: {error_msg}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY:")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print(f"  Total:  {self.passed + self.failed}")
        if self.failed > 0:
            print(f"\n❌ FAILURES:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")
        return self.failed == 0

def test_infrastructure_layer():
    """Test Infrastructure Layer"""
    print("\n🧪 Testing Infrastructure Layer...")
    results = TestResults()
    
    try:
        from infrastructure_layer import InfrastructureLayer
        layer = InfrastructureLayer()
        
        results.test("Layer instantiation", layer is not None)
        results.test("Has cache", hasattr(layer, 'cache'))
        results.test("Has logger", hasattr(layer, 'logger'))
        results.test("Has rate limiter", hasattr(layer, 'rate_limiter'))
        results.test("Has circuit breaker", hasattr(layer, 'circuit_breaker'))
        
        # Test cache
        layer.cache.set('test_key', 'test_value', ttl=60)
        cached = layer.cache.get('test_key')
        results.test("Cache works", cached == 'test_value')
        
        # Test rate limiter
        check = layer.rate_limiter.check()
        results.test("Rate limiter allows requests", check['allowed'])
        
        # Test circuit breaker
        cb_check = layer.circuit_breaker.check()
        results.test("Circuit breaker closed", cb_check['allowed'])
        
    except Exception as e:
        results.test("Infrastructure Layer", False, str(e))
    
    return results.passed, results.failed

def test_market_analysis_layer():
    """Test Market Analysis Layer"""
    print("\n🧪 Testing Market Analysis Layer...")
    results = TestResults()
    
    try:
        from market_analysis_layer import MarketAnalysisLayer
        layer = MarketAnalysisLayer()
        ohlcv = generate_test_ohlcv(100)
        
        results.test("Layer instantiation", layer is not None)
        
        # Run analysis
        analysis = layer.analyze_comprehensive(ohlcv)
        
        results.test("Analysis completed", 'error' not in analysis)
        results.test("Has trend data", 'trend' in analysis)
        results.test("Has momentum data", 'momentum' in analysis)
        results.test("Has volatility data", 'volatility' in analysis)
        results.test("Has volume data", 'volume' in analysis)
        results.test("Has support/resistance", 'support_resistance' in analysis)
        
        # Check trend analysis
        trend = analysis.get('trend', {})
        results.test("Trend has direction", 'direction' in trend)
        results.test("Trend direction valid", trend.get('direction') in 
                    ['STRONG_UPTREND', 'UPTREND', 'SIDEWAYS', 'DOWNTREND', 'STRONG_DOWNTREND'])
        
        # Check momentum
        momentum = analysis.get('momentum', {})
        results.test("Has RSI", 'rsi' in momentum)
        results.test("RSI in valid range", 0 <= momentum.get('rsi', 0) <= 100)
        
    except Exception as e:
        results.test("Market Analysis Layer", False, str(e))
    
    return results.passed, results.failed

def test_signal_generation_layer():
    """Test Signal Generation Layer"""
    print("\n🧪 Testing Signal Generation Layer...")
    results = TestResults()
    
    try:
        from signal_generation_layer import SignalGenerationLayer
        from market_analysis_layer import MarketAnalysisLayer
        
        signal_layer = SignalGenerationLayer()
        analysis_layer = MarketAnalysisLayer()
        
        ohlcv = generate_test_ohlcv(100)
        analysis = analysis_layer.analyze_comprehensive(ohlcv)
        
        results.test("Layer instantiation", signal_layer is not None)
        
        # Generate signal
        signal = signal_layer.generate_unified_signal(analysis)
        
        results.test("Signal generated", signal is not None)
        results.test("Has signal field", 'signal' in signal)
        results.test("Has confidence", 'confidence' in signal)
        results.test("Signal valid", signal.get('signal') in ['BUY', 'SELL', 'HOLD'])
        results.test("Confidence in range", 0 <= signal.get('confidence', 0) <= 1)
        results.test("Has strategies consulted", 'strategies_consulted' in signal)
        
    except Exception as e:
        results.test("Signal Generation Layer", False, str(e))
    
    return results.passed, results.failed

def test_risk_management_layer():
    """Test Risk Management Layer"""
    print("\n🧪 Testing Risk Management Layer...")
    results = TestResults()
    
    try:
        from risk_management_layer import RiskManagementLayer
        from market_analysis_layer import MarketAnalysisLayer
        
        risk_layer = RiskManagementLayer()
        analysis_layer = MarketAnalysisLayer()
        
        ohlcv = generate_test_ohlcv(100)
        analysis = analysis_layer.analyze_comprehensive(ohlcv)
        
        signal = {'signal': 'BUY', 'confidence': 0.75}
        
        results.test("Layer instantiation", risk_layer is not None)
        
        # Validate trade
        risk_check = risk_layer.validate_trade(signal, analysis, 'BTC/USDT')
        
        results.test("Risk check completed", risk_check is not None)
        results.test("Has approved field", 'approved' in risk_check)
        results.test("Has checks field", 'checks' in risk_check)
        
        if risk_check.get('approved'):
            results.test("Has position size", 'position_size' in risk_check)
            results.test("Has stop loss", 'stop_loss' in risk_check)
            results.test("Has take profit", 'take_profit' in risk_check)
        
    except Exception as e:
        results.test("Risk Management Layer", False, str(e))
    
    return results.passed, results.failed

def test_ai_ml_layer():
    """Test AI/ML Layer"""
    print("\n🧪 Testing AI/ML Layer...")
    results = TestResults()
    
    try:
        from ai_ml_layer import AIMLLayer
        
        layer = AIMLLayer()
        ohlcv = generate_test_ohlcv(100)
        
        results.test("Layer instantiation", layer is not None)
        results.test("Has models", hasattr(layer, 'models'))
        
        # Get predictions
        predictions = layer.predict_all(ohlcv)
        
        results.test("Predictions generated", predictions is not None)
        results.test("Has signal", 'signal' in predictions)
        results.test("Has confidence", 'confidence' in predictions)
        results.test("Signal valid", predictions.get('signal') in ['BUY', 'SELL', 'HOLD'])
        
    except Exception as e:
        results.test("AI/ML Layer", False, str(e))
    
    return results.passed, results.failed

def test_persistence():
    """Test Persistence Module"""
    print("\n🧪 Testing Persistence Module...")
    results = TestResults()
    
    try:
        from trade_persistence import PersistenceManager
        
        pm = PersistenceManager()
        
        results.test("Persistence instantiation", pm is not None)
        
        # Test trade logging
        trade_id = pm.log_trade({
            'symbol': 'BTC/USDT',
            'side': 'buy',
            'amount': 0.001,
            'price': 50000
        })
        results.test("Trade logged", trade_id is not None)
        
        # Test position saving
        pm.save_position({
            'symbol': 'ETH/USDT',
            'side': 'long',
            'amount': 0.01,
            'entry_price': 3000
        })
        
        # Test retrieval
        pos = pm.get_position('ETH/USDT')
        results.test("Position retrieved", pos is not None)
        results.test("Position symbol correct", pos.get('symbol') == 'ETH/USDT')
        
        # Test portfolio state
        state = pm.get_portfolio_state()
        results.test("Portfolio state retrieved", state is not None)
        results.test("Has total equity", 'total_equity' in state)
        
    except Exception as e:
        results.test("Persistence Module", False, str(e))
    
    return results.passed, results.failed

def test_system_integration():
    """Test full system integration"""
    print("\n🧪 Testing System Integration...")
    results = TestResults()
    
    try:
        # Test that all layers can work together
        from market_analysis_layer import MarketAnalysisLayer
        from signal_generation_layer import SignalGenerationLayer
        from risk_management_layer import RiskManagementLayer
        from ai_ml_layer import AIMLLayer
        
        ohlcv = generate_test_ohlcv(100)
        
        # Step 1: Analysis
        analysis_layer = MarketAnalysisLayer()
        analysis = analysis_layer.analyze_comprehensive(ohlcv)
        results.test("Analysis step", 'trend' in analysis)
        
        # Step 2: Technical Signal
        signal_layer = SignalGenerationLayer()
        tech_signal = signal_layer.generate_unified_signal(analysis)
        results.test("Signal generation step", 'signal' in tech_signal)
        
        # Step 3: AI Prediction
        ai_layer = AIMLLayer()
        ai_prediction = ai_layer.predict_all(ohlcv)
        results.test("AI prediction step", 'signal' in ai_prediction)
        
        # Step 4: Risk Validation
        risk_layer = RiskManagementLayer()
        risk_check = risk_layer.validate_trade(tech_signal, analysis, 'BTC/USDT')
        results.test("Risk validation step", 'approved' in risk_check)
        
        results.test("Full pipeline", True)
        
    except Exception as e:
        results.test("System Integration", False, str(e))
    
    return results.passed, results.failed

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 TPS19 COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Run all tests
    tests = [
        test_infrastructure_layer,
        test_market_analysis_layer,
        test_signal_generation_layer,
        test_risk_management_layer,
        test_ai_ml_layer,
        test_persistence,
        test_system_integration
    ]
    
    for test_func in tests:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 FINAL TEST RESULTS")
    print("="*60)
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  📊 Total:  {total_passed + total_failed}")
    print(f"  📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
    print("="*60)
    
    if total_failed == 0:
        print("\n✅ ALL TESTS PASSED - SYSTEM READY")
        return 0
    else:
        print(f"\n❌ {total_failed} TESTS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
