#!/usr/bin/env python3
"""Tax Loss Harvesting - Optimize tax liability through strategic loss realization"""
from datetime import datetime
from typing import Dict, List

class TaxLossHarvestingBot:
    def __init__(self):
        self.name = "Tax_Loss_Harvesting"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'harvests': 0, 'tax_saved_est': 0}
    
    def identify_harvest_opportunities(self, positions: List[Dict], tax_rate: float = 0.30) -> Dict:
        """Identify positions with unrealized losses for tax harvesting"""
        opportunities = []
        
        for pos in positions:
            cost_basis = pos.get('cost_basis', 0)
            current_value = pos.get('current_value', 0)
            unrealized_pnl = current_value - cost_basis
            
            if unrealized_pnl < 0:  # Loss position
                tax_benefit = abs(unrealized_pnl) * tax_rate
                
                opportunities.append({
                    'symbol': pos.get('symbol'),
                    'unrealized_loss': abs(unrealized_pnl),
                    'tax_benefit': tax_benefit,
                    'recommendation': 'HARVEST' if tax_benefit > 10 else 'KEEP'
                })
        
        total_harvestable = sum([o['unrealized_loss'] for o in opportunities if o['recommendation'] == 'HARVEST'])
        total_tax_benefit = sum([o['tax_benefit'] for o in opportunities if o['recommendation'] == 'HARVEST'])
        
        self.metrics['harvests'] += 1
        self.metrics['tax_saved_est'] += total_tax_benefit
        
        return {
            'opportunities': opportunities,
            'total_harvestable_loss': total_harvestable,
            'estimated_tax_benefit': total_tax_benefit,
            'positions_to_harvest': len([o for o in opportunities if o['recommendation'] == 'HARVEST']),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = TaxLossHarvestingBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
