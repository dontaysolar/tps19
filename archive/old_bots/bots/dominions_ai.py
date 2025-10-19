#!/usr/bin/env python3
"""
Dominions AI - Resource Allocation & Capital Management
Optimally distributes capital across strategies and assets
Manages portfolio allocation dynamically
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class DominionsAI:
    def __init__(self):
        self.name = "Dominions_AI"
        self.version = "1.0.0"
        self.enabled = True
        self.power_level = 93
        
        self.total_capital = 0
        self.allocations = {}
        self.performance_history = {}
        
        self.metrics = {
            'allocations_made': 0,
            'rebalances_executed': 0,
            'strategies_managed': 0,
            'portfolio_sharpe': 0.0
        }
    
    def allocate_capital(self, total_capital: float, strategies: Dict[str, Dict]) -> Dict:
        """
        Allocate capital across strategies based on performance
        
        Args:
            total_capital: Total available capital
            strategies: {strategy_name: {performance_metrics}}
        """
        self.total_capital = total_capital
        allocations = {}
        
        if not strategies:
            return {'error': 'No strategies provided'}
        
        # Calculate allocation scores
        scores = {}
        for name, metrics in strategies.items():
            score = self._calculate_allocation_score(metrics)
            scores[name] = score
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score == 0:
            # Equal allocation if no performance data
            equal_share = total_capital / len(strategies)
            allocations = {name: equal_share for name in strategies.keys()}
        else:
            # Proportional allocation
            for name, score in scores.items():
                allocations[name] = (score / total_score) * total_capital
        
        # Apply constraints (min/max allocation)
        allocations = self._apply_allocation_constraints(allocations, total_capital)
        
        self.allocations = allocations
        self.metrics['allocations_made'] += 1
        self.metrics['strategies_managed'] = len(strategies)
        
        return {
            'allocations': allocations,
            'allocation_percentages': {k: (v/total_capital)*100 for k, v in allocations.items()},
            'diversification_score': self._calculate_diversification(allocations),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_allocation_score(self, metrics: Dict) -> float:
        """Calculate score for capital allocation"""
        score = 0
        
        # Win rate (0-40 points)
        win_rate = metrics.get('win_rate', 0.5)
        score += win_rate * 40
        
        # Sharpe ratio (0-30 points)
        sharpe = metrics.get('sharpe_ratio', 0)
        score += min(sharpe * 15, 30)
        
        # Profit factor (0-20 points)
        profit_factor = metrics.get('profit_factor', 1.0)
        score += min((profit_factor - 1) * 10, 20)
        
        # Max drawdown (0-10 points, inverse)
        max_dd = metrics.get('max_drawdown_pct', 50)
        score += max(0, 10 * (1 - max_dd / 50))
        
        return max(score, 0)
    
    def _apply_allocation_constraints(self, allocations: Dict, total: float) -> Dict:
        """Apply min/max constraints to allocations"""
        constrained = {}
        
        min_alloc = total * 0.05  # Min 5%
        max_alloc = total * 0.40  # Max 40%
        
        for name, amount in allocations.items():
            constrained[name] = max(min_alloc, min(amount, max_alloc))
        
        # Normalize to total
        current_total = sum(constrained.values())
        if current_total > 0:
            scale_factor = total / current_total
            constrained = {k: v * scale_factor for k, v in constrained.items()}
        
        return constrained
    
    def _calculate_diversification(self, allocations: Dict) -> float:
        """Calculate diversification score (0-100)"""
        if not allocations:
            return 0
        
        # Higher score = more diversified
        values = list(allocations.values())
        total = sum(values)
        
        if total == 0:
            return 0
        
        # Calculate Herfindahl index
        proportions = [v/total for v in values]
        herfindahl = sum([p**2 for p in proportions])
        
        # Convert to diversification score (inverse)
        max_herfindahl = 1.0  # All in one strategy
        min_herfindahl = 1 / len(allocations)  # Perfectly diversified
        
        diversification = 100 * (1 - (herfindahl - min_herfindahl) / (max_herfindahl - min_herfindahl))
        return max(0, min(100, diversification))
    
    def rebalance_portfolio(self, current_allocations: Dict, target_allocations: Dict) -> Dict:
        """Calculate rebalancing trades needed"""
        trades = {}
        
        for strategy, target in target_allocations.items():
            current = current_allocations.get(strategy, 0)
            difference = target - current
            
            if abs(difference) > self.total_capital * 0.01:  # >1% change
                trades[strategy] = {
                    'current': current,
                    'target': target,
                    'adjustment': difference,
                    'action': 'INCREASE' if difference > 0 else 'DECREASE'
                }
        
        self.metrics['rebalances_executed'] += 1
        
        return {
            'rebalancing_needed': len(trades) > 0,
            'trades': trades,
            'total_adjustments': len(trades),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'power_level': self.power_level,
            'total_capital': self.total_capital,
            'current_allocations': self.allocations,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    ai = DominionsAI()
    print(f"✅ {ai.name} v{ai.version} - Power Level: {ai.power_level}")
