#!/usr/bin/env python3
"""
RISK MANAGEMENT LAYER
All risk management features consolidated
"""

import numpy as np
from datetime import datetime
from typing import Dict

class RiskManagementLayer:
    """Comprehensive risk management"""
    
    def __init__(self):
        self.name = "Risk_Management_Layer"
        self.version = "1.0.0"
        
        # Risk parameters
        self.max_position_size_pct = 0.10  # 10% of capital
        self.max_risk_per_trade = 0.02  # 2% max loss
        self.max_portfolio_risk = 0.20  # 20% max drawdown
        self.max_daily_loss = 0.05  # 5% daily loss limit
        self.max_correlation = 0.70  # Max correlation between positions
        
        # State tracking
        self.daily_pnl = 0
        self.peak_equity = 10000  # Starting capital
        self.current_equity = 10000
        self.open_positions = {}
        
    def validate_trade(self, signal: Dict, analysis: Dict, symbol: str) -> Dict:
        """Comprehensive trade validation"""
        
        checks = {
            'confidence': self.check_confidence(signal),
            'volatility': self.check_volatility(analysis),
            'position_size': self.check_position_limits(symbol),
            'correlation': self.check_correlation(symbol),
            'daily_loss': self.check_daily_loss_limit(),
            'drawdown': self.check_max_drawdown(),
            'var': self.calculate_var(analysis),
            'market_regime': self.check_market_regime(analysis)
        }
        
        # All checks must pass
        all_passed = all(check.get('passed', False) for check in checks.values())
        
        if all_passed:
            position_size = self.calculate_position_size(signal, analysis)
            stop_loss = self.calculate_stop_loss(signal, analysis)
            take_profit = self.calculate_take_profit(signal, analysis)
            
            return {
                'approved': True,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': take_profit / stop_loss if stop_loss > 0 else 0,
                'checks': checks
            }
        
        # Find failed check
        failed = [name for name, check in checks.items() if not check.get('passed', False)]
        
        return {
            'approved': False,
            'reason': f"Failed checks: {', '.join(failed)}",
            'checks': checks
        }
    
    def check_confidence(self, signal: Dict) -> Dict:
        """Check signal confidence"""
        confidence = signal.get('confidence', 0)
        passed = confidence >= 0.65
        
        return {
            'passed': passed,
            'confidence': confidence,
            'threshold': 0.65,
            'reason': 'Sufficient confidence' if passed else 'Low confidence'
        }
    
    def check_volatility(self, analysis: Dict) -> Dict:
        """Check if volatility is acceptable"""
        volatility = analysis.get('volatility', {})
        regime = volatility.get('regime', 'MEDIUM')
        atr_pct = volatility.get('atr_pct', 0)
        
        # Reduce size in high volatility, avoid trading in extreme volatility
        if regime == 'HIGH' and atr_pct > 10:
            passed = False
            reason = 'Extreme volatility'
        elif regime == 'HIGH':
            passed = True
            reason = 'High volatility - reduce size'
        else:
            passed = True
            reason = 'Normal volatility'
        
        return {
            'passed': passed,
            'regime': regime,
            'atr_pct': atr_pct,
            'reason': reason
        }
    
    def check_position_limits(self, symbol: str) -> Dict:
        """Check position sizing limits"""
        current_positions = len(self.open_positions)
        max_positions = 5
        
        if symbol in self.open_positions:
            return {
                'passed': False,
                'reason': 'Position already open',
                'current_positions': current_positions
            }
        
        if current_positions >= max_positions:
            return {
                'passed': False,
                'reason': f'Max positions reached ({max_positions})',
                'current_positions': current_positions
            }
        
        return {
            'passed': True,
            'reason': 'Position limits OK',
            'current_positions': current_positions,
            'max_positions': max_positions
        }
    
    def check_correlation(self, symbol: str) -> Dict:
        """Check correlation with existing positions"""
        # Simplified - in production would calculate actual correlations
        passed = True
        reason = 'Correlation acceptable'
        
        return {
            'passed': passed,
            'reason': reason,
            'max_correlation': self.max_correlation
        }
    
    def check_daily_loss_limit(self) -> Dict:
        """Check daily loss limit"""
        daily_loss_pct = abs(self.daily_pnl / self.current_equity) if self.current_equity > 0 else 0
        passed = daily_loss_pct < self.max_daily_loss
        
        return {
            'passed': passed,
            'daily_loss_pct': daily_loss_pct * 100,
            'max_daily_loss_pct': self.max_daily_loss * 100,
            'reason': 'Within daily limits' if passed else 'Daily loss limit exceeded'
        }
    
    def check_max_drawdown(self) -> Dict:
        """Check maximum drawdown"""
        drawdown = (self.peak_equity - self.current_equity) / self.peak_equity if self.peak_equity > 0 else 0
        passed = drawdown < self.max_portfolio_risk
        
        return {
            'passed': passed,
            'current_drawdown_pct': drawdown * 100,
            'max_drawdown_pct': self.max_portfolio_risk * 100,
            'reason': 'Drawdown acceptable' if passed else 'Max drawdown exceeded'
        }
    
    def calculate_var(self, analysis: Dict) -> Dict:
        """Calculate Value at Risk"""
        volatility = analysis.get('volatility', {})
        hist_vol = volatility.get('historical_vol', 0.20)  # 20% default
        
        # VaR at 95% confidence
        var_95 = self.current_equity * hist_vol * 1.65 / np.sqrt(252)  # Daily VaR
        var_pct = (var_95 / self.current_equity) * 100
        
        passed = var_pct < 5  # Max 5% daily VaR
        
        return {
            'passed': passed,
            'var_95': var_95,
            'var_pct': var_pct,
            'reason': 'VaR acceptable' if passed else 'VaR too high'
        }
    
    def check_market_regime(self, analysis: Dict) -> Dict:
        """Check if market regime is tradeable"""
        trend = analysis.get('trend', {})
        volatility = analysis.get('volatility', {})
        
        direction = trend.get('direction', 'SIDEWAYS')
        regime = volatility.get('regime', 'MEDIUM')
        
        # Avoid trading in extreme conditions
        if regime == 'HIGH' and direction == 'SIDEWAYS':
            passed = False
            reason = 'Choppy high volatility market'
        else:
            passed = True
            reason = 'Market regime tradeable'
        
        return {
            'passed': passed,
            'trend': direction,
            'volatility_regime': regime,
            'reason': reason
        }
    
    def calculate_position_size(self, signal: Dict, analysis: Dict) -> float:
        """Calculate optimal position size"""
        confidence = signal.get('confidence', 0.5)
        volatility = analysis.get('volatility', {})
        regime = volatility.get('regime', 'MEDIUM')
        
        # Base size
        base_size = self.max_position_size_pct
        
        # Adjust for confidence
        confidence_multiplier = min(confidence / 0.65, 1.5)  # Up to 1.5x for high confidence
        
        # Adjust for volatility
        if regime == 'HIGH':
            volatility_multiplier = 0.5
        elif regime == 'LOW':
            volatility_multiplier = 1.2
        else:
            volatility_multiplier = 1.0
        
        final_size = base_size * confidence_multiplier * volatility_multiplier
        
        # Cap at max
        return min(final_size, self.max_position_size_pct * 1.5)
    
    def calculate_stop_loss(self, signal: Dict, analysis: Dict) -> float:
        """Calculate stop loss distance"""
        volatility = analysis.get('volatility', {})
        atr = volatility.get('atr', 0)
        atr_pct = volatility.get('atr_pct', 2)
        
        # Stop loss based on ATR (2x ATR typical)
        stop_loss_pct = max(atr_pct * 2, self.max_risk_per_trade * 100)
        
        return stop_loss_pct / 100  # Return as decimal
    
    def calculate_take_profit(self, signal: Dict, analysis: Dict) -> float:
        """Calculate take profit distance"""
        stop_loss = self.calculate_stop_loss(signal, analysis)
        
        # Aim for 2:1 or 3:1 risk/reward
        risk_reward_ratio = 2.5
        
        take_profit = stop_loss * risk_reward_ratio
        
        return take_profit

if __name__ == '__main__':
    layer = RiskManagementLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
