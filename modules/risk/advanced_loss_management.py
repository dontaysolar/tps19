#!/usr/bin/env python3
"""
Advanced Loss Management System
Multiple layers of loss prevention and recovery
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class LossPreventionLayer(Enum):
    """Loss prevention layers"""
    LAYER_1_PRETRADE = 1      # Before trade entry
    LAYER_2_POSITION = 2       # During trade
    LAYER_3_PORTFOLIO = 3      # Portfolio level
    LAYER_4_EMERGENCY = 4      # Circuit breaker


class AdvancedLossManagement:
    """
    Multi-layered loss management system
    Goes beyond simple stop losses
    """
    
    def __init__(self):
        # Layer 1: Pre-trade limits
        self.max_risk_per_trade = 0.02  # 2% max risk
        self.max_daily_loss = 0.05      # 5% max daily loss
        self.max_weekly_loss = 0.10     # 10% max weekly loss
        
        # Layer 2: Position limits
        self.hard_stop_loss = 0.02      # Hard stop at -2%
        self.time_stop_hours = 120      # Max 5 days
        self.adverse_move_threshold = 0.015  # -1.5% rapid move
        
        # Layer 3: Portfolio limits
        self.max_portfolio_risk = 0.15  # 15% max total risk
        self.max_correlated_risk = 0.20  # 20% in correlated positions
        self.max_drawdown_limit = 0.20   # 20% max drawdown
        
        # Layer 4: Emergency circuit breaker
        self.circuit_breaker_drawdown = 0.15  # Stop all at 15% DD
        self.circuit_breaker_consecutive = 5   # Stop after 5 losses
        self.circuit_breaker_daily_loss = 0.08  # Stop at 8% daily loss
        
        # Tracking
        self.circuit_breaker_active = False
        self.loss_events = []
        
    # ========== LAYER 1: PRE-TRADE VALIDATION ==========
    
    def validate_trade_entry(self, signal: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """
        Layer 1: Validate before entering trade
        
        Returns: (approved, reason)
        """
        # Check daily loss limit
        daily_pnl = portfolio.get('daily_pnl', 0)
        portfolio_value = portfolio.get('total_value', 500)
        daily_loss_pct = daily_pnl / portfolio_value if portfolio_value > 0 else 0
        
        if daily_loss_pct < -self.max_daily_loss:
            return False, f"Daily loss limit exceeded: {daily_loss_pct:.2%}"
        
        # Check weekly loss limit
        weekly_pnl = portfolio.get('weekly_pnl', 0)
        weekly_loss_pct = weekly_pnl / portfolio_value if portfolio_value > 0 else 0
        
        if weekly_loss_pct < -self.max_weekly_loss:
            return False, f"Weekly loss limit exceeded: {weekly_loss_pct:.2%}"
        
        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, "Circuit breaker active - trading halted"
        
        # Check consecutive losses
        consecutive_losses = portfolio.get('consecutive_losses', 0)
        if consecutive_losses >= self.circuit_breaker_consecutive:
            self.activate_circuit_breaker("consecutive_losses")
            return False, f"{consecutive_losses} consecutive losses - circuit breaker activated"
        
        # Check position risk
        position_risk = signal.get('size_pct', 0.10)
        if position_risk > self.max_risk_per_trade:
            return False, f"Position risk too high: {position_risk:.2%}"
        
        return True, "All Layer 1 checks passed"
    
    # ========== LAYER 2: POSITION MONITORING ==========
    
    def monitor_position(self, position: Dict, current_price: float) -> List[Dict]:
        """
        Layer 2: Monitor active position for risk events
        
        Returns list of actions to take
        """
        actions = []
        
        entry_price = position['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        
        # Hard stop loss (-2%)
        if pnl_pct <= -self.hard_stop_loss:
            actions.append({
                'action': 'CLOSE_IMMEDIATELY',
                'reason': 'Hard stop loss hit',
                'priority': 'CRITICAL'
            })
            logger.warning(f"Hard stop triggered: {pnl_pct:.2%}")
        
        # Time-based stop
        entry_time = position.get('entry_time', datetime.now())
        hours_held = (datetime.now() - entry_time).total_seconds() / 3600
        
        if hours_held > self.time_stop_hours and pnl_pct < 0.01:
            actions.append({
                'action': 'CLOSE',
                'reason': f'Time stop: held {hours_held:.1f}h with minimal profit',
                'priority': 'HIGH'
            })
        
        # Adverse movement detection
        recent_move = position.get('price_change_1m', 0)
        if abs(recent_move) > self.adverse_move_threshold:
            actions.append({
                'action': 'MONITOR_CLOSELY',
                'reason': f'Adverse movement: {recent_move:.2%}',
                'priority': 'HIGH'
            })
        
        return actions
    
    # ========== LAYER 3: PORTFOLIO PROTECTION ==========
    
    def validate_portfolio_risk(self, portfolio: Dict, 
                               new_position_risk: float) -> Tuple[bool, str]:
        """
        Layer 3: Validate portfolio-level risk
        """
        current_risk = portfolio.get('total_risk_exposure', 0)
        total_risk = current_risk + new_position_risk
        
        if total_risk > self.max_portfolio_risk:
            return False, f"Portfolio risk limit: {total_risk:.2%} > {self.max_portfolio_risk:.2%}"
        
        # Check correlation risk
        correlated_positions = portfolio.get('correlated_positions', [])
        correlated_risk = sum(p.get('risk', 0) for p in correlated_positions)
        
        if correlated_risk > self.max_correlated_risk:
            return False, f"Correlated risk too high: {correlated_risk:.2%}"
        
        # Check drawdown
        current_drawdown = portfolio.get('current_drawdown', 0)
        if current_drawdown > self.max_drawdown_limit:
            return False, f"Drawdown limit exceeded: {current_drawdown:.2%}"
        
        return True, "Portfolio risk acceptable"
    
    # ========== LAYER 4: CIRCUIT BREAKER ==========
    
    def check_circuit_breaker(self, portfolio: Dict) -> bool:
        """
        Layer 4: Emergency circuit breaker
        
        Halts all trading if critical conditions met
        """
        # Drawdown circuit breaker
        drawdown = portfolio.get('current_drawdown', 0)
        if drawdown > self.circuit_breaker_drawdown:
            self.activate_circuit_breaker("excessive_drawdown")
            return True
        
        # Daily loss circuit breaker
        daily_loss_pct = portfolio.get('daily_pnl', 0) / portfolio.get('total_value', 1)
        if daily_loss_pct < -self.circuit_breaker_daily_loss:
            self.activate_circuit_breaker("daily_loss")
            return True
        
        # Consecutive losses
        if portfolio.get('consecutive_losses', 0) >= self.circuit_breaker_consecutive:
            self.activate_circuit_breaker("consecutive_losses")
            return True
        
        return False
    
    def activate_circuit_breaker(self, reason: str):
        """Activate emergency circuit breaker"""
        if not self.circuit_breaker_active:
            self.circuit_breaker_active = True
            logger.critical(f"🚨 CIRCUIT BREAKER ACTIVATED: {reason}")
            
            # Record event
            self.loss_events.append({
                'timestamp': datetime.now(),
                'type': 'circuit_breaker',
                'reason': reason
            })
    
    def deactivate_circuit_breaker(self):
        """Manually deactivate circuit breaker"""
        self.circuit_breaker_active = False
        logger.info("Circuit breaker deactivated")
    
    def get_loss_statistics(self) -> Dict:
        """Get loss management statistics"""
        return {
            'circuit_breaker_active': self.circuit_breaker_active,
            'total_loss_events': len(self.loss_events),
            'circuit_breaker_activations': len([e for e in self.loss_events if e['type'] == 'circuit_breaker']),
            'last_event': self.loss_events[-1] if self.loss_events else None,
            'limits': {
                'max_risk_per_trade': self.max_risk_per_trade,
                'max_daily_loss': self.max_daily_loss,
                'max_drawdown': self.max_drawdown_limit
            }
        }
    
    def calculate_optimal_stop_loss(self, entry_price: float, 
                                    volatility: float,
                                    confidence: float) -> float:
        """
        Calculate optimal stop loss based on volatility and confidence
        
        Higher confidence = tighter stop
        Higher volatility = wider stop
        """
        # Base stop at 2%
        base_stop_pct = 0.02
        
        # Adjust for volatility (higher vol = wider stop)
        vol_adjustment = min(0.01, volatility * 0.5)
        
        # Adjust for confidence (higher confidence = can use tighter stop)
        confidence_adjustment = (1 - confidence) * 0.01
        
        total_stop_pct = base_stop_pct + vol_adjustment + confidence_adjustment
        
        # Cap between 1.5% and 3%
        total_stop_pct = max(0.015, min(0.03, total_stop_pct))
        
        stop_price = entry_price * (1 - total_stop_pct)
        
        return stop_price


# Global instance
advanced_loss_management = AdvancedLossManagement()
