#!/usr/bin/env python3
"""
Thrones AI - Strategy Backtesting & Validation
Tests strategies across historical data
Provides comprehensive performance metrics
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

class ThronesAI:
    def __init__(self):
        self.name = "Thrones_AI"
        self.version = "2.0.0"
        self.enabled = True
        self.power_level = 95
        
        # Backtesting configuration
        self.initial_capital = 10000
        self.commission = 0.001  # 0.1%
        self.slippage = 0.0005  # 0.05%
        
        self.backtest_results = {}
        
        self.metrics = {
            'strategies_tested': 0,
            'total_backtests': 0,
            'best_strategy': None,
            'best_sharpe_ratio': 0.0
        }
    
    def backtest_strategy(self, strategy_func, ohlcv: List, initial_capital: float = None) -> Dict:
        """
        Backtest a trading strategy on historical data
        
        Args:
            strategy_func: Function that takes OHLCV and returns signals
            ohlcv: Historical OHLCV data
            initial_capital: Starting capital
        """
        capital = initial_capital or self.initial_capital
        position = 0  # Current position size
        entry_price = 0
        trades = []
        equity_curve = [capital]
        
        for i in range(50, len(ohlcv)):
            # Get strategy signal
            try:
                signal = strategy_func(ohlcv[:i+1])
                
                current_price = ohlcv[i][4]
                
                # Execute trades based on signal
                if signal == 'BUY' and position == 0:
                    # Enter long position
                    position_size = capital * 0.95  # Use 95% of capital
                    position = position_size / (current_price * (1 + self.commission + self.slippage))
                    entry_price = current_price * (1 + self.commission + self.slippage)
                    capital -= position_size
                    
                    trades.append({
                        'type': 'BUY',
                        'price': entry_price,
                        'size': position,
                        'time': i
                    })
                
                elif signal == 'SELL' and position > 0:
                    # Exit long position
                    exit_price = current_price * (1 - self.commission - self.slippage)
                    pnl = (exit_price - entry_price) * position
                    capital += position * exit_price
                    
                    trades.append({
                        'type': 'SELL',
                        'price': exit_price,
                        'size': position,
                        'pnl': pnl,
                        'return_pct': (pnl / (entry_price * position)) * 100,
                        'time': i
                    })
                    
                    position = 0
                
                # Track equity
                current_equity = capital + (position * current_price if position > 0 else 0)
                equity_curve.append(current_equity)
                
            except Exception as e:
                continue
        
        # Close any open position
        if position > 0:
            final_price = ohlcv[-1][4]
            exit_price = final_price * (1 - self.commission - self.slippage)
            pnl = (exit_price - entry_price) * position
            capital += position * exit_price
            
            trades.append({
                'type': 'SELL',
                'price': exit_price,
                'size': position,
                'pnl': pnl,
                'return_pct': (pnl / (entry_price * position)) * 100,
                'time': len(ohlcv) - 1
            })
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(trades, equity_curve, initial_capital or self.initial_capital)
        
        self.metrics['total_backtests'] += 1
        
        # Update best strategy
        if metrics['sharpe_ratio'] > self.metrics['best_sharpe_ratio']:
            self.metrics['best_sharpe_ratio'] = metrics['sharpe_ratio']
            self.metrics['best_strategy'] = strategy_func.__name__ if hasattr(strategy_func, '__name__') else 'unknown'
        
        return {
            'initial_capital': initial_capital or self.initial_capital,
            'final_capital': capital,
            'total_return': metrics['total_return'],
            'total_return_pct': metrics['total_return_pct'],
            'n_trades': len([t for t in trades if t['type'] == 'SELL']),
            'winning_trades': metrics['winning_trades'],
            'losing_trades': metrics['losing_trades'],
            'win_rate': metrics['win_rate'],
            'avg_win': metrics['avg_win'],
            'avg_loss': metrics['avg_loss'],
            'profit_factor': metrics['profit_factor'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'max_drawdown': metrics['max_drawdown'],
            'max_drawdown_pct': metrics['max_drawdown_pct'],
            'equity_curve': equity_curve,
            'trades': trades,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_performance_metrics(self, trades, equity_curve, initial_capital) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not trades:
            return {
                'total_return': 0, 'total_return_pct': 0,
                'winning_trades': 0, 'losing_trades': 0,
                'win_rate': 0, 'avg_win': 0, 'avg_loss': 0,
                'profit_factor': 0, 'sharpe_ratio': 0,
                'max_drawdown': 0, 'max_drawdown_pct': 0
            }
        
        # Filter sell trades (complete round trips)
        closed_trades = [t for t in trades if t['type'] == 'SELL']
        
        if not closed_trades:
            return {
                'total_return': 0, 'total_return_pct': 0,
                'winning_trades': 0, 'losing_trades': 0,
                'win_rate': 0, 'avg_win': 0, 'avg_loss': 0,
                'profit_factor': 0, 'sharpe_ratio': 0,
                'max_drawdown': 0, 'max_drawdown_pct': 0
            }
        
        # Returns
        total_return = sum([t.get('pnl', 0) for t in closed_trades])
        total_return_pct = (total_return / initial_capital) * 100
        
        # Win/Loss analysis
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('pnl', 0) <= 0]
        
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 0
        
        # Profit factor
        total_wins = sum([t['pnl'] for t in winning_trades])
        total_losses = abs(sum([t['pnl'] for t in losing_trades]))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Sharpe ratio
        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
        
        # Maximum drawdown
        peak = equity_curve[0]
        max_dd = 0
        max_dd_pct = 0
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = peak - equity
            dd_pct = (dd / peak) * 100 if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        return {
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd_pct
        }
    
    def validate_strategy(self, backtest_result: Dict) -> Dict:
        """
        Validate strategy based on performance metrics
        Returns validation score and recommendations
        """
        score = 0
        issues = []
        recommendations = []
        
        # Check win rate
        if backtest_result['win_rate'] >= 0.60:
            score += 25
        elif backtest_result['win_rate'] >= 0.50:
            score += 15
        else:
            issues.append(f"Low win rate: {backtest_result['win_rate']:.1%}")
            recommendations.append("Improve entry criteria")
        
        # Check profit factor
        if backtest_result['profit_factor'] >= 2.0:
            score += 25
        elif backtest_result['profit_factor'] >= 1.5:
            score += 15
        else:
            issues.append(f"Low profit factor: {backtest_result['profit_factor']:.2f}")
            recommendations.append("Increase profit targets or reduce losses")
        
        # Check Sharpe ratio
        if backtest_result['sharpe_ratio'] >= 2.0:
            score += 25
        elif backtest_result['sharpe_ratio'] >= 1.0:
            score += 15
        else:
            issues.append(f"Low Sharpe ratio: {backtest_result['sharpe_ratio']:.2f}")
            recommendations.append("Reduce volatility of returns")
        
        # Check drawdown
        if backtest_result['max_drawdown_pct'] <= 10:
            score += 25
        elif backtest_result['max_drawdown_pct'] <= 20:
            score += 15
        else:
            issues.append(f"High drawdown: {backtest_result['max_drawdown_pct']:.1f}%")
            recommendations.append("Implement tighter stop losses")
        
        # Overall assessment
        if score >= 80:
            assessment = "EXCELLENT - Strategy ready for live trading"
        elif score >= 60:
            assessment = "GOOD - Minor improvements needed"
        elif score >= 40:
            assessment = "FAIR - Significant improvements required"
        else:
            assessment = "POOR - Strategy not recommended"
        
        return {
            'validation_score': score,
            'assessment': assessment,
            'issues': issues,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'power_level': self.power_level,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    ai = ThronesAI()
    print(f"✅ {ai.name} v{ai.version} - Power Level: {ai.power_level}")
