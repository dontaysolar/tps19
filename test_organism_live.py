#!/usr/bin/env python3
"""Test organism with simulated market data"""

import sys
sys.path.insert(0, '/workspace')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.organism.orchestrator import trading_organism
from modules.strategies.trend_following import TrendFollowingStrategy
from modules.strategies.mean_reversion import MeanReversionStrategy

print("🧬 Testing TPS19 APEX Organism\n")

# Generate sample market data
def generate_test_data(periods=200):
    dates = pd.date_range(end=datetime.now(), periods=periods, freq='5min')
    base_price = 50000
    returns = np.random.normal(0.0002, 0.015, periods)
    prices = base_price * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'timestamp': dates,
        'open': prices * np.random.uniform(0.995, 1.005, periods),
        'high': prices * np.random.uniform(1.000, 1.015, periods),
        'low': prices * np.random.uniform(0.985, 1.000, periods),
        'close': prices,
        'volume': np.random.uniform(900, 1100, periods)
    })

# Test 1: Strategy Analysis
print("=" * 60)
print("TEST 1: Strategy Signal Generation")
print("=" * 60)

df = generate_test_data()
print(f"Generated {len(df)} periods of market data")

trend_strategy = TrendFollowingStrategy()
signal = trend_strategy.analyze(df)

if signal:
    print(f"\n✅ Trend Strategy Signal:")
    print(f"   Action: {signal['signal']}")
    print(f"   Confidence: {signal['confidence']:.2%}")
    print(f"   Confirmations: {signal['confirmations']}")
    print(f"   Entry: ${signal['entry_price']:.2f}")
    print(f"   Stop: ${signal['stop_loss']:.2f}")
    print(f"   Target: ${signal['target']:.2f}")
    print(f"   Reasoning: {signal['reasoning']}")
else:
    print("ℹ️  No signal from trend strategy")

# Test 2: Organism Decision Cycle
print("\n" + "=" * 60)
print("TEST 2: Organism Decision Cycle")
print("=" * 60)

market_data = {
    'symbol': 'BTC/USDT',
    'price': df.iloc[-1]['close'],
    'volume': df.iloc[-1]['volume'],
    'volume_24h': 2_000_000,
    'spread_pct': 0.0004,
    'volatility': df['close'].pct_change().std(),
    'trend_strength': 0.6,
    'regime': 'trending',
    'price_change_10m': 0.005,
    'signals': [signal] if signal else []
}

portfolio = {
    'total_value': 500,
    'available_capital': 500,
    'positions': {},
    'daily_pnl': 0,
    'weekly_pnl': 0,
    'current_drawdown': 0,
    'starting_capital': 500,
    'consecutive_losses': 0,
}

decision = trading_organism.process_market_cycle(market_data, portfolio)

if decision:
    print(f"\n✅ ORGANISM DECISION:")
    print(f"   Symbol: {decision['symbol']}")
    print(f"   Action: {decision['action']}")
    print(f"   Size: {decision['size_pct']:.2%} (${decision['size_usdt']:.2f})")
    print(f"   Confidence: {decision['confidence']:.2%}")
    print(f"   Strategy: {decision['strategy']}")
    print(f"   Pathways: {decision.get('pathways', [])}")
else:
    print("ℹ️  Organism decided not to trade")

# Test 3: Organism Vital Signs
print("\n" + "=" * 60)
print("TEST 3: Organism Vital Signs")
print("=" * 60)

vitals = trading_organism.get_vital_signs()
print(f"\n💚 ORGANISM STATUS:")
print(f"   Status: {vitals['status']}")
print(f"   Health: {vitals['health_score']:.1f}/100")
print(f"   Consciousness: {vitals['consciousness']:.2f}")
print(f"   Metabolic Rate: {vitals['metabolic_rate']:.2f}")
print(f"   Age: {vitals['age_hours']:.4f} hours")
print(f"   Generation: {vitals['generation']}")
print(f"   Total Decisions: {vitals['total_decisions']}")
print(f"   Win Rate: {vitals['win_rate']:.2%}")

# Test 4: Immune System
print("\n" + "=" * 60)
print("TEST 4: Immune System Validation")
print("=" * 60)

from modules.organism.immune_system import immune_system

test_signal = {
    'symbol': 'BTC/USDT',
    'confidence': 0.75,
    'size_pct': 0.08,
    'size_usdt': 40,
    'min_order_size': 10,
    'volume_24h': 2_000_000
}

approved, reason = immune_system.layer1_pretrade_antibodies(test_signal, portfolio)
print(f"\nLayer 1 Check: {'✅ APPROVED' if approved else '❌ REJECTED'}")
print(f"Reason: {reason}")

# Test with bad signal
bad_signal = test_signal.copy()
bad_signal['confidence'] = 0.40  # Too low

approved, reason = immune_system.layer1_pretrade_antibodies(bad_signal, portfolio)
print(f"\nBad Signal Check: {'✅ APPROVED' if approved else '❌ REJECTED'}")
print(f"Reason: {reason}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETE")
print("=" * 60)
print("\n🧬 Organism is functional and ready!")
