#!/usr/bin/env python3
"""Position Sizer - Calculate optimal position sizes"""
from datetime import datetime
from typing import Dict

class PositionSizerBot:
    def __init__(self):
        self.name = "Position_Sizer"
        self.version = "1.0.0"
        self.enabled = True
        
        self.risk_per_trade = 0.01  # 1% of capital per trade
        self.max_position_pct = 0.10  # Max 10% of capital
        
        self.metrics = {'calculations': 0}
    
    def calculate_position_size(self, account_balance: float, entry_price: float,
                               stop_loss_price: float, confidence: float = 1.0) -> Dict:
        """Calculate position size based on risk"""
        
        # Risk amount
        risk_amount = account_balance * self.risk_per_trade
        
        # Adjust for confidence
        adjusted_risk = risk_amount * confidence
        
        # Calculate position size
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            return {'error': 'Stop loss equals entry price'}
        
        position_size = adjusted_risk / risk_per_unit
        position_value = position_size * entry_price
        
        # Check max position limit
        max_position_value = account_balance * self.max_position_pct
        
        if position_value > max_position_value:
            position_size = max_position_value / entry_price
            position_value = max_position_value
            limited = True
        else:
            limited = False
        
        # Position as % of account
        position_pct = (position_value / account_balance) * 100
        
        # Risk/Reward
        potential_loss = position_size * risk_per_unit
        potential_loss_pct = (potential_loss / account_balance) * 100
        
        self.metrics['calculations'] += 1
        
        return {
            'position_size': position_size,
            'position_value': position_value,
            'position_pct': position_pct,
            'potential_loss': potential_loss,
            'potential_loss_pct': potential_loss_pct,
            'confidence_applied': confidence,
            'limited_by_max': limited,
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_risk_reward_size(self, account_balance: float, entry_price: float,
                                   stop_loss_price: float, target_price: float) -> Dict:
        """Calculate size based on risk/reward ratio"""
        
        risk_per_unit = abs(entry_price - stop_loss_price)
        reward_per_unit = abs(target_price - entry_price)
        
        if risk_per_unit == 0:
            return {'error': 'Invalid stop loss'}
        
        rr_ratio = reward_per_unit / risk_per_unit
        
        # Base calculation
        base_calc = self.calculate_position_size(account_balance, entry_price, stop_loss_price)
        
        # Adjust for R:R
        if rr_ratio < 2.0:
            # Poor R:R, reduce size
            adjustment = 0.5
        elif rr_ratio < 3.0:
            adjustment = 0.75
        else:
            # Great R:R, full size
            adjustment = 1.0
        
        base_calc['position_size'] *= adjustment
        base_calc['position_value'] *= adjustment
        base_calc['rr_ratio'] = rr_ratio
        base_calc['rr_adjustment'] = adjustment
        
        return base_calc
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'risk_per_trade_pct': self.risk_per_trade * 100,
            'max_position_pct': self.max_position_pct * 100,
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = PositionSizerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
