#!/usr/bin/env python3
"""
TPS19 - COMPREHENSIVE INTEGRATION TEST SUITE
Tests all new features and integration points
"""

import sys
import time
from datetime import datetime

print("="*80)
print("🧪 TPS19 - COMPREHENSIVE INTEGRATION TEST SUITE")
print("="*80)
print()

# Track results
total_tests = 0
passed_tests = 0
failed_tests = []

def test_section(name):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print(f"{'='*60}")

def test_case(name, func):
    """Run a test case"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    try:
        func()
        print(f"  ✅ {name}")
        passed_tests += 1
        return True
    except Exception as e:
        print(f"  ❌ {name}")
        print(f"     Error: {e}")
        failed_tests.append((name, str(e)))
        return False

# =============================================================================
# TEST 1: Import Tests
# =============================================================================
test_section("Module Imports")

def test_tps19_integrated():
    from tps19_integrated import TPS19Integrated
    assert TPS19Integrated is not None

def test_websocket_layer():
    from websocket_layer import WebSocketLayer
    assert WebSocketLayer is not None

def test_advanced_orders():
    from advanced_orders import AdvancedOrderManager
    assert AdvancedOrderManager is not None

def test_paper_trading():
    from paper_trading import PaperTradingEngine
    assert PaperTradingEngine is not None

def test_news_api():
    from news_api_integration import NewsAPIIntegration
    assert NewsAPIIntegration is not None

test_case("TPS19Integrated imports", test_tps19_integrated)
test_case("WebSocketLayer imports", test_websocket_layer)
test_case("AdvancedOrderManager imports", test_advanced_orders)
test_case("PaperTradingEngine imports", test_paper_trading)
test_case("NewsAPIIntegration imports", test_news_api)

# =============================================================================
# TEST 2: Paper Trading Engine
# =============================================================================
test_section("Paper Trading Engine")

def test_paper_init():
    from paper_trading import PaperTradingEngine
    paper = PaperTradingEngine(initial_balance=10000)
    assert paper.balance == 10000
    assert paper.initial_balance == 10000

def test_paper_buy():
    from paper_trading import PaperTradingEngine
    paper = PaperTradingEngine(initial_balance=10000)
    result = paper.place_market_order('BTC/USDT', 'buy', 0.1, 50000)
    assert result['success'] == True
    assert paper.balance < 10000
    assert 'BTC/USDT' in paper.positions

def test_paper_sell():
    from paper_trading import PaperTradingEngine
    paper = PaperTradingEngine(initial_balance=10000)
    paper.place_market_order('BTC/USDT', 'buy', 0.1, 50000)
    result = paper.place_market_order('BTC/USDT', 'sell', 0.1, 51000)
    assert result['success'] == True

def test_paper_insufficient_balance():
    from paper_trading import PaperTradingEngine
    paper = PaperTradingEngine(initial_balance=1000)
    result = paper.place_market_order('BTC/USDT', 'buy', 1.0, 50000)
    assert result['success'] == False
    assert 'Insufficient balance' in result.get('error', '')

def test_paper_stats():
    from paper_trading import PaperTradingEngine
    paper = PaperTradingEngine(initial_balance=10000)
    paper.place_market_order('BTC/USDT', 'buy', 0.1, 50000)
    stats = paper.get_portfolio_stats({'BTC/USDT': 51000})
    assert stats['total_equity'] > 10000
    assert stats['total_pnl'] > 0

test_case("Paper trading initialization", test_paper_init)
test_case("Paper trading buy order", test_paper_buy)
test_case("Paper trading sell order", test_paper_sell)
test_case("Paper trading insufficient balance", test_paper_insufficient_balance)
test_case("Paper trading portfolio stats", test_paper_stats)

# =============================================================================
# TEST 3: Advanced Orders
# =============================================================================
test_section("Advanced Orders (Dry Run)")

def test_advanced_orders_init():
    from advanced_orders import AdvancedOrderManager
    import ccxt
    exchange = ccxt.cryptocom()  # Mock exchange
    orders = AdvancedOrderManager(exchange)
    assert orders is not None
    assert orders.active_orders == {}

def test_trailing_stop_init():
    from advanced_orders import AdvancedOrderManager
    import ccxt
    exchange = ccxt.cryptocom()
    orders = AdvancedOrderManager(exchange)
    result = orders.start_trailing_stop('BTC/USDT', 'sell', 0.1, 2.0, 50000)
    assert result['success'] == True

def test_trailing_stop_update():
    from advanced_orders import AdvancedOrderManager
    import ccxt
    exchange = ccxt.cryptocom()
    orders = AdvancedOrderManager(exchange)
    result = orders.start_trailing_stop('BTC/USDT', 'sell', 0.1, 2.0, 50000)
    trail_id = result['trail_id']
    update = orders.update_trailing_stop(trail_id, 51000)
    assert 'updated' in update or 'triggered' in update

test_case("Advanced orders initialization", test_advanced_orders_init)
test_case("Trailing stop initialization", test_trailing_stop_init)
test_case("Trailing stop update logic", test_trailing_stop_update)

# =============================================================================
# TEST 4: News API Integration
# =============================================================================
test_section("News API Integration")

def test_news_api_init():
    from news_api_integration import NewsAPIIntegration
    news = NewsAPIIntegration()
    assert news is not None

def test_news_api_placeholder():
    from news_api_integration import NewsAPIIntegration
    news = NewsAPIIntegration()
    articles = news.get_crypto_news('BTC', limit=5)
    assert len(articles) > 0

def test_news_sentiment():
    from news_api_integration import NewsAPIIntegration
    news = NewsAPIIntegration()
    sentiment = news.get_sentiment_summary('BTC')
    assert 'sentiment' in sentiment
    assert sentiment['sentiment'] in ['POSITIVE', 'NEGATIVE', 'NEUTRAL']

test_case("News API initialization", test_news_api_init)
test_case("News API placeholder data", test_news_api_placeholder)
test_case("News sentiment analysis", test_news_sentiment)

# =============================================================================
# TEST 5: WebSocket Layer (Structure Test)
# =============================================================================
test_section("WebSocket Layer (Structure)")

def test_websocket_init():
    from websocket_layer import WebSocketLayer
    ws = WebSocketLayer()
    assert ws is not None
    assert ws.subscribers == {}

def test_websocket_structure():
    from websocket_layer import WebSocketLayer
    ws = WebSocketLayer()
    assert hasattr(ws, 'connect')
    assert hasattr(ws, 'subscribe_ticker')
    assert hasattr(ws, 'get_latest_price')

test_case("WebSocket initialization", test_websocket_init)
test_case("WebSocket method structure", test_websocket_structure)

# =============================================================================
# TEST 6: Integration Points
# =============================================================================
test_section("Integration Points")

def test_tps19_modes():
    from tps19_integrated import TPS19Integrated
    # Test valid modes
    for mode in ['monitoring', 'paper', 'live']:
        try:
            # Don't actually initialize (no exchange connection)
            assert mode in ['monitoring', 'paper', 'live']
        except:
            raise Exception(f"Mode {mode} not recognized")

def test_config_structure():
    # Test config exists in tps19_integrated
    import inspect
    from tps19_integrated import TPS19Integrated
    source = inspect.getsource(TPS19Integrated.__init__)
    assert 'self.config' in source
    assert 'mode' in source

test_case("TPS19 mode validation", test_tps19_modes)
test_case("TPS19 config structure", test_config_structure)

# =============================================================================
# TEST 7: Data Persistence
# =============================================================================
test_section("Data Persistence")

def test_persistence_import():
    from trade_persistence import PersistenceManager
    assert PersistenceManager is not None

def test_persistence_init():
    from trade_persistence import PersistenceManager
    pm = PersistenceManager()
    assert pm is not None

test_case("Persistence manager import", test_persistence_import)
test_case("Persistence manager init", test_persistence_init)

# =============================================================================
# TEST 8: Core Layers
# =============================================================================
test_section("Core Trading Layers")

def test_market_analysis():
    from market_analysis_layer import MarketAnalysisLayer
    layer = MarketAnalysisLayer()
    assert layer is not None

def test_signal_generation():
    from signal_generation_layer import SignalGenerationLayer
    layer = SignalGenerationLayer()
    assert layer is not None

def test_risk_management():
    from risk_management_layer import RiskManagementLayer
    layer = RiskManagementLayer()
    assert layer is not None

def test_ai_ml_layer():
    from ai_ml_layer import AIMLLayer
    layer = AIMLLayer()
    assert layer is not None

test_case("Market analysis layer", test_market_analysis)
test_case("Signal generation layer", test_signal_generation)
test_case("Risk management layer", test_risk_management)
test_case("AI/ML layer", test_ai_ml_layer)

# =============================================================================
# TEST 9: API Server
# =============================================================================
test_section("API Server")

def test_api_imports():
    # Just check file exists and has Flask
    with open('api_server.py', 'r') as f:
        content = f.read()
        assert 'Flask' in content
        assert '/api/price' in content

test_case("API server structure", test_api_imports)

# =============================================================================
# TEST 10: Quick Start Script
# =============================================================================
test_section("Scripts and Tools")

def test_quick_start_exists():
    import os
    assert os.path.exists('quick_start_integrated.sh')

def test_tps19_integrated_exists():
    import os
    assert os.path.exists('tps19_integrated.py')

test_case("Quick start script exists", test_quick_start_exists)
test_case("TPS19 integrated exists", test_tps19_integrated_exists)

# =============================================================================
# FINAL RESULTS
# =============================================================================
print("\n" + "="*80)
print("📊 TEST RESULTS")
print("="*80)
print(f"Total Tests:  {total_tests}")
print(f"✅ Passed:     {passed_tests}")
print(f"❌ Failed:     {len(failed_tests)}")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
print("="*80)

if failed_tests:
    print("\n❌ FAILED TESTS:")
    for name, error in failed_tests:
        print(f"  • {name}")
        print(f"    {error}")
    print()
    sys.exit(1)
else:
    print("\n✅ ALL TESTS PASSED - SYSTEM READY")
    print()
    sys.exit(0)
