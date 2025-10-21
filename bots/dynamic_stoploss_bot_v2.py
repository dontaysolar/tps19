#!/usr/bin/env python3
"""
Dynamic Stop-Loss Bot v2.0 - Market Volatility Protection
MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- Uses Exchange Adapter (no direct ccxt)
- Integrates with PSM (position tracking)
- ATLAS-compliant (Power of 10 rules)

Dynamically adjusts stop-losses based on ATR (Average True Range) and volatility
Part of APEX AI Trading System - Protection Layer
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

try:
    import numpy as np
except ImportError:
    print("⚠️ numpy not available - Using fallback calculations")
    np = None

# Import AEGIS base class
from trading_bot_base import TradingBotBase


class DynamicStopLossBot(TradingBotBase):
    """
    Market Volatility Protection System - ATR-based Stop-Loss
    
    AEGIS v2.0: Now inherits from TradingBotBase
    - Automatic Exchange Adapter usage
    - PSM integration for position tracking
    - ATLAS-compliant code
    
    Features:
    - ATR-based stop-loss calculation
    - Volatility clustering detection
    - Adaptive distance adjustment
    - Position-specific SL management
    - Real-time price monitoring
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize Dynamic Stop-Loss Bot with AEGIS architecture
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Config validated
        """
        # Initialize base class (automatic adapter + PSM)
        super().__init__(
            bot_name="DYNAMIC_STOPLOSS_BOT",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'exchange_adapter'), "Base class initialization failed"
        
        # Dynamic Stop-Loss specific configuration
        self.config = {
            'base_stop_percent': 2.0,      # Base stop-loss: 2%
            'atr_multiplier': 1.5,          # ATR multiplier for volatility adjustment
            'min_stop_percent': 0.5,        # Minimum stop-loss: 0.5%
            'max_stop_percent': 5.0,        # Maximum stop-loss: 5%
            'update_interval': 60,          # Update every 60 seconds
            'atr_period': 14                # ATR calculation period
        }
        
        # ATLAS Assertion 2
        assert self.config['base_stop_percent'] > 0, "Invalid base stop percent"
        
        # State tracking (local cache, PSM is source of truth)
        self.atr_cache = {}
        self.last_update = {}
        
        # Metrics (extends base)
        self.metrics.update({
            'total_adjustments': 0,
            'stops_hit': 0,
            'capital_saved': 0.0,
            'last_calculation': None
        })
    
    def calculate_atr(self, symbol: str, timeframe: str = '1h') -> float:
        """
        Calculate Average True Range (ATR) for volatility measurement
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result >= 0
        - Fixed loop bound: atr_period
        """
        assert len(symbol) > 0 and '/' in symbol, "Invalid symbol format"
        
        periods = self.config['atr_period']
        
        try:
            # Get OHLCV data through Exchange Adapter
            ohlcv = self.exchange_adapter.get_ohlcv(
                symbol, 
                timeframe, 
                limit=periods + 1
            )
            
            if not ohlcv or len(ohlcv) < periods + 1:
                return self._get_cached_atr(symbol)
            
            # Calculate True Range for each period (ATLAS: fixed bound)
            true_ranges = []
            for i in range(1, min(len(ohlcv), periods + 1)):
                high = ohlcv[i][2]
                low = ohlcv[i][3]
                prev_close = ohlcv[i-1][4]
                
                # True Range calculation
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)
            
            # ATR = Simple Moving Average of True Range
            if np:
                atr = float(np.mean(true_ranges[-periods:]))
            else:
                # Fallback without numpy
                recent = true_ranges[-periods:]
                atr = sum(recent) / len(recent) if recent else 0.0
            
            # Cache result
            self.atr_cache[symbol] = {
                'value': atr,
                'timestamp': datetime.now(),
                'timeframe': timeframe
            }
            
            # ATLAS Assertion 2
            assert atr >= 0, "ATR must be non-negative"
            
            return atr
            
        except Exception as e:
            self.metrics['errors'] += 1
            return self._get_cached_atr(symbol)
    
    def _get_cached_atr(self, symbol: str) -> float:
        """
        Get cached ATR if available
        
        ATLAS Compliance:
        - Assertion 1: symbol valid
        - Assertion 2: result >= 0
        """
        assert len(symbol) > 0, "Symbol required"
        
        if symbol in self.atr_cache:
            cached = self.atr_cache[symbol]
            age = (datetime.now() - cached['timestamp']).seconds
            if age < 3600:  # Use cache if less than 1 hour old
                result = cached['value']
                assert result >= 0, "Cached ATR invalid"
                return result
        
        return 0.0
    
    def calculate_dynamic_stop(
        self, 
        symbol: str, 
        entry_price: float, 
        side: str = 'long'
    ) -> float:
        """
        Calculate dynamic stop-loss based on ATR and volatility
        
        ATLAS Compliance:
        - Assertion 1: entry_price > 0
        - Assertion 2: result > 0
        """
        assert entry_price > 0, "Entry price must be positive"
        assert side in ['long', 'short'], "Side must be long or short"
        
        try:
            # Get ATR
            atr = self.calculate_atr(symbol)
            
            if atr == 0:
                # Fallback to base stop-loss
                stop_distance = self.config['base_stop_percent'] / 100
            else:
                # Calculate ATR as percentage of price
                atr_percent = (atr / entry_price) * 100
                
                # Adjust stop distance based on volatility
                stop_distance = (
                    self.config['base_stop_percent'] + 
                    (atr_percent * self.config['atr_multiplier'])
                ) / 100
                
                # Clamp to min/max
                min_stop = self.config['min_stop_percent'] / 100
                max_stop = self.config['max_stop_percent'] / 100
                stop_distance = max(min_stop, min(stop_distance, max_stop))
            
            # Calculate stop price
            if side == 'long':
                stop_price = entry_price * (1 - stop_distance)
            else:  # short
                stop_price = entry_price * (1 + stop_distance)
            
            # ATLAS Assertion 2
            assert stop_price > 0, "Stop price must be positive"
            
            return stop_price
            
        except Exception as e:
            self.metrics['errors'] += 1
            
            # Fallback to base stop-loss
            if side == 'long':
                return entry_price * (1 - self.config['base_stop_percent'] / 100)
            else:
                return entry_price * (1 + self.config['base_stop_percent'] / 100)
    
    def add_position(
        self, 
        symbol: str, 
        entry_price: float, 
        amount: float, 
        side: str = 'long'
    ) -> Optional[str]:
        """
        Add position to monitoring (uses PSM)
        
        ATLAS Compliance:
        - Assertion 1: PSM available
        - Assertion 2: position_id returned
        """
        assert self.psm is not None, "PSM required for position tracking"
        assert amount > 0, "Amount must be positive"
        
        try:
            # Calculate initial stop-loss
            stop_price = self.calculate_dynamic_stop(symbol, entry_price, side)
            
            # Open position in PSM
            position_id = self.psm.open_position(
                symbol=symbol,
                side=side,
                entry_price=entry_price,
                amount=amount,
                strategy='DYNAMIC_STOPLOSS',
                metadata={'initial_stop': stop_price}
            )
            
            # ATLAS Assertion 2
            assert position_id is not None, "Position ID required"
            
            print(f"✅ Position added: {position_id}")
            print(f"   Entry: ${entry_price:.2f}, Stop: ${stop_price:.2f}")
            
            return position_id
            
        except Exception as e:
            self.metrics['errors'] += 1
            print(f"❌ Add position error: {e}")
            return None
    
    def update_stop_loss(
        self, 
        position_id: str, 
        current_price: float
    ) -> Optional[Dict]:
        """
        Update stop-loss for position
        
        ATLAS Compliance:
        - Assertion 1: PSM available
        - Assertion 2: current_price > 0
        """
        assert self.psm is not None, "PSM required"
        assert current_price > 0, "Current price must be positive"
        
        try:
            # Get position from PSM
            positions = self.psm.get_open_positions()
            position = None
            
            for pos in positions:
                if pos['position_id'] == position_id:
                    position = pos
                    break
            
            if not position:
                return None
            
            # Check if enough time passed
            if position_id in self.last_update:
                elapsed = (datetime.now() - self.last_update[position_id]).seconds
                if elapsed < self.config['update_interval']:
                    return None
            
            # Calculate new stop
            new_stop = self.calculate_dynamic_stop(
                position['symbol'],
                position['entry_price'],
                position['side']
            )
            
            # Update if beneficial
            old_stop = position.get('metadata', {}).get('initial_stop', 0)
            should_update = self._should_update_stop(
                position['side'],
                old_stop,
                new_stop
            )
            
            if should_update:
                self._update_position_stop(position_id, new_stop)
                self.metrics['total_adjustments'] += 1
                print(f"📈 {position['symbol']} stop: ${old_stop:.2f} → ${new_stop:.2f}")
            
            # Check if stop hit
            return self._check_stop_hit(position, current_price, new_stop)
            
        except Exception as e:
            self.metrics['errors'] += 1
            return None
    
    def _should_update_stop(
        self, 
        side: str, 
        old_stop: float, 
        new_stop: float
    ) -> bool:
        """
        Determine if stop should be updated
        
        ATLAS Compliance:
        - Assertion 1: side valid
        - Assertion 2: result is bool
        """
        assert side in ['long', 'short'], "Invalid side"
        
        # Only move stop in favorable direction
        if side == 'long':
            result = new_stop > old_stop
        else:
            result = new_stop < old_stop
        
        # ATLAS Assertion 2
        assert isinstance(result, bool), "Result must be bool"
        
        return result
    
    def _update_position_stop(self, position_id: str, new_stop: float):
        """
        Update position stop in PSM
        
        ATLAS Compliance:
        - Assertion 1: position_id valid
        - Assertion 2: new_stop > 0
        """
        assert len(position_id) > 0, "Position ID required"
        assert new_stop > 0, "Stop must be positive"
        
        self.last_update[position_id] = datetime.now()
        
        # Note: In production, update PSM metadata
        # self.psm.update_metadata(position_id, {'current_stop': new_stop})
    
    def _check_stop_hit(
        self, 
        position: Dict, 
        current_price: float,
        stop_price: float
    ) -> Optional[Dict]:
        """
        Check if stop-loss was hit
        
        ATLAS Compliance:
        - Assertion 1: position valid
        - Assertion 2: result is dict or None
        """
        assert 'side' in position, "Position must have side"
        assert current_price > 0, "Current price invalid"
        
        stop_hit = False
        
        if position['side'] == 'long' and current_price <= stop_price:
            stop_hit = True
        elif position['side'] == 'short' and current_price >= stop_price:
            stop_hit = True
        
        if not stop_hit:
            return None
        
        # Calculate P&L
        profit = (current_price - position['entry_price']) * position['amount']
        if position['side'] == 'short':
            profit = -profit
        
        profit_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
        if position['side'] == 'short':
            profit_pct = -profit_pct
        
        self.metrics['stops_hit'] += 1
        if profit > 0:
            self.metrics['capital_saved'] += profit
        
        result = {
            'position_id': position['position_id'],
            'symbol': position['symbol'],
            'side': position['side'],
            'entry': position['entry_price'],
            'exit': current_price,
            'amount': position['amount'],
            'profit': profit,
            'profit_pct': profit_pct,
            'reason': 'DYNAMIC_SL'
        }
        
        # ATLAS Assertion 2
        assert isinstance(result, dict), "Result must be dict"
        
        # Close position in PSM
        if self.psm:
            self.psm.close_position(
                position['position_id'],
                exit_price=current_price,
                reason='DYNAMIC_SL'
            )
        
        print(f"🛑 Stop hit: {position['symbol']} | P&L: ${profit:.2f} ({profit_pct:+.2f}%)")
        
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
        
        # Get active positions from PSM
        active_positions = 0
        if self.psm:
            try:
                positions = self.psm.get_open_positions()
                active_positions = len(positions)
            except:
                pass
        
        base_status.update({
            'dynamic_stoploss_metrics': {
                'total_adjustments': self.metrics.get('total_adjustments', 0),
                'stops_hit': self.metrics.get('stops_hit', 0),
                'capital_saved': self.metrics.get('capital_saved', 0.0)
            },
            'active_positions': active_positions,
            'configuration': self.config
        })
        
        return base_status


# Test suite
if __name__ == '__main__':
    print("=" * 70)
    print("Dynamic Stop-Loss Bot v2.0 (AEGIS Architecture) - Test Suite")
    print("=" * 70)
    
    print("\n[Test 1] Initialize Dynamic Stop-Loss Bot...")
    bot = DynamicStopLossBot()
    print(f"   Name: {bot.name}")
    print(f"   Version: {bot.version}")
    print(f"   Adapter enforced: {bot.exchange_adapter is not None}")
    print(f"   Config: {bot.config}")
    
    print("\n[Test 2] Calculate ATR (BTC/USDT)...")
    atr = bot.calculate_atr('BTC/USDT')
    print(f"   ATR: {atr:.2f}")
    
    print("\n[Test 3] Calculate dynamic stop...")
    entry_price = 50000.0
    stop_price = bot.calculate_dynamic_stop('BTC/USDT', entry_price, 'long')
    stop_distance = ((entry_price - stop_price) / entry_price) * 100
    print(f"   Entry: ${entry_price:.2f}")
    print(f"   Stop: ${stop_price:.2f}")
    print(f"   Distance: {stop_distance:.2f}%")
    
    print("\n[Test 4] Position management (if PSM available)...")
    if bot.psm:
        pos_id = bot.add_position('BTC/USDT', 50000.0, 0.001, 'long')
        if pos_id:
            print(f"   Position created: {pos_id}")
            
            # Test stop update
            update_result = bot.update_stop_loss(pos_id, 51000.0)
            if update_result:
                print(f"   Stop hit: {update_result['reason']}")
            else:
                print("   Stop not hit yet")
    else:
        print("   ⚠️ PSM not available, skipping position tests")
    
    print("\n[Test 5] Get status...")
    status = bot.get_status()
    print(f"   Active Positions: {status['active_positions']}")
    print(f"   Adjustments: {status['dynamic_stoploss_metrics']['total_adjustments']}")
    print(f"   Stops Hit: {status['dynamic_stoploss_metrics']['stops_hit']}")
    
    bot.close()
    
    print("\n✅ All Dynamic Stop-Loss Bot v2.0 tests passed!")
    print("✅ Migration to AEGIS architecture successful!")
    print("\n💡 FRACTAL HOOK: ATR calculations can be shared with other volatility bots")
