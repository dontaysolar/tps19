#!/usr/bin/env python3
"""
Advanced Position Manager - Dynamic position management
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from modules.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Position:
    """Trading position"""
    id: str
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    current_price: float
    size: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    entry_volatility: float = 0.02
    unrealized_pnl: float = 0
    unrealized_pnl_pct: float = 0
    total_fees: float = 0
    scaled_out_once: bool = False
    strategy: str = ''


@dataclass
class Action:
    """Position management action"""
    action_type: str  # 'UPDATE_STOP', 'CLOSE', 'SCALE_OUT', 'HEDGE'
    value: Optional[float] = None
    reason: str = ''
    symbol: Optional[str] = None
    size: Optional[float] = None


class AdvancedPositionManager:
    """
    Dynamic position management with adaptive risk control
    """
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        
        # Configuration
        self.max_hold_hours = 120  # 5 days
        self.breakeven_fee_multiplier = 2
        self.profit_lock_threshold = 0.05  # Lock in 50% at 5% profit
        self.scale_out_threshold = 0.03  # Scale out at 3% profit
        
    def manage_position(self, position: Position, market_data: Dict) -> List[Action]:
        """
        Analyze position and generate management actions
        
        Args:
            position: Current position
            market_data: Current market state
            
        Returns:
            List of actions to take
        """
        actions = []
        
        # Update position metrics
        position.unrealized_pnl = (position.current_price - position.entry_price) * position.size
        position.unrealized_pnl_pct = (position.current_price - position.entry_price) / position.entry_price
        
        # 1. VOLATILITY-ADJUSTED STOPS
        current_vol = market_data.get('volatility', 0.02)
        if current_vol > position.entry_volatility * 1.5:
            # Volatility increased, tighten stop
            new_stop = self._calculate_atr_stop(position, current_vol, multiplier=1.5)
            if new_stop > position.stop_loss:  # Only tighten, never widen
                actions.append(Action(
                    'UPDATE_STOP',
                    new_stop,
                    f'Volatility increased to {current_vol:.4f}'
                ))
                logger.info(f"Tightening stop due to volatility: {new_stop}")
        
        # 2. TIME DECAY EXIT
        hours_held = (datetime.now() - position.entry_time).total_seconds() / 3600
        if hours_held > self.max_hold_hours:
            if position.unrealized_pnl_pct < 0.01:  # Less than 1% profit
                actions.append(Action(
                    'CLOSE',
                    reason=f'Held {hours_held:.1f}h with minimal profit'
                ))
                logger.info(f"Time decay exit for {position.symbol}")
        
        # 3. BREAKEVEN STOP (After Fee Recovery)
        fee_recovery_pct = position.total_fees * self.breakeven_fee_multiplier
        if position.unrealized_pnl_pct > fee_recovery_pct:
            breakeven_price = position.entry_price * 1.001  # Breakeven + 0.1%
            if position.stop_loss < breakeven_price:
                actions.append(Action(
                    'UPDATE_STOP',
                    breakeven_price,
                    'Moving stop to breakeven (fees recovered)'
                ))
                logger.info(f"Moving stop to breakeven for {position.symbol}")
        
        # 4. PROFIT PROTECTION (Lock in gains)
        if position.unrealized_pnl_pct > self.profit_lock_threshold:
            # Lock in 50% of gains
            lock_price = position.entry_price * (1 + position.unrealized_pnl_pct * 0.5)
            if lock_price > position.stop_loss:
                actions.append(Action(
                    'UPDATE_STOP',
                    lock_price,
                    f'Locking in 50% of {position.unrealized_pnl_pct:.2%} profit'
                ))
                logger.info(f"Profit protection activated for {position.symbol}")
        
        # 5. PARTIAL PROFIT TAKING
        if position.unrealized_pnl_pct > self.scale_out_threshold and not position.scaled_out_once:
            scale_size = position.size * 0.25  # Take 25% off
            actions.append(Action(
                'SCALE_OUT',
                scale_size,
                f'Taking partial profit at {position.unrealized_pnl_pct:.2%}'
            ))
            position.scaled_out_once = True
            logger.info(f"Scaling out 25% of {position.symbol}")
        
        # 6. TRAILING STOP (For profitable positions)
        if position.unrealized_pnl_pct > 0.02:  # 2%+ profit
            trailing_stop = self._calculate_trailing_stop(position, market_data)
            if trailing_stop > position.stop_loss:
                actions.append(Action(
                    'UPDATE_STOP',
                    trailing_stop,
                    'Trailing stop adjustment'
                ))
        
        # 7. EMERGENCY EXIT (Rapid adverse movement)
        if self._detect_adverse_movement(position, market_data):
            actions.append(Action(
                'CLOSE',
                reason='Rapid adverse price movement detected'
            ))
            logger.warning(f"Emergency exit triggered for {position.symbol}")
        
        # 8. CORRELATION HEDGING (Advanced)
        if position.symbol == 'BTC/USDT':
            hedge_action = self._check_correlation_hedge(position, market_data)
            if hedge_action:
                actions.append(hedge_action)
        
        return actions
    
    def _calculate_atr_stop(self, position: Position, volatility: float, 
                           multiplier: float = 2.0) -> float:
        """Calculate ATR-based stop loss"""
        atr = position.entry_price * volatility
        stop = position.entry_price - (atr * multiplier)
        return max(stop, position.entry_price * 0.98)  # Never worse than -2%
    
    def _calculate_trailing_stop(self, position: Position, market_data: Dict) -> float:
        """Calculate trailing stop price"""
        # Trail by 1% of current price
        trailing_distance = position.current_price * 0.01
        trailing_stop = position.current_price - trailing_distance
        
        return trailing_stop
    
    def _detect_adverse_movement(self, position: Position, market_data: Dict) -> bool:
        """Detect rapid adverse price movement"""
        # Check if price dropped >1% in last minute
        recent_change = market_data.get('price_change_1m', 0)
        
        if position.side == 'LONG' and recent_change < -0.01:  # -1% drop
            return True
        elif position.side == 'SHORT' and recent_change > 0.01:  # +1% spike
            return True
        
        return False
    
    def _check_correlation_hedge(self, position: Position, market_data: Dict) -> Optional[Action]:
        """
        Check if position needs correlation hedging
        
        Example: If BTC is dropping and correlation with ETH is high,
        consider hedging with ETH position
        """
        # Simplified logic - would use actual correlation calculation
        btc_dropping = market_data.get('price_change_5m', 0) < -0.02  # -2% in 5min
        correlation_high = market_data.get('btc_eth_correlation', 0) > 0.9
        
        if btc_dropping and correlation_high:
            # Suggest hedge
            hedge_size = position.size * 0.3  # 30% hedge
            return Action(
                'HEDGE',
                value=hedge_size,
                reason='High correlation, BTC dropping',
                symbol='ETH/USDT'
            )
        
        return None
    
    def add_position(self, position: Position):
        """Add new position to tracking"""
        self.positions[position.id] = position
        logger.info(f"Added position: {position.symbol} {position.side} @ {position.entry_price}")
    
    def remove_position(self, position_id: str):
        """Remove position (closed)"""
        if position_id in self.positions:
            position = self.positions.pop(position_id)
            self.closed_positions.append(position)
            logger.info(f"Closed position: {position.symbol} P&L: {position.unrealized_pnl:.2f}")
    
    def get_all_positions(self) -> List[Position]:
        """Get all active positions"""
        return list(self.positions.values())
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        if not self.positions:
            return {
                'total_positions': 0,
                'total_value': 0,
                'total_pnl': 0,
                'total_pnl_pct': 0
            }
        
        total_value = sum(p.size * p.current_price for p in self.positions.values())
        total_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        
        return {
            'total_positions': len(self.positions),
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl / total_value if total_value > 0 else 0,
            'positions': [
                {
                    'symbol': p.symbol,
                    'side': p.side,
                    'pnl': p.unrealized_pnl,
                    'pnl_pct': p.unrealized_pnl_pct
                }
                for p in self.positions.values()
            ]
        }


# Global instance
advanced_position_manager = AdvancedPositionManager()
