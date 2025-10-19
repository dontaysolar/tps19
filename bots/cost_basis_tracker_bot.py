#!/usr/bin/env python3
"""Cost Basis Tracker - FIFO, LIFO, HIFO tracking for tax optimization"""
from datetime import datetime
from typing import Dict, List

class CostBasisTrackerBot:
    def __init__(self):
        self.name = "Cost_Basis_Tracker"
        self.version = "1.0.0"
        self.enabled = True
        
        self.method = 'FIFO'  # FIFO, LIFO, HIFO
        self.lots = {}  # {symbol: [lots]}
        
        self.metrics = {'lots_tracked': 0, 'sales_calculated': 0}
    
    def add_purchase(self, symbol: str, quantity: float, price: float, timestamp: str = None):
        """Add purchase lot"""
        if symbol not in self.lots:
            self.lots[symbol] = []
        
        self.lots[symbol].append({
            'quantity': quantity,
            'price': price,
            'timestamp': timestamp or datetime.now().isoformat(),
            'remaining': quantity
        })
        
        self.metrics['lots_tracked'] += 1
    
    def calculate_cost_basis(self, symbol: str, sell_quantity: float, sell_price: float) -> Dict:
        """Calculate cost basis and gain/loss for sale"""
        if symbol not in self.lots or not self.lots[symbol]:
            return {'error': 'No lots found for symbol'}
        
        lots_to_use = self.lots[symbol].copy()
        
        # Sort based on method
        if self.method == 'FIFO':
            lots_to_use.sort(key=lambda x: x['timestamp'])
        elif self.method == 'LIFO':
            lots_to_use.sort(key=lambda x: x['timestamp'], reverse=True)
        elif self.method == 'HIFO':
            lots_to_use.sort(key=lambda x: x['price'], reverse=True)  # Highest cost first
        
        remaining_to_sell = sell_quantity
        total_cost = 0
        used_lots = []
        
        for lot in lots_to_use:
            if remaining_to_sell <= 0:
                break
            
            quantity_from_lot = min(lot['remaining'], remaining_to_sell)
            cost_from_lot = quantity_from_lot * lot['price']
            
            total_cost += cost_from_lot
            remaining_to_sell -= quantity_from_lot
            
            used_lots.append({
                'quantity': quantity_from_lot,
                'cost_basis': lot['price'],
                'cost': cost_from_lot
            })
            
            lot['remaining'] -= quantity_from_lot
        
        avg_cost_basis = total_cost / sell_quantity if sell_quantity > 0 else 0
        proceeds = sell_quantity * sell_price
        gain_loss = proceeds - total_cost
        gain_loss_pct = (gain_loss / total_cost * 100) if total_cost > 0 else 0
        
        self.metrics['sales_calculated'] += 1
        
        return {
            'sell_quantity': sell_quantity,
            'sell_price': sell_price,
            'avg_cost_basis': avg_cost_basis,
            'total_cost': total_cost,
            'proceeds': proceeds,
            'gain_loss': gain_loss,
            'gain_loss_pct': gain_loss_pct,
            'method': self.method,
            'lots_used': len(used_lots),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'method': self.method,
            'tracked_symbols': len(self.lots),
            'total_lots': sum([len(lots) for lots in self.lots.values()]),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    bot = CostBasisTrackerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
