#!/usr/bin/env python3
"""
Kelly Criterion Position Sizing Bot
Calculates optimal position size using Kelly formula:
f* = (bp - q) / b
where:
f* = fraction of capital to bet
b = odds (reward/risk ratio)
p = probability of win
q = probability of loss (1-p)
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class KellyCriterionBot:
    def __init__(self):
        self.name = "Kelly_Criterion"
        self.version = "1.0.0"
        self.enabled = True
        
        self.max_kelly = 0.25  # Cap at 25% (1/4 Kelly for safety)
        self.min_kelly = 0.01  # Minimum 1%
        
        self.trade_history = []
        
        self.metrics = {
            'calculations': 0,
            'avg_position_size': 0,
            'max_size_recommended': 0
        }
    
    def calculate_position_size(self, 
                               win_probability: float,
                               win_loss_ratio: float,
                               current_capital: float,
                               risk_per_trade: float = 0.02) -> Dict:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            win_probability: Probability of winning (0-1)
            win_loss_ratio: Average win / average loss
            current_capital: Current account balance
            risk_per_trade: Max risk per trade (default 2%)
        """
        
        # Kelly formula: f* = (bp - q) / b
        b = win_loss_ratio
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Apply safety constraints
        kelly_fraction = max(min(kelly_fraction, self.max_kelly), 0)
        
        # Calculate position sizes
        kelly_position_size = current_capital * kelly_fraction
        half_kelly = kelly_position_size * 0.5  # Conservative
        quarter_kelly = kelly_position_size * 0.25  # Very conservative
        
        # Risk-based position size
        risk_based_size = current_capital * risk_per_trade
        
        # Recommended: Use 1/2 Kelly for safety
        recommended_size = half_kelly
        recommended_percent = (half_kelly / current_capital) * 100
        
        # Update metrics
        self.metrics['calculations'] += 1
        self.metrics['avg_position_size'] = (
            (self.metrics['avg_position_size'] * (self.metrics['calculations'] - 1) + recommended_percent) /
            self.metrics['calculations']
        )
        self.metrics['max_size_recommended'] = max(
            self.metrics['max_size_recommended'], 
            recommended_percent
        )
        
        return {
            'full_kelly': kelly_fraction * 100,
            'half_kelly': kelly_fraction * 50,
            'quarter_kelly': kelly_fraction * 25,
            'recommended_percent': recommended_percent,
            'recommended_size_usd': recommended_size,
            'kelly_position_size': kelly_position_size,
            'half_kelly_size': half_kelly,
            'quarter_kelly_size': quarter_kelly,
            'risk_based_size': risk_based_size,
            'edge': (b * p - q),
            'is_positive_edge': kelly_fraction > 0,
            'recommendation': self._get_recommendation(kelly_fraction, win_probability),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_optimal_size_from_history(self, trade_history: List[Dict]) -> Dict:
        """
        Calculate Kelly from historical trades
        
        Args:
            trade_history: List of {result: 'win'/'loss', pnl: float}
        """
        if not trade_history:
            return {'error': 'No trade history'}
        
        wins = [t for t in trade_history if t['result'] == 'win']
        losses = [t for t in trade_history if t['result'] == 'loss']
        
        if not wins or not losses:
            return {'error': 'Need both wins and losses'}
        
        # Calculate statistics
        num_wins = len(wins)
        num_losses = len(losses)
        total_trades = len(trade_history)
        
        win_probability = num_wins / total_trades
        
        avg_win = np.mean([abs(t['pnl']) for t in wins])
        avg_loss = np.mean([abs(t['pnl']) for t in losses])
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Calculate Kelly
        return self.calculate_position_size(
            win_probability=win_probability,
            win_loss_ratio=win_loss_ratio,
            current_capital=1000,  # Normalized
            risk_per_trade=0.02
        )
    
    def estimate_from_strategy_stats(self,
                                    win_rate: float,
                                    avg_win: float,
                                    avg_loss: float,
                                    capital: float) -> Dict:
        """
        Calculate Kelly from strategy statistics
        
        Args:
            win_rate: Win rate (0-1)
            avg_win: Average winning trade %
            avg_loss: Average losing trade %
            capital: Current capital
        """
        win_loss_ratio = abs(avg_win) / abs(avg_loss) if avg_loss != 0 else 1
        
        result = self.calculate_position_size(
            win_probability=win_rate,
            win_loss_ratio=win_loss_ratio,
            current_capital=capital
        )
        
        result['strategy_stats'] = {
            'win_rate': win_rate * 100,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'expectancy': (win_rate * avg_win) - ((1 - win_rate) * abs(avg_loss))
        }
        
        return result
    
    def _get_recommendation(self, kelly_fraction: float, win_prob: float) -> str:
        """Get human-readable recommendation"""
        if kelly_fraction <= 0:
            return "❌ NO EDGE - Do not trade this setup"
        elif kelly_fraction < 0.05:
            return "⚠️ WEAK EDGE - Trade very small (1-2%)"
        elif kelly_fraction < 0.15:
            return "✅ GOOD EDGE - Trade moderate size (5-10%)"
        elif kelly_fraction < 0.25:
            return "🔥 STRONG EDGE - Trade larger size (10-15%)"
        else:
            return "⚡ EXCEPTIONAL EDGE - Trade max size (15-25%)"
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'max_kelly': self.max_kelly * 100,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = KellyCriterionBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
    
    # Example calculation
    result = bot.calculate_position_size(
        win_probability=0.60,
        win_loss_ratio=2.0,
        current_capital=1000
    )
    print(f"Recommended position: {result['recommended_percent']:.1f}%")
