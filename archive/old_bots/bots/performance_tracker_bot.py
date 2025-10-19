#!/usr/bin/env python3
"""
Performance Tracker Bot
Comprehensive performance analytics
Tracks all system metrics and KPIs
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class PerformanceTrackerBot:
    def __init__(self):
        self.name = "Performance_Tracker"
        self.version = "1.0.0"
        self.enabled = True
        
        self.trade_history = []
        self.equity_curve = []
        self.daily_returns = []
        
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
    
    def record_trade(self, trade: Dict):
        """Record completed trade"""
        self.trade_history.append(trade)
        
        pnl = trade.get('pnl', 0)
        self.metrics['total_pnl'] += pnl
        self.metrics['total_trades'] += 1
        
        if pnl > 0:
            self.metrics['winning_trades'] += 1
        else:
            self.metrics['losing_trades'] += 1
        
        # Update win rate
        self.metrics['win_rate'] = self.metrics['winning_trades'] / self.metrics['total_trades'] if self.metrics['total_trades'] > 0 else 0
        
        # Update profit factor
        gross_profit = sum([t.get('pnl', 0) for t in self.trade_history if t.get('pnl', 0) > 0])
        gross_loss = abs(sum([t.get('pnl', 0) for t in self.trade_history if t.get('pnl', 0) < 0]))
        self.metrics['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else 0
    
    def update_equity_curve(self, current_equity: float):
        """Update equity curve"""
        self.equity_curve.append({
            'equity': current_equity,
            'timestamp': datetime.now().isoformat()
        })
        
        # Calculate daily returns
        if len(self.equity_curve) > 1:
            prev_equity = self.equity_curve[-2]['equity']
            daily_return = (current_equity - prev_equity) / prev_equity if prev_equity > 0 else 0
            self.daily_returns.append(daily_return)
            
            # Update Sharpe ratio
            if len(self.daily_returns) >= 30:
                mean_return = np.mean(self.daily_returns[-30:])
                std_return = np.std(self.daily_returns[-30:])
                self.metrics['sharpe_ratio'] = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0
            
            # Update max drawdown
            peak = max([e['equity'] for e in self.equity_curve])
            drawdown = (peak - current_equity) / peak if peak > 0 else 0
            self.metrics['max_drawdown'] = max(self.metrics['max_drawdown'], drawdown)
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            'total_trades': self.metrics['total_trades'],
            'win_rate': self.metrics['win_rate'] * 100,
            'profit_factor': self.metrics['profit_factor'],
            'total_pnl': self.metrics['total_pnl'],
            'sharpe_ratio': self.metrics['sharpe_ratio'],
            'max_drawdown_pct': self.metrics['max_drawdown'] * 100,
            'avg_win': np.mean([t.get('pnl', 0) for t in self.trade_history if t.get('pnl', 0) > 0]) if self.metrics['winning_trades'] > 0 else 0,
            'avg_loss': abs(np.mean([t.get('pnl', 0) for t in self.trade_history if t.get('pnl', 0) < 0])) if self.metrics['losing_trades'] > 0 else 0,
            'current_equity': self.equity_curve[-1]['equity'] if self.equity_curve else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'metrics': self.metrics,
            'total_trades_recorded': len(self.trade_history),
            'equity_data_points': len(self.equity_curve),
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    tracker = PerformanceTrackerBot()
    print(f"✅ {tracker.name} v{tracker.version} initialized")
