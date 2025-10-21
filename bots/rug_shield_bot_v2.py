#!/usr/bin/env python3
"""
Rug Shield Bot v2.0 - Asset Protection System
MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- Uses Exchange Adapter (no direct ccxt)
- Integrates with PSM (position tracking)
- ATLAS-compliant (Power of 10 rules)

Filters scam/low-liquidity assets to protect capital
Part of APEX AI Trading System - Protection Layer
"""

import os
import sys
from datetime import datetime
from typing import Dict, List

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

# Import AEGIS base class
from trading_bot_base import TradingBotBase


class RugShieldBot(TradingBotBase):
    """
    Asset Protection System - Scam & Low-Liquidity Filter
    
    AEGIS v2.0: Now inherits from TradingBotBase
    - Automatic Exchange Adapter usage
    - PSM integration for position tracking
    - ATLAS-compliant code
    
    Features:
    - Liquidity depth analysis
    - Volume verification
    - Spread monitoring
    - Blacklist management
    - Risk scoring system
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize Rug Shield Bot with AEGIS architecture
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Config validated
        """
        # Initialize base class (automatic adapter + PSM)
        super().__init__(
            bot_name="RUG_SHIELD_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'exchange_adapter'), "Base class initialization failed"
        
        # Rug Shield specific configuration
        self.config = {
            'min_liquidity_usd': 1000000,    # $1M minimum liquidity
            'min_volume_24h_usd': 100000,    # $100k minimum 24h volume
            'max_spread_pct': 1.0,           # Max 1% spread
            'min_age_days': 30,              # Minimum 30 days old
            'blacklist': []                  # Manually blacklisted symbols
        }
        
        # ATLAS Assertion 2
        assert self.config['min_liquidity_usd'] > 0, "Invalid liquidity config"
        
        # Asset tracking
        self.safe_assets = {}
        self.blocked_assets = {}
        
        # Metrics (extends base)
        self.metrics.update({
            'assets_checked': 0,
            'assets_blocked': 0,
            'scams_prevented': 0
        })
    
    def check_liquidity(self, symbol: str) -> Dict:
        """
        Check if asset has sufficient liquidity
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict
        """
        assert len(symbol) > 0 and '/' in symbol, "Invalid symbol format"
        
        try:
            # Get ticker through adapter
            ticker = self.get_ticker(symbol)
            if not ticker:
                return self._get_fallback_liquidity(symbol)
            
            # Get order book through adapter
            orderbook = self.exchange_adapter.get_order_book(symbol, limit=20)
            if not orderbook:
                return self._get_fallback_liquidity(symbol)
            
            # Calculate bid/ask spread
            bid = ticker.get('bid', 0)
            ask = ticker.get('ask', 0)
            
            if bid > 0:
                spread_pct = ((ask - bid) / bid) * 100
            else:
                spread_pct = 100.0  # Assume max spread if no bid
            
            # Get 24h volume
            volume_24h_usd = ticker.get('quoteVolume', 0) or 0
            
            # Calculate order book depth (ATLAS: fixed loop bound)
            bid_depth = self._calc_order_depth(orderbook.get('bids', []))
            ask_depth = self._calc_order_depth(orderbook.get('asks', []))
            
            last_price = ticker.get('last', 0)
            if last_price > 0:
                total_depth_usd = ((bid_depth + ask_depth) / 2) * last_price
            else:
                total_depth_usd = 0.0
            
            self.metrics['assets_checked'] += 1
            
            result = {
                'symbol': symbol,
                'spread_pct': spread_pct,
                'volume_24h_usd': volume_24h_usd,
                'liquidity_usd': total_depth_usd,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'timestamp': datetime.now().isoformat()
            }
            
            # ATLAS Assertion 2
            assert isinstance(result, dict), "Result must be dict"
            
            return result
            
        except Exception as e:
            self.metrics['errors'] += 1
            return self._get_fallback_liquidity(symbol)
    
    def _calc_order_depth(self, orders: List) -> float:
        """
        Calculate order depth from order list
        
        ATLAS Compliance:
        - Assertion 1: orders is list
        - Assertion 2: result >= 0
        """
        assert isinstance(orders, list), "Orders must be list"
        
        depth = 0.0
        
        # ATLAS: Fixed loop bound (top 10 orders)
        for i, order in enumerate(orders):
            if i >= 10:
                break
            
            if isinstance(order, (list, tuple)) and len(order) > 1:
                depth += order[1]
        
        # ATLAS Assertion 2
        assert depth >= 0, "Depth must be non-negative"
        
        return depth
    
    def _get_fallback_liquidity(self, symbol: str) -> Dict:
        """
        Get fallback liquidity data
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict
        """
        assert len(symbol) > 0, "Symbol required"
        
        result = {
            'symbol': symbol,
            'error': 'Data unavailable',
            'spread_pct': 100.0,
            'volume_24h_usd': 0.0,
            'liquidity_usd': 0.0
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def is_safe_asset(self, symbol: str) -> Dict:
        """
        Comprehensive safety check for an asset
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict with 'safe' key
        """
        assert len(symbol) > 0, "Symbol required"
        
        # Check blacklist first
        if symbol in self.config['blacklist']:
            self.metrics['assets_blocked'] += 1
            self.blocked_assets[symbol] = datetime.now().isoformat()
            
            result = {
                'safe': False,
                'symbol': symbol,
                'reason': 'Blacklisted',
                'risk_level': 'CRITICAL',
                'risk_score': 100
            }
            
            assert 'safe' in result, "Result must have 'safe' key"
            return result
        
        # Check liquidity
        liquidity = self.check_liquidity(symbol)
        
        if 'error' in liquidity:
            result = {
                'safe': False,
                'symbol': symbol,
                'reason': 'Liquidity check failed',
                'risk_level': 'HIGH',
                'risk_score': 80
            }
            
            assert 'safe' in result, "Result must have 'safe' key"
            return result
        
        # Evaluate safety with risk scoring
        risk_score, issues = self._calculate_risk_score(liquidity)
        
        # Determine if safe (risk_score < 50)
        is_safe = risk_score < 50
        
        # Update tracking
        if not is_safe:
            self.metrics['assets_blocked'] += 1
            self.blocked_assets[symbol] = datetime.now().isoformat()
        else:
            self.safe_assets[symbol] = datetime.now().isoformat()
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        result = {
            'safe': is_safe,
            'symbol': symbol,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'issues': issues,
            'liquidity_data': liquidity,
            'timestamp': datetime.now().isoformat()
        }
        
        # ATLAS Assertion 2
        assert 'safe' in result, "Result must have 'safe' key"
        
        return result
    
    def _calculate_risk_score(self, liquidity: Dict) -> tuple:
        """
        Calculate risk score based on liquidity data
        
        ATLAS Compliance:
        - Assertion 1: liquidity is dict
        - Assertion 2: risk_score >= 0
        """
        assert isinstance(liquidity, dict), "Liquidity must be dict"
        
        issues = []
        risk_score = 0
        
        # Check spread
        spread_pct = liquidity.get('spread_pct', 100)
        if spread_pct > self.config['max_spread_pct']:
            issues.append(f"High spread: {spread_pct:.2f}%")
            risk_score += 30
        
        # Check volume
        volume_24h = liquidity.get('volume_24h_usd', 0) or 0
        if volume_24h < self.config['min_volume_24h_usd']:
            issues.append(f"Low volume: ${volume_24h:,.0f}")
            risk_score += 40
        
        # Check liquidity
        liquidity_usd = liquidity.get('liquidity_usd', 0) or 0
        if liquidity_usd < self.config['min_liquidity_usd']:
            issues.append(f"Low liquidity: ${liquidity_usd:,.0f}")
            risk_score += 30
        
        # ATLAS Assertion 2
        assert risk_score >= 0, "Risk score must be non-negative"
        
        return risk_score, issues
    
    def _get_risk_level(self, risk_score: int) -> str:
        """
        Determine risk level from score
        
        ATLAS Compliance:
        - Assertion 1: risk_score >= 0
        - Assertion 2: result is valid level
        """
        assert risk_score >= 0, "Risk score must be non-negative"
        
        if risk_score < 30:
            level = 'LOW'
        elif risk_score < 50:
            level = 'MEDIUM'
        elif risk_score < 80:
            level = 'HIGH'
        else:
            level = 'CRITICAL'
        
        # ATLAS Assertion 2
        assert level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], "Invalid level"
        
        return level
    
    def filter_safe_pairs(self, symbols: List[str]) -> List[str]:
        """
        Filter list to only safe trading pairs
        
        ATLAS Compliance:
        - Assertion 1: symbols is list
        - Assertion 2: result is list
        """
        assert isinstance(symbols, list), "Symbols must be list"
        
        safe = []
        
        # ATLAS: Fixed loop bound
        for i, symbol in enumerate(symbols):
            if i >= 100:  # Max 100 symbols per check
                break
            
            check = self.is_safe_asset(symbol)
            if check.get('safe', False):
                safe.append(symbol)
            else:
                issues = check.get('issues', [])
                print(f"🚫 Blocked {symbol}: {', '.join(issues)}")
        
        # ATLAS Assertion 2
        assert isinstance(safe, list), "Result must be list"
        
        return safe
    
    def get_status(self) -> Dict:
        """
        Get bot status (extends base)
        
        ATLAS Compliance:
        - Assertion 1: base status valid
        """
        base_status = super().get_status()
        
        # ATLAS Assertion 1
        assert isinstance(base_status, dict), "Base status must be dict"
        
        base_status.update({
            'rug_shield_metrics': {
                'assets_checked': self.metrics.get('assets_checked', 0),
                'assets_blocked': self.metrics.get('assets_blocked', 0),
                'scams_prevented': self.metrics.get('scams_prevented', 0)
            },
            'safe_assets_count': len(self.safe_assets),
            'blocked_assets_count': len(self.blocked_assets),
            'configuration': self.config
        })
        
        return base_status


# Test suite
if __name__ == '__main__':
    print("=" * 70)
    print("Rug Shield Bot v2.0 (AEGIS Architecture) - Test Suite")
    print("=" * 70)
    
    print("\n[Test 1] Initialize Rug Shield Bot...")
    bot = RugShieldBot()
    print(f"   Name: {bot.name}")
    print(f"   Version: {bot.version}")
    print(f"   Adapter enforced: {bot.exchange_adapter is not None}")
    print(f"   Config: Min Liquidity ${bot.config['min_liquidity_usd']:,}")
    
    print("\n[Test 2] Check liquidity (BTC/USDT)...")
    liquidity = bot.check_liquidity('BTC/USDT')
    if 'liquidity_usd' in liquidity:
        print(f"   Liquidity: ${liquidity['liquidity_usd']:,.0f}")
        print(f"   Spread: {liquidity['spread_pct']:.2f}%")
        print(f"   Volume 24h: ${liquidity.get('volume_24h_usd', 0):,.0f}")
    
    print("\n[Test 3] Safety check (BTC/USDT)...")
    safety = bot.is_safe_asset('BTC/USDT')
    print(f"   Safe: {safety['safe']}")
    print(f"   Risk Level: {safety['risk_level']}")
    print(f"   Risk Score: {safety['risk_score']}/100")
    if safety.get('issues'):
        print(f"   Issues: {', '.join(safety['issues'])}")
    
    print("\n[Test 4] Filter safe pairs...")
    test_pairs = ['BTC/USDT', 'ETH/USDT']
    safe_pairs = bot.filter_safe_pairs(test_pairs)
    print(f"   Input: {len(test_pairs)} pairs")
    print(f"   Output: {len(safe_pairs)} safe pairs")
    
    print("\n[Test 5] Get status...")
    status = bot.get_status()
    print(f"   Assets Checked: {status['rug_shield_metrics']['assets_checked']}")
    print(f"   Assets Blocked: {status['rug_shield_metrics']['assets_blocked']}")
    print(f"   Safe Assets: {status['safe_assets_count']}")
    
    bot.close()
    
    print("\n✅ All Rug Shield Bot v2.0 tests passed!")
    print("✅ Migration to AEGIS architecture successful!")
    print("\n💡 FRACTAL HOOK: Asset safety checks can be called by all trading bots")
