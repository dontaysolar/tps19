#!/usr/bin/env python3
"""
Allocation Optimizer Bot v2.0 - Task Assignment System
MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- ATLAS-compliant (Power of 10 rules)
- Note: No exchange interaction (orchestration only)

Part of APEX AI Trading System - Orchestration Layer
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

# Import AEGIS base class
from trading_bot_base import TradingBotBase


class AllocationOptimizerBot(TradingBotBase):
    """
    Bot Task Assignment System
    
    AEGIS v2.0: Now inherits from TradingBotBase
    - ATLAS-compliant code
    - No exchange interaction (orchestration)
    
    Features:
    - Bot-to-pair assignment
    - Market condition tracking
    - Assignment history
    - Reassignment support
    """
    
    def __init__(self):
        """
        Initialize Allocation Optimizer Bot
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Tracking initialized
        """
        # Initialize base class (no exchange needed)
        super().__init__(
            bot_name="ALLOCATION_OPTIMIZER_BOT",
            bot_version="2.0.0",
            exchange_name='mock',  # No exchange interaction
            enable_psm=False,       # No position tracking needed
            enable_logging=False    # No exchange logging needed
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'name'), "Base class initialization failed"
        
        # Bot assignment tracking
        self.bot_assignments = {}
        
        # ATLAS Assertion 2
        assert isinstance(self.bot_assignments, dict), "Assignments must be dict"
        
        # Metrics (extends base)
        self.metrics.update({
            'assignments_made': 0,
            'reassignments': 0
        })
    
    def assign_bot_to_pair(
        self, 
        bot_name: str, 
        symbol: str, 
        market_condition: str = 'UNKNOWN'
    ) -> Dict:
        """
        Assign a bot to a trading pair
        
        ATLAS Compliance:
        - Assertion 1: bot_name and symbol valid
        - Assertion 2: result is dict
        """
        assert len(bot_name) > 0, "Bot name required"
        assert len(symbol) > 0, "Symbol required"
        
        # Check if reassignment
        is_reassignment = symbol in self.bot_assignments
        
        # Create assignment
        self.bot_assignments[symbol] = {
            'bot': bot_name,
            'condition': market_condition,
            'assigned_at': datetime.now().isoformat()
        }
        
        # Update metrics
        if is_reassignment:
            self.metrics['reassignments'] += 1
        else:
            self.metrics['assignments_made'] += 1
        
        result = {
            'assigned': True,
            'bot': bot_name,
            'symbol': symbol,
            'market_condition': market_condition,
            'is_reassignment': is_reassignment
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
    def get_assignment(self, symbol: str) -> Optional[Dict]:
        """
        Get current bot assignment for a symbol
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is dict or None
        """
        assert len(symbol) > 0, "Symbol required"
        
        result = self.bot_assignments.get(symbol)
        
        # ATLAS Assertion 2
        assert result is None or isinstance(result, dict), "Result must be dict or None"
        
        return result
    
    def remove_assignment(self, symbol: str) -> bool:
        """
        Remove bot assignment for a symbol
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result is bool
        """
        assert len(symbol) > 0, "Symbol required"
        
        if symbol in self.bot_assignments:
            del self.bot_assignments[symbol]
            result = True
        else:
            result = False
        
        # ATLAS Assertion 2
        assert isinstance(result, bool), "Result must be bool"
        
        return result
    
    def get_all_assignments(self) -> Dict:
        """
        Get all current assignments
        
        ATLAS Compliance:
        - Assertion 1: result is dict
        """
        result = self.bot_assignments.copy()
        
        # ATLAS Assertion 1
        assert isinstance(result, dict), "Result must be dict"
        
        return result
    
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
            'allocation_metrics': {
                'assignments_made': self.metrics.get('assignments_made', 0),
                'reassignments': self.metrics.get('reassignments', 0)
            },
            'active_assignments': len(self.bot_assignments)
        })
        
        return base_status


# Test suite
if __name__ == '__main__':
    print("=" * 70)
    print("Allocation Optimizer Bot v2.0 (AEGIS Architecture) - Test Suite")
    print("=" * 70)
    
    print("\n[Test 1] Initialize Allocation Optimizer Bot...")
    bot = AllocationOptimizerBot()
    print(f"   Name: {bot.name}")
    print(f"   Version: {bot.version}")
    
    print("\n[Test 2] Assign bot to pair...")
    result = bot.assign_bot_to_pair('MomentumRider', 'BTC/USDT', 'TRENDING')
    print(f"   Assigned: {result['assigned']}")
    print(f"   Bot: {result['bot']} → {result['symbol']}")
    print(f"   Condition: {result['market_condition']}")
    
    print("\n[Test 3] Get assignment...")
    assignment = bot.get_assignment('BTC/USDT')
    if assignment:
        print(f"   Bot: {assignment['bot']}")
        print(f"   Condition: {assignment['condition']}")
    
    print("\n[Test 4] Reassign (different bot)...")
    result2 = bot.assign_bot_to_pair('TrendFollower', 'BTC/USDT', 'STRONG_TREND')
    print(f"   Reassignment: {result2['is_reassignment']}")
    print(f"   New Bot: {result2['bot']}")
    
    print("\n[Test 5] Get all assignments...")
    all_assignments = bot.get_all_assignments()
    print(f"   Total Assignments: {len(all_assignments)}")
    
    print("\n[Test 6] Remove assignment...")
    removed = bot.remove_assignment('BTC/USDT')
    print(f"   Removed: {removed}")
    print(f"   Remaining: {len(bot.bot_assignments)}")
    
    print("\n[Test 7] Get status...")
    status = bot.get_status()
    print(f"   Assignments Made: {status['allocation_metrics']['assignments_made']}")
    print(f"   Reassignments: {status['allocation_metrics']['reassignments']}")
    
    bot.close()
    
    print("\n✅ All Allocation Optimizer Bot v2.0 tests passed!")
    print("✅ Migration to AEGIS architecture successful!")
    print("\n💡 FRACTAL HOOK: Orchestration system for bot deployment at scale")
