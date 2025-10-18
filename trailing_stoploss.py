#!/usr/bin/env python3
"""
Trailing Stop-Loss Manager
Dynamically adjusts stop-loss to follow price up
"""

import os
import sys
import json
from datetime import datetime

class TrailingStopLoss:
    """Manages trailing stop-losses for open positions"""
    
    def __init__(self, db_path='data/trailing_stops.json'):
        self.db_path = db_path
        self.positions = self.load_positions()
        
    def load_positions(self):
        """Load active positions from file"""
        if not os.path.exists(self.db_path):
            return {}
        
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_positions(self):
        """Save positions to file"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def add_position(self, symbol, entry_price, amount, stop_loss_percent=2.0, trailing_percent=1.5):
        """
        Add a new position with trailing stop-loss
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            entry_price: Entry price
            amount: Position size
            stop_loss_percent: Initial stop-loss distance (%)
            trailing_percent: Trailing distance (%)
        """
        position_id = f"{symbol}_{datetime.now().timestamp()}"
        
        initial_stop = entry_price * (1 - stop_loss_percent / 100)
        
        self.positions[position_id] = {
            'symbol': symbol,
            'entry_price': entry_price,
            'amount': amount,
            'stop_loss': initial_stop,
            'highest_price': entry_price,
            'trailing_percent': trailing_percent,
            'stop_loss_percent': stop_loss_percent,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.save_positions()
        
        return position_id
    
    def update_price(self, symbol, current_price):
        """
        Update trailing stop-loss based on current price
        
        Returns: List of positions to close (if stop-loss hit)
        """
        to_close = []
        
        for pos_id, pos in self.positions.items():
            if pos['symbol'] != symbol:
                continue
            
            # Update highest price if new high
            if current_price > pos['highest_price']:
                pos['highest_price'] = current_price
                
                # Calculate new trailing stop
                new_stop = current_price * (1 - pos['trailing_percent'] / 100)
                
                # Only move stop-loss UP (trailing)
                if new_stop > pos['stop_loss']:
                    old_stop = pos['stop_loss']
                    pos['stop_loss'] = new_stop
                    pos['updated_at'] = datetime.now().isoformat()
                    
                    print(f"📈 {symbol} trailing SL updated: ${old_stop:.2f} → ${new_stop:.2f}")
            
            # Check if stop-loss hit
            if current_price <= pos['stop_loss']:
                profit = (current_price - pos['entry_price']) * pos['amount']
                profit_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                
                to_close.append({
                    'position_id': pos_id,
                    'symbol': symbol,
                    'entry': pos['entry_price'],
                    'exit': current_price,
                    'amount': pos['amount'],
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'reason': 'TRAILING_SL'
                })
        
        self.save_positions()
        
        return to_close
    
    def remove_position(self, position_id):
        """Remove a closed position"""
        if position_id in self.positions:
            del self.positions[position_id]
            self.save_positions()
    
    def get_position_status(self, symbol):
        """Get all positions for a symbol"""
        return [pos for pos_id, pos in self.positions.items() if pos['symbol'] == symbol]
    
    def get_all_positions(self):
        """Get all active positions"""
        return self.positions

if __name__ == '__main__':
    # Test trailing stop-loss
    tsl = TrailingStopLoss()
    
    # Simulate BTC position
    pos_id = tsl.add_position('BTC/USDT', 50000, 0.001, stop_loss_percent=2.0, trailing_percent=1.5)
    print(f"✅ Position created: {pos_id}")
    
    # Simulate price movements
    prices = [50000, 51000, 52000, 53000, 52500, 52000, 51000]
    
    for price in prices:
        print(f"\n💰 Price: ${price}")
        closed = tsl.update_price('BTC/USDT', price)
        
        if closed:
            for close_data in closed:
                print(f"🛑 Position closed: {close_data['reason']}")
                print(f"   Entry: ${close_data['entry']:.2f}")
                print(f"   Exit: ${close_data['exit']:.2f}")
                print(f"   P&L: ${close_data['profit']:.2f} ({close_data['profit_pct']:.2f}%)")
                tsl.remove_position(close_data['position_id'])
