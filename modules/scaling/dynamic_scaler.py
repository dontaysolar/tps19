#!/usr/bin/env python3
"""
Dynamic Scaler - Self-scaling capital and risk management
Automatically adjusts to capital growth and market conditions
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class DynamicScaler:
    """
    Self-scaling system that adapts to capital growth and performance
    
    Automatically:
    - Scales position sizes with capital
    - Adjusts risk based on performance
    - Manages compounding vs extraction
    - Adapts to market conditions
    """
    
    def __init__(self, initial_capital: float = 500):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Scaling curves
        self.position_size_curve = {
            500: 0.08,      # 8% per position at £500
            1000: 0.10,     # 10% at £1,000
            2500: 0.12,     # 12% at £2,500
            5000: 0.12,     # Keep at 12% (safer at scale)
            10000: 0.10,    # Reduce to 10% (large capital)
        }
        
        # Risk scaling
        self.risk_scale_factor = 1.0
        self.min_risk_scale = 0.25  # Never below 25%
        self.max_risk_scale = 2.0   # Never above 200%
        
        # Performance tracking
        self.performance_window = []
        self.drawdown_history = []
        
    def calculate_dynamic_position_size(self, signal_confidence: float,
                                       portfolio: Dict) -> float:
        """
        Calculate position size that scales with:
        - Capital level
        - Signal confidence
        - Recent performance
        - Current drawdown
        """
        # Base size from capital level
        base_size = self._get_base_position_size(self.current_capital)
        
        # Confidence multiplier (0.7 to 1.2)
        confidence_multiplier = 0.7 + (signal_confidence - 0.5) * 1.0
        confidence_multiplier = max(0.7, min(1.2, confidence_multiplier))
        
        # Performance multiplier
        performance_multiplier = self._calculate_performance_multiplier(portfolio)
        
        # Drawdown multiplier (reduce size in drawdown)
        drawdown_multiplier = self._calculate_drawdown_multiplier(portfolio)
        
        # Combined position size
        position_size = (
            base_size * 
            confidence_multiplier * 
            performance_multiplier * 
            drawdown_multiplier *
            self.risk_scale_factor
        )
        
        # Safety caps
        position_size = max(0.02, min(0.20, position_size))  # Between 2% and 20%
        
        logger.info(f"Dynamic position size: {position_size:.2%} "
                   f"(base: {base_size:.2%}, conf: {confidence_multiplier:.2f}, "
                   f"perf: {performance_multiplier:.2f}, dd: {drawdown_multiplier:.2f})")
        
        return position_size
    
    def _get_base_position_size(self, capital: float) -> float:
        """Get base position size for capital level"""
        # Find appropriate size from curve
        sizes = sorted(self.position_size_curve.items())
        
        for i, (threshold, size) in enumerate(sizes):
            if capital < threshold:
                if i == 0:
                    return size
                # Interpolate between levels
                prev_threshold, prev_size = sizes[i-1]
                progress = (capital - prev_threshold) / (threshold - prev_threshold)
                return prev_size + (size - prev_size) * progress
        
        # Above all thresholds - use last
        return sizes[-1][1]
    
    def _calculate_performance_multiplier(self, portfolio: Dict) -> float:
        """
        Adjust size based on recent performance
        
        Hot streak = increase size
        Cold streak = decrease size
        """
        # Get recent win rate
        recent_trades = portfolio.get('recent_trades', [])
        if len(recent_trades) < 10:
            return 1.0
        
        last_10 = recent_trades[-10:]
        wins = sum(1 for t in last_10 if t.get('pnl', 0) > 0)
        win_rate = wins / len(last_10)
        
        # Scale based on performance
        if win_rate >= 0.70:  # Hot streak
            return 1.15
        elif win_rate >= 0.60:  # Good
            return 1.05
        elif win_rate <= 0.30:  # Cold streak
            return 0.70
        elif win_rate <= 0.40:  # Below average
            return 0.85
        else:
            return 1.0
    
    def _calculate_drawdown_multiplier(self, portfolio: Dict) -> float:
        """
        Reduce size during drawdown
        
        Protects capital when struggling
        """
        drawdown = portfolio.get('current_drawdown', 0)
        
        if drawdown > 0.10:  # 10%+ drawdown
            return 0.50  # Half size
        elif drawdown > 0.05:  # 5%+ drawdown
            return 0.75  # 75% size
        elif drawdown > 0.02:  # 2%+ drawdown
            return 0.90  # 90% size
        else:
            return 1.0   # Full size
    
    def adapt_risk_scaling(self, portfolio: Dict):
        """
        Adapt overall risk scaling based on performance
        
        Self-adjusting risk appetite
        """
        # Get recent performance
        if len(self.performance_window) < 20:
            return
        
        recent_pnl = sum(p['pnl'] for p in self.performance_window[-20:])
        recent_return = recent_pnl / self.current_capital
        
        # Adjust risk scale factor
        if recent_return > 0.10:  # 10%+ profit in recent trades
            # Increase risk gradually
            self.risk_scale_factor = min(self.max_risk_scale, 
                                        self.risk_scale_factor * 1.05)
            logger.info(f"Increasing risk scale to {self.risk_scale_factor:.2f}")
        
        elif recent_return < -0.05:  # 5%+ loss
            # Decrease risk
            self.risk_scale_factor = max(self.min_risk_scale,
                                        self.risk_scale_factor * 0.90)
            logger.info(f"Decreasing risk scale to {self.risk_scale_factor:.2f}")
    
    def should_compound_or_extract(self, current_capital: float,
                                   total_profit: float) -> Dict:
        """
        Decide between compounding growth or extracting profit
        
        Early stage: Compound for growth
        Later stage: Extract for security
        """
        growth_ratio = (current_capital - self.initial_capital) / self.initial_capital
        
        # Extraction schedule
        if current_capital < 1000:
            # Small capital - aggressive compounding
            compound_pct = 0.80  # Reinvest 80%
            extract_pct = 0.20   # Extract 20%
            reason = "Small capital - focus on growth"
        
        elif current_capital < 2500:
            # Medium capital - balanced
            compound_pct = 0.60
            extract_pct = 0.40
            reason = "Balanced growth and security"
        
        elif current_capital < 5000:
            # Larger capital - more extraction
            compound_pct = 0.40
            extract_pct = 0.60
            reason = "Securing profits while growing"
        
        else:
            # Large capital - mostly extraction
            compound_pct = 0.30
            extract_pct = 0.70
            reason = "Large capital - prioritize security"
        
        return {
            'compound_percentage': compound_pct,
            'extract_percentage': extract_pct,
            'compound_amount': total_profit * compound_pct,
            'extract_amount': total_profit * extract_pct,
            'reason': reason,
            'next_extraction_at': self.initial_capital * (1 + self.extraction_threshold)
        }
    
    def get_scaling_status(self) -> Dict:
        """Get current scaling status"""
        current_milestone = None
        for milestone in self.scaling_milestones:
            if self.current_capital >= milestone['capital']:
                current_milestone = milestone
        
        return {
            'current_capital': self.current_capital,
            'initial_capital': self.initial_capital,
            'growth': (self.current_capital - self.initial_capital) / self.initial_capital,
            'current_milestone': current_milestone,
            'risk_scale_factor': self.risk_scale_factor,
            'base_position_size': self._get_base_position_size(self.current_capital)
        }


# Global instance
dynamic_scaler = DynamicScaler()
