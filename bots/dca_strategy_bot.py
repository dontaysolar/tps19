#!/usr/bin/env python3
"""
DCA (Dollar Cost Averaging) Strategy Bot
Averages down on dips to lower cost basis
Part of APEX AI Trading System
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

try:
    import ccxt
except ImportError:
    os.system("pip3 install --break-system-packages ccxt -q")
    import ccxt

class DCAStrategyBot:
    """Implements Dollar Cost Averaging strategy"""
    
    def __init__(self, exchange_config=None):
        self.name = "DCAStrategyBot"
        self.version = "1.0.0"
        
        if exchange_config:
            self.exchange = ccxt.cryptocom(exchange_config)
        else:
            from dotenv import load_dotenv
            load_dotenv()
            self.exchange = ccxt.cryptocom({
                'apiKey': os.getenv('EXCHANGE_API_KEY'),
                'secret': os.getenv('EXCHANGE_API_SECRET'),
                'enableRateLimit': True
            })
        
        self.config = {
            'dip_threshold_pct': 3.0,        # 3% dip to trigger DCA
            'max_dca_levels': 3,              # Max 3 DCA levels
            'dca_size_multiplier': 1.5,       # 1.5x size on each DCA
            'min_time_between_dca': 3600      # 1 hour between DCAs
        }
        
        self.positions = {}
        
        self.metrics = {
            'dca_triggers': 0,
            'total_dca_amount': 0.0,
            'positions_saved': 0
        }
    
    def add_position(self, symbol: str, entry_price: float, amount: float) -> str:
        """Add position for DCA tracking"""
        pos_id = f"{symbol}_{datetime.now().timestamp()}"
        
        self.positions[pos_id] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'current_amount': amount,
            'total_cost': entry_price * amount,
            'dca_levels': 0,
            'last_dca': None,
            'dca_prices': [entry_price],
            'created_at': datetime.now().isoformat()
        }
        
        return pos_id
    
    def check_dca_opportunity(self, pos_id: str, current_price: float) -> Dict:
        """Check if DCA opportunity exists"""
        if pos_id not in self.positions:
            return {'should_dca': False}
        
        pos = self.positions[pos_id]
        
        # Check if max DCAs reached
        if pos['dca_levels'] >= self.config['max_dca_levels']:
            return {'should_dca': False, 'reason': 'Max DCA levels reached'}
        
        # Check time since last DCA
        if pos['last_dca']:
            last_dca_time = datetime.fromisoformat(pos['last_dca'])
            time_since = (datetime.now() - last_dca_time).total_seconds()
            
            if time_since < self.config['min_time_between_dca']:
                return {'should_dca': False, 'reason': 'Too soon since last DCA'}
        
        # Check price drop
        avg_entry = pos['total_cost'] / pos['current_amount']
        drop_pct = ((avg_entry - current_price) / avg_entry) * 100
        
        if drop_pct >= self.config['dip_threshold_pct']:
            # Calculate DCA size
            dca_size = pos['current_amount'] * (self.config['dca_size_multiplier'] ** pos['dca_levels'])
            
            return {
                'should_dca': True,
                'drop_pct': drop_pct,
                'dca_size': dca_size,
                'dca_level': pos['dca_levels'] + 1,
                'current_avg': avg_entry,
                'new_price': current_price
            }
        
        return {'should_dca': False, 'reason': f'Drop only {drop_pct:.2f}%'}
    
    def execute_dca(self, pos_id: str, current_price: float) -> Dict:
        """Execute DCA buy"""
        if pos_id not in self.positions:
            return {'success': False, 'error': 'Position not found'}
        
        opportunity = self.check_dca_opportunity(pos_id, current_price)
        
        if not opportunity['should_dca']:
            return {'success': False, 'reason': opportunity.get('reason', 'No DCA needed')}
        
        pos = self.positions[pos_id]
        dca_size = opportunity['dca_size']
        
        # Update position
        pos['total_cost'] += current_price * dca_size
        pos['current_amount'] += dca_size
        pos['dca_levels'] += 1
        pos['last_dca'] = datetime.now().isoformat()
        pos['dca_prices'].append(current_price)
        
        # Calculate new average
        new_avg = pos['total_cost'] / pos['current_amount']
        old_avg = opportunity['current_avg']
        avg_improvement = ((old_avg - new_avg) / old_avg) * 100
        
        self.metrics['dca_triggers'] += 1
        self.metrics['total_dca_amount'] += dca_size
        
        return {
            'success': True,
            'symbol': pos['symbol'],
            'dca_level': pos['dca_levels'],
            'dca_size': dca_size,
            'dca_price': current_price,
            'old_avg': old_avg,
            'new_avg': new_avg,
            'avg_improvement_pct': avg_improvement,
            'total_amount': pos['current_amount']
        }
    
    def get_position_status(self, pos_id: str) -> Dict:
        """Get DCA position status"""
        if pos_id not in self.positions:
            return {}
        
        pos = self.positions[pos_id]
        avg_entry = pos['total_cost'] / pos['current_amount']
        
        return {
            'symbol': pos['symbol'],
            'average_entry': avg_entry,
            'total_amount': pos['current_amount'],
            'total_cost': pos['total_cost'],
            'dca_levels': pos['dca_levels'],
            'dca_prices': pos['dca_prices'],
            'last_dca': pos['last_dca']
        }
    
    def get_status(self) -> Dict:
        """Get bot status"""
        return {
            'name': self.name,
            'version': self.version,
            'active_positions': len(self.positions),
            'metrics': self.metrics,
            'config': self.config
        }

if __name__ == '__main__':
    bot = DCAStrategyBot()
    print("📊 DCA Strategy Bot - Test Mode\n")
    
    # Simulate position with price drops
    pos_id = bot.add_position('BTC/USDT', 50000, 0.001)
    print(f"✅ Position created: {pos_id}")
    
    # Simulate 5% drop
    result = bot.execute_dca(pos_id, 47500)
    if result['success']:
        print(f"\n💰 DCA executed:")
        print(f"   Level: {result['dca_level']}")
        print(f"   Size: {result['dca_size']:.6f}")
        print(f"   Old avg: ${result['old_avg']:.2f}")
        print(f"   New avg: ${result['new_avg']:.2f}")
        print(f"   Improvement: {result['avg_improvement_pct']:.2f}%")
