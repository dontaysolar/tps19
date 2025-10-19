#!/usr/bin/env python3
"""Trailing Stop Bot - Dynamic stop loss that trails price"""
from datetime import datetime
from typing import Dict

class TrailingStopBot:
    def __init__(self):
        self.name = "Trailing_Stop"
        self.version = "1.0.0"
        self.enabled = True
        
        self.trail_percent = 0.03  # 3% trail
        self.active_trails = {}
        
        self.metrics = {'stops_created': 0, 'stops_triggered': 0}
    
    def create_trailing_stop(self, position_id: str, entry_price: float, 
                            side: str, trail_percent: float = None) -> Dict:
        """Create trailing stop for position"""
        trail_pct = trail_percent or self.trail_percent
        
        if side == 'LONG':
            initial_stop = entry_price * (1 - trail_pct)
        else:  # SHORT
            initial_stop = entry_price * (1 + trail_pct)
        
        self.active_trails[position_id] = {
            'entry_price': entry_price,
            'side': side,
            'trail_percent': trail_pct,
            'current_stop': initial_stop,
            'highest_price': entry_price if side == 'LONG' else None,
            'lowest_price': entry_price if side == 'SHORT' else None,
            'created_at': datetime.now().isoformat()
        }
        
        self.metrics['stops_created'] += 1
        
        return {
            'position_id': position_id,
            'initial_stop': initial_stop,
            'trail_percent': trail_pct * 100,
            'status': 'ACTIVE'
        }
    
    def update_trailing_stop(self, position_id: str, current_price: float) -> Dict:
        """Update trailing stop based on price"""
        if position_id not in self.active_trails:
            return {'error': 'Position not found'}
        
        trail = self.active_trails[position_id]
        side = trail['side']
        trail_pct = trail['trail_percent']
        
        stop_triggered = False
        
        if side == 'LONG':
            # Update highest price
            if current_price > trail['highest_price']:
                trail['highest_price'] = current_price
                new_stop = current_price * (1 - trail_pct)
                
                # Only move stop up, never down
                if new_stop > trail['current_stop']:
                    trail['current_stop'] = new_stop
            
            # Check if stop triggered
            if current_price <= trail['current_stop']:
                stop_triggered = True
                self.metrics['stops_triggered'] += 1
        
        else:  # SHORT
            # Update lowest price
            if current_price < trail['lowest_price']:
                trail['lowest_price'] = current_price
                new_stop = current_price * (1 + trail_pct)
                
                # Only move stop down, never up
                if new_stop < trail['current_stop']:
                    trail['current_stop'] = new_stop
            
            # Check if stop triggered
            if current_price >= trail['current_stop']:
                stop_triggered = True
                self.metrics['stops_triggered'] += 1
        
        if stop_triggered:
            del self.active_trails[position_id]
        
        return {
            'position_id': position_id,
            'current_price': current_price,
            'stop_price': trail['current_stop'],
            'stop_triggered': stop_triggered,
            'unrealized_gain': current_price - trail['entry_price'] if side == 'LONG' else trail['entry_price'] - current_price,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'trail_percent': self.trail_percent * 100,
            'active_positions': len(self.active_trails),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = TrailingStopBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
