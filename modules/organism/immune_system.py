#!/usr/bin/env python3
"""
Organism Immune System - Multi-Layer Protection

Like a biological immune system, this protects the organism from:
- Bad trades (pathogens)
- Excessive losses (disease)
- Market crashes (catastrophic events)
- Over-trading (exhaustion)

4 Layers of defense, each progressively more severe
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class ImmuneSystem:
    """
    4-Layer immune protection system
    
    Layer 1: Pre-Trade Antibodies (immediate defense)
    Layer 2: Position Protection (ongoing monitoring)
    Layer 3: Portfolio Immunity (system-wide health)
    Layer 4: Emergency Response (catastrophic protection)
    """
    
    def __init__(self):
        # Load immune system configuration
        self.layer1_thresholds = {
            'max_daily_loss': config.get('immune.max_daily_loss', 0.05),
            'max_weekly_loss': config.get('immune.max_weekly_loss', 0.10),
            'max_drawdown': config.get('immune.max_drawdown', 0.15),
            'min_confidence': config.get('immune.min_confidence', 0.65),
            'max_positions': config.get('immune.max_positions', 5),
            'max_position_size': config.get('immune.max_position_size', 0.10),
        }
        
        self.layer4_emergency = {
            'flash_crash_threshold': 0.10,  # 10% drop triggers emergency
            'max_consecutive_losses': 5,
            'extreme_volatility': 0.15,  # 15% volatility
        }
        
        # Immune system state
        self.threat_log = []
        self.last_emergency = None
        
        logger.info("🛡️ Immune System activated - 4 layers online")
    
    def layer1_pretrade_antibodies(self, signal: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """
        Layer 1: Immediate threat detection BEFORE trade
        
        Like antibodies attacking pathogens immediately
        
        Args:
            signal: Proposed trade signal
            portfolio: Current portfolio state
            
        Returns:
            (approved: bool, reason: str)
        """
        checks = []
        
        # Check 1: Daily loss limit
        daily_pnl_pct = portfolio.get('daily_pnl', 0) / max(portfolio.get('total_value', 1), 1)
        if daily_pnl_pct < -self.layer1_thresholds['max_daily_loss']:
            return False, f"Layer 1: Daily loss limit ({daily_pnl_pct:.2%})"
        
        # Check 2: Confidence threshold
        if signal.get('confidence', 0) < self.layer1_thresholds['min_confidence']:
            return False, f"Layer 1: Confidence too low ({signal.get('confidence', 0):.2%})"
        
        # Check 3: Position count
        if len(portfolio.get('positions', {})) >= self.layer1_thresholds['max_positions']:
            return False, f"Layer 1: Max positions reached ({self.layer1_thresholds['max_positions']})"
        
        # Check 4: Position size
        position_size_pct = signal.get('size_pct', 0)
        if position_size_pct > self.layer1_thresholds['max_position_size']:
            return False, f"Layer 1: Position too large ({position_size_pct:.2%})"
        
        # Check 5: Drawdown limit
        if portfolio.get('current_drawdown', 0) > self.layer1_thresholds['max_drawdown']:
            return False, f"Layer 1: Drawdown exceeded ({portfolio.get('current_drawdown', 0):.2%})"
        
        # Check 6: Minimum order size
        if signal.get('size_usdt', 0) < signal.get('min_order_size', 10):
            return False, f"Layer 1: Below minimum order size"
        
        # Check 7: Liquidity check
        if not self._check_liquidity(signal):
            return False, f"Layer 1: Insufficient liquidity"
        
        # Check 8: Time of day (circadian rhythm)
        if not self._check_trading_hours():
            return False, f"Layer 1: Outside optimal trading hours"
        
        logger.info("✅ Layer 1: All antibodies cleared the trade")
        return True, "Layer 1: Passed"
    
    def layer2_position_protection(self, position: Dict) -> List[str]:
        """
        Layer 2: Ongoing position monitoring
        
        Like white blood cells patrolling for infections
        
        Args:
            position: Current position details
            
        Returns:
            List of actions to take
        """
        actions = []
        
        current_pnl_pct = position.get('pnl_pct', 0)
        time_held = (datetime.now() - position.get('entry_time', datetime.now())).total_seconds() / 3600
        
        # Stop loss protection
        if current_pnl_pct <= -0.02:  # -2% stop loss
            actions.append('STOP_LOSS')
            logger.warning(f"Layer 2: Stop loss triggered at {current_pnl_pct:.2%}")
        
        # Take profit levels
        if current_pnl_pct >= 0.10:  # 10% profit
            actions.append('TAKE_PROFIT_FULL')
        elif current_pnl_pct >= 0.06:  # 6% profit
            actions.append('TAKE_PROFIT_50PCT')
        elif current_pnl_pct >= 0.03:  # 3% profit
            actions.append('TAKE_PROFIT_25PCT')
        
        # Time-based exit
        if time_held > 120 and current_pnl_pct < 0.02:  # 5 days, <2% profit
            actions.append('TIME_STOP')
            logger.info(f"Layer 2: Time stop after {time_held:.1f} hours")
        
        # Trail stop for winners
        if current_pnl_pct > 0.05:
            actions.append('TRAIL_STOP')
        
        return actions
    
    def layer3_portfolio_immunity(self, portfolio: Dict) -> List[str]:
        """
        Layer 3: Portfolio-wide protection
        
        Like the immune system protecting the whole body
        
        Args:
            portfolio: Full portfolio state
            
        Returns:
            List of portfolio-level actions
        """
        actions = []
        
        current_drawdown = portfolio.get('current_drawdown', 0)
        total_risk = portfolio.get('total_risk_exposure', 0)
        
        # Drawdown response
        if current_drawdown > 0.15:  # 15% drawdown
            actions.append('EMERGENCY_STOP')
            logger.critical(f"Layer 3: EMERGENCY STOP at {current_drawdown:.2%} drawdown")
            
        elif current_drawdown > 0.10:  # 10% drawdown
            actions.append('REDUCE_RISK_50PCT')
            logger.warning(f"Layer 3: Reducing risk by 50% at {current_drawdown:.2%} drawdown")
        
        # Risk exposure check
        if total_risk > 0.20:  # 20% of capital at risk
            actions.append('REDUCE_POSITIONS')
            logger.warning(f"Layer 3: Risk exposure too high ({total_risk:.2%})")
        
        # Concentration check
        if self._check_concentration(portfolio):
            actions.append('DIVERSIFY')
            logger.info("Layer 3: Portfolio too concentrated")
        
        return actions
    
    def layer4_emergency_response(self, portfolio: Dict, market_data: Dict) -> Tuple[bool, str]:
        """
        Layer 4: Emergency system shutdown
        
        Like the immune system triggering inflammation/fever
        Most severe response - stops ALL trading
        
        Args:
            portfolio: Portfolio state
            market_data: Market conditions
            
        Returns:
            (shutdown: bool, reason: str)
        """
        # Check for flash crash
        if market_data.get('price_change_10m', 0) < -self.layer4_emergency['flash_crash_threshold']:
            logger.critical("⚠️ LAYER 4: FLASH CRASH DETECTED - EMERGENCY STOP")
            return True, "Flash crash detected"
        
        # Check consecutive losses
        consecutive_losses = portfolio.get('consecutive_losses', 0)
        if consecutive_losses >= self.layer4_emergency['max_consecutive_losses']:
            logger.critical(f"⚠️ LAYER 4: {consecutive_losses} consecutive losses - EMERGENCY STOP")
            return True, f"{consecutive_losses} consecutive losses"
        
        # Check extreme volatility
        if market_data.get('volatility', 0) > self.layer4_emergency['extreme_volatility']:
            logger.critical("⚠️ LAYER 4: EXTREME VOLATILITY - EMERGENCY STOP")
            return True, "Extreme market volatility"
        
        # Check if recently had emergency
        if self.last_emergency:
            cooldown_hours = 24
            time_since = (datetime.now() - self.last_emergency).total_seconds() / 3600
            if time_since < cooldown_hours:
                return True, f"Emergency cooldown ({time_since:.1f}h / {cooldown_hours}h)"
        
        return False, "Layer 4: No emergency"
    
    def _check_liquidity(self, signal: Dict) -> bool:
        """Check if sufficient liquidity for trade"""
        # Placeholder - implement with real order book data
        return signal.get('volume_24h', 0) > 1_000_000
    
    def _check_trading_hours(self) -> bool:
        """Check if within optimal trading hours"""
        hour = datetime.now().hour
        # Avoid 2-6 AM UTC (low liquidity)
        return not (2 <= hour < 6)
    
    def _check_concentration(self, portfolio: Dict) -> bool:
        """Check if portfolio too concentrated in one asset"""
        positions = portfolio.get('positions', {})
        if not positions:
            return False
        
        total_value = portfolio.get('total_value', 1)
        max_position_pct = max(p['value'] / total_value for p in positions.values())
        
        return max_position_pct > 0.25  # 25% max single asset
    
    def execute_immune_response(self, action: str, portfolio: Dict) -> Dict:
        """
        Execute immune system action
        
        Args:
            action: Action to take
            portfolio: Current portfolio
            
        Returns:
            Response details
        """
        responses = {
            'STOP_LOSS': {'close_pct': 1.0, 'reason': 'Stop loss hit'},
            'TAKE_PROFIT_FULL': {'close_pct': 1.0, 'reason': 'Take profit target'},
            'TAKE_PROFIT_50PCT': {'close_pct': 0.5, 'reason': 'Partial profit'},
            'TAKE_PROFIT_25PCT': {'close_pct': 0.25, 'reason': 'Partial profit'},
            'TIME_STOP': {'close_pct': 1.0, 'reason': 'Time limit exceeded'},
            'TRAIL_STOP': {'close_pct': 0.0, 'update_stop': True},
            'EMERGENCY_STOP': {'close_all': True, 'pause_hours': 24},
            'REDUCE_RISK_50PCT': {'reduce_sizes': 0.5},
            'REDUCE_POSITIONS': {'close_weakest': 2},
            'DIVERSIFY': {'block_concentrated': True},
        }
        
        response = responses.get(action, {})
        response['action'] = action
        response['timestamp'] = datetime.now()
        
        if action == 'EMERGENCY_STOP':
            self.last_emergency = datetime.now()
        
        return response


# Global immune system instance
immune_system = ImmuneSystem()
