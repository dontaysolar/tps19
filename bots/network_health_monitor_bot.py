#!/usr/bin/env python3
"""Network Health Monitor - Track blockchain network metrics"""
import numpy as np
from datetime import datetime
from typing import Dict

class NetworkHealthMonitorBot:
    def __init__(self):
        self.name = "Network_Health_Monitor"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'health_checks': 0}
    
    def assess_network_health(self, network_data: Dict) -> Dict:
        """Assess blockchain network health"""
        health_score = 100
        issues = []
        
        # Active addresses
        active_addresses = network_data.get('active_addresses', 0)
        historical_avg = network_data.get('avg_active_addresses', 0)
        
        if active_addresses < historical_avg * 0.7:
            health_score -= 20
            issues.append('Low network activity')
        
        # Transaction count
        tx_count = network_data.get('transactions_24h', 0)
        avg_tx = network_data.get('avg_transactions', 0)
        
        if tx_count < avg_tx * 0.6:
            health_score -= 15
            issues.append('Reduced transaction volume')
        
        # Hash rate (for PoW chains)
        hash_rate = network_data.get('hash_rate', 0)
        if hash_rate < network_data.get('avg_hash_rate', 0) * 0.8:
            health_score -= 10
            issues.append('Declining hash rate')
        
        self.metrics['health_checks'] += 1
        
        if health_score >= 85:
            status = 'HEALTHY'
            signal = 'BUY'
        elif health_score >= 65:
            status = 'NORMAL'
            signal = 'HOLD'
        else:
            status = 'UNHEALTHY'
            signal = 'SELL'
        
        return {
            'health_score': health_score,
            'status': status,
            'signal': signal,
            'confidence': 0.70 if health_score != 100 else 0.85,
            'issues': issues,
            'metrics': {
                'active_addresses': active_addresses,
                'transactions_24h': tx_count,
                'hash_rate': hash_rate
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = NetworkHealthMonitorBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
