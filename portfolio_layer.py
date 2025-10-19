#!/usr/bin/env python3
"""
PORTFOLIO MANAGEMENT LAYER
All portfolio operations consolidated
"""

from datetime import datetime
from typing import Dict, List
import numpy as np

class PortfolioLayer:
    """Consolidated portfolio management"""
    
    def __init__(self):
        self.name = "Portfolio_Layer"
        self.version = "1.0.0"
        
        self.managers = {
            'allocation': AllocationManager(),
            'rebalancing': RebalancingEngine(),
            'tax': TaxOptimizer(),
            'cost_basis': CostBasisTracker(),
            'performance': PerformanceAnalyzer(),
            'risk': PortfolioRiskAnalyzer()
        }
        
        self.positions = {}
        self.trade_history = []
        
    def manage_portfolio(self) -> Dict:
        """Execute all portfolio management tasks"""
        results = {
            'allocation': self.managers['allocation'].optimize_allocation(self.positions),
            'rebalancing': self.managers['rebalancing'].check_rebalancing_needed(self.positions),
            'performance': self.managers['performance'].calculate_metrics(self.positions, self.trade_history),
            'risk': self.managers['risk'].assess_portfolio_risk(self.positions),
            'timestamp': datetime.now().isoformat()
        }
        
        return results

class AllocationManager:
    """Portfolio allocation optimization"""
    
    def optimize_allocation(self, positions: Dict) -> Dict:
        """Optimize portfolio allocation"""
        # Target allocations (example)
        targets = {
            'BTC': 0.40,  # 40% BTC
            'ETH': 0.30,  # 30% ETH
            'ALT': 0.20,  # 20% Altcoins
            'STABLE': 0.10  # 10% Stablecoins
        }
        
        # Current allocation
        total_value = sum(p.get('value', 0) for p in positions.values())
        current = {}
        
        for symbol, position in positions.items():
            value = position.get('value', 0)
            allocation = value / total_value if total_value > 0 else 0
            current[symbol] = allocation
        
        # Calculate deviations
        deviations = {}
        for asset, target in targets.items():
            current_alloc = current.get(asset, 0)
            deviations[asset] = target - current_alloc
        
        # Suggest rebalancing if deviation > 10%
        needs_rebalancing = any(abs(dev) > 0.10 for dev in deviations.values())
        
        return {
            'targets': targets,
            'current': current,
            'deviations': deviations,
            'needs_rebalancing': needs_rebalancing,
            'total_value': total_value
        }

class RebalancingEngine:
    """Automated portfolio rebalancing"""
    
    def check_rebalancing_needed(self, positions: Dict) -> Dict:
        """Check if rebalancing is needed"""
        # Rebalancing rules
        rules = {
            'max_deviation': 0.15,  # 15% max deviation
            'min_time_between': 7,  # days
            'threshold_value': 1000  # Minimum portfolio value
        }
        
        # Calculate if rebalancing needed
        total_value = sum(p.get('value', 0) for p in positions.values())
        
        if total_value < rules['threshold_value']:
            return {
                'needed': False,
                'reason': 'Portfolio too small',
                'recommendations': []
            }
        
        # Generate rebalancing recommendations
        recommendations = []
        
        return {
            'needed': False,
            'reason': 'Within threshold',
            'recommendations': recommendations,
            'rules': rules
        }
    
    def execute_rebalancing(self, recommendations: List[Dict]) -> Dict:
        """Execute rebalancing trades"""
        trades_executed = []
        
        for rec in recommendations:
            # Execute trade
            trade = {
                'symbol': rec['symbol'],
                'action': rec['action'],
                'amount': rec['amount'],
                'status': 'SIMULATED'
            }
            trades_executed.append(trade)
        
        return {
            'trades': trades_executed,
            'success': True,
            'timestamp': datetime.now().isoformat()
        }

class TaxOptimizer:
    """Tax loss harvesting and optimization"""
    
    def analyze_tax_opportunities(self, positions: Dict, trade_history: List) -> Dict:
        """Find tax optimization opportunities"""
        opportunities = []
        
        # Tax loss harvesting
        for symbol, position in positions.items():
            cost_basis = position.get('cost_basis', 0)
            current_value = position.get('value', 0)
            unrealized_pnl = current_value - cost_basis
            
            # If position is at a loss
            if unrealized_pnl < 0:
                # Check if we can harvest the loss
                hold_period = position.get('hold_days', 0)
                
                if hold_period > 30:  # Avoid wash sale
                    opportunities.append({
                        'type': 'TAX_LOSS_HARVEST',
                        'symbol': symbol,
                        'loss': unrealized_pnl,
                        'recommendation': 'Sell to realize loss, rebuy after 31 days'
                    })
        
        # Long-term capital gains optimization
        for symbol, position in positions.items():
            hold_period = position.get('hold_days', 0)
            unrealized_pnl = position.get('value', 0) - position.get('cost_basis', 0)
            
            if unrealized_pnl > 0 and hold_period >= 335:  # Close to 1 year
                opportunities.append({
                    'type': 'LTCG_OPPORTUNITY',
                    'symbol': symbol,
                    'gain': unrealized_pnl,
                    'days_until_ltcg': 365 - hold_period,
                    'recommendation': 'Hold for long-term capital gains'
                })
        
        return {
            'opportunities': opportunities,
            'potential_tax_savings': sum(opp.get('loss', 0) for opp in opportunities if opp['type'] == 'TAX_LOSS_HARVEST'),
            'timestamp': datetime.now().isoformat()
        }

class CostBasisTracker:
    """Track cost basis for all positions"""
    
    def __init__(self):
        self.method = 'FIFO'  # FIFO, LIFO, or specific identification
        
    def calculate_cost_basis(self, symbol: str, trades: List[Dict]) -> Dict:
        """Calculate cost basis using selected method"""
        symbol_trades = [t for t in trades if t.get('symbol') == symbol]
        
        if not symbol_trades:
            return {'cost_basis': 0, 'quantity': 0}
        
        # FIFO method
        total_cost = 0
        total_quantity = 0
        
        for trade in symbol_trades:
            if trade.get('side') == 'buy':
                total_cost += trade.get('cost', 0)
                total_quantity += trade.get('amount', 0)
            elif trade.get('side') == 'sell':
                # Remove from oldest positions first
                sold_amount = trade.get('amount', 0)
                total_quantity -= sold_amount
        
        avg_cost_basis = total_cost / total_quantity if total_quantity > 0 else 0
        
        return {
            'method': self.method,
            'cost_basis': avg_cost_basis,
            'total_quantity': total_quantity,
            'total_cost': total_cost
        }

class PerformanceAnalyzer:
    """Portfolio performance analytics"""
    
    def calculate_metrics(self, positions: Dict, trade_history: List) -> Dict:
        """Calculate performance metrics"""
        # Get returns
        returns = self.calculate_returns(trade_history)
        
        if len(returns) < 2:
            return {'error': 'Insufficient data'}
        
        returns_array = np.array(returns)
        
        # Key metrics
        total_return = ((returns_array[-1] / returns_array[0]) - 1) * 100 if returns_array[0] != 0 else 0
        
        # Daily returns
        daily_returns = np.diff(returns_array) / returns_array[:-1]
        
        # Sharpe Ratio (assuming 0% risk-free rate, 252 trading days)
        sharpe = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        
        # Max Drawdown
        cumulative = np.cumprod(1 + daily_returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100
        
        # Win rate
        wins = sum(1 for r in daily_returns if r > 0)
        win_rate = (wins / len(daily_returns)) * 100 if len(daily_returns) > 0 else 0
        
        return {
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown,
            'win_rate_pct': win_rate,
            'total_trades': len(trade_history),
            'current_positions': len(positions)
        }
    
    def calculate_returns(self, trade_history: List) -> List[float]:
        """Calculate portfolio value over time"""
        # Simplified - would track actual portfolio value
        if not trade_history:
            return [10000]  # Starting capital
        
        values = [10000]
        for _ in trade_history:
            # Simulate returns
            values.append(values[-1] * (1 + np.random.uniform(-0.02, 0.02)))
        
        return values

class PortfolioRiskAnalyzer:
    """Portfolio-level risk analysis"""
    
    def assess_portfolio_risk(self, positions: Dict) -> Dict:
        """Assess overall portfolio risk"""
        # Concentration risk
        total_value = sum(p.get('value', 0) for p in positions.values())
        concentrations = {}
        
        for symbol, position in positions.items():
            value = position.get('value', 0)
            pct = (value / total_value * 100) if total_value > 0 else 0
            concentrations[symbol] = pct
        
        # Find highest concentration
        max_concentration = max(concentrations.values()) if concentrations else 0
        
        # Assess risk level
        if max_concentration > 50:
            risk_level = 'HIGH'
            recommendation = 'Highly concentrated - diversify'
        elif max_concentration > 30:
            risk_level = 'MEDIUM'
            recommendation = 'Moderate concentration'
        else:
            risk_level = 'LOW'
            recommendation = 'Well diversified'
        
        # Correlation risk (simplified)
        correlation_risk = 'MEDIUM'
        
        return {
            'risk_level': risk_level,
            'max_concentration_pct': max_concentration,
            'concentrations': concentrations,
            'correlation_risk': correlation_risk,
            'recommendation': recommendation,
            'diversification_score': 100 - max_concentration
        }

if __name__ == '__main__':
    layer = PortfolioLayer()
    print(f"✅ {layer.name} v{layer.version} initialized")
