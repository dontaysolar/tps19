#!/usr/bin/env python3
"""
Continuity Bot Unified v2.0 - AEGIS Consolidated Bot
Consolidates Continuity Bots 1-3 into single flexible bot

AEGIS v2.3 Enhancement: Bot Consolidation (NEW-1 Phase 2)
Replaces 3 separate Continuity Bots with 1 configurable bot

HOLD PERIODS:
- SHORT: 24 hours (profit target: 15%)
- MEDIUM: 48 hours (profit target: 20%)
- LONG: 72 hours (profit target: 25%)
- CUSTOM: User-defined hours and targets

PURPOSE:
Long-term position holder that maintains positions through market cycles.
Resists short-term volatility to capture larger moves.

USAGE:
    # Create bot with specific hold period
    bot = ContinuityBotUnified(hold_period='MEDIUM')
    
    # Or custom configuration
    bot = ContinuityBotUnified(hold_period='CUSTOM', 
                               min_hold_hours=36, 
                               profit_target=18.0)
    
    # Check if position should close
    should_close = bot.should_close_position(position, current_price)
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))
from trading_bot_base import TradingBotBase


class ContinuityBotUnified(TradingBotBase):
    """
    Unified Continuity Bot with configurable hold periods
    
    Consolidates functionality of Continuity Bots 1-3 into single flexible implementation.
    Uses hold_period parameter to switch between different time horizons.
    
    ATLAS Compliance:
    - Assertion 1: Hold period is valid
    - Assertion 2: Custom values are positive
    """
    
    VALID_PERIODS = ['SHORT', 'MEDIUM', 'LONG', 'CUSTOM']
    
    # Preset configurations
    PRESETS = {
        'SHORT': {'min_hold_hours': 24, 'profit_target': 15.0, 'max_loss': 10.0},
        'MEDIUM': {'min_hold_hours': 48, 'profit_target': 20.0, 'max_loss': 12.0},
        'LONG': {'min_hold_hours': 72, 'profit_target': 25.0, 'max_loss': 15.0}
    }
    
    def __init__(
        self, 
        hold_period: str = 'MEDIUM',
        min_hold_hours: Optional[float] = None,
        profit_target: Optional[float] = None,
        max_loss: Optional[float] = None,
        continuity_id: Optional[int] = None,
        exchange_config=None
    ):
        """
        Initialize Continuity Bot with specific hold period
        
        Args:
            hold_period: Time horizon (SHORT, MEDIUM, LONG, CUSTOM)
            min_hold_hours: Custom hold hours (only for CUSTOM mode)
            profit_target: Custom profit target % (only for CUSTOM mode)
            max_loss: Custom max loss % (only for CUSTOM mode)
            continuity_id: Optional legacy continuity ID for backward compatibility (1-3)
            exchange_config: Optional exchange configuration
        
        ATLAS Compliance:
        - Assertion 1: Hold period is valid
        - Assertion 2: Continuity ID if provided is 1-3
        """
        assert hold_period in self.VALID_PERIODS, f"Period must be one of {self.VALID_PERIODS}"
        assert continuity_id is None or (1 <= continuity_id <= 3), "Continuity ID must be 1-3 if provided"
        
        # Determine bot name
        if continuity_id:
            if continuity_id == 1:
                bot_name = "CONTINUITY_BOT"
            else:
                bot_name = f"CONTINUITY_BOT_{continuity_id}"
        else:
            bot_name = f"CONTINUITY_BOT_UNIFIED_{hold_period}"
        
        super().__init__(
            bot_name=bot_name,
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # Configuration
        self.hold_period = hold_period
        self.continuity_id = continuity_id
        
        # Load preset or custom config
        if hold_period == 'CUSTOM':
            assert min_hold_hours is not None and min_hold_hours > 0, "Custom hold_hours required"
            assert profit_target is not None and profit_target > 0, "Custom profit_target required"
            assert max_loss is None or max_loss > 0, "Max loss must be positive"
            
            self.config = {
                'min_hold_hours': min_hold_hours,
                'profit_target_pct': profit_target,
                'max_loss_pct': max_loss or 10.0
            }
        else:
            preset = self.PRESETS[hold_period]
            self.config = {
                'min_hold_hours': preset['min_hold_hours'],
                'profit_target_pct': preset['profit_target'],
                'max_loss_pct': preset['max_loss']
            }
        
        # Metrics
        self.metrics.update({
            'long_term_trades': 0,
            'avg_hold_hours': 0.0,
            'positions_held': 0,
            'hold_period': hold_period
        })
        
        print(f"✅ {bot_name} initialized (hold: {self.config['min_hold_hours']}h, target: {self.config['profit_target_pct']}%)")
    
    def should_close_position(self, position: Dict, current_price: float) -> Dict:
        """
        Determine if position should be closed based on hold period and targets
        
        Args:
            position: Position dict with entry_price and created_at
            current_price: Current market price
        
        Returns:
            Dict with should_close, hours_held, profit_pct, reason
        
        ATLAS Compliance:
        - Assertion 1: Position is valid dict
        - Assertion 2: Price is positive
        """
        assert isinstance(position, dict), "Position must be dict"
        assert 'entry_price' in position, "Position must have entry_price"
        assert 'created_at' in position or 'opened_at' in position, "Position must have timestamp"
        assert current_price > 0, "Price must be positive"
        
        # Get entry time (handle both PSM and legacy formats)
        timestamp = position.get('created_at') or position.get('opened_at')
        entry_time = datetime.fromisoformat(timestamp)
        
        # Calculate metrics
        hours_held = (datetime.now() - entry_time).total_seconds() / 3600
        entry_price = position['entry_price']
        profit_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Determine if should close
        hold_time_met = hours_held >= self.config['min_hold_hours']
        profit_target_met = profit_pct >= self.config['profit_target_pct']
        stop_loss_hit = profit_pct <= -self.config['max_loss_pct']
        
        should_close = hold_time_met and (profit_target_met or stop_loss_hit)
        
        # Determine reason
        if not hold_time_met:
            reason = f"Still holding ({hours_held:.1f}h / {self.config['min_hold_hours']}h)"
        elif profit_target_met:
            reason = f"Profit target reached ({profit_pct:.2f}% >= {self.config['profit_target_pct']}%)"
        elif stop_loss_hit:
            reason = f"Stop-loss hit ({profit_pct:.2f}% <= -{self.config['max_loss_pct']}%)"
        else:
            reason = f"Holding for target ({profit_pct:.2f}%)"
        
        result = {
            'should_close': should_close,
            'hours_held': hours_held,
            'profit_pct': profit_pct,
            'reason': reason,
            'hold_time_met': hold_time_met,
            'profit_target_met': profit_target_met,
            'stop_loss_hit': stop_loss_hit
        }
        
        assert isinstance(result, dict), "Result must be dict"
        return result
    
    def get_config(self) -> Dict:
        """
        Get current configuration
        
        Returns:
            Configuration dict with hold hours and targets
        """
        return {
            'hold_period': self.hold_period,
            'min_hold_hours': self.config['min_hold_hours'],
            'profit_target_pct': self.config['profit_target_pct'],
            'max_loss_pct': self.config['max_loss_pct']
        }
    
    def update_config(
        self, 
        min_hold_hours: Optional[float] = None,
        profit_target: Optional[float] = None,
        max_loss: Optional[float] = None
    ) -> Dict:
        """
        Update configuration dynamically
        
        Args:
            min_hold_hours: New minimum hold hours
            profit_target: New profit target %
            max_loss: New max loss %
        
        Returns:
            Updated configuration dict
        
        ATLAS Compliance:
        - Assertion 1: At least one parameter provided
        - Assertion 2: Values are positive
        """
        assert any([min_hold_hours, profit_target, max_loss]), "Provide at least one parameter"
        
        if min_hold_hours is not None:
            assert min_hold_hours > 0, "Hold hours must be positive"
            self.config['min_hold_hours'] = min_hold_hours
        
        if profit_target is not None:
            assert profit_target > 0, "Profit target must be positive"
            self.config['profit_target_pct'] = profit_target
        
        if max_loss is not None:
            assert max_loss > 0, "Max loss must be positive"
            self.config['max_loss_pct'] = max_loss
        
        # Update hold_period to CUSTOM
        self.hold_period = 'CUSTOM'
        self.metrics['hold_period'] = 'CUSTOM'
        
        print(f"✅ Config updated: {self.config['min_hold_hours']}h hold, {self.config['profit_target_pct']}% target")
        return self.get_config()


# Backward compatibility: Create instances for legacy Continuity Bots 1-3
def create_continuity_bot_1():
    """Legacy Continuity Bot 1 (24h SHORT)"""
    return ContinuityBotUnified(hold_period='SHORT', continuity_id=1)


def create_continuity_bot_2():
    """Legacy Continuity Bot 2 (48h MEDIUM)"""
    return ContinuityBotUnified(hold_period='MEDIUM', continuity_id=2)


def create_continuity_bot_3():
    """Legacy Continuity Bot 3 (72h LONG)"""
    return ContinuityBotUnified(hold_period='LONG', continuity_id=3)


# Self-test
if __name__ == '__main__':
    print("=" * 70)
    print("CONTINUITY BOT UNIFIED - SELF-TEST")
    print("=" * 70)
    print("")
    
    # Test 1: Create with each preset
    print("Test 1: Preset initialization")
    for period in ['SHORT', 'MEDIUM', 'LONG']:
        bot = ContinuityBotUnified(hold_period=period)
        config = bot.get_config()
        assert config['hold_period'] == period, f"Period mismatch"
        expected_hours = ContinuityBotUnified.PRESETS[period]['min_hold_hours']
        assert config['min_hold_hours'] == expected_hours, f"Hold hours mismatch"
        bot.close()
        print(f"✅ {period} mode: {config['min_hold_hours']}h hold, {config['profit_target_pct']}% target")
    print("")
    
    # Test 2: Custom configuration
    print("Test 2: Custom configuration")
    bot = ContinuityBotUnified(
        hold_period='CUSTOM',
        min_hold_hours=36,
        profit_target=18.0,
        max_loss=8.0
    )
    config = bot.get_config()
    assert config['min_hold_hours'] == 36, "Custom hours not set"
    assert config['profit_target_pct'] == 18.0, "Custom target not set"
    print(f"✅ Custom config works: {config}")
    bot.close()
    print("")
    
    # Test 3: Position evaluation
    print("Test 3: Position close decision")
    bot = ContinuityBotUnified(hold_period='SHORT')  # 24h, 15% target
    
    # Mock position (recent)
    from datetime import timedelta
    recent_time = (datetime.now() - timedelta(hours=12)).isoformat()
    position_recent = {
        'entry_price': 50000.0,
        'created_at': recent_time
    }
    
    result = bot.should_close_position(position_recent, 52500.0)  # +5% profit
    assert not result['should_close'], "Should not close yet (hold time not met)"
    assert result['profit_pct'] == 5.0, "Profit calc wrong"
    print(f"✅ Recent position (12h): {result['reason']}")
    
    # Mock position (old with profit)
    old_time = (datetime.now() - timedelta(hours=30)).isoformat()
    position_old = {
        'entry_price': 50000.0,
        'created_at': old_time
    }
    
    result = bot.should_close_position(position_old, 58000.0)  # +16% profit
    assert result['should_close'], "Should close (hold time met + profit target)"
    assert result['profit_target_met'], "Profit target should be met"
    print(f"✅ Old position (30h, +16%): {result['reason']}")
    
    bot.close()
    print("")
    
    # Test 4: Config update
    print("Test 4: Dynamic config update")
    bot = ContinuityBotUnified(hold_period='MEDIUM')
    original = bot.get_config()
    updated = bot.update_config(min_hold_hours=60, profit_target=22.0)
    assert updated['min_hold_hours'] == 60, "Update failed"
    assert updated['hold_period'] == 'CUSTOM', "Should switch to CUSTOM"
    print(f"✅ Config updated: {original['min_hold_hours']}h → {updated['min_hold_hours']}h")
    bot.close()
    print("")
    
    # Test 5: Legacy compatibility
    print("Test 5: Legacy bot creation")
    legacy_bots = [
        ('Continuity Bot 1', create_continuity_bot_1, 24),
        ('Continuity Bot 2', create_continuity_bot_2, 48),
        ('Continuity Bot 3', create_continuity_bot_3, 72)
    ]
    
    for name, creator, expected_hours in legacy_bots:
        bot = creator()
        config = bot.get_config()
        assert config['min_hold_hours'] == expected_hours, f"{name} hours mismatch"
        assert bot.continuity_id is not None, f"{name} missing continuity_id"
        bot.close()
        print(f"✅ {name} legacy compatibility confirmed ({expected_hours}h)")
    print("")
    
    print("=" * 70)
    print("✅ ALL SELF-TESTS PASSED")
    print("=" * 70)
    print("")
    print("CONSOLIDATION COMPLETE:")
    print("  Before: 3 separate Continuity Bot files")
    print("  After:  1 unified file with 3+ presets")
    print("  Reduction: 67% fewer files")
    print("  Backward Compatible: ✅ YES")
    print("  Custom Config: ✅ YES")
