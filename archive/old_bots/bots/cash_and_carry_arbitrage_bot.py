#!/usr/bin/env python3
"""Cash and Carry Arbitrage - Spot vs futures arbitrage"""
from datetime import datetime
from typing import Dict

class CashAndCarryArbitrageBot:
    def __init__(self):
        self.name = "Cash_And_Carry_Arbitrage"
        self.version = "1.0.0"
        self.enabled = True
        
        self.min_basis_pct = 0.01  # 1% minimum basis
        
        self.metrics = {'opportunities': 0, 'positions': 0}
    
    def analyze_cash_and_carry(self, spot_price: float, futures_price: float,
                               days_to_expiry: int, funding_cost: float = 0) -> Dict:
        """Analyze cash and carry arbitrage opportunity"""
        
        # Calculate basis (futures premium over spot)
        basis = futures_price - spot_price
        basis_pct = (basis / spot_price) * 100
        
        # Annualized return
        if days_to_expiry > 0:
            annualized_return = (basis_pct / days_to_expiry) * 365
        else:
            return {'error': 'Invalid days to expiry'}
        
        # Account for costs
        net_basis_pct = basis_pct - funding_cost
        net_annualized_return = (net_basis_pct / days_to_expiry) * 365
        
        # Check if opportunity exists
        if net_basis_pct > self.min_basis_pct:
            self.metrics['opportunities'] += 1
            
            # Strategy: Buy spot, Short futures
            return {
                'opportunity': True,
                'strategy': 'BUY_SPOT_SHORT_FUTURES',
                'spot_price': spot_price,
                'futures_price': futures_price,
                'basis': basis,
                'basis_pct': basis_pct,
                'days_to_expiry': days_to_expiry,
                'annualized_return_pct': annualized_return,
                'net_annualized_return_pct': net_annualized_return,
                'funding_cost': funding_cost,
                'signal': 'EXECUTE',
                'confidence': 0.85,
                'reason': f"Cash-and-carry: {net_annualized_return:.2f}% annual return",
                'timestamp': datetime.now().isoformat()
            }
        
        # Check reverse opportunity (contango too steep)
        elif basis_pct < -self.min_basis_pct:
            return {
                'opportunity': True,
                'strategy': 'SHORT_SPOT_LONG_FUTURES',
                'basis_pct': basis_pct,
                'signal': 'EXECUTE_REVERSE',
                'confidence': 0.75,
                'reason': 'Reverse cash-and-carry opportunity'
            }
        
        return {
            'opportunity': False,
            'basis_pct': basis_pct,
            'net_basis_pct': net_basis_pct,
            'reason': 'Basis below threshold'
        }
    
    def calculate_risk_adjusted_size(self, opportunity: Dict, account_balance: float) -> Dict:
        """Calculate position size for cash-and-carry"""
        
        # Calculate expected return
        annual_return = opportunity.get('net_annualized_return_pct', 0)
        
        # Position sizing based on return
        if annual_return > 20:
            allocation_pct = 0.30  # 30% allocation for great returns
        elif annual_return > 10:
            allocation_pct = 0.20
        else:
            allocation_pct = 0.10
        
        position_size = account_balance * allocation_pct
        
        # Calculate expected profit
        days_to_expiry = opportunity.get('days_to_expiry', 30)
        holding_period_return = (annual_return / 365) * days_to_expiry
        expected_profit = position_size * (holding_period_return / 100)
        
        return {
            'position_size': position_size,
            'allocation_pct': allocation_pct * 100,
            'expected_profit': expected_profit,
            'holding_period_days': days_to_expiry,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'min_basis_pct': self.min_basis_pct,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = CashAndCarryArbitrageBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
