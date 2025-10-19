#!/usr/bin/env python3
"""Profit Target Ladder - Scaled exits at multiple targets"""
from datetime import datetime
from typing import Dict, List

class ProfitTargetLadderBot:
    def __init__(self):
        self.name = "Profit_Target_Ladder"
        self.version = "1.0.0"
        self.enabled = True
        
        # Default ladder: 25% at +2%, 25% at +5%, 50% at +10%
        self.default_ladder = [
            {'pct_gain': 2.0, 'position_pct': 25},
            {'pct_gain': 5.0, 'position_pct': 25},
            {'pct_gain': 10.0, 'position_pct': 50}
        ]
        
        self.metrics = {'ladders_created': 0, 'exits_executed': 0}
    
    def create_ladder(self, entry_price: float, position_size: float, 
                     custom_ladder: List[Dict] = None) -> Dict:
        """Create profit target ladder"""
        ladder = custom_ladder or self.default_ladder
        
        targets = []
        remaining_position = position_size
        
        for level in ladder:
            target_price = entry_price * (1 + level['pct_gain'] / 100)
            exit_size = position_size * (level['position_pct'] / 100)
            
            targets.append({
                'target_price': target_price,
                'exit_size': exit_size,
                'gain_pct': level['pct_gain'],
                'position_pct': level['position_pct'],
                'status': 'PENDING',
                'potential_profit': (target_price - entry_price) * exit_size
            })
            
            remaining_position -= exit_size
        
        self.metrics['ladders_created'] += 1
        
        return {
            'entry_price': entry_price,
            'total_position': position_size,
            'targets': targets,
            'total_potential_profit': sum([t['potential_profit'] for t in targets]),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_targets(self, current_price: float, targets: List[Dict]) -> Dict:
        """Check if any targets hit"""
        hits = []
        
        for target in targets:
            if target['status'] == 'PENDING' and current_price >= target['target_price']:
                target['status'] = 'HIT'
                target['executed_price'] = current_price
                target['actual_profit'] = (current_price - target.get('entry_price', 0)) * target['exit_size']
                hits.append(target)
                self.metrics['exits_executed'] += 1
        
        return {
            'current_price': current_price,
            'targets_hit': len(hits),
            'hits': hits,
            'pending_targets': len([t for t in targets if t['status'] == 'PENDING']),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'default_ladder': self.default_ladder, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = ProfitTargetLadderBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
