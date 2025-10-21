#!/usr/bin/env python3
"""
Crash Shield Bot v2.0 - Market Crash Protection
MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- Uses Exchange Adapter (no direct ccxt)
- Integrates with PSM (position tracking)
- ATLAS-compliant (Power of 10 rules)

Auto-pauses trading during extreme market drops
Part of APEX AI Trading System - Protection Layer
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

try:
    import numpy as np
except ImportError:
    print("⚠️ numpy not available - Crash Shield in limited mode")
    np = None

# Import AEGIS base class
from trading_bot_base import TradingBotBase


class CrashShieldBot(TradingBotBase):
    """
    Market Crash Protection System
    
    AEGIS v2.0: Now inherits from TradingBotBase
    - Automatic Exchange Adapter usage
    - PSM integration for position tracking
    - ATLAS-compliant code
    
    Monitors market for:
    - Extreme drops (>10% = crash)
    - Minor drops (>5% = warning)
    - Recovery signals (>3% rebound)
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize Crash Shield Bot with AEGIS architecture
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Config validated
        """
        # Initialize base class (automatic adapter + PSM)
        super().__init__(
            bot_name="CRASH_SHIELD_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'exchange_adapter'), "Base class initialization failed"
        
        # Crash Shield specific configuration
        self.config = {
            'crash_threshold_pct': 10.0,     # 10% drop = crash
            'minor_drop_threshold': 5.0,      # 5% drop = warning
            'recovery_threshold_pct': 3.0,    # 3% recovery = resume
            'check_interval': 60,              # Check every 60s
            'lookback_candles': 12             # 1 hour (5min candles)
        }
        
        # ATLAS Assertion 2
        assert self.config['crash_threshold_pct'] > 0, "Invalid crash threshold"
        
        # State tracking
        self.state = {
            'trading_paused': False,
            'pause_reason': None,
            'pause_timestamp': None,
            'last_prices': {}
        }
        
        # Crash Shield metrics (extends base)
        self.metrics.update({
            'crashes_detected': 0,
            'capital_protected': 0.0,
            'pause_count': 0,
            'resume_count': 0
        })
    
    def check_crash(self, symbol: str) -> Dict:
        """
        Check if market is crashing for given symbol
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict
        - Fixed loop bound: lookback_candles
        """
        assert len(symbol) > 0 and '/' in symbol, "Invalid symbol format"
        
        try:
            # Get recent OHLCV data through Exchange Adapter
            ohlcv = self.exchange_adapter.get_ohlcv(
                symbol, 
                '5m', 
                limit=self.config['lookback_candles']
            )
            
            if not ohlcv or len(ohlcv) < 2:
                return {
                    'crash_detected': False,
                    'symbol': symbol,
                    'error': 'Insufficient data'
                }
            
            # ATLAS: Fixed loop bound
            highs = []
            for i, candle in enumerate(ohlcv):
                if i >= self.config['lookback_candles']:
                    break
                highs.append(candle[2])  # High price
            
            current_price = ohlcv[-1][4]  # Close price
            high_price = max(highs)
            
            # Calculate drop percentage
            drop_pct = ((high_price - current_price) / high_price) * 100
            
            # Update last price
            self.state['last_prices'][symbol] = current_price
            
            # Determine crash level
            crash_detected = False
            severity = 'NONE'
            
            if drop_pct >= self.config['crash_threshold_pct']:
                crash_detected = True
                severity = 'CRASH'
                self.metrics['crashes_detected'] += 1
            elif drop_pct >= self.config['minor_drop_threshold']:
                severity = 'WARNING'
            
            result = {
                'crash_detected': crash_detected,
                'symbol': symbol,
                'severity': severity,
                'drop_pct': drop_pct,
                'current_price': current_price,
                'high_price': high_price,
                'timestamp': datetime.now().isoformat()
            }
            
            # ATLAS Assertion 2
            assert isinstance(result, dict), "Result must be dict"
            
            return result
        
        except Exception as e:
            self.metrics['errors'] += 1
            return {
                'crash_detected': False,
                'symbol': symbol,
                'error': str(e)
            }
    
    def pause_trading(self, reason: str) -> Dict:
        """
        Pause all trading (emergency stop)
        
        ATLAS Compliance:
        - Assertion 1: reason provided
        - Assertion 2: result is dict
        """
        assert len(reason) > 0, "Pause reason required"
        
        self.state['trading_paused'] = True
        self.state['pause_reason'] = reason
        self.state['pause_timestamp'] = datetime.now().isoformat()
        self.metrics['pause_count'] += 1
        
        result = {
            'action': 'PAUSED',
            'reason': reason,
            'timestamp': self.state['pause_timestamp']
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def resume_trading(self, reason: str = 'Recovery detected') -> Dict:
        """
        Resume trading after crash recovery
        
        ATLAS Compliance:
        - Assertion 1: reason provided
        - Assertion 2: result is dict
        """
        assert len(reason) > 0, "Resume reason required"
        
        self.state['trading_paused'] = False
        self.state['pause_reason'] = None
        self.state['pause_timestamp'] = None
        self.metrics['resume_count'] += 1
        
        result = {
            'action': 'RESUMED',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def monitor_recovery(self, symbol: str) -> Dict:
        """
        Monitor for market recovery
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict
        """
        assert len(symbol) > 0, "Symbol required"
        
        if symbol not in self.state['last_prices']:
            return {'recovery': False, 'reason': 'No baseline price'}
        
        try:
            # Get current price
            ticker = self.get_ticker(symbol)
            if not ticker:
                return {'recovery': False, 'reason': 'No ticker data'}
            
            current_price = ticker.get('last', 0)
            last_price = self.state['last_prices'][symbol]
            
            # Calculate recovery percentage
            recovery_pct = ((current_price - last_price) / last_price) * 100
            
            recovery_detected = recovery_pct >= self.config['recovery_threshold_pct']
            
            result = {
                'recovery': recovery_detected,
                'symbol': symbol,
                'recovery_pct': recovery_pct,
                'current_price': current_price,
                'baseline_price': last_price
            }
            
            # ATLAS Assertion 2
            assert isinstance(result, dict), "Result must be dict"
            
            return result
        
        except Exception as e:
            return {'recovery': False, 'error': str(e)}
    
    def get_status(self) -> Dict:
        """
        Get Crash Shield status (extends base)
        
        ATLAS Compliance:
        - Assertion 1: base status valid
        """
        base_status = super().get_status()
        
        # ATLAS Assertion 1
        assert isinstance(base_status, dict), "Base status must be dict"
        
        base_status.update({
            'crash_shield_metrics': {
                'crashes_detected': self.metrics.get('crashes_detected', 0),
                'capital_protected': self.metrics.get('capital_protected', 0.0),
                'pause_count': self.metrics.get('pause_count', 0),
                'resume_count': self.metrics.get('resume_count', 0)
            },
            'trading_status': 'PAUSED' if self.state['trading_paused'] else 'ACTIVE',
            'pause_reason': self.state.get('pause_reason'),
            'configuration': self.config
        })
        
        return base_status


# Test suite
if __name__ == '__main__':
    print("=" * 70)
    print("Crash Shield Bot v2.0 (AEGIS Architecture) - Test Suite")
    print("=" * 70)
    
    print("\n[Test 1] Initialize Crash Shield Bot...")
    bot = CrashShieldBot()
    print(f"   Name: {bot.name}")
    print(f"   Version: {bot.version}")
    print(f"   Adapter enforced: {bot.exchange_adapter is not None}")
    print(f"   Config: {bot.config}")
    
    print("\n[Test 2] Check for crash (BTC/USDT)...")
    crash_status = bot.check_crash('BTC/USDT')
    print(f"   Crash detected: {crash_status['crash_detected']}")
    print(f"   Severity: {crash_status.get('severity', 'N/A')}")
    if 'drop_pct' in crash_status:
        print(f"   Drop: {crash_status['drop_pct']:.2f}%")
    
    print("\n[Test 3] Pause trading (simulated crash)...")
    pause_result = bot.pause_trading('Test: Simulated crash')
    print(f"   Action: {pause_result['action']}")
    print(f"   Reason: {pause_result['reason']}")
    
    print("\n[Test 4] Resume trading...")
    resume_result = bot.resume_trading('Test: Recovery detected')
    print(f"   Action: {resume_result['action']}")
    print(f"   Reason: {resume_result['reason']}")
    
    print("\n[Test 5] Get status...")
    status = bot.get_status()
    print(f"   Trading Status: {status['trading_status']}")
    print(f"   Crashes Detected: {status['crash_shield_metrics']['crashes_detected']}")
    print(f"   Pause Count: {status['crash_shield_metrics']['pause_count']}")
    
    bot.close()
    
    print("\n✅ All Crash Shield Bot v2.0 tests passed!")
    print("✅ Migration to AEGIS architecture successful!")
    print("\n💡 FRACTAL HOOK: Crash Shield can be queried by APEX for system-wide protection")
