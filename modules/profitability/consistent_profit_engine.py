#!/usr/bin/env python3
"""
Consistent Profit Engine - Ensures steady, reliable profitability
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class ConsistentProfitEngine:
    """
    Ensures consistent profitability through multiple mechanisms
    
    Features:
    - Profit targets with scaling
    - Consistency tracking
    - Performance-based adaptation
    - Profit extraction
    - Compound growth management
    """
    
    def __init__(self, initial_capital: float = 500):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Profit targets (daily)
        self.profit_targets = {
            'minimum': 0.012,    # 1.2% daily (minimum to continue)
            'target': 0.024,     # 2.4% daily (target)
            'excellent': 0.048   # 4.8% daily (excellent)
        }
        
        # Profit extraction rules
        self.extraction_threshold = 0.20  # Extract at 20% account growth
        self.extraction_percentage = 0.50  # Extract 50% of profit
        
        # Consistency tracking
        self.daily_results = []
        self.weekly_results = []
        
        # Scaling thresholds
        self.scaling_milestones = [
            {'capital': 500, 'daily_target': 12},     # £500 → £12/day
            {'capital': 1000, 'daily_target': 24},    # £1,000 → £24/day
            {'capital': 2500, 'daily_target': 60},    # £2,500 → £60/day
            {'capital': 5000, 'daily_target': 120},   # £5,000 → £120/day
            {'capital': 10000, 'daily_target': 240},  # £10,000 → £240/day
        ]
        
    def evaluate_daily_performance(self, daily_pnl: float, 
                                  trades_today: int) -> Dict:
        """
        Evaluate if daily performance meets profitability standards
        
        Returns actions to take
        """
        daily_return = daily_pnl / self.current_capital
        target_return = self.profit_targets['target']
        
        # Record result
        self.daily_results.append({
            'date': datetime.now().date(),
            'pnl': daily_pnl,
            'return_pct': daily_return,
            'trades': trades_today,
            'met_target': daily_return >= self.profit_targets['minimum']
        })
        
        # Keep only last 30 days
        if len(self.daily_results) > 30:
            self.daily_results = self.daily_results[-30:]
        
        evaluation = {
            'performance': 'excellent' if daily_return >= self.profit_targets['excellent']
                          else 'good' if daily_return >= self.profit_targets['target']
                          else 'acceptable' if daily_return >= self.profit_targets['minimum']
                          else 'below_target',
            'daily_pnl': daily_pnl,
            'daily_return': daily_return,
            'target_met': daily_return >= self.profit_targets['minimum'],
            'actions': []
        }
        
        # Generate actions based on performance
        if daily_return < self.profit_targets['minimum']:
            evaluation['actions'].append({
                'action': 'INCREASE_ACTIVITY',
                'reason': 'Below minimum profit target',
                'recommendation': 'Increase position frequency or size'
            })
        
        if daily_return >= self.profit_targets['excellent']:
            evaluation['actions'].append({
                'action': 'LOCK_PROFITS',
                'reason': 'Excellent performance',
                'recommendation': 'Secure profits, reduce risk for rest of day'
            })
        
        # Check consistency
        consistency = self._check_consistency()
        evaluation['consistency'] = consistency
        
        if consistency['status'] == 'inconsistent':
            evaluation['actions'].append({
                'action': 'IMPROVE_CONSISTENCY',
                'reason': 'Performance too volatile',
                'recommendation': 'Focus on high-confidence setups only'
            })
        
        return evaluation
    
    def _check_consistency(self) -> Dict:
        """
        Check profit consistency over time
        
        Consistent profit > large volatile swings
        """
        if len(self.daily_results) < 7:
            return {'status': 'insufficient_data'}
        
        recent_returns = [r['return_pct'] for r in self.daily_results[-7:]]
        
        # Calculate metrics
        avg_return = statistics.mean(recent_returns)
        std_return = statistics.stdev(recent_returns) if len(recent_returns) > 1 else 0
        
        # Positive days
        positive_days = sum(1 for r in recent_returns if r > 0)
        consistency_ratio = positive_days / len(recent_returns)
        
        # Consistency score
        if consistency_ratio >= 0.70 and std_return < 0.03:
            status = 'very_consistent'
        elif consistency_ratio >= 0.60 and std_return < 0.05:
            status = 'consistent'
        elif consistency_ratio >= 0.50:
            status = 'moderately_consistent'
        else:
            status = 'inconsistent'
        
        return {
            'status': status,
            'positive_days': positive_days,
            'consistency_ratio': consistency_ratio,
            'avg_return': avg_return,
            'volatility': std_return,
            'recommendation': self._get_consistency_recommendation(status)
        }
    
    def _get_consistency_recommendation(self, status: str) -> str:
        """Get recommendation based on consistency"""
        recommendations = {
            'very_consistent': 'Maintain current approach - excellent consistency',
            'consistent': 'Good consistency - continue with slight optimization',
            'moderately_consistent': 'Improve trade selection criteria',
            'inconsistent': 'Focus on high-confidence setups only, reduce trading frequency'
        }
        return recommendations.get(status, 'Monitor performance')
    
    def check_profit_extraction(self, current_capital: float) -> Optional[Dict]:
        """
        Check if profits should be extracted
        
        Systematic profit-taking prevents giving back gains
        """
        self.current_capital = current_capital
        
        growth = (current_capital - self.initial_capital) / self.initial_capital
        
        if growth >= self.extraction_threshold:
            profit = current_capital - self.initial_capital
            extraction_amount = profit * self.extraction_percentage
            
            return {
                'should_extract': True,
                'amount': extraction_amount,
                'remaining_capital': current_capital - extraction_amount,
                'growth': growth,
                'reason': f'Account grew {growth:.1%} - extracting {self.extraction_percentage:.0%} of profit'
            }
        
        return None
    
    def calculate_scaling_parameters(self, current_capital: float) -> Dict:
        """
        Calculate position sizing and targets based on capital level
        
        Auto-scales as capital grows
        """
        # Find current milestone
        current_milestone = None
        next_milestone = None
        
        for i, milestone in enumerate(self.scaling_milestones):
            if current_capital >= milestone['capital']:
                current_milestone = milestone
            else:
                next_milestone = milestone
                break
        
        if current_milestone is None:
            current_milestone = self.scaling_milestones[0]
        
        # Calculate scaling factor
        if next_milestone:
            progress = (current_capital - current_milestone['capital']) / \
                      (next_milestone['capital'] - current_milestone['capital'])
        else:
            progress = 1.0
        
        # Base position size scales with capital
        base_position_size = min(0.15, 0.08 + (current_capital / 10000) * 0.05)
        
        return {
            'current_milestone': current_milestone,
            'next_milestone': next_milestone,
            'progress_to_next': progress,
            'base_position_size': base_position_size,
            'daily_target_gbp': current_milestone['daily_target'],
            'daily_target_pct': current_milestone['daily_target'] / current_capital,
            'scaling_recommendations': self._get_scaling_recommendations(current_capital)
        }
    
    def _get_scaling_recommendations(self, capital: float) -> List[str]:
        """Get recommendations for current capital level"""
        recommendations = []
        
        if capital < 1000:
            recommendations.append("Focus on consistency over growth")
            recommendations.append("Build track record with current capital")
            recommendations.append("Extract 50% of profits at £200 gain")
        elif capital < 2500:
            recommendations.append("Maintain consistent profitability")
            recommendations.append("Start increasing position sizes gradually")
            recommendations.append("Extract profits at 20% account growth")
        elif capital < 5000:
            recommendations.append("Optimize for risk-adjusted returns")
            recommendations.append("Diversify across multiple strategies")
            recommendations.append("Consider adding more trading pairs")
        else:
            recommendations.append("Professional capital management")
            recommendations.append("Regular profit extraction")
            recommendations.append("Consider options strategies")
        
        return recommendations
    
    def get_consistency_report(self) -> Dict:
        """Generate consistency report"""
        if len(self.daily_results) < 5:
            return {'error': 'Insufficient data'}
        
        # Calculate metrics
        total_days = len(self.daily_results)
        profitable_days = sum(1 for d in self.daily_results if d['pnl'] > 0)
        losing_days = sum(1 for d in self.daily_results if d['pnl'] < 0)
        
        total_profit = sum(d['pnl'] for d in self.daily_results if d['pnl'] > 0)
        total_loss = sum(d['pnl'] for d in self.daily_results if d['pnl'] < 0)
        
        avg_win = total_profit / profitable_days if profitable_days > 0 else 0
        avg_loss = total_loss / losing_days if losing_days > 0 else 0
        
        return {
            'total_days': total_days,
            'profitable_days': profitable_days,
            'losing_days': losing_days,
            'win_day_rate': profitable_days / total_days,
            'avg_daily_win': avg_win,
            'avg_daily_loss': avg_loss,
            'profit_factor': abs(total_profit / total_loss) if total_loss != 0 else 0,
            'consistency_score': self._calculate_consistency_score()
        }
    
    def _calculate_consistency_score(self) -> float:
        """
        Calculate overall consistency score (0-100)
        
        Higher = more consistent profits
        """
        if len(self.daily_results) < 7:
            return 50
        
        recent = self.daily_results[-30:]
        
        # Factors
        positive_ratio = sum(1 for d in recent if d['pnl'] > 0) / len(recent)
        target_met_ratio = sum(1 for d in recent if d['met_target']) / len(recent)
        
        returns = [d['return_pct'] for d in recent]
        volatility = statistics.stdev(returns) if len(returns) > 1 else 1
        
        # Score calculation
        score = (
            positive_ratio * 40 +        # 40 points for positive days
            target_met_ratio * 40 +      # 40 points for meeting targets
            (1 - min(1, volatility * 10)) * 20  # 20 points for low volatility
        )
        
        return min(100, max(0, score))


# Global instance
consistent_profit_engine = ConsistentProfitEngine()
