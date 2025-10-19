#!/usr/bin/env python3
"""
VaR (Value at Risk) Risk Management Bot
Calculates portfolio risk metrics
Monitors and controls risk exposure
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class VaRRiskBot:
    def __init__(self):
        self.name = "VaR_Risk"
        self.version = "1.0.0"
        self.enabled = True
        
        self.confidence_levels = [0.90, 0.95, 0.99]
        self.lookback_period = 252  # 1 year
        
        self.metrics = {
            'var_calculations': 0,
            'risk_breaches': 0,
            'risk_alerts': 0
        }
    
    def calculate_parametric_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Parametric VaR (assumes normal distribution)
        Fastest method, good for liquid markets
        """
        mean = np.mean(returns)
        std = np.std(returns)
        
        # Z-score for confidence level
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(confidence, 1.65)
        
        var = mean - z * std
        self.metrics['var_calculations'] += 1
        
        return var
    
    def calculate_historical_var(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Historical VaR (uses actual historical data)
        No distribution assumptions
        """
        percentile = (1 - confidence) * 100
        var = np.percentile(returns, percentile)
        self.metrics['var_calculations'] += 1
        
        return var
    
    def calculate_cvar(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Conditional VaR (Expected Shortfall)
        Average loss in worst cases
        """
        var = self.calculate_historical_var(returns, confidence)
        cvar = returns[returns <= var].mean()
        
        return cvar
    
    def calculate_portfolio_var(self, positions: Dict[str, Dict], 
                               returns_history: Dict[str, np.ndarray],
                               confidence: float = 0.95) -> Dict:
        """
        Calculate VaR for entire portfolio
        
        Args:
            positions: {asset: {value: float}}
            returns_history: {asset: np.ndarray of returns}
        """
        # Calculate portfolio value
        total_value = sum([p['value'] for p in positions.values()])
        
        # Calculate portfolio returns
        assets = list(positions.keys())
        weights = np.array([positions[a]['value'] / total_value for a in assets])
        
        # Get aligned returns
        min_length = min([len(returns_history[a]) for a in assets])
        returns_matrix = np.array([returns_history[a][-min_length:] for a in assets]).T
        
        # Portfolio returns
        portfolio_returns = returns_matrix @ weights
        
        # Calculate VaR using multiple methods
        parametric_var = self.calculate_parametric_var(portfolio_returns, confidence)
        historical_var = self.calculate_historical_var(portfolio_returns, confidence)
        cvar = self.calculate_cvar(portfolio_returns, confidence)
        
        # VaR in dollar terms
        var_dollar = historical_var * total_value
        cvar_dollar = cvar * total_value
        
        return {
            'portfolio_value': total_value,
            'var_pct': historical_var * 100,
            'var_dollar': abs(var_dollar),
            'cvar_pct': cvar * 100,
            'cvar_dollar': abs(cvar_dollar),
            'parametric_var_pct': parametric_var * 100,
            'confidence_level': confidence,
            'interpretation': f"With {confidence:.0%} confidence, maximum 1-day loss won't exceed ${abs(var_dollar):.2f}",
            'timestamp': datetime.now().isoformat()
        }
    
    def monitor_risk_limits(self, current_var: float, var_limit: float) -> Dict:
        """
        Monitor if VaR exceeds limits
        """
        var_utilization = (current_var / var_limit) * 100 if var_limit > 0 else 0
        
        if var_utilization > 100:
            status = 'BREACH'
            action = 'REDUCE_POSITIONS'
            self.metrics['risk_breaches'] += 1
        elif var_utilization > 90:
            status = 'WARNING'
            action = 'MONITOR_CLOSELY'
            self.metrics['risk_alerts'] += 1
        elif var_utilization > 75:
            status = 'CAUTION'
            action = 'BE_SELECTIVE'
        else:
            status = 'NORMAL'
            action = 'CONTINUE'
        
        return {
            'current_var': current_var,
            'var_limit': var_limit,
            'utilization_pct': var_utilization,
            'status': status,
            'recommended_action': action,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_marginal_var(self, asset: str, position_delta: float,
                              current_portfolio_var: float) -> float:
        """
        Calculate how much VaR changes if position changes
        Marginal VaR = change in VaR per unit change in position
        """
        # Simplified calculation
        marginal_var = position_delta * current_portfolio_var * 0.01
        return marginal_var
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'confidence_levels': self.confidence_levels,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = VaRRiskBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
