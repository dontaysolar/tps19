#!/usr/bin/env python3
"""
Adaptive Risk Manager - Risk that adapts to performance and market
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class RiskMode(Enum):
    """Risk operating modes"""
    AGGRESSIVE = "aggressive"      # High risk, high reward
    NORMAL = "normal"             # Balanced risk/reward
    CONSERVATIVE = "conservative" # Low risk, capital preservation
    DEFENSIVE = "defensive"       # Minimal risk, recovery mode


class AdaptiveRiskManager:
    """
    Risk management that adapts to:
    - Performance (winning/losing streaks)
    - Market conditions (volatility, regime)
    - Capital level
    - Time factors
    """
    
    def __init__(self):
        self.current_mode = RiskMode.NORMAL
        self.mode_history = []
        
        # Risk parameters by mode
        self.risk_parameters = {
            RiskMode.AGGRESSIVE: {
                'max_position_size': 0.15,
                'max_positions': 5,
                'min_confidence': 0.65,
                'stop_loss_pct': 0.025,  # 2.5%
            },
            RiskMode.NORMAL: {
                'max_position_size': 0.10,
                'max_positions': 4,
                'min_confidence': 0.70,
                'stop_loss_pct': 0.020,  # 2.0%
            },
            RiskMode.CONSERVATIVE: {
                'max_position_size': 0.06,
                'max_positions': 3,
                'min_confidence': 0.75,
                'stop_loss_pct': 0.015,  # 1.5%
            },
            RiskMode.DEFENSIVE: {
                'max_position_size': 0.03,
                'max_positions': 2,
                'min_confidence': 0.80,
                'stop_loss_pct': 0.010,  # 1.0%
            }
        }
        
    def adapt_risk_mode(self, portfolio: Dict, market_conditions: Dict):
        """
        Automatically adapt risk mode based on conditions
        
        Args:
            portfolio: Current portfolio state
            market_conditions: Current market analysis
        """
        previous_mode = self.current_mode
        
        # Factors to consider
        factors = self._analyze_risk_factors(portfolio, market_conditions)
        
        # Decision logic
        risk_score = self._calculate_risk_score(factors)
        
        # Determine mode
        if risk_score >= 75:
            new_mode = RiskMode.AGGRESSIVE
        elif risk_score >= 50:
            new_mode = RiskMode.NORMAL
        elif risk_score >= 25:
            new_mode = RiskMode.CONSERVATIVE
        else:
            new_mode = RiskMode.DEFENSIVE
        
        # Mode change
        if new_mode != previous_mode:
            self.current_mode = new_mode
            self.mode_history.append({
                'timestamp': datetime.now(),
                'from_mode': previous_mode.value,
                'to_mode': new_mode.value,
                'reason': self._explain_mode_change(factors),
                'risk_score': risk_score
            })
            
            logger.warning(f"🎯 Risk mode changed: {previous_mode.value} → {new_mode.value}")
            logger.info(f"   Reason: {self.mode_history[-1]['reason']}")
    
    def _analyze_risk_factors(self, portfolio: Dict, 
                             market_conditions: Dict) -> Dict:
        """Analyze all risk factors"""
        return {
            # Performance factors (positive = good)
            'win_rate': portfolio.get('win_rate', 0.5),
            'consecutive_wins': portfolio.get('consecutive_wins', 0),
            'consecutive_losses': -portfolio.get('consecutive_losses', 0),  # Negative impact
            'current_drawdown': -portfolio.get('current_drawdown', 0),
            'profit_trend': portfolio.get('profit_trend', 0),
            
            # Market factors
            'volatility_regime': market_conditions.get('volatility_score', 50),
            'trend_strength': market_conditions.get('trend_strength', 0.5),
            'market_regime': market_conditions.get('regime_score', 50),
            
            # Time factors
            'time_in_market': portfolio.get('days_trading', 0),
            'recent_accuracy': portfolio.get('recent_accuracy', 0.5),
        }
    
    def _calculate_risk_score(self, factors: Dict) -> float:
        """
        Calculate overall risk score (0-100)
        
        Higher score = can take more risk
        """
        score = 50  # Start neutral
        
        # Performance adjustments
        if factors['win_rate'] > 0.65:
            score += 15
        elif factors['win_rate'] < 0.45:
            score -= 15
        
        if factors['consecutive_wins'] >= 3:
            score += 10
        elif factors['consecutive_losses'] <= -3:
            score -= 20
        
        if factors['current_drawdown'] < -0.10:  # 10%+ drawdown
            score -= 30
        elif factors['current_drawdown'] < -0.05:
            score -= 15
        
        # Market adjustments
        if factors['volatility_regime'] > 70:  # High volatility
            score -= 10
        elif factors['volatility_regime'] < 30:  # Low volatility
            score += 5
        
        if factors['trend_strength'] > 0.7:  # Strong trend
            score += 10
        
        # Recent accuracy
        if factors['recent_accuracy'] > 0.70:
            score += 10
        elif factors['recent_accuracy'] < 0.50:
            score -= 15
        
        return max(0, min(100, score))
    
    def _explain_mode_change(self, factors: Dict) -> str:
        """Generate explanation for mode change"""
        reasons = []
        
        if factors['win_rate'] > 0.65:
            reasons.append("high win rate")
        elif factors['win_rate'] < 0.45:
            reasons.append("low win rate")
        
        if factors['consecutive_losses'] <= -3:
            reasons.append("consecutive losses")
        
        if factors['current_drawdown'] < -0.10:
            reasons.append("significant drawdown")
        
        if factors['volatility_regime'] > 70:
            reasons.append("high market volatility")
        
        return ", ".join(reasons) if reasons else "routine adaptation"
    
    def get_current_parameters(self) -> Dict:
        """Get current risk parameters for active mode"""
        return self.risk_parameters[self.current_mode]
    
    def scale_capital(self, new_capital: float):
        """Update current capital for scaling calculations"""
        old_capital = self.current_capital
        self.current_capital = new_capital
        
        growth = (new_capital - old_capital) / old_capital if old_capital > 0 else 0
        
        if abs(growth) > 0.10:  # 10%+ change
            logger.info(f"Capital scaled: £{old_capital:.2f} → £{new_capital:.2f} ({growth:+.1%})")
    
    def get_risk_adaptation_report(self) -> Dict:
        """Get risk adaptation history and current state"""
        return {
            'current_mode': self.current_mode.value,
            'current_parameters': self.get_current_parameters(),
            'mode_changes': len(self.mode_history),
            'recent_changes': self.mode_history[-5:] if self.mode_history else [],
            'risk_scale_factor': self.risk_scale_factor,
            'capital_level': self.current_capital,
            'recommendations': self._get_risk_recommendations()
        }
    
    def _get_risk_recommendations(self) -> List[str]:
        """Get recommendations for current risk mode"""
        mode = self.current_mode
        params = self.risk_parameters[mode]
        
        recommendations = [
            f"Current mode: {mode.value.upper()}",
            f"Max position size: {params['max_position_size']:.1%}",
            f"Max positions: {params['max_positions']}",
            f"Min confidence: {params['min_confidence']:.0%}",
        ]
        
        if mode == RiskMode.DEFENSIVE:
            recommendations.append("⚠️ DEFENSIVE MODE - Focus on capital preservation")
            recommendations.append("Only take highest-confidence setups")
            recommendations.append("Consider pausing trading until conditions improve")
        elif mode == RiskMode.AGGRESSIVE:
            recommendations.append("🚀 AGGRESSIVE MODE - Capitalize on hot streak")
            recommendations.append("Maintain discipline - don't overtrade")
            recommendations.append("Lock in profits regularly")
        
        return recommendations


# Global instance
adaptive_risk_manager = AdaptiveRiskManager()
