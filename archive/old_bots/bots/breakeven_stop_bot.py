#!/usr/bin/env python3
"""Breakeven Stop Bot - Moves stop to entry after profit target"""
from datetime import datetime
from typing import Dict

class BreakevenStopBot:
    def __init__(self):
        self.name = "Breakeven_Stop"
        self.version = "1.0.0"
        self.enabled = True
        
        self.trigger_percent = 0.015  # Move to BE after 1.5% profit
        self.be_offset = 0.001  # Small offset above/below entry
        
        self.active_positions = {}
        self.metrics = {'be_stops_set': 0, 'be_exits': 0}
    
    def monitor_position(self, position_id: str, entry_price: float, 
                        current_price: float, side: str) -> Dict:
        """Monitor position for breakeven stop trigger"""
        
        if position_id not in self.active_positions:
            self.active_positions[position_id] = {
                'entry_price': entry_price,
                'side': side,
                'be_stop_set': False,
                'stop_price': None
            }
        
        position = self.active_positions[position_id]
        
        # Calculate profit
        if side == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
            
            if profit_pct >= self.trigger_percent and not position['be_stop_set']:
                # Set breakeven stop
                be_stop = entry_price * (1 + self.be_offset)
                position['be_stop_set'] = True
                position['stop_price'] = be_stop
                self.metrics['be_stops_set'] += 1
                
                return {
                    'action': 'BE_STOP_SET',
                    'stop_price': be_stop,
                    'current_profit_pct': profit_pct * 100,
                    'message': f"Breakeven stop set at ${be_stop:.2f}"
                }
            
            # Check if BE stop triggered
            if position['be_stop_set'] and current_price <= position['stop_price']:
                self.metrics['be_exits'] += 1
                del self.active_positions[position_id]
                
                return {
                    'action': 'BE_STOP_TRIGGERED',
                    'exit_price': current_price,
                    'profit_loss': current_price - entry_price,
                    'message': 'Breakeven stop triggered - minimal loss/gain'
                }
        
        else:  # SHORT
            profit_pct = (entry_price - current_price) / entry_price
            
            if profit_pct >= self.trigger_percent and not position['be_stop_set']:
                be_stop = entry_price * (1 - self.be_offset)
                position['be_stop_set'] = True
                position['stop_price'] = be_stop
                self.metrics['be_stops_set'] += 1
                
                return {
                    'action': 'BE_STOP_SET',
                    'stop_price': be_stop,
                    'current_profit_pct': profit_pct * 100
                }
            
            if position['be_stop_set'] and current_price >= position['stop_price']:
                self.metrics['be_exits'] += 1
                del self.active_positions[position_id]
                
                return {
                    'action': 'BE_STOP_TRIGGERED',
                    'exit_price': current_price,
                    'profit_loss': entry_price - current_price
                }
        
        return {
            'action': 'MONITORING',
            'be_stop_set': position['be_stop_set'],
            'current_profit_pct': profit_pct * 100 if 'profit_pct' in locals() else 0
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'trigger_percent': self.trigger_percent * 100,
            'active_positions': len(self.active_positions),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = BreakevenStopBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
