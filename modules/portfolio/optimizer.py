#!/usr/bin/env python3
"""
Portfolio Optimizer - Modern Portfolio Theory implementation
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta

try:
    from scipy.optimize import minimize
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioOptimizer:
    """
    Optimize capital allocation across strategies and assets
    """
    
    def __init__(self):
        self.optimization_history = []
        
    def optimize_allocation(self, strategies: List[Dict], 
                           constraints: Optional[Dict] = None) -> Dict:
        """
        Find optimal capital allocation using Modern Portfolio Theory
        
        Args:
            strategies: List of strategy dicts with historical returns
            constraints: Optional constraints (min/max allocation per strategy)
            
        Returns:
            Optimal allocation weights
        """
        if not HAS_SCIPY:
            logger.warning("SciPy not installed, using equal weight allocation")
            return self._equal_weight_allocation(strategies)
        
        if len(strategies) < 2:
            logger.warning("Need at least 2 strategies for optimization")
            return self._equal_weight_allocation(strategies)
        
        # Get returns matrix
        returns_matrix = self._build_returns_matrix(strategies)
        
        if returns_matrix is None or len(returns_matrix) == 0:
            return self._equal_weight_allocation(strategies)
        
        # Calculate mean returns and covariance
        mean_returns = np.mean(returns_matrix, axis=1)
        cov_matrix = np.cov(returns_matrix)
        
        # Default constraints
        if constraints is None:
            constraints = {
                'min_weight': 0.05,  # Minimum 5% per strategy
                'max_weight': 0.40   # Maximum 40% per strategy
            }
        
        # Objective function: Maximize Sharpe ratio
        def negative_sharpe(weights):
            """Negative Sharpe ratio (for minimization)"""
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            
            if portfolio_std == 0:
                return 999  # Penalize zero variance
            
            sharpe = portfolio_return / portfolio_std
            return -sharpe  # Negative for minimization
        
        # Constraints
        constraints_list = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1 (100%)
        ]
        
        # Bounds (min and max weight per strategy)
        bounds = [
            (constraints['min_weight'], constraints['max_weight']) 
            for _ in strategies
        ]
        
        # Initial guess (equal weight)
        x0 = np.array([1/len(strategies)] * len(strategies))
        
        # Optimize
        try:
            result = minimize(
                negative_sharpe,
                x0=x0,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_list,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = result.x
                expected_sharpe = -result.fun
                
                allocation = {
                    'weights': optimal_weights.tolist(),
                    'expected_sharpe': expected_sharpe,
                    'allocations': {
                        strategies[i]['name']: float(w) 
                        for i, w in enumerate(optimal_weights)
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Portfolio optimized - Expected Sharpe: {expected_sharpe:.2f}")
                self.optimization_history.append(allocation)
                
                return allocation
            else:
                logger.warning(f"Optimization failed: {result.message}")
                return self._equal_weight_allocation(strategies)
                
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return self._equal_weight_allocation(strategies)
    
    def _build_returns_matrix(self, strategies: List[Dict]) -> Optional[np.ndarray]:
        """Build returns matrix from strategy historical data"""
        returns_list = []
        
        for strategy in strategies:
            if 'historical_returns' in strategy:
                returns_list.append(strategy['historical_returns'])
            elif 'trades' in strategy:
                # Calculate returns from trade history
                trades = strategy['trades']
                returns = [t.get('return', 0) for t in trades if 'return' in t]
                if returns:
                    returns_list.append(returns)
        
        if not returns_list:
            return None
        
        # Ensure all same length (pad with zeros if needed)
        max_len = max(len(r) for r in returns_list)
        padded_returns = []
        for returns in returns_list:
            if len(returns) < max_len:
                returns = list(returns) + [0] * (max_len - len(returns))
            padded_returns.append(returns[:max_len])
        
        return np.array(padded_returns)
    
    def _equal_weight_allocation(self, strategies: List[Dict]) -> Dict:
        """Fallback to equal weight allocation"""
        n = len(strategies)
        if n == 0:
            return {'weights': [], 'allocations': {}}
        
        weight = 1.0 / n
        
        return {
            'weights': [weight] * n,
            'expected_sharpe': 1.0,  # Placeholder
            'allocations': {
                s['name']: weight for s in strategies
            },
            'method': 'equal_weight',
            'timestamp': datetime.now().isoformat()
        }
    
    def rebalance_portfolio(self, current_allocations: Dict, 
                           target_allocations: Dict,
                           total_capital: float) -> List[Dict]:
        """
        Generate rebalancing trades to achieve target allocation
        
        Args:
            current_allocations: Current strategy allocations
            target_allocations: Target strategy allocations
            total_capital: Total portfolio value
            
        Returns:
            List of rebalancing trades
        """
        rebalance_trades = []
        
        for strategy_name, target_weight in target_allocations.items():
            current_weight = current_allocations.get(strategy_name, 0)
            difference = target_weight - current_weight
            
            # Only rebalance if difference > 5%
            if abs(difference) > 0.05:
                trade_value = difference * total_capital
                
                rebalance_trades.append({
                    'strategy': strategy_name,
                    'action': 'INCREASE' if difference > 0 else 'DECREASE',
                    'amount': abs(trade_value),
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'difference': difference
                })
        
        return rebalance_trades
    
    def get_diversification_score(self, allocations: Dict) -> float:
        """
        Calculate portfolio diversification score (0-1)
        
        Higher score = better diversification
        """
        weights = list(allocations.values())
        
        if not weights:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum(w ** 2 for w in weights)
        
        # Convert to diversification score (1 = perfectly diversified)
        # For n assets, minimum HHI is 1/n (equal weight)
        n = len(weights)
        min_hhi = 1 / n if n > 0 else 1
        
        diversification = 1 - ((hhi - min_hhi) / (1 - min_hhi))
        
        return max(0, min(1, diversification))


# Global instance
portfolio_optimizer = PortfolioOptimizer()
