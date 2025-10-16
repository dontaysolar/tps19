#!/usr/bin/env python3
"""Pre-Trade Guardrails - Validate BEFORE Every Trade"""

from typing import Dict, Tuple
from datetime import datetime
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class PreTradeGuardrails:
    """
    Pre-trade validation - ALL checks must pass
    """
    
    def __init__(self):
        self.MAX_DAILY_LOSS = config.get('guardrails.max_daily_loss', 0.05)
        self.MAX_WEEKLY_LOSS = config.get('guardrails.max_weekly_loss', 0.10)
        self.MAX_DRAWDOWN = config.get('guardrails.max_drawdown', 0.15)
        self.MAX_POSITIONS = config.get('guardrails.max_positions', 5)
        self.MAX_POSITION_SIZE = config.get('guardrails.max_position_size', 0.10)
        self.MIN_CONFIDENCE = config.get('guardrails.min_confidence', 0.65)
        self.MIN_VOLUME = config.get('guardrails.min_volume', 1_000_000)
        self.MAX_SPREAD = config.get('guardrails.max_spread', 0.005)
        
    def validate(self, signal: Dict, portfolio: Dict) -> Tuple[bool, str]:
        """Validate trade against all guardrails"""
        
        # Check 1: Daily loss limit
        daily_pnl_pct = portfolio.get('daily_pnl', 0) / max(portfolio.get('total_value', 1), 1)
        if daily_pnl_pct < -self.MAX_DAILY_LOSS:
            return False, f"Daily loss {daily_pnl_pct:.2%} exceeds limit"
        
        # Check 2: Weekly loss limit
        weekly_pnl_pct = portfolio.get('weekly_pnl', 0) / max(portfolio.get('total_value', 1), 1)
        if weekly_pnl_pct < -self.MAX_WEEKLY_LOSS:
            return False, f"Weekly loss {weekly_pnl_pct:.2%} exceeds limit"
        
        # Check 3: Drawdown limit
        if portfolio.get('current_drawdown', 0) > self.MAX_DRAWDOWN:
            return False, f"Drawdown {portfolio.get('current_drawdown', 0):.2%} too high"
        
        # Check 4: Position count
        if len(portfolio.get('positions', {})) >= self.MAX_POSITIONS:
            return False, f"Max positions ({self.MAX_POSITIONS}) reached"
        
        # Check 5: Position size
        size_pct = signal.get('size_pct', 0)
        if size_pct > self.MAX_POSITION_SIZE:
            return False, f"Position size {size_pct:.2%} too large"
        
        # Check 6: Confidence
        if signal.get('confidence', 0) < self.MIN_CONFIDENCE:
            return False, f"Confidence {signal.get('confidence', 0):.2%} too low"
        
        # Check 7: Consecutive losses
        if portfolio.get('consecutive_losses', 0) >= 5:
            return False, "5 consecutive losses - circuit breaker"
        
        # Check 8: Time of day
        hour = datetime.utcnow().hour
        if 2 <= hour < 6:
            return False, "Low liquidity hours (2-6 AM UTC)"
        
        # Check 9: Volume
        if signal.get('volume_24h', 0) < self.MIN_VOLUME:
            return False, f"Volume ${signal.get('volume_24h', 0):,.0f} too low"
        
        # Check 10: Spread
        if signal.get('spread_pct', 0) > self.MAX_SPREAD:
            return False, f"Spread {signal.get('spread_pct', 0):.2%} too wide"
        
        # All checks passed
        return True, "All guardrails passed"


# Global instance
pre_trade_guardrails = PreTradeGuardrails()
